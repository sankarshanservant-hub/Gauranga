extends Node2D
## Нитьянанда — технический тест ходьбы v0.5 (варианты длины шага) (Godot 4.3). См. README_RU.md.
##
## Один исходный рисунок разложен на 7 слоёв (tools/build_rig.py → rig.json, assets/).
## Жёсткие части — Sprite2D: корпус с головой (без вращения), две стопы.
## Ткань и рука — Polygon2D с сеткой; вершины считаются в скрипте (линейное смешивание
## костей по весам из rig.json). Ноги под дхоти — виртуальные цепи бедро→колено→щиколотка
## с двухзвенной IK; рисунка голеней нет, он и не нужен, пока дхоти их закрывает.

# Параметры походки — начальная гипотеза из planning_landmarks.json, не норма.
var G := {
	"cycle": 1.2,          # с, полный цикл (два шага)
	"amp": 70.0,           # px холста: ход стопы вперёд и назад относительно корпуса
	"duty": 0.6,           # доля цикла в опоре (двойная опора 2 × 0.1)
	"heel_phase": 0.08,    # касание пяткой, носок опускается
	"heel_off": 0.42,      # начало отрыва пятки
	"toe_up_deg": 5.0,     # носок вверх при касании
	"heel_up_deg": 14.0,   # пятка вверх при отталкивании
	# Перенос: стопа наклоняется носком вниз (щиколотка поднимается, колено сгибается),
	# затем выравнивается и перед касанием носок слегка вверх; нога разгибается.
	"swing_pitch_deg": 30.0,  # наибольший наклон стопы носком вниз в начале переноса
	"pitch_peak": 0.22,       # доля переноса, где наклон наибольший
	"flat_at": 0.65,          # доля переноса, где стопа ровная
	"clearance": 12.0,        # px, наибольший зазор нижней точки подошвы над землёй
	"min_knee_deg": 5.0,      # колено в опоре не выпрямляется полностью
	"bob": 1.5,            # px, вертикальное движение корпуса
	"bob_high": 0.0,       # фаза, где корпус выше всего (касание пяткой)
	# v0.4: общий центр хода обеих стоп (≈625 px по подушечке) — каждая стопа обгоняет другую
	# примерно на 120 px. В рисунке ближняя стопа стоит на 94 px позади дальней, поэтому центры
	# сдвинуты навстречу: ближняя +47, дальняя −47 от положения в покое (в v0.3: +10 / −10).
	"near_center": 47.0,   # px, центр хода ближней стопы относительно её положения в покое
	"far_center": -47.0,   # px, то же для дальней
	"arm_deg": 4.0,        # мах видимой руки в плече
	"elbow_deg": 4.0,      # дополнительный сгиб локтя при махе вперёд
	"shawl_deg": 1.0,      # колебание шали
	"shawl_trail_deg": 1.0,  # отставание шали при продвижении
	"knee_slack": 0.003,   # запас длины ноги в покое: колено в покое согнуто ≈9°
}

enum Mode { REST, IN_PLACE, FORWARD }
const MODE_NAMES := ["REST", "WALK_IN_PLACE", "WALK_FORWARD"]
var forward_cycles := 4   # после стольких циклов продвижение начинается заново

# v0.5: варианты длины шага. A — v0.4; B и C — шаг длиннее на 25 % и 40 %, перебирание ног медленнее.
# Скорость корпуса не задаётся: v = 2·amp / (duty·cycle) — опорная стопа не скользит.
const VARIANTS := {
	"A": {"amp": 70.0, "cycle": 1.2, "title": "A: как v0.4"},
	"B": {"amp": 87.5, "cycle": 1.35, "title": "B: шаг +25 %, цикл 1,35 с"},
	"C": {"amp": 98.0, "cycle": 1.45, "title": "C: шаг +40 %, цикл 1,45 с"},
}
var variant := "A"
# Пороги разметки ткани (σ — растяжение/сжатие треугольника сетки относительно покоя).
const STRETCH_HI := 1.2
const STRETCH_LO := 0.8
const STRETCH_WARN := 0.08   # предупреждение: в пределах 0,08 до порога

var mode: int = Mode.REST
var t := 0.0
var speed := 1.0
var paused := false
var show_debug := false
var show_ground := false   # линия земли и следы опоры без костей
var show_stretch := false  # разметка растяжения/сжатия ткани
var show_mesh := false
var show_synth := false
var show_orig := false
var show_hud := true
var log_knees := false  # печать углов колена и зазора стоп по кадрам (проверка)
var only_layer := ""   # отладка: показать один слой

var view_scale := 0.56
var view_origin := Vector2(349, 68)
var forward_origin_x := -128.0

var rig: Dictionary
var figure := Node2D.new()
var overlay := Node2D.new()
var orig_sprite := Sprite2D.new()
var caption := Label.new()
var meshes: Array = []
var rigids: Array = []
var R := {}
var legs := {}
var M := {}
var feet := {}
var root_off := Vector2.ZERO
var world_x := 0.0
var max_drift := {"near": 0.0, "far": 0.0}
var anchor := {"near": NAN, "far": NAN}
var prints: Array = []


func _ready() -> void:
	rig = JSON.parse_string(FileAccess.get_file_as_string("res://rig.json"))
	for k in rig.bones_rest:
		R[k] = Vector2(rig.bones_rest[k][0], rig.bones_rest[k][1])
	for side in ["near", "far"]:
		var lg := {
			"hip": R[side + "_hip"], "ankle": R[side + "_ankle"], "heel": R[side + "_heel"],
			"ball": R[side + "_ball"], "toe": R[side + "_toe"],
			"phase": 0.0 if side == "near" else 0.5,
		}
		lg.l = lg.hip.distance_to(lg.ankle) * 0.5 * (1.0 + G.knee_slack)
		lg.knee = _ik(lg.hip, lg.ankle, lg.l, lg.l)
		lg.center = lg.ball.x + G[side + "_center"]
		legs[side] = lg
	_parse_args()
	add_child(figure)
	figure.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	_build_layers()
	orig_sprite.texture = load("res://" + rig.source)
	orig_sprite.centered = false
	orig_sprite.modulate = Color(1, 1, 1, 0.5)
	figure.add_child(orig_sprite)
	figure.add_child(overlay)
	overlay.draw.connect(_draw_overlay)
	var ui := CanvasLayer.new()
	add_child(ui)
	caption.position = Vector2(16, 10)
	caption.add_theme_color_override("font_color", Color(0.18, 0.16, 0.14))
	caption.add_theme_font_size_override("font_size", 15)
	ui.add_child(caption)
	_apply_view()
	_update_pose()


func _parse_args() -> void:
	for a in OS.get_cmdline_user_args():
		var kv: PackedStringArray = a.trim_prefix("--").split("=")
		match kv[0]:
			"mode":
				mode = {"rest": Mode.REST, "in_place": Mode.IN_PLACE, "forward": Mode.FORWARD}[kv[1]]
			"debug": show_debug = true
			"mesh": show_mesh = true
			"synth": show_synth = true
			"orig": show_orig = true
			"nohud": show_hud = false
			"slow": speed = float(kv[1])
			"start": t = float(kv[1]) * G.cycle
			"scale": view_scale = float(kv[1])
			"ox": view_origin.x = float(kv[1])
			"oy": view_origin.y = float(kv[1])
			"only": only_layer = kv[1]
			"logknees": log_knees = true
			"variant": _set_variant(kv[1])
			"ground": show_ground = true
			"stretch": show_stretch = true
			"cycles": forward_cycles = int(kv[1])
			"fx": forward_origin_x = float(kv[1])
			"compare":
				# 1:1 с исходным холстом для попиксельного сравнения покоя
				view_scale = 1.0
				view_origin = Vector2.ZERO
				show_hud = false
				mode = Mode.REST


func _set_variant(v: String) -> void:
	variant = v
	G.amp = VARIANTS[v].amp
	G.cycle = VARIANTS[v].cycle


func _tex(path: String) -> Texture2D:
	var img: Image = load("res://" + path).get_image()
	if img.is_compressed():
		img.decompress()
	if view_scale < 1.0:
		img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


func _build_layers() -> void:
	for L in rig.layers:
		var origin := Vector2(L.origin[0], L.origin[1])
		var tex := _tex(L.texture)
		var tex_d := _tex(L.texture_diag)
		if L.has("rigid"):
			var holder := Node2D.new()
			holder.name = L.name
			figure.add_child(holder)
			var sp := Sprite2D.new()
			sp.texture = tex
			sp.centered = false
			sp.position = origin
			holder.add_child(sp)
			rigids.append({"holder": holder, "bone": L.rigid, "item": sp, "tex": tex, "tex_d": tex_d})
		else:
			var m: Dictionary = L.mesh
			var rest := PackedVector2Array()
			var uv := PackedVector2Array()
			for i in range(0, m.verts.size(), 2):
				var p := Vector2(m.verts[i], m.verts[i + 1])
				rest.append(p)
				uv.append(p - origin)
			var polys := []
			for i in range(0, m.tris.size(), 3):
				polys.append(PackedInt32Array([int(m.tris[i]), int(m.tris[i + 1]), int(m.tris[i + 2])]))
			var poly := Polygon2D.new()
			poly.name = L.name
			poly.texture = tex
			poly.polygon = rest
			poly.uv = uv
			poly.polygons = polys
			figure.add_child(poly)
			var bones: Array = []
			var ws: Array = []
			for b in m.weights:
				bones.append(b)
				ws.append(PackedFloat32Array(m.weights[b]))
			# для разметки ткани: обратные матрицы рёбер треугольников в покое и видимость
			var alpha_img: Image = load("res://" + L.texture).get_image()
			if alpha_img.is_compressed():
				alpha_img.decompress()
			var inv := PackedFloat32Array()
			var vis := PackedByteArray()
			for tri in polys:
				var a0 := rest[tri[0]]
				var e1 := rest[tri[1]] - a0
				var e2 := rest[tri[2]] - a0
				var det := e1.x * e2.y - e2.x * e1.y
				inv.append_array([e2.y / det, -e2.x / det, -e1.y / det, e1.x / det])
				var c := (a0 + rest[tri[1]] + rest[tri[2]]) / 3.0 - origin
				var ci := Vector2i(clampi(int(c.x), 0, alpha_img.get_width() - 1), clampi(int(c.y), 0, alpha_img.get_height() - 1))
				vis.append(1 if alpha_img.get_pixelv(ci).a > 0.0 else 0)
			meshes.append({"poly": poly, "rest": rest, "bones": bones, "w": ws, "tris": polys,
				"tex": tex, "tex_d": tex_d, "inv": inv, "vis": vis})


func _apply_view() -> void:
	figure.scale = Vector2(view_scale, view_scale)
	orig_sprite.visible = show_orig
	for r in rigids:
		r.item.texture = r.tex_d if show_synth else r.tex
	for mm in meshes:
		mm.poly.texture = mm.tex_d if show_synth else mm.tex
	caption.visible = show_hud
	if only_layer != "":
		for r in rigids:
			r.holder.visible = r.holder.name == only_layer
		for mm in meshes:
			mm.poly.visible = mm.poly.name == only_layer


func _input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_1: _set_mode(Mode.REST)
		KEY_2: _set_mode(Mode.IN_PLACE)
		KEY_3: _set_mode(Mode.FORWARD)
		KEY_4: _set_variant("A"); _set_mode(mode)
		KEY_5: _set_variant("B"); _set_mode(mode)
		KEY_6: _set_variant("C"); _set_mode(mode)
		KEY_G: show_ground = not show_ground
		KEY_T: show_stretch = not show_stretch
		KEY_SPACE: paused = not paused
		KEY_RIGHT: t += 1.0 / 30.0
		KEY_LEFT: t = max(t - 1.0 / 30.0, 0.0)
		KEY_S: speed = 0.25 if speed == 1.0 else 1.0
		KEY_D: show_debug = not show_debug
		KEY_M: show_mesh = not show_mesh
		KEY_U: show_synth = not show_synth
		KEY_O: show_orig = not show_orig
		KEY_H: show_hud = not show_hud
	_apply_view()


func _set_mode(m: int) -> void:
	mode = m
	t = 0.0
	prints.clear()
	max_drift = {"near": 0.0, "far": 0.0}
	anchor = {"near": NAN, "far": NAN}


func _process(delta: float) -> void:
	if not paused and mode != Mode.REST:
		t += delta * speed
	_update_pose()


# ---------- походка ----------

func _stance_pose(lg: Dictionary, p: float) -> Array:
	var A: float = G.amp
	var duty: float = G.duty
	var ball_cur := Vector2(lg.center + A - 2.0 * A * p / duty, lg.ball.y)
	if p < G.heel_phase:
		var th := -deg_to_rad(G.toe_up_deg) * (1.0 - smoothstep(0.0, G.heel_phase, p))
		var heel_cur: Vector2 = ball_cur - (lg.ball - lg.heel)
		return [heel_cur + (lg.ankle - lg.heel).rotated(th), th, heel_cur]
	var th2 := 0.0
	if p > G.heel_off:
		th2 = deg_to_rad(G.heel_up_deg) * smoothstep(G.heel_off, duty, p)
	return [ball_cur + (lg.ankle - lg.ball).rotated(th2), th2, ball_cur]


func _foot_pose(lg: Dictionary, p: float) -> Array:
	var duty: float = G.duty
	if p < duty:
		return _stance_pose(lg, p)
	var s := (p - duty) / (1.0 - duty)
	var a0 := _stance_pose(lg, duty)
	var a1 := _stance_pose(lg, 0.0)
	var p0: Vector2 = a0[0]
	var p1: Vector2 = a1[0]
	# Эрмит по x: на концах скорость равна ходу опорной стопы (без рывка при смене опоры)
	var m: float = -2.0 * G.amp * (1.0 - duty) / duty
	var s2 := s * s
	var s3 := s2 * s
	var x: float = (2 * s3 - 3 * s2 + 1) * p0.x + (s3 - 2 * s2 + s) * m + (-2 * s3 + 3 * s2) * p1.x + (s3 - s2) * m
	var th := _swing_pitch(s)
	# высота щиколотки из условия: нижняя точка подошвы на высоте clearance·sin(πs) над землёй
	var c: float = G.clearance * sin(PI * s)
	var y := INF
	for q in [lg.heel, lg.ball, lg.toe]:
		y = min(y, lg.ball.y - c - (q - lg.ankle).rotated(th).y)
	var ank := Vector2(x, y)
	return [ank, th, null]


func _swing_pitch(s: float) -> float:
	var a0 := deg_to_rad(G.heel_up_deg)
	var a1 := deg_to_rad(G.swing_pitch_deg)
	var a3 := -deg_to_rad(G.toe_up_deg)
	if s < G.pitch_peak:
		return lerp(a0, a1, smoothstep(0.0, G.pitch_peak, s))
	if s < G.flat_at:
		return lerp(a1, 0.0, smoothstep(G.pitch_peak, G.flat_at, s))
	return lerp(0.0, a3, smoothstep(G.flat_at, 1.0, s))


func _ik(hip: Vector2, ankle: Vector2, l1: float, l2: float) -> Vector2:
	var d: float = clamp(hip.distance_to(ankle), abs(l1 - l2) + 0.001, l1 + l2 - 0.001)
	var dir := (ankle - hip).normalized()
	var a := (l1 * l1 - l2 * l2 + d * d) / (2.0 * d)
	var h := sqrt(max(l1 * l1 - a * a, 0.0))
	return hip + dir * a + Vector2(dir.y, -dir.x) * h   # колено вперёд (вправо)


func _bone(rest_a: Vector2, rest_b: Vector2, cur_a: Vector2, cur_b: Vector2) -> Transform2D:
	var ang := (cur_b - cur_a).angle() - (rest_b - rest_a).angle()
	return Transform2D(ang, cur_a) * Transform2D(0.0, -rest_a)


func _rot_about(pivot: Vector2, ang: float) -> Transform2D:
	return Transform2D(ang, pivot) * Transform2D(0.0, -pivot)


func _update_pose() -> void:
	var cyc: float = G.cycle
	var p := fposmod(t / cyc, 1.0)
	var walking := mode != Mode.REST
	root_off = Vector2.ZERO
	world_x = 0.0
	if mode == Mode.FORWARD:
		var v: float = 2.0 * G.amp / (G.duty * cyc)   # скорость следует из хода и периода
		world_x = v * fposmod(t, cyc * forward_cycles)
	for side in legs:
		var lg: Dictionary = legs[side]
		if walking:
			feet[side] = _foot_pose(lg, fposmod(p + lg.phase, 1.0))
		else:
			feet[side] = [lg.ankle, 0.0, null]
	if walking:
		root_off.y = -G.bob * cos(TAU * 2.0 * (p - G.bob_high))
		var low := 0.0
		for side in legs:
			var lg: Dictionary = legs[side]
			var hip: Vector2 = lg.hip + root_off
			var ank: Vector2 = feet[side][0]
			var lmax: float = lg.l * 2.0 * cos(deg_to_rad(G.min_knee_deg) * 0.5)
			var dx := ank.x - hip.x
			low = max(low, (ank.y - hip.y) - sqrt(max(lmax * lmax - dx * dx, 0.0)))
		root_off.y += low
	var root := Transform2D(0.0, root_off)
	M["root"] = root
	for side in legs:
		var lg: Dictionary = legs[side]
		var hip: Vector2 = lg.hip + root_off
		var ank: Vector2 = feet[side][0]
		var knee := _ik(hip, ank, lg.l, lg.l)
		lg.cur = [hip, knee, ank]
		var t1 := knee - hip
		var t2 := ank - knee
		lg.flex = rad_to_deg(atan2(t1.cross(t2), t1.dot(t2)))   # >0 колено вперёд
		M[side + "_thigh"] = _bone(lg.hip, lg.knee, hip, knee)
		M[side + "_leg"] = _bone(lg.hip, lg.ankle, hip, ank)
		M[side + "_shin"] = _bone(lg.knee, lg.ankle, knee, ank)
		M[side + "_foot"] = Transform2D(float(feet[side][1]), ank) * Transform2D(0.0, -lg.ankle)
	var arm := 0.0
	var elbow := 0.0
	var sh_a := 0.0
	var sh_b := 0.0
	if walking:
		arm = deg_to_rad(G.arm_deg) * cos(TAU * p)          # ближняя нога впереди → рука сзади
		elbow = -deg_to_rad(G.elbow_deg) * (0.5 + 0.5 * cos(TAU * (p - 0.58)))
		var trail: float = G.shawl_trail_deg if mode == Mode.FORWARD else 0.0
		sh_a = deg_to_rad(G.shawl_deg * sin(TAU * 2.0 * p + 0.6) + trail)
		sh_b = deg_to_rad(0.6 * G.shawl_deg * sin(TAU * 2.0 * p - 0.4) + 0.5 * trail)
	M["arm_upper"] = root * _rot_about(R.shoulder, arm)
	M["arm_fore"] = M.arm_upper * _rot_about(R.elbow, elbow)
	M["shawl_a"] = root * _rot_about(R.shawl_attach, sh_a)
	M["shawl_b"] = M.shawl_a * _rot_about(R.shawl_mid, sh_b)

	for r in rigids:
		r.holder.transform = M[r.bone]
	for mm in meshes:
		var rest: PackedVector2Array = mm.rest
		var out := PackedVector2Array()
		out.resize(rest.size())
		var xf: Array = []
		for b in mm.bones:
			xf.append(M[b])
		var nb: int = xf.size()
		for i in rest.size():
			var v := rest[i]
			var acc := Vector2.ZERO
			var wsum := 0.0
			for j in nb:
				var w: float = mm.w[j][i]
				if w > 0.0:
					acc += (xf[j] * v) * w
					wsum += w
			out[i] = acc / wsum   # веса в rig.json округлены: нормируем, чтобы покой был точным
		mm.poly.polygon = out
	figure.position = view_origin
	if mode == Mode.FORWARD:
		figure.position.x = forward_origin_x + world_x * view_scale
	_track_contacts(p)
	if log_knees:
		var row := "KNEES p=%.3f" % p
		for side in legs:
			var lg: Dictionary = legs[side]
			var fm: Transform2D = M[side + "_foot"]
			var low := -INF
			for q in [lg.heel, lg.ball, lg.toe]:
				low = max(low, (fm * q).y)
			row += " %s flex=%.1f clear=%.1f" % [side, lg.flex, lg.ball.y - low]
		row += " drift_near=%.3f drift_far=%.3f root_y=%.2f" % [max_drift.near, max_drift.far, root_off.y]
		print(row)
	overlay.queue_redraw()
	_update_caption(p)


var _prev_world_x := 0.0


func _track_contacts(p: float) -> void:
	# Проверка скольжения: точка опоры (подушечка) в мировых координатах во время опоры.
	if world_x < _prev_world_x:   # фигура вернулась к началу экрана — замер начинается заново
		anchor = {"near": NAN, "far": NAN}
		prints.clear()
	_prev_world_x = world_x
	for side in legs:
		var lg: Dictionary = legs[side]
		var q := fposmod(p + lg.phase, 1.0)
		if mode == Mode.FORWARD and q >= G.heel_phase and q < G.duty:
			var ball_w: float = (M[side + "_foot"] * lg.ball).x + world_x
			if is_nan(anchor[side]):
				anchor[side] = ball_w
				prints.append(Vector2(ball_w, lg.ball.y))
				if prints.size() > 12:
					prints.pop_front()
			max_drift[side] = max(max_drift[side], abs(ball_w - anchor[side]))
		else:
			anchor[side] = NAN


func _update_caption(p: float) -> void:
	if not show_hud:
		return
	var s := "Нитьянанда — технический тест v0.5 (черновик, не утверждённая анимация)\n"
	var vv: float = 2.0 * G.amp / (G.duty * G.cycle)
	s += "вариант %s · ход стопы ±%.1f px · длина шага %.0f px · %.0f шагов/мин · скорость %.0f px/с\n" % [
		VARIANTS[variant].title, G.amp, vv * G.cycle * 0.5, 120.0 / G.cycle, vv]
	s += "режим: %s   фаза: %.2f   скорость: ×%.2f%s\n" % [MODE_NAMES[mode], p, speed, "   ПАУЗА" if paused else ""]
	if mode == Mode.FORWARD:
		s += "сдвиг опорной стопы: ближняя %.2f px, дальняя %.2f px (px холста)\n" % [max_drift.near, max_drift.far]
	if mode != Mode.REST:
		s += "сгиб колена: ближнее %.0f°, дальнее %.0f°\n" % [legs.near.flex, legs.far.flex]
	s += "1 REST · 2 WALK_IN_PLACE · 3 WALK_FORWARD · Space пауза · ←/→ кадр · S замедление\n"
	s += "4/5/6 вариант A/B/C · G линия земли · T растяжение ткани\n"
	s += "D кости и опоры · M сетка · U дорисованные участки · O исходник 50% · H скрыть текст"
	caption.text = s


# ---------- диагностика ----------

func _draw_overlay() -> void:
	var lw := 2.0 / view_scale
	if show_mesh:
		for mm in meshes:
			var pts: PackedVector2Array = mm.poly.polygon
			var lines := PackedVector2Array()
			for tri in mm.tris:
				lines.append_array([pts[tri[0]], pts[tri[1]], pts[tri[1]], pts[tri[2]], pts[tri[2]], pts[tri[0]]])
			overlay.draw_multiline(lines, Color(0, 0.6, 0.3, 0.35), 1.0 / view_scale)
	var off := -world_x
	if show_stretch:
		_draw_stretch()
	if show_ground and not show_debug:
		for side in legs:
			var gy: float = legs[side].ball.y
			overlay.draw_line(Vector2(-3000, gy + 2), Vector2(5000, gy + 2), Color(0.35, 0.33, 0.3, 0.8), lw * 0.6)
		for pr in prints:
			overlay.draw_rect(Rect2(Vector2(pr.x + off - 7, pr.y + 5), Vector2(14, 7)), Color(0.15, 0.5, 0.2))
	if not show_debug:
		return
	for side in legs:
		var lg: Dictionary = legs[side]
		var col := Color(0.85, 0.1, 0.1) if side == "near" else Color(0.1, 0.3, 0.9)
		var gy: float = lg.ball.y
		overlay.draw_line(Vector2(-3000, gy), Vector2(4000, gy), Color(col, 0.35), lw * 0.5)
		var c: Array = lg.cur
		overlay.draw_line(c[0], c[1], col, lw * 1.6)                       # бедро
		overlay.draw_line(c[1], c[2], col.darkened(0.35), lw * 1.6)        # голень
		overlay.draw_circle(c[0], 6.0 / view_scale, col)                   # тазобедренный
		overlay.draw_circle(c[1], 9.0 / view_scale, Color.WHITE)           # колено
		overlay.draw_circle(c[1], 6.0 / view_scale, col)
		overlay.draw_circle(c[2], 6.0 / view_scale, col.darkened(0.35))    # голеностоп
		var fm: Transform2D = M[side + "_foot"]
		overlay.draw_polyline(PackedVector2Array([fm * lg.heel, fm * lg.ball, fm * lg.toe]), col, lw)
		overlay.draw_circle(fm * lg.heel, 4.0 / view_scale, Color.BLACK)
		overlay.draw_circle(fm * lg.ball, 4.0 / view_scale, Color.BLACK)
		if feet[side][2] != null:
			overlay.draw_circle(feet[side][2], 9.0 / view_scale, Color(col, 0.5))
	for pr in prints:
		overlay.draw_rect(Rect2(Vector2(pr.x + off - 6, pr.y + 4), Vector2(12, 8)), Color(0.2, 0.6, 0.2))
	var ac := Color(0.1, 0.55, 0.2)
	overlay.draw_polyline(PackedVector2Array([M.arm_upper * R.shoulder, M.arm_upper * R.elbow,
		M.arm_fore * R.wrist]), ac, lw)
	var sc := Color(0.5, 0.1, 0.6)
	overlay.draw_polyline(PackedVector2Array([M.shawl_a * R.shawl_attach, M.shawl_a * R.shawl_mid,
		M.shawl_b * Vector2(400, 1100)]), sc, lw)
	var pr0: Vector2 = M.root * R.pelvis_root
	overlay.draw_line(pr0 - Vector2(14, 0), pr0 + Vector2(14, 0), Color.BLACK, lw)
	overlay.draw_line(pr0 - Vector2(0, 14), pr0 + Vector2(0, 14), Color.BLACK, lw)


func _draw_stretch() -> void:
	# Треугольники сетки дхоти и шали, растянутые/сжатые сверх порога (σ — сингулярные числа
	# отображения треугольника из покоя). Красный — растяжение > STRETCH_HI, синий — сжатие
	# < STRETCH_LO, жёлтый — в пределах STRETCH_WARN до порога.
	for mm in meshes:
		if mm.poly.name == "arm":
			continue
		var pts: PackedVector2Array = mm.poly.polygon
		var inv: PackedFloat32Array = mm.inv
		for k in mm.tris.size():
			if mm.vis[k] == 0:
				continue
			var tri: PackedInt32Array = mm.tris[k]
			var b0 := pts[tri[0]]
			var e1 := pts[tri[1]] - b0
			var e2 := pts[tri[2]] - b0
			var j00 := e1.x * inv[4 * k] + e2.x * inv[4 * k + 2]
			var j01 := e1.x * inv[4 * k + 1] + e2.x * inv[4 * k + 3]
			var j10 := e1.y * inv[4 * k] + e2.y * inv[4 * k + 2]
			var j11 := e1.y * inv[4 * k + 1] + e2.y * inv[4 * k + 3]
			var tt := j00 * j00 + j01 * j01 + j10 * j10 + j11 * j11
			var dd := j00 * j11 - j01 * j10
			var smax := sqrt((tt + sqrt(max(tt * tt - 4.0 * dd * dd, 0.0))) * 0.5)
			var smin := dd / smax
			var col := Color(0, 0, 0, 0)
			if smax > STRETCH_HI or smin < STRETCH_LO:
				col = Color(0.95, 0.1, 0.1, 0.6) if smax > STRETCH_HI else Color(0.1, 0.3, 1.0, 0.6)
			elif smax > STRETCH_HI - STRETCH_WARN or smin < STRETCH_LO + STRETCH_WARN:
				col = Color(1.0, 0.85, 0.0, 0.45)
			if col.a > 0.0:
				overlay.draw_colored_polygon(PackedVector2Array([b0, pts[tri[1]], pts[tri[2]]]), col)
