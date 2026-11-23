## Пробный («серый») уровень: двор дома Джаганнатхи Мишры, лила «Брахман-паломник» (ЧБ Ади 5).
## Пререндеренный фон (Blender/Cycles) + прокси-геометрия из той же сцены + фигуры персонажей.
## Запуск теста без участия человека: godot --path . -- --autoplay --shots=/путь
extends Node3D

const LAYER_GROUND := 1
const LAYER_HOTSPOT := 2
const LAYER_NPC := 4
const TIMES := {
	"day": {"tex": "res://assets/bg/courtyard_day.jpg", "sun": 0.85, "sun_col": Color(1.0, 0.93, 0.82), "amb": 0.45, "amb_col": Color(0.72, 0.74, 0.8), "lamps": 0.0},
	"dusk": {"tex": "res://assets/bg/courtyard_dusk.jpg", "sun": 0.5, "sun_col": Color(1.0, 0.7, 0.45), "amb": 0.3, "amb_col": Color(0.55, 0.5, 0.6), "lamps": 0.6},
	"night": {"tex": "res://assets/bg/courtyard_night.jpg", "sun": 0.15, "sun_col": Color(0.6, 0.7, 1.0), "amb": 0.14, "amb_col": Color(0.35, 0.4, 0.6), "lamps": 1.4},
}
# лампады сцены (координаты Blender x, y, z) — для подсветки персонажей ночью
const LAMPS_BL := [[-2.5, -3.0, 0.25], [3.4, -2.2, 0.25], [-3.6, 3.4, 0.25], [2.8, 3.6, 0.25], [0.3, -0.18, 0.4],
	[-0.5, 4.25, 2.4], [-6.4, 0.5, 1.4], [0.36, 4.85, 0.75]]
const PERCEPT_LINES := {
	"shachi": "Будто тень мелькнула у порога… Нрисимха, защити дитя!",
	"neighbor": "Кто там? Ветер, что ли, лампу качнул?",
	"nimai": "(Нимай смотрит прямо на вас — и смеётся. Он видит.)",
}

var cam: Camera3D
var bg_mat: ShaderMaterial
var cur_time := "day"
var spots := {}
var specs := {}
var codex := {}
var scenario := {}
var figures := {}
var placed := {}
var ui: GameUI
var player: Figure
var nav_region: NavigationRegion3D
var sun: DirectionalLight3D
var env: Environment
var lamps: Array[OmniLight3D] = []
var hotspots := {}
var found := {}
var flags := []
var hovered := ""
var mouse_pos := Vector2.ZERO
var celestial_on := false
var highlight_on := false
var marker: Node3D
var waiting_marker := ""
var autoplay := false
var shots_dir := ""
var shot_i := 0
var percept := 0.0
var percept_cool := 0.0
var walk_token := 0
var debug_proxy := false
var dump_nav := ""

signal marker_reached

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a == "--autoplay": autoplay = true
		elif a.begins_with("--shots="): shots_dir = a.substr(8)
		elif a == "--debug-proxy": debug_proxy = true
		elif a.begins_with("--dump-nav="): dump_nav = a.substr(11)
	specs = _json("res://data/characters.json")
	codex = _json("res://data/codex.json")
	scenario = _json("res://data/scenario.json")
	var camj := _json("res://assets/proxy/camera.json")
	for k in camj["spots"]:
		var v: Array = camj["spots"][k]
		spots[k] = Vector3(v[0], v[1], v[2])
	_setup_camera(camj)
	_setup_env()
	_setup_world()
	ui = GameUI.new(); ui.autoplay = autoplay
	add_child(ui)
	_setup_figures()
	_setup_hotspots()
	ui.set_counter(0, hotspots.size())
	marker = _make_marker(); add_child(marker); marker.visible = false
	await _bake_nav()
	if dump_nav != "":
		_dump_nav(); get_tree().quit(); return
	if autoplay:
		ui.displayed.connect(_capture)
	_run_scenario()

func _json(p: String) -> Dictionary:
	var f := FileAccess.open(p, FileAccess.READ)
	return JSON.parse_string(f.get_as_text())

# ---------------------------------------------------------------- мир
func _setup_camera(j: Dictionary) -> void:
	cam = Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.size = j["ortho_width"]
	var c: Array = j["basis_columns"]
	var b := Basis(Vector3(c[0][0], c[0][1], c[0][2]), Vector3(c[1][0], c[1][1], c[1][2]), Vector3(c[2][0], c[2][1], c[2][2]))
	var o: Array = j["origin"]
	cam.transform = Transform3D(b, Vector3(o[0], o[1], o[2]))
	cam.near = 0.5; cam.far = 200.0
	add_child(cam)
	cam.current = true

func _setup_env() -> void:
	var we := WorldEnvironment.new()
	env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color.BLACK
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = TIMES["day"]["amb_col"]
	env.ambient_light_energy = TIMES["day"]["amb"]
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	we.environment = env
	add_child(we)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, 35, 0)
	sun.light_energy = TIMES["day"]["sun"]
	sun.light_color = TIMES["day"]["sun_col"]
	add_child(sun)
	for p in LAMPS_BL:
		var l := OmniLight3D.new()
		l.position = Vector3(p[0], p[2], -p[1])
		l.light_color = Color(1.0, 0.62, 0.3)
		l.omni_range = 3.5
		l.light_energy = 0.0
		add_child(l)
		lamps.append(l)

func _bg_tex(t: String) -> Texture2D:
	var p: String = TIMES[t]["tex"]
	if ResourceLoader.exists(p): return load(p)
	return load(TIMES["day"]["tex"])

func _setup_world() -> void:
	bg_mat = ShaderMaterial.new()
	bg_mat.shader = load("res://shaders/bg_proxy.gdshader")
	bg_mat.set_shader_parameter("bg_a", _bg_tex("day"))
	bg_mat.set_shader_parameter("bg_b", _bg_tex("day"))
	bg_mat.set_shader_parameter("debug_tint", 0.5 if debug_proxy else 0.0)
	nav_region = NavigationRegion3D.new()
	add_child(nav_region)
	var scene: Node = load("res://assets/proxy/courtyard_proxy.glb").instantiate()
	nav_region.add_child(scene)
	var nav_keys := ["proxy_ground", "_plinth", "_wall", "_inside", "int_", "tm_", "haystack", "fence", "fpost", "shed_post",
		"palm_trunk", "banana_stem", "log", "line_post", "ghat", "hay_pole"]
	for n in scene.find_children("*", "", true, false):
		if n is Camera3D:
			n.current = false
			n.queue_free()
		elif n is MeshInstance3D:
			var mi := n as MeshInstance3D
			mi.material_override = bg_mat
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			for k in nav_keys:
				if mi.name.contains(k):
					mi.add_to_group("navsrc"); break
			# коллайдер для кликов по миру
			var body := StaticBody3D.new()
			body.collision_layer = LAYER_GROUND
			var cs := CollisionShape3D.new()
			cs.shape = mi.mesh.create_trimesh_shape()
			body.add_child(cs)
			mi.add_child(body)
	# пруд — непроходимое место (невидимый цилиндр для навигации)
	var pond := MeshInstance3D.new()
	var pc := CylinderMesh.new(); pc.top_radius = 1.0; pc.bottom_radius = 1.0; pc.height = 2.0
	pond.mesh = pc
	var inv := ShaderMaterial.new(); inv.shader = Shader.new()
	inv.shader.code = "shader_type spatial; render_mode unshaded, depth_draw_never; void fragment(){ discard; }"
	pond.material_override = inv
	pond.position = Vector3(-2.5, 1.0, 9.8)
	pond.scale = Vector3(3.7, 1.0, 2.5)
	pond.add_to_group("navsrc")
	nav_region.add_child(pond)

func _bake_nav() -> void:
	var nm := NavigationMesh.new()
	nm.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_MESH_INSTANCES
	nm.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_GROUPS_WITH_CHILDREN
	nm.geometry_source_group_name = "navsrc"
	nm.cell_size = 0.1
	nm.cell_height = 0.05
	nm.agent_radius = 0.25
	nm.agent_height = 1.4
	nm.agent_max_climb = 0.6
	nm.agent_max_slope = 40.0
	var map := get_world_3d().navigation_map
	NavigationServer3D.map_set_cell_size(map, 0.1)
	NavigationServer3D.map_set_cell_height(map, 0.05)
	nav_region.navigation_mesh = nm
	nav_region.bake_navigation_mesh(false)
	# карта навигации обновляется асинхронно — ждём, пока регион войдёт в карту
	var probe := Vector3(3.0, 0.0, 4.0)
	for i in 300:
		await get_tree().physics_frame
		var c := NavigationServer3D.map_get_closest_point(map, probe)
		if c != Vector3.ZERO and c.distance_to(probe) < 2.0:
			break

## Сетка проходимости для веб-версии: высота точки навмеша или -1 (шаг 0.2 м, x,z от -16 до 16)
func _dump_nav() -> void:
	var map := get_world_3d().navigation_map
	print("polys: ", nav_region.navigation_mesh.get_polygon_count(), " verts: ", nav_region.navigation_mesh.get_vertices().size(), " navsrc: ", get_tree().get_nodes_in_group("navsrc").size())
	print("closest 0,0,0: ", NavigationServer3D.map_get_closest_point(map, Vector3(0, 0, 0)), " iter ", NavigationServer3D.map_get_iteration_id(map))
	var rows := []
	var n := 161
	for iz in n:
		var row := []
		for ix in n:
			var x := -16.0 + ix * 0.2
			var z := -16.0 + iz * 0.2
			var best := -1.0
			for y0 in [0.0, 0.6]:
				var c := NavigationServer3D.map_get_closest_point(map, Vector3(x, y0, z))
				if Vector2(c.x - x, c.z - z).length() < 0.07 and abs(c.y - y0) < 0.25:
					best = max(best, snappedf(c.y, 0.01))
			row.append(best)
		rows.append(row)
	var f := FileAccess.open(dump_nav, FileAccess.WRITE)
	f.store_string(JSON.stringify({"x0": -16.0, "z0": -16.0, "step": 0.2, "n": n, "h": rows}))
	print("NAV DUMPED ", dump_nav)

func nav_path(from: Vector3, to: Vector3) -> PackedVector3Array:
	var map := get_world_3d().navigation_map
	var p := NavigationServer3D.map_get_path(map, from, to, true)
	if p.size() == 0:
		return PackedVector3Array([to])
	return p

func nav_closest(p: Vector3) -> Vector3:
	return NavigationServer3D.map_get_closest_point(get_world_3d().navigation_map, p)

# ---------------------------------------------------------------- персонажи и предметы
func _setup_figures() -> void:
	for id in specs:
		var f := Figure.new()
		f.build(specs[id])
		add_child(f)
		f.visible = false
		figures[id] = f
		# область для клика по персонажу
		var a := Area3D.new()
		a.collision_layer = LAYER_NPC; a.collision_mask = 0
		a.set_meta("npc", id)
		var cs := CollisionShape3D.new()
		var cap := CapsuleShape3D.new(); cap.radius = 0.35 * f.height / 1.65; cap.height = f.height
		cs.shape = cap; cs.position.y = f.height / 2
		a.add_child(cs); f.add_child(a)
		if id != "player":
			f.add_xray(Color(0.95, 0.88, 0.7, 0.22))
	player = figures["player"]
	player.visible = true
	player.add_xray(Color(0.75, 0.8, 1.0, 0.35))
	player.global_position = spots.get("sp_player_start", Vector3.ZERO)

func _setup_hotspots() -> void:
	var items: Dictionary = codex["items"]
	for id in items:
		if not spots.has(id): continue
		var a := Area3D.new()
		a.collision_layer = LAYER_HOTSPOT; a.collision_mask = 0
		a.set_meta("hs", id)
		var cs := CollisionShape3D.new(); var sp := SphereShape3D.new(); sp.radius = 0.85
		cs.shape = sp; a.add_child(cs)
		a.position = spots[id]
		add_child(a)
		var m := MeshInstance3D.new()
		var sm := SphereMesh.new(); sm.radius = 0.14; sm.height = 0.36; sm.radial_segments = 4; sm.rings = 2
		m.mesh = sm
		m.material_override = Figure.make_mat(Color("#ffd98a"), 2.5, 0.9)
		m.position = Vector3(0, 0.55, 0)
		m.visible = false
		a.add_child(m)
		hotspots[id] = {"area": a, "mark": m}

func _make_marker() -> Node3D:
	var n := Node3D.new()
	var ring := MeshInstance3D.new()
	var t := TorusMesh.new(); t.inner_radius = 0.75; t.outer_radius = 0.9; t.rings = 32
	ring.mesh = t; ring.material_override = Figure.make_mat(Color("#ffd27a"), 3.0, 0.85)
	ring.scale = Vector3(1, 0.12, 1)
	n.add_child(ring)
	var col := MeshInstance3D.new()
	var c := CylinderMesh.new(); c.top_radius = 0.05; c.bottom_radius = 0.6; c.height = 3.0
	col.mesh = c; col.position.y = 1.5
	col.material_override = Figure.make_mat(Color("#ffe6a0"), 1.5, 0.18)
	n.add_child(col)
	return n

func fig_color(id: String) -> Color:
	var s: Dictionary = specs.get(id, {})
	return Color(s.get("cloth2", s.get("cloth", "#d9b56a"))) if id != "nimai" else Color("#f0b85a")

# ---------------------------------------------------------------- ввод
func _unhandled_input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		mouse_pos = ev.position
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		if ui.dlg.visible:
			ui.try_advance(); return
		if ui.journal.visible: return
		_on_click(ev.position)
	elif ev is InputEventKey and ev.pressed and not ev.echo:
		match ev.keycode:
			KEY_SPACE, KEY_ENTER:
				if ui.dlg.visible: ui.try_advance()
				elif ev.keycode == KEY_SPACE: _toggle_highlight()
			KEY_TAB: toggle_celestial()
			KEY_J: ui.toggle_journal()
			KEY_ESCAPE:
				ui.hide_card(); ui.journal.visible = false; ui.hint_panel.visible = false
			KEY_1, KEY_2, KEY_3:
				if ui.dlg_choices.visible: ui.chosen.emit(ev.keycode - KEY_1)

func _toggle_highlight() -> void:
	highlight_on = not highlight_on
	for id in hotspots:
		hotspots[id]["mark"].visible = highlight_on or id == hovered

func toggle_celestial() -> void:
	celestial_on = not celestial_on
	ui.set_plane(celestial_on)
	for id in figures:
		var f: Figure = figures[id]
		if f.celestial:
			f.visible = celestial_on and placed.get(id, false)

func _ray(mask: int, areas: bool) -> Dictionary:
	var from := cam.project_ray_origin(mouse_pos)
	var to := from + cam.project_ray_normal(mouse_pos) * 300.0
	var q := PhysicsRayQueryParameters3D.create(from, to, mask)
	q.collide_with_areas = areas
	q.collide_with_bodies = not areas
	return get_world_3d().direct_space_state.intersect_ray(q)

func _physics_process(_d: float) -> void:
	if ui == null: return
	var h := ""
	var label := ""
	if not ui.is_modal():
		var r := _ray(LAYER_HOTSPOT | LAYER_NPC, true)
		if r.has("collider"):
			var c: Node = r["collider"]
			if c.has_meta("hs"):
				h = c.get_meta("hs"); label = codex["items"][h]["title"] + ("  ✓" if found.has(h) else "")
			elif c.has_meta("npc"):
				var nid: String = c.get_meta("npc")
				var f: Figure = figures[nid]
				if f.visible and nid != "player":
					h = "npc:" + nid; label = f.display_name
	if h != hovered:
		if hotspots.has(hovered): hotspots[hovered]["mark"].visible = highlight_on
		hovered = h
		if hotspots.has(hovered): hotspots[hovered]["mark"].visible = true
	ui.show_tooltip(label, mouse_pos)

func _on_click(pos: Vector2) -> void:
	mouse_pos = pos
	if hovered.begins_with("npc:"):
		var nid := hovered.substr(4)
		var e: Dictionary = codex["persons"].get(nid, {"title": figures[nid].display_name, "kind": "Лицо", "text": ""})
		_open_entry("p:" + nid, e)
		return
	if hotspots.has(hovered):
		walk_to_hotspot(hovered)
		return
	var r := _ray(LAYER_GROUND, false)
	if r.has("position"):
		walk_token += 1
		player.walk_path(nav_path(player.global_position, nav_closest(r["position"])))

func walk_to_hotspot(id: String) -> void:
	walk_token += 1
	var tok := walk_token
	var p: Vector3 = spots[id]
	var dest := nav_closest(p)
	await player.walk_path(nav_path(player.global_position, dest))
	if tok != walk_token: return
	player.face_to(p)
	_open_entry(id, codex["items"][id])

func _open_entry(key: String, e: Dictionary) -> void:
	if key.begins_with("hs_") and not found.has(key):
		found[key] = true
		ui.set_counter(found.size(), hotspots.size())
	ui.add_journal(key, e)
	ui.show_card(e, celestial_on)

# ---------------------------------------------------------------- время суток, ощутимость, маркер
func set_time(t: String, sec: float) -> void:
	if t == cur_time: return
	bg_mat.set_shader_parameter("bg_b", _bg_tex(t))
	var d: Dictionary = TIMES[t]
	var tw := create_tween().set_parallel(true)
	tw.tween_method(func(v): bg_mat.set_shader_parameter("mix_ab", v), 0.0, 1.0, sec)
	tw.tween_property(sun, "light_energy", d["sun"], sec)
	tw.tween_property(sun, "light_color", d["sun_col"], sec)
	tw.tween_property(env, "ambient_light_energy", d["amb"], sec)
	tw.tween_property(env, "ambient_light_color", d["amb_col"], sec)
	for l in lamps:
		tw.tween_property(l, "light_energy", d["lamps"], sec)
	await tw.finished
	bg_mat.set_shader_parameter("bg_a", _bg_tex(t))
	bg_mat.set_shader_parameter("mix_ab", 0.0)
	cur_time = t

func _process(delta: float) -> void:
	if marker.visible:
		marker.rotation.y += delta * 0.8
		var s := 1.0 + 0.08 * sin(Time.get_ticks_msec() / 300.0)
		marker.scale = Vector3(s, 1, s)
		if waiting_marker != "" and player.global_position.distance_to(marker.global_position) < 1.7:
			waiting_marker = ""
			marker.visible = false
			marker_reached.emit()
	# ощутимость: незримый гость не должен подходить слишком близко
	percept_cool = max(percept_cool - delta, 0.0)
	var near := ""
	for id in ["nimai", "shachi", "neighbor"]:
		var f: Figure = figures[id]
		if f.visible and not f.carried and f.global_position.distance_to(player.global_position) < 1.3:
			near = id
	if near != "" and not ui.dlg.visible and percept_cool <= 0.0:
		percept = min(percept + delta * 0.45, 1.0)
	else:
		percept = max(percept - delta * 0.25, 0.0)
	ui.set_perceptibility(percept)
	if percept >= 1.0 and near != "":
		percept = 0.0; percept_cool = 4.0
		_perceived(near)

func _perceived(id: String) -> void:
	var f: Figure = figures[id]
	f.face_to(player.global_position)
	var away := (player.global_position - f.global_position)
	away.y = 0
	var dest := nav_closest(f.global_position + away.normalized() * 3.0)
	player.walk_path(nav_path(player.global_position, dest))
	await ui.say(f.display_name, PERCEPT_LINES.get(id, "…"), "", fig_color(id), id == "nimai")

func wait_marker(spot: String, hint: String) -> void:
	marker.global_position = spots[spot]
	marker.visible = true
	waiting_marker = spot
	ui.show_tooltip("", Vector2.ZERO)
	if hint != "":
		ui.set_objective(ui.objective_label.text + "\n✦ " + hint)
	if autoplay:
		player.global_position = spots[spot] + Vector3(0.6, 0, 0.6)
	await marker_reached

# ---------------------------------------------------------------- режиссёр сценария
func _spot_or_fig(name: String) -> Vector3:
	if figures.has(name): return figures[name].global_position
	return spots.get(name, Vector3.ZERO)

func _run_scenario() -> void:
	for beat in scenario["beats"]:
		if beat.has("marker"):
			await wait_marker(beat["marker"], beat.get("marker_hint", ""))
		for step in beat["steps"]:
			await _do(step)
		if autoplay and beat["id"] == "intro":
			await _autoplay_explore()

func _do(s: Dictionary) -> void:
	var who: String = s.get("who", "")
	var f: Figure = figures.get(who)
	var off := Vector3.ZERO
	if s.has("offset"):
		var o: Array = s["offset"]; off = Vector3(o[0], o[1], o[2])
	match s["do"]:
		"place":
			f.carried = false
			if f.get_parent() != self: f.reparent(self)
			f.global_position = spots[s["at"]] + off
			f.stop()
			placed[who] = true
			f.visible = (not f.celestial) or celestial_on
		"hide":
			f.visible = false; placed[who] = false
		"pose":
			f.set_pose(s["pose"])
		"face":
			f.face_to(_spot_or_fig(s["to"]))
		"walk":
			var dest := nav_closest(spots[s["to"]] + off)
			if s.has("with") and s.get("carry", false):
				var child: Figure = figures[s["with"]]
				child.carried = true
				child.reparent(f.upper)
				child.position = Vector3(0, 0.12, 0.28); child.rotation = Vector3.ZERO
				child.set_pose("sit")
			var path := nav_path(f.global_position, dest)
			if s.get("nowait", false):
				f.walk_path(path, s.get("run", false))
			else:
				await f.walk_path(path, s.get("run", false))
		"drop":
			var by: Figure = figures[s["by"]]
			f.reparent(self)
			f.carried = false
			f.global_position = nav_closest(by.global_position + off)
			f.rotation = Vector3.ZERO
			f.set_pose("idle")
		"say":
			await ui.say(s.get("as", f.display_name if f else who), s["text"], s.get("ref", ""), fig_color(who))
		"narrate":
			await ui.say("Шри Чайтанья-бхагавата", s["text"], s.get("ref", ""), Color("#8a6a2a"), true)
		"narrate_game":
			await ui.say(player.display_name, s["text"], "", fig_color("player"), true)
		"hint":
			ui.show_hint(s["text"])
		"objective":
			ui.set_objective(s["text"])
		"title":
			await ui.title_card(s["text"], s.get("sub", ""), s.get("sec", 3.0))
		"fade":
			await ui.fade_text(s["text"], s.get("ref", ""))
		"time":
			await set_time(s["value"], s.get("sec", 2.0))
		"choice":
			var opts: Array = s["options"]
			var labels := []
			for o in opts: labels.append(o["text"])
			var i := await ui.choose(player.display_name, s["prompt"], labels, fig_color("player"))
			flags.append(opts[i].get("flag", ""))
			await ui.say(player.display_name, opts[i]["reply"], "", fig_color("player"), true)
		"unlock":
			var e: Dictionary = codex["lilas"][s["id"]]
			_open_entry(s["id"], e)
		"vision":
			if s.get("on", false):
				var p := _spot_or_fig(s.get("at", "")) + Vector3(0, 0.6, 0)
				var uv := cam.unproject_position(p) / get_viewport().get_visible_rect().size
				await ui.vision(true, uv)
			else:
				await ui.vision(false, Vector2(0.5, 0.5))
		"wait":
			await get_tree().create_timer(s.get("sec", 1.0)).timeout
		"celestial_hint":
			pass
		"end":
			await _finale()

func _finale() -> void:
	var txt := "Вы открыли %d из %d предметов быта.\n\nИсточники лилы: «Шри Чайтанья-бхагавата», Ади 5.16–166; «Шри Чайтанья-чаритамрита», Ади 14.37; Мурари Гупта, 1.6.8; «Гаура-кришнодая», 3; «Бхакти-ратнакара», 12.\n\nКонец пробного уровня." % [found.size(), hotspots.size()]
	await ui.title_card("Слава Бала-Гопалу!", txt, 6.0)
	ui.set_objective("Пробный уровень пройден. Можно бродить по двору и открывать предметы.")
	if autoplay:
		await get_tree().create_timer(0.5).timeout
		get_tree().quit()

# ---------------------------------------------------------------- автотест
func _capture() -> void:
	if shots_dir == "": return
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	shot_i += 1
	img.save_jpg("%s/shot_%03d.jpg" % [shots_dir, shot_i], 0.85)

func _autoplay_explore() -> void:
	for id in ["hs_tulasi", "hs_handi", "hs_chala"]:
		await walk_to_hotspot(id)
		await _capture()
		await get_tree().create_timer(0.5).timeout
	highlight_on = false; _toggle_highlight()
	await get_tree().create_timer(0.3).timeout
	await _capture()
	_toggle_highlight()
	toggle_celestial()
	await get_tree().create_timer(0.8).timeout
	await _capture()
	toggle_celestial()
	ui.toggle_journal()
	await get_tree().create_timer(0.3).timeout
	await _capture()
	ui.toggle_journal()
