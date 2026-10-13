#!/usr/bin/env python3
"""Пример сборки недостающих рисунков (missing/*.png) поверх исходного рисунка.

Каждый PNG — прозрачный, в координатах холста исходника (1054×1492): кладётся в точку offset из
missing/missing.json без масштаба и поворота. Маска (*_mask.png) — те же размеры, белое = участок.
Так же их подключает tools/build_parts.py (в покое): художник может заменить PNG своим рисунком того же
размера и смещения, затем пересобрать части — проект Godot подхватит новые текстуры без правки кода.

Запуск: python3 tools/compose_missing.py   → missing/example_assembly.png
"""
import json
import os

from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, '..', 'missing')
SRC = os.path.join(HERE, '..', '..', 'nityananda_v07', 'source', 'Nityananda_Standing_Accepted_Working.png')
man = json.load(open(os.path.join(M, 'missing.json')))
base = ImageEnhance.Color(Image.open(SRC).convert('RGB')).enhance(0.15)
base = Image.blend(base, Image.new('RGB', base.size, 'white'), 0.55).convert('RGBA')
for name, e in man['parts'].items():
    if name in ('hand_grip', 'vessel'):
        continue          # новые предметы, а не скрытые участки: показаны отдельно в assets/
    base.alpha_composite(Image.open(os.path.join(M, e['png'])), tuple(e['offset']))
base.convert('RGB').crop((330, 20, 900, 1000)).save(os.path.join(M, 'example_assembly.png'))
print('missing/example_assembly.png')
