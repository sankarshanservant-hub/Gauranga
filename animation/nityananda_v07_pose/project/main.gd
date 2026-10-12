extends Node2D
## Нитьянанда — технический тест ходьбы v0.7 (по конспекту: волна корпуса, проход, ткань за коленом) (Godot 4.3). См. README_RU.md.
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
	# v0.6: пятка отрывается раньше (0.42 → 0.30 цикла), как в обычной ходьбе: иначе дальняя нога
	# в конце опоры упиралась в предел длины — колено замирало на 5° почти четверть цикла, корпус
	# проседал, а при отрыве колено сгибалось рывком. Наклон при отрыве носка прежний (14°).
	"heel_off": 0.30,      # начало отрыва пятки
	"toe_up_deg": 5.0,     # носок вверх при касании
	"heel_up_deg": 14.0,   # пятка вверх при отталкивании
	# Перенос: стопа наклоняется носком вниз (щиколотка поднимается, колено сгибается),
	# затем выравнивается и перед касанием носок слегка вверх; нога разгибается.
	"swing_pitch_deg": 30.0,  # наибольший наклон стопы носком вниз в начале переноса
	"pitch_peak": 0.22,       # доля переноса, где наклон наибольший
	"flat_at": 0.65,          # доля переноса, где стопа ровная
	"clearance": 16.0,        # px, наибольший зазор подошвы над землёй (v0.7: 12 → 16, проход читается яснее)
	"min_knee_deg": 5.0,      # колено в опоре не выпрямляется полностью
	# v0.7 (Лутц 1920, Марей 1895): корпус выше всего, когда стоит на прямой опорной ноге (проход),
	# и ниже всего сразу после касания. В v0.3–v0.6 было наоборот (выше всего при касании) и почти
	# без размаха (±1,5 px). Теперь ±4 px — умеренно, для спокойной походки.
	"bob": 4.0,            # px, вертикальное движение корпуса (половина размаха)
	"bob_high": 0.27,      # фаза, где корпус выше всего (середина опоры ближней ноги)
	"far_bulge": 0.0,      # тест позы A: компенсация v0.7 (дальняя штанина выдвигается за ближним коленом) отключена; 1 — как в v0.7
	"near_margin": 14.0,   # тест позы A: px запаса ближней штанины перед её коленом
	"bulge_margin": 14.0,  # px: запас ткани перед выдвинутым ближним коленом
	"lag": 0.04,           # доля цикла: запаздывание середины штанины за ногой (захлёст ткани)
	# v0.4: общий центр хода обеих стоп (≈625 px по подушечке) — каждая стопа обгоняет другую
	# примерно на 120 px. В рисунке ближняя стопа стоит на 94 px позади дальней, поэтому центры
	# сдвинуты навстречу: ближняя +47, дальняя −47 от положения в покое (в v0.3: +10 / −10).
	"near_center": 47.0,   # px, центр хода ближней стопы относительно её положения в покое
	"far_center": -47.0,   # px, то же для дальней
	"arm_deg": 4.0,        # мах видимой руки в плече
	"elbow_deg": 4.0,      # дополнительный сгиб локтя при махе вперёд
	"shawl_deg": 1.0,      # колебание шали
	"shawl_trail_deg": 1.0,  # отставание шали при продвижении
	# v0.6: 0.003 → 0.010. Скрытое под дхоти колено в покое согнуто ≈16° (было ≈9°): в опоре
	# нога не выпрямляется «в замок». Положение бёдер, щиколоток и стоп не меняется.
	"knee_slack": 0.010,   # запас длины ноги в покое
	"land_hold": 0.10,     # v0.6: последняя доля переноса — пятка неподвижна над точкой постановки и опускается
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
var variant := "C"
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
var log_contact := false  # печать мировых координат точек подошвы (проверка контакта)
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
var bulge_d := 0.0   # v0.7: выдвижение переднего края дхоти за ближним коленом, px
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
	_set_variant(variant)
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
			"logcontact": log_contact = true
			"set":   # отладка: --set=ключ:значение для параметров походки G
				var kv2: PackedStringArray = kv[1].split(":")
				G[kv2[0]] = float(kv2[1])
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
			var bulge := PackedFloat32Array(m.bulge) if m.has("bulge") else PackedFloat32Array()
			var edge_idx := -1   # вершина переднего края дальней штанины на высоте колена
			if bulge.size() > 0:
				var bd := INF
				for i in rest.size():
					var dd := rest[i].distance_to(R.far_front_knee)
					if dd < bd:
						bd = dd
						edge_idx = i
			var kfollow := PackedFloat32Array(m.kfollow) if m.has("kfollow") else PackedFloat32Array()
			meshes.append({"poly": poly, "rest": rest, "bones": bones, "w": ws, "tris": polys, "bulge": bulge, "edge_idx": edge_idx, "kfollow": kfollow,
				"front_edge": PackedInt32Array(m.front_edge) if m.has("front_edge") else PackedInt32Array(),
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
		th2 = _pitch_curve(p)
	return [ball_cur + (lg.ankle - lg.ball).rotated(th2), th2, ball_cur]


func _foot_pose(lg: Dictionary, p: float) -> Array:
	var duty: float = G.duty
	if p < duty:
		return _stance_pose(lg, p)
	var s := (p - duty) / (1.0 - duty)
	var a0 := _stance_pose(lg, duty - 1e-6)
	var a1 := _stance_pose(lg, 0.0)
	var m: float = -2.0 * G.amp * (1.0 - duty) / duty   # ход опорной стопы за перенос (в долях s)
	# v0.6: траектория ведётся по пятке — от её положения при отрыве носка до точки постановки
	# (в v0.5 — по щиколотке: при повороте стопы пятка перед постановкой «подкатывалась» по земле).
	# Последние land_hold переноса пятка в мире неподвижна и только опускается.
	var th := _pitch_curve(duty + s * (1.0 - duty))
	var hv: Vector2 = lg.heel - lg.ankle
	var h0: Vector2 = a0[0] + hv.rotated(float(a0[1]))
	var h1: Vector2 = a1[0] + hv.rotated(float(a1[1]))
	var s1: float = 1.0 - G.land_hold
	var hx: float
	if s > s1:
		hx = h1.x - m * (1.0 - s)
	else:
		var u := s / s1
		var u2 := u * u
		var u3 := u2 * u
		var mt := m * s1
		hx = (2 * u3 - 3 * u2 + 1) * h0.x + (u3 - 2 * u2 + u) * mt + (-2 * u3 + 3 * u2) * (h1.x - m * (1.0 - s1)) + (u3 - u2) * mt
	var x: float = hx - hv.rotated(th).x
	# высота щиколотки из условия: нижняя точка подошвы на высоте clearance·sin(πs) над землёй
	# v0.6: в первой половине переноса подошва поднимается чуть быстрее (sin^0.85), чтобы носок
	# сразу после отрыва не скользил у самой земли; вторая половина и наибольший зазор — как в v0.5.
	var c: float = G.clearance * (pow(sin(PI * s), 0.85) if s < 0.5 else sin(PI * s))
	var y := INF
	for q in [lg.heel, lg.ball, lg.toe]:
		y = min(y, lg.ball.y - c - (q - lg.ankle).rotated(th).y)
	var ank := Vector2(x, y)
	return [ank, th, null]


func _pitch_curve(q: float) -> float:
	# v0.6: наклон стопы как одна гладкая кривая по фазе цикла через те же опорные значения, что в v0.5:
	# 0 (начало отрыва пятки) → heel_up (отрыв носка) → swing_pitch → 0 → −toe_up (касание).
	# Монотонный кубический сплайн (Фритч–Карлсон): без остановки наклона в момент отрыва носка.
	var d: float = G.duty
	var sw := 1.0 - d
	var xs := [G.heel_off, d, d + G.pitch_peak * sw, d + G.flat_at * sw, 1.0]
	var ys := [0.0, deg_to_rad(G.heel_up_deg), deg_to_rad(G.swing_pitch_deg), 0.0, -deg_to_rad(G.toe_up_deg)]
	var n := xs.size()
	var sec := []
	for i in n - 1:
		sec.append((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]))
	var sl := [0.0]
	for i in range(1, n - 1):
		sl.append(2.0 / (1.0 / sec[i - 1] + 1.0 / sec[i]) if sec[i - 1] * sec[i] > 0.0 else 0.0)
	sl.append(0.0)
	var i := 0
	while i < n - 2 and q > xs[i + 1]:
		i += 1
	var h: float = xs[i + 1] - xs[i]
	var u: float = clamp((q - xs[i]) / h, 0.0, 1.0)
	var u2 := u * u
	var u3 := u2 * u
	return (2 * u3 - 3 * u2 + 1) * ys[i] + (u3 - 2 * u2 + u) * sl[i] * h + (-2 * u3 + 3 * u2) * ys[i + 1] + (u3 - u2) * sl[i + 1] * h


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
		M[side + "_hang"] = Transform2D(0.0, knee - lg.knee)   # тест позы A: ткань свисает с колена
		M[side + "_foot"] = Transform2D(float(feet[side][1]), ank) * Transform2D(0.0, -lg.ankle)
		# поза той же ноги на lag цикла раньше — для запаздывания ткани
		var fl: Array = _foot_pose(lg, fposmod(p - G.lag + lg.phase, 1.0)) if walking else [lg.ankle, 0.0, null]
		var ank_l: Vector2 = fl[0]
		var knee_l := _ik(hip, ank_l, lg.l, lg.l)
		M[side + "_leg_lag"] = _bone(lg.hip, lg.ankle, hip, ank_l)
		M[side + "_shin_lag"] = _bone(lg.knee, lg.ankle, knee_l, ank_l)
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
		mm.cur = out
		mm.poly.polygon = out
	_apply_bulge()
	figure.position = view_origin
	if mode == Mode.FORWARD:
		figure.position.x = forward_origin_x + world_x * view_scale
	_track_contacts(p)
	if log_contact:
		var row := "CONTACT t=%.4f p=%.4f wx=%.3f" % [t, p, world_x]
		for side in legs:
			var lg: Dictionary = legs[side]
			var fm: Transform2D = M[side + "_foot"]
			var mid: Vector2 = (lg.heel + lg.ball) * 0.5
			for nm in ["heel", "mid", "ball", "toe"]:
				var q: Vector2 = mid if nm == "mid" else lg[nm]
				var w: Vector2 = fm * q
				row += " %s_%s=%.3f,%.3f" % [side, nm, w.x + world_x, w.y]
		print(row)
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
		if show_stretch:
			row += " sigma=%.3f..%.3f bulge=%.1f kfollow=%.1f max_at=%s" % [sigma_min, sigma_max, bulge_d, kfollow_d, sigma_at]
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
	var s := "Нитьянанда — технический тест v0.7 (черновик, не утверждённая анимация)\n"
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


var sigma_max := 0.0
var sigma_min := 9.0
var sigma_at := ""   # где наибольшее растяжение (слой@x,y холста)


func _draw_stretch() -> void:
	sigma_max = 0.0
	sigma_min = 9.0
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
			if smax > sigma_max:
				sigma_at = "%s@%d,%d" % [mm.poly.name, int((b0.x + pts[tri[1]].x + pts[tri[2]].x) / 3.0), int((b0.y + pts[tri[1]].y + pts[tri[2]].y) / 3.0)]
			sigma_max = max(sigma_max, smax)
			sigma_min = min(sigma_min, smin)
			var col := Color(0, 0, 0, 0)
			if smax > STRETCH_HI or smin < STRETCH_LO:
				col = Color(0.95, 0.1, 0.1, 0.6) if smax > STRETCH_HI else Color(0.1, 0.3, 1.0, 0.6)
			elif smax > STRETCH_HI - STRETCH_WARN or smin < STRETCH_LO + STRETCH_WARN:
				col = Color(1.0, 0.85, 0.0, 0.45)
			if col.a > 0.0:
				overlay.draw_colored_polygon(PackedVector2Array([b0, pts[tri[1]], pts[tri[2]]]), col)


var kfollow_d := 0.0   # тест позы A: остаточный сдвиг переднего края ближней штанины, px


func _apply_bulge() -> void:
	_apply_near_follow()
	if G.far_bulge <= 0.0:
		bulge_d = 0.0
		return
	_apply_far_bulge()


func _apply_near_follow() -> void:
	# Тест позы A: передний край БЛИЖНЕЙ штанины на высоте её колена должен быть впереди колена
	# на near_margin. Основную часть даёт перенос ткани у колена на кость бедра (rig.json);
	# если не хватает — передняя зона ближней штанины плавно сдвигается вперёд на недостающее.
	kfollow_d = 0.0
	var kn: Vector2 = legs.near.cur[1]
	for mm in meshes:
		if mm.kfollow.size() == 0:
			continue
		var ex := -INF
		for vi in mm.front_edge:
			if abs(mm.cur[vi].y - kn.y) < 30.0:
				ex = max(ex, mm.cur[vi].x)
		if ex == -INF:
			return
		kfollow_d = max(0.0, kn.x + G.near_margin - ex)
		if kfollow_d <= 0.0:
			return
		var out: PackedVector2Array = mm.cur
		for i in out.size():
			out[i].x += mm.kfollow[i] * kfollow_d
		mm.cur = out
		mm.poly.polygon = out


func _apply_far_bulge() -> void:
	# v0.7: передний край силуэта дхоти — край той штанины, что сейчас впереди. Если ближнее колено
	# выходит за этот край (по высоте колена), передняя зона дальней штанины выдвигается вперёд
	# ровно настолько (+ запас bulge_margin); иначе ткань не трогаем.
	bulge_d = 0.0
	var far_mm = null
	var kn: Vector2 = legs.near.cur[1]
	var ex := -INF
	for mm in meshes:
		if mm.front_edge.size() == 0:
			continue
		if mm.bulge.size() > 0:
			far_mm = mm
		for vi in mm.front_edge:
			if abs(mm.cur[vi].y - kn.y) < 30.0:
				ex = max(ex, mm.cur[vi].x)
	if far_mm == null or ex == -INF:
		return
	bulge_d = max(0.0, kn.x + G.bulge_margin - ex)
	if bulge_d <= 0.0:
		return
	var out: PackedVector2Array = far_mm.cur
	for i in out.size():
		out[i].x += far_mm.bulge[i] * bulge_d
	far_mm.poly.polygon = out
