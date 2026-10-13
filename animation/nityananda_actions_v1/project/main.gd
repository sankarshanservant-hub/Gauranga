extends Node2D
## Нитьянанда — тест повторно используемых действий v1 (Godot 4.3). См. ../README_RU.md.
##
## Части (parts.json, assets/) собраны из слоёв v0.7 скриптом tools/build_parts.py. Каждая часть —
## жёсткий Sprite2D (без деформаций сетки). Поза задаётся тремя независимыми параметрами персонажа:
##   raise_amount   — подъём сосуда (плечо, локоть, запястье), 0 = держит у бедра, 1 = у нижней части груди;
##   incline_amount — наклон головы к сосуду, 0..1;
##   idle_phase     — дыхание руки при удержании (hold_idle), 0..1 по кругу.
## Действия hold_idle, raise_object, head_incline — отдельные Animation на отдельных AnimationPlayer;
## каждое меняет только свой параметр, поэтому их можно проигрывать по одному и вместе.

@export var raise_amount := 0.0
@export var incline_amount := 0.0
@export var idle_phase := 0.0

# Ключевые позы руки (градусы; знак Godot: + по часовой на экране; вперёд для правого профиля — минус).
const POSE_HOLD := {"shoulder": 0.0, "elbow": -40.0, "wrist": -30.0}
const POSE_RAISED := {"shoulder": 23.8, "elbow": -118.9, "wrist": 15.0}
const HEAD_INCLINE_DEG := 8.0       # наклон головы при incline_amount = 1 (вокруг точки у уха)
const IDLE_ELBOW_DEG := 1.2         # дыхание руки при удержании

var parts := {}
var P := {}
var nodes := {}          # имя → {"line": Node2D, "fill": Node2D|null}
var M := {}              # имя части → Transform2D
var figure := Node2D.new()
var overlay := Node2D.new()
var caption := Label.new()
var players := {}
var view_scale := 0.6
var view_origin := Vector2(60, 20)
var show_debug := false
var show_synth := false
var show_hud := true
var log_pose := false
var action := "episode"
var hidden_parts: Array = []
var t := 0.0


func _ready() -> void:
	var man: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://parts.json"))
	parts = man.parts
	for k in man.points:
		P[k] = Vector2(man.points[k][0], man.points[k][1])
	_parse_args()
	add_child(figure)
	figure.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	_build()
	figure.add_child(overlay)
	overlay.draw.connect(_draw_overlay)
	var ui := CanvasLayer.new()
	add_child(ui)
	caption.position = Vector2(14, 8)
	caption.add_theme_color_override("font_color", Color(0.18, 0.16, 0.14))
	caption.add_theme_font_size_override("font_size", 15)
	caption.visible = show_hud
	ui.add_child(caption)
	figure.scale = Vector2(view_scale, view_scale)
	figure.position = view_origin
	_make_actions()
	_start_action(action)
	_update_pose()


func _parse_args() -> void:
	for a in OS.get_cmdline_user_args():
		var kv: PackedStringArray = a.trim_prefix("--").split("=")
		match kv[0]:
			"action": action = kv[1]
			"debug": show_debug = true
			"synth": show_synth = true
			"nohud": show_hud = false
			"log": log_pose = true
			"hide": hidden_parts = Array(kv[1].split(","))   # диагностика: скрыть части
			"scale": view_scale = float(kv[1])
			"ox": view_origin.x = float(kv[1])
			"oy": view_origin.y = float(kv[1])
			"bg":   # проверка дыр: яркий фон проступает в щелях между частями
				var c: PackedStringArray = kv[1].split(",")
				RenderingServer.set_default_clear_color(Color(float(c[0]), float(c[1]), float(c[2])))


func _tex(path: String) -> Texture2D:
	var img: Image = load("res://" + path).get_image()
	if img.is_compressed():
		img.decompress()
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


func _sprite(name: String, key: String) -> Node2D:
	var e: Dictionary = parts[name]
	var holder := Node2D.new()
	holder.name = name + "_" + key
	var sp := Sprite2D.new()
	sp.texture = _tex(e[key])
	sp.centered = false
	sp.position = Vector2(e.origin[0], e.origin[1])
	holder.add_child(sp)
	figure.add_child(holder)
	return holder


func _build() -> void:
	# Порядок перекрытий задан явно (снизу вверх). Рука рисуется в два прохода: сначала части с контуром,
	# затем их заливки без внешнего контура — стыки в локте и запястье не видны, внешний контур остаётся.
	# Сосуд — между проходами: кисть (заливка и контур) поверх сосуда, браслет поверх кисти.
	var line_key := "texture_diag" if show_synth else "texture"
	var order := [["body", line_key], ["head", line_key], ["upper_arm", line_key], ["forearm", line_key],
		["vessel", line_key], ["hand_grip", line_key]]
	if not show_synth:
		order += [["upper_arm", "texture_fill"], ["hand_grip", "texture_fill"], ["forearm", "texture_fill"]]
	order += [["band", line_key]]
	for o in order:
		if o[0] in hidden_parts:
			continue
		var holder := _sprite(o[0], o[1])
		if not nodes.has(o[0]):
			nodes[o[0]] = []
		nodes[o[0]].append(holder)


func _rot_about(pivot: Vector2, deg: float) -> Transform2D:
	return Transform2D(0.0, pivot) * Transform2D(deg_to_rad(deg), Vector2.ZERO) * Transform2D(0.0, -pivot)


func _update_pose() -> void:
	var s := raise_amount
	var idle := IDLE_ELBOW_DEG * sin(TAU * idle_phase) * (1.0 - 0.6 * s)
	var a_s: float = lerp(POSE_HOLD.shoulder, POSE_RAISED.shoulder, s)
	var a_e: float = lerp(POSE_HOLD.elbow, POSE_RAISED.elbow, s) + idle
	var a_w: float = lerp(POSE_HOLD.wrist, POSE_RAISED.wrist, s) - idle
	M["body"] = Transform2D.IDENTITY
	M["band"] = Transform2D.IDENTITY
	M["head"] = _rot_about(P.head_pivot, HEAD_INCLINE_DEG * incline_amount)
	M["upper_arm"] = _rot_about(P.shoulder, a_s)
	M["forearm"] = M.upper_arm * _rot_about(P.elbow, a_e)
	M["hand_grip"] = M.forearm * _rot_about(P.wrist, a_w)
	M["vessel"] = M.hand_grip          # сосуд жёстко привязан к кисти: не скользит относительно пальцев
	for name in nodes:
		for holder in nodes[name]:
			holder.transform = M[name]
	if log_pose:
		# контроль: точки сосуда под пальцами в системе координат кисти должны быть неизменны
		var c1: Vector2 = M.hand_grip.affine_inverse() * (M.vessel * (P.wrist + Vector2(-60, 40)))
		var up: Vector2 = (M.vessel.basis_xform(Vector2(parts.vessel.size[0], 0))).normalized()
		print("POSE t=%.3f raise=%.3f incline=%.3f idle=%.3f shoulder=%.2f elbow=%.2f wrist=%.2f head=%.2f vessel_tilt=%.1f grip_local=%.3f,%.3f elbow_flex=%.1f" % [
			t, raise_amount, incline_amount, idle_phase, a_s, a_e, a_w, HEAD_INCLINE_DEG * incline_amount,
			_vessel_tilt(), c1.x, c1.y, -a_e])
	overlay.queue_redraw()
	caption.text = "Нитьянанда · действия v1 · %s · t=%.2f с\nraise=%.2f  incline=%.2f  idle=%.2f\nТехнический тест: кисть с хватом и сосуд — черновики" % [action, t, raise_amount, incline_amount, idle_phase]


func _vessel_tilt() -> float:
	# ось сосуда в покое (нарисован вдоль кисти поперёк) → её наклон от вертикали в текущей позе
	var man_up := Vector2(0.987, -0.163)    # «вверх» сосуда в покое (parts.json: grip.vessel_up_rest)
	var w: Vector2 = M.vessel.basis_xform(man_up)
	return rad_to_deg(atan2(w.x, -w.y))


func _process(delta: float) -> void:
	t += delta
	_update_pose()


# ---------- действия ----------

func _anim(prop: String, keys: Array, length: float, loop := false) -> Animation:
	# keys: [[время, значение], ...]; между ключами — плавный разгон и торможение
	var an := Animation.new()
	an.length = length
	an.loop_mode = Animation.LOOP_LINEAR if loop else Animation.LOOP_NONE
	var tr := an.add_track(Animation.TYPE_VALUE)
	an.track_set_path(tr, NodePath(".:" + prop))
	# итерация 2: линейная интерполяция (для цикла кубическая давала мусорные значения фазы — дрожание руки)
	an.track_set_interpolation_type(tr, Animation.INTERPOLATION_LINEAR)
	an.track_set_interpolation_loop_wrap(tr, false)
	for k in keys:
		var i := an.track_insert_key(tr, k[0], k[1])
		an.track_set_key_transition(tr, i, 1.0 if loop else -2.0)   # -2: плавный разгон и торможение
	return an


func _make_actions() -> void:
	var lib := {
		"hold_idle": _anim("idle_phase", [[0.0, 0.0], [2.4, 1.0]], 2.4, true),
		# подъём: 1,4 с вверх, 1,0 с удержание, 1,4 с вниз
		"raise_object": _anim("raise_amount", [[0.0, 0.0], [1.4, 1.0], [2.4, 1.0], [3.8, 0.0]], 3.8),
		# наклон: 0,9 с к сосуду, 1,2 с удержание, 0,9 с обратно
		"head_incline": _anim("incline_amount", [[0.0, 0.0], [0.9, 1.0], [2.1, 1.0], [3.0, 0.0]], 3.0),
	}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://actions"))
	for name in lib:
		var al := AnimationLibrary.new()
		al.add_animation(name, lib[name])
		var ap := AnimationPlayer.new()
		ap.name = "AP_" + name
		add_child(ap)
		ap.root_node = NodePath("..")
		ap.add_animation_library("", al)
		players[name] = ap
		ResourceSaver.save(lib[name], "res://actions/%s.tres" % name)


func _start_action(a: String) -> void:
	match a:
		"episode":
			# общий эпизод: удержание всё время; подъём с 0,6 с; голова начинает позже руки (захлёст) и
			# возвращается раньше — по 0,4 с запаздывания
			players.hold_idle.play("hold_idle")
			get_tree().create_timer(0.6).timeout.connect(func(): players.raise_object.play("raise_object"))
			get_tree().create_timer(1.0).timeout.connect(func(): players.head_incline.play("head_incline"))
		"raise":
			players.hold_idle.play("hold_idle")
			get_tree().create_timer(0.4).timeout.connect(func(): players.raise_object.play("raise_object"))
		"incline":
			players.hold_idle.play("hold_idle")
			get_tree().create_timer(0.4).timeout.connect(func(): players.head_incline.play("head_incline"))
		"idle":
			players.hold_idle.play("hold_idle")
		"start":
			raise_amount = 0.0
			incline_amount = 0.0
		"end":
			raise_amount = 1.0
			incline_amount = 1.0


# ---------- диагностика ----------

func _draw_overlay() -> void:
	if not show_debug:
		return
	var lw := 2.5 / view_scale
	var S: Vector2 = M.upper_arm * P.shoulder
	var E: Vector2 = M.upper_arm * P.elbow
	var Wr: Vector2 = M.forearm * P.wrist
	var hand_dir: Vector2 = M.hand_grip.basis_xform(Vector2(0.163, 0.987))
	var col := Color(0.85, 0.1, 0.1)
	overlay.draw_line(S, E, col, lw)
	overlay.draw_line(E, Wr, col.darkened(0.3), lw)
	overlay.draw_line(Wr, Wr + hand_dir * 60.0, Color(0.9, 0.5, 0.0), lw)
	for p in [S, E, Wr]:
		overlay.draw_circle(p, 9.0 / view_scale, Color.WHITE)
		overlay.draw_circle(p, 6.0 / view_scale, col)
	# ось сосуда
	var vc: Vector2 = M.vessel * (P.wrist + Vector2(0.163, 0.987) * 46.0)
	var vu: Vector2 = M.vessel.basis_xform(Vector2(0.987, -0.163))
	overlay.draw_line(vc - vu * 55.0, vc + vu * 55.0, Color(0.6, 0.4, 0.0), lw)
	overlay.draw_circle(vc, 5.0 / view_scale, Color(0.6, 0.4, 0.0))
	# голова: точка наклона и ось
	var hp: Vector2 = P.head_pivot
	var top: Vector2 = M.head * Vector2(530, 60)
	overlay.draw_line(hp, top, Color(0.1, 0.3, 0.9), lw)
	overlay.draw_circle(hp, 9.0 / view_scale, Color.WHITE)
	overlay.draw_circle(hp, 6.0 / view_scale, Color(0.1, 0.3, 0.9))
