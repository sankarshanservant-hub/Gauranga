extends Node2D

var rig := Node2D.new()
var joints: Dictionary = {}
var elapsed := 0.0
var playing := false
var caption: Label

func _ready() -> void:
    var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://rig.json"))
    add_child(rig)
    rig.position = Vector2(530, 500)
    rig.scale = Vector2(0.58, 0.58)
    var origin := Vector2(data.origin[0], data.origin[1])
    var pivots: Dictionary = {"root": origin}
    joints["root"] = rig
    for part in data.parts:
        var joint := Node2D.new()
        joint.name = part.name
        var pivot := Vector2(part.pivot[0], part.pivot[1])
        joint.position = pivot - pivots[part.parent]
        joints[part.parent].add_child(joint)
        joints[part.name] = joint
        pivots[part.name] = pivot
        var sprite := Sprite2D.new()
        sprite.texture = load("res://" + part.file)
        sprite.centered = false
        sprite.position = Vector2(part.bbox[0], part.bbox[1]) - pivot
        sprite.z_as_relative = false
        sprite.z_index = part.z
        joint.add_child(sprite)
    caption = Label.new()
    caption.position = Vector2(20, 20)
    caption.text = "SPACE: joint test | R: exact rest pose\nTechnical draft. No natural walk cycle; hidden legs are missing."
    add_child(caption)

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            playing = not playing
        elif event.keycode == KEY_R:
            playing = false
            elapsed = 0.0
            reset_pose()

func reset_pose() -> void:
    rig.position = Vector2(530, 500)
    for key in joints:
        joints[key].rotation = 0.0

func _process(delta: float) -> void:
    if not playing:
        return
    elapsed += delta
    var phase := elapsed * 2.0
    rig.position = Vector2(530 + 70 * sin(phase * 0.25), 500 + 1.5 * sin(phase))
    joints["arm_down_upper"].rotation = deg_to_rad(1.5) * sin(phase)
    joints["arm_down_forearm"].rotation = deg_to_rad(2.0) * sin(phase + 0.5)
    joints["arm_down_hand"].rotation = deg_to_rad(1.0) * sin(phase)
    joints["arm_open_forearm"].rotation = deg_to_rad(1.0) * sin(phase)
    joints["arm_open_hand"].rotation = deg_to_rad(2.0) * sin(phase + 0.5)
