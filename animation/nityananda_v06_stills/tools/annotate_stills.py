#!/usr/bin/env python3
"""Листы неподвижных кадров v0.6: без костей | с костями | разметка, с выводами по каждому кадру.

Разметка:
  пурпурный — скрытые участки, которых нет в рисунке (видна автоматическая подложка), буква «Д»;
  оранжевый — сетка искажает рисунок (σ ткани ≥ 1,12 или ≤ 0,88; порог 1,2/0,8), буква «С»;
  кольцо — колено (скрыто дхоти), пунктир — скрытая голень переносимой ноги, буква «К».
Запуск:  python3 tools/annotate_stills.py <папка сырых кадров>
"""
import json
import os
import sys
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

RAW = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'stills')
INFO = json.load(open(os.path.join(OUT, 'frames_info.json')))
SCALE, OX, OY = 0.75, -210, -30
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font, fbig, fsm = ImageFont.truetype(F, 17), ImageFont.truetype(FB, 21), ImageFont.truetype(FB, 16)

# Выводы по кадрам — визуальная оценка по кадру без костей плюс замеры (frames_info.json).
FRAMES = [
    ('0.50', 'near', '1_raskrytie_shaga', '1. Наибольшее раскрытие шага (q = 0,50; переносить будет ближняя нога)', [
        'Читается без линий: да. Стопы разведены, ближняя стопа позади на носке, дальняя впереди только что встала на пятку.',
        'К  Обе штанины почти прямые. Колени согнуты на 23° и 17°, ткань передаёт 2° и 1°. Для этой фазы это допустимо.',
        'Д  В просвете между штанинами видна дорисованная задняя часть дальней штанины с прямой кромкой (место 1 карты).',
        '    Ещё видны полоса под рукой (место 3) и дорисованная пятка дальней стопы (место 4).',
        'С  Искажения сетки нет: σ 0,95…1,04.',
    ]),
    ('0.77', 'near', '2_prohozhdenie', '2. Переносимая (ближняя) нога проходит мимо опорной (q = 0,77)', [
        'Читается без линий: слабо. Стопа проходит у самой земли (зазор ≈12 px холста), почти целиком перекрывая опорную стопу.',
        '    Подъём ноги угадывается в основном по стопе.',
        'К  Колено согнуто на 42°, ткань передаёт 9°. Голень наклонена назад на 23°, низ штанины — на 8°: голень скрыта.',
        'К  Колено выходит за передний край дхоти на 16 px. Передний край принадлежит дальней штанине и не выдвигается за ближним коленом.',
        'С  Сетка тянет рисунок под кистью и на задней драпировке ближней дхоти: σ до 1,16, точки ткани там растянуты.',
        'Д  Видны задняя часть дальней штанины (широкая полоса между шалью и ближней штаниной), подложка под кистью и пятка дальней стопы.',
    ]),
    ('0.80', 'near', '3_seredina_perenosa', '3. Середина переноса (q = 0,80, через 44 мс после кадра 2)', [
        'Читается без линий: почти как кадр 2. Проход мимо опорной наступает чуть раньше середины, поэтому позы почти совпадают.',
        'К  Колено согнуто на 37°, ткань передаёт 8°. Колено снаружи переднего края на 13 px. Голень скрыта (−19° против −5° у штанины).',
        'С  σ до 1,16 там же: под кистью и на задней драпировке.',
        'Д  То же, что в кадре 2: задняя часть дальней штанины, подложка под кистью, пятка дальней стопы.',
    ]),
    ('0.98', 'near', '4_pered_postanovkoi', '4. Непосредственно перед постановкой (q = 0,98)', [
        'Читается без линий: да. Ближняя стопа впереди, носок слегка поднят, пятка над точкой постановки.',
        '    Нога почти прямая (21°), сгиб на ткани не виден (2°). Колено у самого края силуэта (запас 8 px).',
        'Д  Наибольшая за цикл площадь дорисовок: задняя часть дальней штанины за ближней, продолжение шали за ближней дхоти,',
        '    полоса под рукой, пятка дальней стопы.',
        'С  Остаток растяжения на задней драпировке ближней дхоти: σ до 1,15.',
    ]),
    ('0.00', 'far', '5_far_raskrytie', '5. Дальняя нога: наибольшее раскрытие (q = 0,00; ближняя пятка касается)', [
        'Читается: да, это зеркальная поза кадра 1. Дальняя стопа позади на носке.',
        'Д  Те же дорисовки, что в кадре 4. С  σ до 1,15 на задней драпировке ближней дхоти.',
    ]),
    ('0.27', 'far', '6_far_prohozhdenie', '6. Дальняя нога проходит мимо опорной (q = 0,27)', [
        'Читается без линий: плохо. Переносимую дальнюю стопу почти целиком закрывает ближняя, видна узкая полоска.',
        'К  Колено согнуто на 38°, ткань передаёт 7°. Передний край дальней штанины слегка выдаётся у колена, колено внутри силуэта (23 px).',
        'С  Искажения сетки нет: σ 0,89…1,11.',
        'Д  Немного: полоса под кистью.',
    ]),
    ('0.30', 'far', '7_far_seredina', '7. Дальняя нога: середина переноса (q = 0,30)', [
        'Как кадр 6: переносимая нога видна только по выпуклости переднего края дхоти. Колено 35°, ткань 6°.',
    ]),
    ('0.48', 'far', '8_far_pered_postanovkoi', '8. Дальняя нога перед постановкой (q = 0,48)', [
        'Читается: да. Дальняя стопа впереди, почти на земле. Нога почти прямая (18°).',
        'Д  Задняя часть дальней штанины в просвете и полоса под рукой.',
    ]),
]


def load(ph, m):
    return np.array(Image.open(f'{RAW}/f_{ph}_{m}00000001.png').convert('RGB')).astype(int)


def scr(p):
    return (p[0] * SCALE + OX, p[1] * SCALE + OY)


def badge(d, xy, txt, col):
    x, y = xy
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(255, 255, 255), outline=col, width=3)
    d.text((x - 7, y - 10), txt, fill=col, font=fsm)


def annotated(ph, swing):
    n, sy, st = load(ph, 'n'), load(ph, 's'), load(ph, 't')
    ms = np.abs(sy - n).max(2) > 30
    mt = np.abs(st - n).max(2) > 12
    g = n.mean(2, keepdims=True)
    out = 0.55 * n + 0.45 * g
    out[mt] = 0.35 * out[mt] + 0.65 * np.array([255, 140, 0])
    out[ms] = 0.35 * out[ms] + 0.65 * np.array([225, 0, 165])
    im = Image.fromarray(out.astype(np.uint8))
    d = ImageDraw.Draw(im)
    info = INFO[ph]
    for side, col in (('near', (215, 20, 20)), ('far', (20, 60, 215))):
        k = scr(info[side]['knee']); a = scr(info[side]['ankle'])
        d.ellipse([k[0] - 10, k[1] - 10, k[0] + 10, k[1] + 10], outline=col, width=3)
        if side == swing:
            n_ = 14
            for i in range(n_):
                if i % 2 == 0:
                    t0, t1 = i / n_, (i + 1) / n_
                    d.line([(k[0] + (a[0] - k[0]) * t0, k[1] + (a[1] - k[1]) * t0),
                            (k[0] + (a[0] - k[0]) * t1, k[1] + (a[1] - k[1]) * t1)], fill=col, width=3)
            badge(d, (k[0] + 22, k[1] - 18), 'К', col)
    for mask, letter, col, nmax in ((ms, 'Д', (190, 0, 140), 3), (mt, 'С', (205, 105, 0), 2)):
        lab, nl = ndimage.label(ndimage.binary_dilation(mask, iterations=4))
        if nl == 0:
            continue
        sizes = ndimage.sum(mask, lab, range(1, nl + 1))
        for idx in np.argsort(sizes)[::-1][:nmax]:
            if sizes[idx] < 250:
                continue
            ys, xs = np.nonzero(lab == idx + 1)
            badge(d, (int(xs.mean()), int(ys.mean())), letter, col)
    return im


def sheet(ph, swing, fname, title, notes):
    panels = [Image.fromarray(load(ph, 'n').astype(np.uint8)), Image.fromarray(load(ph, 'd').astype(np.uint8)),
              annotated(ph, swing)]
    heads = ['без костей', 'с костями', 'разметка']
    w, h = panels[0].size
    top, gap = 64, 6
    lines = []
    for line in notes:
        lines += textwrap.wrap(line, 112, subsequent_indent='    ') or ['']
    notes = lines
    text_h = 30 + 24 * len(notes) + 10
    out = Image.new('RGB', (3 * w + 2 * gap, top + h + text_h), (255, 255, 255))
    d = ImageDraw.Draw(out)
    d.text((10, 8), title, fill=(30, 30, 30), font=fbig)
    for i, (p, hd) in enumerate(zip(panels, heads)):
        out.paste(p, (i * (w + gap), top))
        d.text((i * (w + gap) + 10, top - 24), hd, fill=(80, 80, 80), font=font)
    y = top + h + 10
    for line in notes:
        d.text((10, y), line, fill=(30, 30, 30), font=font)
        y += 24
    path = os.path.join(OUT, fname + '.png')
    out.save(path)
    return path


def overview(items, fname, title):
    n_row = [Image.fromarray(load(ph, 'n').astype(np.uint8)) for ph, *_ in items]
    d_row = [Image.fromarray(load(ph, 'd').astype(np.uint8)) for ph, *_ in items]
    a_row = [annotated(ph, sw) for ph, sw, *_ in items]
    w, h = n_row[0].size
    out = Image.new('RGB', (4 * w, 40 + 3 * h + 2 * 30), (255, 255, 255))
    d = ImageDraw.Draw(out)
    d.text((10, 8), title, fill=(30, 30, 30), font=fbig)
    for r, (row, hd) in enumerate(((n_row, 'без костей'), (d_row, 'с костями'), (a_row, 'разметка'))):
        y = 40 + r * (h + 30)
        d.text((10, y), hd, fill=(80, 80, 80), font=font)
        for i, p in enumerate(row):
            out.paste(p, (i * w, y + 26))
            d.text((i * w + 10, y + 30), str(i + 1 if 'ближ' in title else i + 5), fill=(30, 30, 30), font=fbig)
    out.save(os.path.join(OUT, fname + '.png'))


for ph, swing, fname, title, notes in FRAMES:
    print(sheet(ph, swing, fname, title, notes))
overview([(f[0], f[1]) for f in FRAMES[:4]], '0_obzor_blizhnyaya', 'Перенос ближней ноги: 1 раскрытие · 2 проход · 3 середина · 4 перед постановкой')
overview([(f[0], f[1]) for f in FRAMES[4:]], '0_obzor_dalnyaya', 'Перенос дальней ноги: 5 раскрытие · 6 проход · 7 середина · 8 перед постановкой')
