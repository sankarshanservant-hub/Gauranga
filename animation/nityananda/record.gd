extends "res://main.gd"
# Обёртка для записи: сразу включает тест (как SPACE) и поднимает кадр на 50 px,
# т.к. при viewport 900 и rig.y=500 ступни (y=1936 в исходнике) уходят за нижний край.
func _ready() -> void:
    super._ready()
    position.y = -50
    caption.modulate = Color(0.2, 0.2, 0.2)
    playing = true
