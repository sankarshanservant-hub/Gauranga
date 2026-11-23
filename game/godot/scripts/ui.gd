## Интерфейс: диалоги со ссылкой на источник, выбор, карточки кодекса, журнал, подсказки, титры, оверлеи.
class_name GameUI
extends CanvasLayer

signal advanced
signal chosen(index: int)
signal card_closed
signal displayed

const GOLD := Color("#d9b56a")
const INK := Color("#f3ead6")
const DIM := Color("#b9ab8e")

var autoplay := false
var font_reg: Font
var font_it: Font
var font_bold: Font
var font_sc: Font

var celestial_rect: ColorRect
var vision_rect: ColorRect
var dlg: PanelContainer
var dlg_portrait: Panel
var dlg_initial: Label
var dlg_name: Label
var dlg_text: RichTextLabel
var dlg_ref: Label
var dlg_choices: VBoxContainer
var card: PanelContainer
var card_title: Label
var card_kind: Label
var card_text: RichTextLabel
var tooltip: PanelContainer
var tooltip_label: Label
var objective_label: Label
var hint_panel: PanelContainer
var hint_label: Label
var counter_label: Label
var plane_label: Label
var percept_bar: ProgressBar
var percept_box: VBoxContainer
var fade_rect: ColorRect
var fade_label: Label
var fade_sub: Label
var journal: PanelContainer
var journal_list: ItemList
var journal_text: RichTextLabel
var journal_entries: Array = []   # [{title, kind, text}]
var _waiting_advance := false
var _waiting_choice := false

func _ready() -> void:
	layer = 10
	font_reg = load("res://assets/fonts/Alegreya-Regular.ttf")
	font_it = load("res://assets/fonts/Alegreya-Italic.ttf")
	font_bold = load("res://assets/fonts/Alegreya-Bold.ttf")
	font_sc = load("res://assets/fonts/AlegreyaSC-Medium.ttf")
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	# небесное зрение и даршан — полноэкранные шейдеры
	celestial_rect = ColorRect.new()
	celestial_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	celestial_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var cm := ShaderMaterial.new(); cm.shader = load("res://shaders/celestial.gdshader")
	celestial_rect.material = cm
	celestial_rect.visible = false
	root.add_child(celestial_rect)
	vision_rect = ColorRect.new()
	vision_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	vision_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var vm := ShaderMaterial.new(); vm.shader = load("res://shaders/vision.gdshader")
	vision_rect.material = vm
	vision_rect.visible = false
	root.add_child(vision_rect)

	# верхняя строка: цель и счётчики
	var top := PanelContainer.new()
	top.add_theme_stylebox_override("panel", _style(Color(0.06, 0.045, 0.03, 0.78), 0, 10))
	top.position = Vector2(24, 18)
	top.custom_minimum_size = Vector2(900, 0)
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(top)
	var tv := VBoxContainer.new(); top.add_child(tv)
	var chap := _label("Глава I · Детство · Брахман-паломник", font_sc, 20, GOLD); tv.add_child(chap)
	objective_label = _label("", font_reg, 22, INK); objective_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tv.add_child(objective_label)

	var tr := VBoxContainer.new()
	tr.position = Vector2(1500, 18); tr.custom_minimum_size = Vector2(396, 0)
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(tr)
	var bp := PanelContainer.new(); bp.add_theme_stylebox_override("panel", _style(Color(0.06, 0.045, 0.03, 0.78), 0, 10))
	bp.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tr.add_child(bp)
	var bv := VBoxContainer.new(); bp.add_child(bv)
	counter_label = _label("Быт: 0", font_reg, 20, INK); bv.add_child(counter_label)
	plane_label = _label("План: земной", font_reg, 20, INK); bv.add_child(plane_label)
	bv.add_child(_label("Пробел — подсветка · Tab — небо · J — журнал", font_reg, 16, DIM))

	# ощутимость
	percept_box = VBoxContainer.new()
	percept_box.position = Vector2(24, 980); percept_box.custom_minimum_size = Vector2(320, 0)
	percept_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(percept_box)
	percept_box.add_child(_label("Ощутимость", font_sc, 18, GOLD))
	percept_bar = ProgressBar.new(); percept_bar.max_value = 1.0; percept_bar.show_percentage = false
	percept_bar.custom_minimum_size = Vector2(320, 14)
	var fg := StyleBoxFlat.new(); fg.bg_color = Color("#e0c27a")
	var bgs := StyleBoxFlat.new(); bgs.bg_color = Color(0, 0, 0, 0.5)
	percept_bar.add_theme_stylebox_override("fill", fg); percept_bar.add_theme_stylebox_override("background", bgs)
	percept_box.add_child(percept_bar)
	percept_box.visible = false

	# подсказка
	hint_panel = PanelContainer.new()
	hint_panel.add_theme_stylebox_override("panel", _style(Color(0.08, 0.06, 0.04, 0.9), 1, 14))
	hint_panel.position = Vector2(460, 140); hint_panel.custom_minimum_size = Vector2(1000, 0)
	root.add_child(hint_panel)
	var hv := VBoxContainer.new(); hint_panel.add_child(hv)
	hint_label = _label("", font_reg, 22, INK); hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hv.add_child(hint_label)
	var hb := _button("Понятно"); hb.pressed.connect(func(): hint_panel.visible = false)
	hv.add_child(hb)
	hint_panel.visible = false

	# диалог
	dlg = PanelContainer.new()
	dlg.add_theme_stylebox_override("panel", _style(Color(0.07, 0.05, 0.035, 0.94), 2, 18))
	dlg.position = Vector2(210, 800); dlg.custom_minimum_size = Vector2(1500, 250)
	root.add_child(dlg)
	var dh := HBoxContainer.new(); dh.add_theme_constant_override("separation", 22); dlg.add_child(dh)
	dlg_portrait = Panel.new(); dlg_portrait.custom_minimum_size = Vector2(170, 200)
	dh.add_child(dlg_portrait)
	dlg_initial = _label("", font_sc, 84, INK)
	dlg_initial.set_anchors_preset(Control.PRESET_FULL_RECT)
	dlg_initial.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	dlg_initial.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	dlg_portrait.add_child(dlg_initial)
	var dv := VBoxContainer.new(); dv.size_flags_horizontal = Control.SIZE_EXPAND_FILL; dh.add_child(dv)
	dlg_name = _label("", font_sc, 26, GOLD); dv.add_child(dlg_name)
	dlg_text = RichTextLabel.new(); dlg_text.bbcode_enabled = true; dlg_text.fit_content = true
	dlg_text.add_theme_font_override("normal_font", font_reg); dlg_text.add_theme_font_override("italics_font", font_it)
	dlg_text.add_theme_font_size_override("normal_font_size", 27); dlg_text.add_theme_font_size_override("italics_font_size", 27)
	dlg_text.add_theme_color_override("default_color", INK)
	dlg_text.custom_minimum_size = Vector2(1240, 110); dlg_text.scroll_active = false
	dlg_text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dv.add_child(dlg_text)
	dlg_choices = VBoxContainer.new(); dv.add_child(dlg_choices)
	dlg_ref = _label("", font_it, 18, DIM); dv.add_child(dlg_ref)
	dlg.gui_input.connect(_on_dlg_input)
	dlg.visible = false

	# карточка кодекса
	card = PanelContainer.new()
	card.add_theme_stylebox_override("panel", _style(Color(0.09, 0.07, 0.05, 0.96), 2, 22))
	card.position = Vector2(1180, 150); card.custom_minimum_size = Vector2(700, 0)
	root.add_child(card)
	var cv := VBoxContainer.new(); cv.add_theme_constant_override("separation", 8); card.add_child(cv)
	card_kind = _label("", font_sc, 18, DIM); cv.add_child(card_kind)
	card_title = _label("", font_bold, 34, GOLD); card_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; cv.add_child(card_title)
	card_text = RichTextLabel.new(); card_text.bbcode_enabled = true; card_text.fit_content = true
	card_text.custom_minimum_size = Vector2(660, 0); card_text.scroll_active = false
	card_text.add_theme_font_override("normal_font", font_reg); card_text.add_theme_font_override("italics_font", font_it)
	card_text.add_theme_font_override("bold_font", font_bold)
	card_text.add_theme_font_size_override("normal_font_size", 23); card_text.add_theme_font_size_override("italics_font_size", 21)
	card_text.add_theme_font_size_override("bold_font_size", 23)
	card_text.add_theme_color_override("default_color", INK)
	cv.add_child(card_text)
	var cb := _button("Закрыть"); cb.pressed.connect(hide_card); cv.add_child(cb)
	card.visible = false

	# журнал
	journal = PanelContainer.new()
	journal.add_theme_stylebox_override("panel", _style(Color(0.07, 0.05, 0.035, 0.97), 2, 24))
	journal.position = Vector2(160, 90); journal.custom_minimum_size = Vector2(1600, 900)
	root.add_child(journal)
	var jv := VBoxContainer.new(); journal.add_child(jv)
	jv.add_child(_label("Журнал · открытое в этой главе", font_sc, 30, GOLD))
	var jh := HBoxContainer.new(); jh.size_flags_vertical = Control.SIZE_EXPAND_FILL; jv.add_child(jh)
	journal_list = ItemList.new(); journal_list.custom_minimum_size = Vector2(520, 760)
	journal_list.add_theme_font_override("font", font_reg); journal_list.add_theme_font_size_override("font_size", 22)
	journal_list.item_selected.connect(_on_journal_pick)
	jh.add_child(journal_list)
	journal_text = RichTextLabel.new(); journal_text.bbcode_enabled = true
	journal_text.custom_minimum_size = Vector2(1020, 760)
	journal_text.add_theme_font_override("normal_font", font_reg); journal_text.add_theme_font_override("italics_font", font_it)
	journal_text.add_theme_font_override("bold_font", font_bold)
	journal_text.add_theme_font_size_override("normal_font_size", 24); journal_text.add_theme_font_size_override("bold_font_size", 30)
	journal_text.add_theme_font_size_override("italics_font_size", 21)
	journal_text.add_theme_color_override("default_color", INK)
	jh.add_child(journal_text)
	var jb := _button("Закрыть (J)"); jb.pressed.connect(func(): journal.visible = false); jv.add_child(jb)
	journal.visible = false

	# подпись под курсором
	tooltip = PanelContainer.new()
	tooltip.add_theme_stylebox_override("panel", _style(Color(0.05, 0.04, 0.03, 0.88), 1, 8))
	tooltip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tooltip_label = _label("", font_reg, 21, INK); tooltip.add_child(tooltip_label)
	tooltip.visible = false
	root.add_child(tooltip)

	# затемнение и титры
	fade_rect = ColorRect.new(); fade_rect.color = Color(0, 0, 0, 0)
	fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT); fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(fade_rect)
	var fv := VBoxContainer.new(); fv.set_anchors_preset(Control.PRESET_FULL_RECT)
	fv.alignment = BoxContainer.ALIGNMENT_CENTER; fv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fade_rect.add_child(fv)
	fade_label = _label("", font_bold, 56, GOLD); fade_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fade_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	fv.add_child(fade_label)
	fade_sub = _label("", font_it, 28, INK); fade_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fade_sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	fv.add_child(fade_sub)
	fade_label.modulate.a = 0; fade_sub.modulate.a = 0

func _style(bg: Color, border: int, pad: int) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = Color(GOLD.r, GOLD.g, GOLD.b, 0.75)
	s.set_border_width_all(border)
	s.set_corner_radius_all(6)
	s.content_margin_left = pad; s.content_margin_right = pad; s.content_margin_top = pad * 0.7; s.content_margin_bottom = pad * 0.7
	return s

func _label(t: String, f: Font, size: int, c: Color) -> Label:
	var l := Label.new(); l.text = t
	l.add_theme_font_override("font", f); l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", c)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l

func _button(t: String) -> Button:
	var b := Button.new(); b.text = t
	b.add_theme_font_override("font", font_reg); b.add_theme_font_size_override("font_size", 22)
	b.add_theme_stylebox_override("normal", _style(Color(0.16, 0.12, 0.07, 0.95), 1, 10))
	b.add_theme_stylebox_override("hover", _style(Color(0.28, 0.21, 0.11, 0.95), 1, 10))
	b.add_theme_stylebox_override("pressed", _style(Color(0.35, 0.27, 0.14, 0.95), 1, 10))
	b.add_theme_color_override("font_color", INK)
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	return b

func is_modal() -> bool:
	return dlg.visible or journal.visible or fade_rect.color.a > 0.5

func ui_blocking_mouse() -> bool:
	return dlg.visible or journal.visible or card.visible or hint_panel.visible

# ---------------------------------------------------------------- диалог
func say(speaker: String, text: String, ref: String, col: Color, italic := false) -> void:
	dlg.visible = true
	dlg_choices.visible = false
	for c in dlg_choices.get_children(): c.queue_free()
	dlg_name.text = speaker
	dlg_initial.text = speaker.substr(0, 1) if speaker != "" else "❧"
	var ps := StyleBoxFlat.new(); ps.bg_color = col.darkened(0.35); ps.set_corner_radius_all(8)
	ps.border_color = GOLD; ps.set_border_width_all(2)
	dlg_portrait.add_theme_stylebox_override("panel", ps)
	dlg_text.text = ("[i]%s[/i]" % text) if italic else ("«%s»" % text if speaker != "" and not italic else text)
	dlg_ref.text = ("Источник: " + ref) if ref != "" else "Игровой рассказ"
	dlg_text.visible_ratio = 0.0
	var tw := create_tween(); tw.tween_property(dlg_text, "visible_ratio", 1.0, clamp(text.length() / 90.0, 0.3, 2.5))
	_waiting_advance = true
	if autoplay:
		dlg_text.visible_ratio = 1.0
		await get_tree().process_frame
		displayed.emit()
		await get_tree().create_timer(0.25).timeout
		_waiting_advance = false
		advanced.emit()
	else:
		await advanced
	dlg.visible = false

func _on_dlg_input(ev: InputEvent) -> void:
	if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		try_advance()

func try_advance() -> void:
	if not _waiting_advance: return
	if dlg_text.visible_ratio < 1.0:
		dlg_text.visible_ratio = 1.0
		return
	_waiting_advance = false
	advanced.emit()

func choose(speaker: String, prompt: String, options: Array, col: Color) -> int:
	dlg.visible = true
	dlg_name.text = speaker
	dlg_initial.text = speaker.substr(0, 1)
	var ps := StyleBoxFlat.new(); ps.bg_color = col.darkened(0.35); ps.set_corner_radius_all(8)
	dlg_portrait.add_theme_stylebox_override("panel", ps)
	dlg_text.text = "[i]%s[/i]" % prompt
	dlg_text.visible_ratio = 1.0
	dlg_ref.text = "Ваш выбор (игровой рассказ)"
	for c in dlg_choices.get_children(): c.queue_free()
	dlg_choices.visible = true
	for i in options.size():
		var b := _button("%d. %s" % [i + 1, options[i]])
		b.pressed.connect(func(): chosen.emit(i))
		dlg_choices.add_child(b)
	var idx := 0
	if autoplay:
		await get_tree().process_frame
		displayed.emit()
		await get_tree().create_timer(0.3).timeout
		idx = 1
	else:
		idx = await chosen
	dlg_choices.visible = false
	dlg.visible = false
	return idx

# ---------------------------------------------------------------- карточка и журнал
func show_card(entry: Dictionary, celestial_on: bool) -> void:
	card_kind.text = entry.get("kind", "")
	card_title.text = entry.get("title", "")
	var t: String = entry.get("text", "")
	if celestial_on and entry.has("divya"):
		t += "\n\n[i]" + entry["divya"] + "[/i]"
	elif entry.has("divya"):
		t += "\n\n[i]Здесь есть и то, что видно лишь небесным зрением (Tab).[/i]"
	var refs: Array = entry.get("refs", [])
	if refs.size() > 0:
		t += "\n\n[b]В житиях:[/b] " + "; ".join(refs)
	if entry.get("status", "") == "draft":
		t += "\n[i]Черновик — уточнит историческая база.[/i]"
	card_text.text = t
	card.visible = true
	if autoplay:
		await get_tree().process_frame
		displayed.emit()
		await get_tree().create_timer(0.4).timeout
		hide_card()

func hide_card() -> void:
	if card.visible:
		card.visible = false
		card_closed.emit()

func add_journal(key: String, entry: Dictionary) -> bool:
	for e in journal_entries:
		if e["key"] == key: return false
	journal_entries.append({"key": key, "title": entry.get("title", ""), "kind": entry.get("kind", ""),
		"text": entry.get("text", ""), "refs": entry.get("refs", [])})
	journal_list.add_item("%s — %s" % [entry.get("kind", "").split(" · ")[0], entry.get("title", "")])
	return true

func toggle_journal() -> void:
	journal.visible = not journal.visible
	if journal.visible and journal_entries.size() > 0:
		journal_list.select(0); _on_journal_pick(0)

func _on_journal_pick(i: int) -> void:
	var e: Dictionary = journal_entries[i]
	var t := "[b]%s[/b]\n[i]%s[/i]\n\n%s" % [e["title"], e["kind"], e["text"]]
	if e["refs"].size() > 0:
		t += "\n\n[i]Источники: " + "; ".join(e["refs"]) + "[/i]"
	journal_text.text = t

# ---------------------------------------------------------------- прочее
func set_objective(t: String) -> void:
	objective_label.text = t

func show_hint(t: String) -> void:
	hint_label.text = t
	hint_panel.visible = true
	if autoplay:
		await get_tree().create_timer(0.3).timeout
		hint_panel.visible = false

func set_counter(found: int, total: int) -> void:
	counter_label.text = "Быт: открыто %d из %d" % [found, total]

func set_plane(celestial_on: bool) -> void:
	plane_label.text = "План: небесный ✦" if celestial_on else "План: земной"
	celestial_rect.visible = true
	var tw := create_tween()
	tw.tween_method(func(v): (celestial_rect.material as ShaderMaterial).set_shader_parameter("amount", v),
		0.0 if celestial_on else 1.0, 1.0 if celestial_on else 0.0, 0.6)
	if not celestial_on:
		tw.tween_callback(func(): celestial_rect.visible = false)

func show_tooltip(t: String, at: Vector2) -> void:
	tooltip_label.text = t
	tooltip.visible = t != ""
	tooltip.position = at + Vector2(18, 18)

func set_perceptibility(v: float) -> void:
	percept_box.visible = v > 0.01
	percept_bar.value = v

func vision(on: bool, center_uv: Vector2) -> void:
	var m := vision_rect.material as ShaderMaterial
	m.set_shader_parameter("center", center_uv)
	vision_rect.visible = true
	var tw := create_tween()
	tw.tween_method(func(v): m.set_shader_parameter("amount", v), 0.0 if on else 1.0, 1.0 if on else 0.0, 1.6)
	if not on:
		tw.tween_callback(func(): vision_rect.visible = false)
	await tw.finished

func title_card(t: String, sub: String, sec: float) -> void:
	fade_label.text = t; fade_sub.text = sub
	fade_rect.color.a = 1.0
	var tw := create_tween()
	tw.tween_property(fade_label, "modulate:a", 1.0, 0.8)
	tw.parallel().tween_property(fade_sub, "modulate:a", 1.0, 1.2)
	tw.tween_interval(0.1 if autoplay else sec)
	tw.tween_property(fade_label, "modulate:a", 0.0, 0.6)
	tw.parallel().tween_property(fade_sub, "modulate:a", 0.0, 0.6)
	tw.tween_property(fade_rect, "color:a", 0.0, 1.0)
	await tw.finished

func fade_text(t: String, ref: String, mid: Callable = Callable()) -> void:
	fade_label.text = ""; fade_sub.text = t + ("\n\n" + ref if ref != "" else "")
	var tw := create_tween()
	tw.tween_property(fade_rect, "color:a", 1.0, 0.8)
	tw.tween_property(fade_sub, "modulate:a", 1.0, 0.6)
	tw.tween_interval(0.1 if autoplay else 2.6)
	await tw.finished
	if mid.is_valid(): mid.call()
	var tw2 := create_tween()
	tw2.tween_property(fade_sub, "modulate:a", 0.0, 0.5)
	tw2.tween_property(fade_rect, "color:a", 0.0, 0.9)
	await tw2.finished
