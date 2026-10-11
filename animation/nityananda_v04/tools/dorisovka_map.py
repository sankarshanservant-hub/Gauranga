#!/usr/bin/env python3
"""Карта мест для дорисовки: скрытые участки, которые сейчас заполнены автоматической подложкой
и открываются при ходьбе. Рисует их на исходном рисунке (координаты холста 1054×1492).

Запуск из корня проекта:  python3 -I tools/dorisovka_map.py
Результат: diagnostics/dorisovka_map.png, diagnostics/dorisovka_regions.json
"""
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

rig = json.load(open('rig.json'))
src = Image.open(rig['source']).convert('RGB')
W, H = src.size


def canvas_mask(name):
    L = [l for l in rig['layers'] if l['name'] == name][0]
    a = np.array(Image.open(L['texture']).convert('RGBA')).astype(int)
    d = np.array(Image.open(L['texture_diag']).convert('RGBA')).astype(int)
    m = np.abs(a[..., :3] - d[..., :3]).max(2) > 8
    full = np.zeros((H, W), bool)
    ox, oy = L['origin']
    full[oy:oy + m.shape[0], ox:ox + m.shape[1]] = m
    return full


def canvas_alpha(name):
    L = [l for l in rig['layers'] if l['name'] == name][0]
    a = np.array(Image.open(L['texture']).convert('RGBA'))[..., 3] > 0
    full = np.zeros((H, W), bool)
    ox, oy = L['origin']
    full[oy:oy + a.shape[0], ox:ox + a.shape[1]] = a
    return full


arm = canvas_alpha('arm')
yy, xx = np.mgrid[0:H, 0:W]
REG = [
    ('1', 'Задняя часть дальней штанины за ближней: контур от пояса до просвета между штанинами, '
          'складки, точки ткани. Сейчас край задан прямой линией (предположение). Открывается почти '
          'весь цикл — главное место.', canvas_mask('dhoti_far') & ~arm, (230, 0, 160)),
    ('2', 'Продолжение шали за задним краем ближней дхоти (полосы и нижний край шали). '
          'Открывается, когда ближняя нога впереди.', canvas_mask('shawl') & ~arm & (yy > 700), (255, 120, 0)),
    ('3', 'Под рукой: шаль, пояс и дхоти за плечом, предплечьем и кистью; продолжение белого шнура. '
          'Открываются узкие полосы при махе руки.',
     (canvas_mask('shawl') | canvas_mask('dhoti_near') | canvas_mask('dhoti_far') | canvas_mask('torso')) & arm,
     (0, 150, 255)),
    ('4', 'Пятка дальней стопы (сейчас — копия пятки ближней стопы).',
     canvas_mask('far_foot') & (yy > 1365), (0, 170, 60)),
    ('5', 'Щиколотки под краями штанин (верх стоп при наклоне в переносе).',
     (canvas_mask('near_foot') | canvas_mask('far_foot')) & (yy <= 1365), (150, 90, 0)),
]

SHORT = {'1': 'Задняя часть дальней штанины за ближней (главное)',
         '2': 'Шаль за задним краем ближней дхоти',
         '3': 'Под рукой: шаль, пояс, дхоти, белый шнур',
         '4': 'Пятка дальней стопы',
         '5': 'Щиколотки под краями штанин'}
img = src.convert('RGBA')
over = np.zeros((H, W, 4), np.uint8)
regions = []
for key, text, m, col in REG:
    over[m] = (*col, 150)
    ys, xs = np.nonzero(m)
    if len(ys):
        regions.append({'n': key, 'description': text, 'pixels': int(m.sum()),
                        'bbox_canvas': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]})
img = Image.alpha_composite(img, Image.fromarray(over, 'RGBA'))
dr = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
except OSError:
    font = small = ImageFont.load_default()
for (key, text, m, col), r in zip(REG, regions):
    x0, y0, x1, y1 = r['bbox_canvas']
    dr.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=(*col, 255), width=3)
    lx = x0 - 46 if key in ('1', '2', '4', '5') else x1 + 10
    dr.ellipse([lx, y0, lx + 38, y0 + 38], fill=(*col, 255))
    dr.text((lx + 10, y0 + 2), key, fill=(255, 255, 255, 255), font=font)
# легенда
crop = img.crop((250, 230, 800, 1450)).convert('RGB')
leg_h = 250
out = Image.new('RGB', (crop.width, crop.height + leg_h), (255, 255, 255))
out.paste(crop, (0, 0))
d2 = ImageDraw.Draw(out)
y = crop.height + 8
d2.text((10, y), 'Места для дорисовки (v0.4), холст исходного PNG', fill=(0, 0, 0), font=small)
y += 26
for key, text, m, col in REG:
    d2.ellipse([10, y, 30, y + 20], fill=col)
    d2.text((38, y), f'{key}. {SHORT[key]}', fill=(0, 0, 0), font=small)
    y += 40
out.save('diagnostics/dorisovka_map.png')
json.dump(regions, open('diagnostics/dorisovka_regions.json', 'w'), ensure_ascii=False, indent=1)
for r in regions:
    print(r['n'], r['bbox_canvas'], r['pixels'])
