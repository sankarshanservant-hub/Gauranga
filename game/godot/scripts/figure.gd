## Процедурная фигура-манекен для «серого» уровня: силуэт, одежда, цвета, простая анимация.
## Позже заменяется 3D-моделью персонажа (тот же интерфейс: walk_to, set_pose, face_to).
class_name Figure
extends Node3D

signal arrived

var id := ""
var display_name := ""
var height := 1.65
var speed := 1.6
var pose := "idle"
var path: PackedVector3Array = []
var phase := 0.0
var celestial := false       # видна только в небесном зрении
var carried := false

var hips: Node3D
var upper: Node3D
var leg_l: Node3D
var leg_r: Node3D
var arm_l: Node3D
var arm_r: Node3D
var head: Node3D
var body_root: Node3D
var _target_yaw := 0.0
var _mats: Array[StandardMaterial3D] = []

static func make_mat(c: Color, emission := 0.0, alpha := 1.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(c.r, c.g, c.b, alpha)
	m.roughness = 0.85
	if emission > 0.0:
		m.emission_enabled = true
		m.emission = c
		m.emission_energy_multiplier = emission
	if alpha < 1.0:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	return m

func _part(parent: Node3D, mesh: Mesh, mat: Material, pos: Vector3, rot := Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = pos
	mi.rotation = rot
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	if mat is StandardMaterial3D:
		_mats.append(mat)
	return mi

static func capsule(r: float, h: float) -> CapsuleMesh:
	var c := CapsuleMesh.new(); c.radius = r; c.height = max(h, 2.0 * r + 0.01); c.radial_segments = 12; c.rings = 4
	return c

static func cyl(r_top: float, r_bot: float, h: float, seg := 14) -> CylinderMesh:
	var c := CylinderMesh.new(); c.top_radius = r_top; c.bottom_radius = r_bot; c.height = h; c.radial_segments = seg
	return c

static func sphere(r: float) -> SphereMesh:
	var s := SphereMesh.new(); s.radius = r; s.height = 2.0 * r; s.radial_segments = 14; s.rings = 8
	return s

static func box(x: float, y: float, z: float) -> BoxMesh:
	var b := BoxMesh.new(); b.size = Vector3(x, y, z)
	return b

## spec: словарь из data/characters.json
func build(spec: Dictionary) -> void:
	id = spec.get("id", "")
	display_name = spec.get("name", id)
	height = spec.get("height", 1.65)
	speed = spec.get("speed", 1.6)
	celestial = spec.get("celestial", false)
	var alpha: float = spec.get("alpha", 1.0)
	var glow: float = spec.get("glow", 0.0)
	var skin := make_mat(Color(spec.get("skin", "#b5835a")), glow, alpha)
	var cloth := make_mat(Color(spec.get("cloth", "#efe8d8")), glow * 0.5, alpha)
	var cloth2 := make_mat(Color(spec.get("cloth2", "#efe8d8")), glow * 0.5, alpha)
	var border := make_mat(Color(spec.get("border", "#9b1c12")), 0.0, alpha)
	var hair := make_mat(Color(spec.get("hair", "#1c140e")), 0.0, alpha)
	var dress: String = spec.get("dress", "dhoti")
	var child: bool = spec.get("child", false)

	body_root = Node3D.new(); add_child(body_root)
	var s := height / 1.65
	body_root.scale = Vector3.ONE * s
	# мягкая тень-пятно
	var blob := MeshInstance3D.new()
	var pm := PlaneMesh.new(); pm.size = Vector2(0.8, 0.8)
	blob.mesh = pm
	var sm := ShaderMaterial.new(); sm.shader = load("res://shaders/blob_shadow.gdshader")
	sm.set_shader_parameter("strength", 0.45 if alpha >= 1.0 else 0.15)
	blob.material_override = sm
	blob.position.y = 0.02
	body_root.add_child(blob)

	hips = Node3D.new(); hips.position = Vector3(0, 0.86, 0); body_root.add_child(hips)
	leg_l = Node3D.new(); leg_l.position = Vector3(-0.09, 0, 0); hips.add_child(leg_l)
	leg_r = Node3D.new(); leg_r.position = Vector3(0.09, 0, 0); hips.add_child(leg_r)
	for leg in [leg_l, leg_r]:
		_part(leg, capsule(0.065, 0.86), skin, Vector3(0, -0.42, 0))
	# одежда нижней части
	match dress:
		"dhoti":
			_part(hips, cyl(0.17, 0.21, 0.5), cloth, Vector3(0, -0.2, 0))
		"sari":
			_part(hips, cyl(0.17, 0.27, 0.84), cloth, Vector3(0, -0.4, 0))
			_part(hips, cyl(0.272, 0.275, 0.07), border, Vector3(0, -0.79, 0))
		"loin":
			_part(hips, cyl(0.15, 0.15, 0.1), cloth, Vector3(0, -0.04, 0))
		"robe":
			_part(hips, cyl(0.18, 0.3, 0.86), cloth, Vector3(0, -0.4, 0))
	upper = Node3D.new(); hips.add_child(upper)
	var torso_mat := skin if dress != "sari" and dress != "robe" else cloth
	_part(upper, capsule(0.16, 0.62), torso_mat, Vector3(0, 0.27, 0))
	if dress == "sari":   # конец сари через плечо
		_part(upper, box(0.36, 0.08, 0.34), cloth, Vector3(0, 0.33, 0.0), Vector3(0, 0, 0.75))
	if spec.get("uttariya", false):
		_part(upper, box(0.38, 0.06, 0.33), cloth2, Vector3(0, 0.33, 0.0), Vector3(0, 0, -0.8))
	if spec.get("thread", false):   # священный шнур
		_part(upper, box(0.42, 0.012, 0.335), make_mat(Color("#f4f0e0")), Vector3(0, 0.3, 0.0), Vector3(0, 0, -0.9))
	if spec.get("pendant", false):  # Бала-Гопала на шее
		_part(upper, sphere(0.035), make_mat(Color("#e8b84a"), 2.0), Vector3(0, 0.36, 0.16))
	arm_l = Node3D.new(); arm_l.position = Vector3(-0.2, 0.5, 0); upper.add_child(arm_l)
	arm_r = Node3D.new(); arm_r.position = Vector3(0.2, 0.5, 0); upper.add_child(arm_r)
	for arm in [arm_l, arm_r]:
		_part(arm, capsule(0.048, 0.6), skin, Vector3(0, -0.28, 0))
	head = Node3D.new(); head.position = Vector3(0, 0.72, 0); upper.add_child(head)
	var hs := 1.35 if child else 1.0
	head.scale = Vector3.ONE * hs
	_part(head, sphere(0.11), skin, Vector3.ZERO)
	match spec.get("hair_style", "shikha"):
		"shikha":
			_part(head, sphere(0.03), hair, Vector3(0, 0.1, -0.05))
		"long":
			_part(head, sphere(0.115), hair, Vector3(0, 0.02, -0.025))
			_part(head, sphere(0.05), hair, Vector3(0, -0.02, -0.12))
		"veil":
			_part(head, sphere(0.122), cloth, Vector3(0, 0.02, -0.02))
		"curls":
			_part(head, sphere(0.112), hair, Vector3(0, 0.03, -0.03))
		"crown":
			_part(head, cyl(0.06, 0.09, 0.12), make_mat(Color("#e6c25a"), 1.0, alpha), Vector3(0, 0.13, 0))
	if spec.get("beard", false):
		_part(head, box(0.13, 0.08, 0.06), hair, Vector3(0, -0.09, 0.07))
	if spec.get("vina", false):     # вина за спиной
		var vm := make_mat(Color("#c99a4a"), 0.8, alpha)
		_part(upper, cyl(0.015, 0.015, 1.0), vm, Vector3(0.05, 0.3, -0.2), Vector3(0, 0, 0.5))
		_part(upper, sphere(0.09), vm, Vector3(0.28, -0.12, -0.22))
		_part(upper, sphere(0.07), vm, Vector3(-0.18, 0.74, -0.2))
	if spec.get("halo", false):
		var ring := TorusMesh.new(); ring.inner_radius = 0.16; ring.outer_radius = 0.18
		_part(head, ring, make_mat(Color("#ffe8a0"), 3.0, 0.8), Vector3(0, 0.18, -0.02), Vector3(1.2, 0, 0))
	if celestial:
		visible = false

## Силуэт, видимый сквозь кровли и стены (как у героев в изометрических RPG)
func add_xray(c: Color) -> void:
	var sm := ShaderMaterial.new()
	sm.shader = Shader.new()
	sm.shader.code = "shader_type spatial; render_mode unshaded, depth_test_disabled, depth_draw_never, cull_back; uniform vec4 col : source_color; void fragment(){ ALBEDO = col.rgb; ALPHA = col.a; }"
	sm.set_shader_parameter("col", c)
	sm.render_priority = -1
	for m in _mats:
		m.next_pass = sm

func set_alpha(a: float) -> void:
	for m in _mats:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA if a < 1.0 else BaseMaterial3D.TRANSPARENCY_DISABLED
		m.albedo_color.a = a

func set_pose(p: String) -> void:
	pose = p

func face_to(target: Vector3) -> void:
	var d := target - global_position
	d.y = 0
	if d.length() > 0.01:
		_target_yaw = atan2(d.x, d.z)

func face_yaw_now(target: Vector3) -> void:
	face_to(target)
	body_root.rotation.y = _target_yaw

## Пройти по пути (из навигационной сетки). Ждать: await fig.walk_path(p)
func walk_path(p: PackedVector3Array, run := false) -> void:
	path = p
	if run:
		pose = "run"
	elif pose != "run":
		pose = "walk"
	if path.is_empty():
		pose = "idle"
		arrived.emit()
		return
	await arrived

func stop() -> void:
	path = PackedVector3Array()
	pose = "idle"

func _process(delta: float) -> void:
	if carried:
		_animate(delta)
		return
	if not path.is_empty():
		var tgt := path[0]
		var to := tgt - global_position
		var flat := Vector3(to.x, 0, to.z)
		var sp := speed * (1.9 if pose == "run" else 1.0)
		if flat.length() < 0.06:
			global_position.y = tgt.y
			path.remove_at(0)
			if path.is_empty():
				pose = "idle"
				arrived.emit()
		else:
			var step: float = min(sp * delta, flat.length())
			global_position += flat.normalized() * step
			global_position.y = lerp(global_position.y, tgt.y, clamp(delta * 8.0, 0.0, 1.0))
			_target_yaw = atan2(flat.x, flat.z)
	body_root.rotation.y = lerp_angle(body_root.rotation.y, _target_yaw, clamp(delta * 10.0, 0.0, 1.0))
	_animate(delta)

func _animate(delta: float) -> void:
	phase += delta
	var t := phase
	# по умолчанию — стойка
	var hip_y := 0.86
	var leg_a := 0.0
	var arm_la := Vector3.ZERO
	var arm_ra := Vector3.ZERO
	var up_rx := 0.0
	var body_rz := 0.0
	var root_y := 0.0
	match pose:
		"idle":
			arm_la = Vector3(0, 0, -0.08 + 0.02 * sin(t * 1.5)); arm_ra = Vector3(0, 0, 0.08 - 0.02 * sin(t * 1.5))
		"walk", "run":
			var f := 7.0 if pose == "walk" else 11.0
			var amp := 0.5 if pose == "walk" else 0.8
			leg_a = sin(t * f) * amp
			arm_la = Vector3(-sin(t * f) * amp * 0.8, 0, -0.08); arm_ra = Vector3(sin(t * f) * amp * 0.8, 0, 0.08)
			root_y = abs(sin(t * f)) * 0.03
		"sit":
			hip_y = 0.18
			arm_la = Vector3(-0.6, 0, -0.2); arm_ra = Vector3(-0.6, 0, 0.2)
		"meditate":
			hip_y = 0.18
			arm_la = Vector3(-0.9, 0, 0.35); arm_ra = Vector3(-0.9, 0, -0.35)
			up_rx = 0.05
		"cook":
			hip_y = 0.18
			arm_ra = Vector3(-1.1 + 0.25 * sin(t * 4.0), 0.3 * cos(t * 4.0), 0.1); arm_la = Vector3(-0.8, 0, -0.1)
			up_rx = 0.25
		"eat":
			arm_ra = Vector3(-2.2 + 0.5 * abs(sin(t * 3.0)), 0, 0.15); arm_la = Vector3(-0.3, 0, -0.1)
		"lie", "sleep":
			body_rz = PI / 2
			root_y = 0.12
			arm_la = Vector3(0, 0, -0.1); arm_ra = Vector3(0, 0, 0.1)
		"faint":
			body_rz = PI / 2
			root_y = 0.12
			arm_la = Vector3(-1.2, 0, -0.4); arm_ra = Vector3(-1.4, 0, 0.3)
		"dance":
			arm_la = Vector3(-2.8 + 0.25 * sin(t * 5.0), 0, -0.25); arm_ra = Vector3(-2.8 - 0.25 * sin(t * 5.0), 0, 0.25)
			leg_a = sin(t * 5.0) * 0.35
			root_y = abs(sin(t * 5.0)) * 0.06
			up_rx = 0.08 * sin(t * 2.5)
		"grief":
			hip_y = 0.18
			arm_la = Vector3(-2.6, 0, 0.5); arm_ra = Vector3(-2.6, 0, -0.5)
			up_rx = 0.6
		"bow":
			up_rx = 0.8
			arm_la = Vector3(-1.2, 0, 0.3); arm_ra = Vector3(-1.2, 0, -0.3)
		"angry":
			arm_ra = Vector3(-2.6 + 0.4 * sin(t * 6.0), 0, 0.2); arm_la = Vector3(-0.2, 0, -0.1)
		"carry":
			arm_la = Vector3(-1.2, 0, 0.5); arm_ra = Vector3(-1.2, 0, -0.5)
		"plead":
			arm_la = Vector3(-1.3, 0, 0.25); arm_ra = Vector3(-1.3, 0, -0.25)
		"float":
			root_y = 0.35 + 0.08 * sin(t * 1.3)
			arm_la = Vector3(-0.5, 0, -0.5 + 0.1 * sin(t)); arm_ra = Vector3(-0.5, 0, 0.5 - 0.1 * sin(t))
	hips.position.y = lerp(hips.position.y, hip_y, clamp(delta * 10.0, 0.0, 1.0))
	var sitting := pose in ["sit", "meditate", "cook", "grief"]
	if sitting:
		leg_l.rotation = leg_l.rotation.lerp(Vector3(-1.45, 0, -0.6), clamp(delta * 10.0, 0.0, 1.0))
		leg_r.rotation = leg_r.rotation.lerp(Vector3(-1.45, 0, 0.6), clamp(delta * 10.0, 0.0, 1.0))
	else:
		leg_l.rotation = leg_l.rotation.lerp(Vector3(leg_a, 0, 0), clamp(delta * 12.0, 0.0, 1.0))
		leg_r.rotation = leg_r.rotation.lerp(Vector3(-leg_a, 0, 0), clamp(delta * 12.0, 0.0, 1.0))
	arm_l.rotation = arm_l.rotation.lerp(arm_la, clamp(delta * 10.0, 0.0, 1.0))
	arm_r.rotation = arm_r.rotation.lerp(arm_ra, clamp(delta * 10.0, 0.0, 1.0))
	upper.rotation.x = lerp(upper.rotation.x, up_rx, clamp(delta * 8.0, 0.0, 1.0))
	body_root.rotation.z = lerp(body_root.rotation.z, body_rz, clamp(delta * 6.0, 0.0, 1.0))
	body_root.position.y = lerp(body_root.position.y, root_y, clamp(delta * 10.0, 0.0, 1.0))
