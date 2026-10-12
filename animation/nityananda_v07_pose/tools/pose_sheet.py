#!/usr/bin/env python3
"""Листы теста позы прохода ближней ноги (q = 0,77): исходник v0.7 | A (риг и веса) | B (эскиз формы).

Лист 1 — без костей, лист 2 — с костями, лист 3 — разметка (растяжение ткани и дорисовки).
B — схема корректирующей формы ближней дхоти поверх позы A: контур, направление складок,
перекрытие дальней ноги. Это эскиз для доработки ассета, не текстура.

Запуск:  python3 tools/pose_sheet.py <папка сырых кадров render_pose.sh>
(в той же папке нужны only_dhoti_near/only_dhoti_far — рендер слоёв варианта A, см. README_RU.md)
"""
import os
import sys
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAW = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stills')
os.makedirs(OUT, exist_ok=True)
CROP = (330, 540, 800, 1440)          # пояс → стопы, масштаб 1:1 к холсту рисунка
X0, Y0 = CROP[:2]
BG = np.array([254, 252, 235])
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font, fsm, fbig, fhead = (ImageFont.truetype(F, 17), ImageFont.truetype(F, 14),
                          ImageFont.truetype(FB, 24), ImageFont.truetype(FB, 19))


def frame(tag, m):
    return Image.open(f'{RAW}/{tag}_{m}00000001.png').convert('RGB')


def mask(layer):
    a = np.array(Image.open(f'{RAW}/only_{layer}00000001.png').convert('RGB')).astype(int)
    return np.abs(a - BG).max(2) > 10


def c(p):
    return (p[0] - X0, p[1] - Y0)


def spline(pts, n=12):
    """Кривая Катмулла — Рома через точки (холст) → точки кадра-врезки."""
    P = np.array(pts, float)
    P = np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return [c(p) for p in out]


def arrow(d, a, b, col, w=3):
    a, b = np.array(c(a), float), np.array(c(b), float)
    d.line([tuple(a), tuple(b)], fill=col, width=w)
    v = (b - a) / np.linalg.norm(b - a)
    n_ = np.array([-v[1], v[0]])
    d.polygon([tuple(b), tuple(b - 12 * v + 6 * n_), tuple(b - 12 * v - 6 * n_)], fill=col)


# --- схема B (координаты холста; поза A при q = 0,77: бедро ближней ноги (579, 606),
#     колено (700, 967), щиколотка (552, 1317); см. diagnostics/pose_numbers.txt) ---
B_FRONT = [(648, 612), (652, 640), (668, 730), (690, 830), (710, 915), (722, 968), (719, 1030), (703, 1105),
           (684, 1175), (664, 1235), (642, 1290)]
B_BACK = [(552, 612), (548, 640), (556, 760), (572, 870), (590, 950), (586, 1030), (576, 1115), (569, 1200),
          (566, 1270), (570, 1312)]
B_CUFF = [(570, 1312), (600, 1322), (642, 1290)]
TENSION = [[(714, 958), (676, 840), (640, 710)], [(705, 975), (650, 860), (602, 735)],
           [(698, 992), (640, 905), (586, 800)]]
DRAPE = [[(596, 975), (622, 1003), (660, 995)], [(592, 1015), (626, 1048), (672, 1040)],
         [(588, 1058), (628, 1088), (680, 1082)]]
HANG = [[(690, 1030), (672, 1150), (648, 1262)], [(660, 1060), (632, 1175), (610, 1285)]]
CUFF_Z = [(584, 1262), (600, 1250), (612, 1272), (626, 1255), (636, 1280)]


def sketch(base):
    """B: схема поверх приглушённой позы A."""
    a = np.array(base).astype(float)
    g = a.mean(2, keepdims=True)
    a = 0.30 * a + 0.70 * (0.55 * g + 0.45 * 255)
    N, Fm = mask('dhoti_near')[Y0:CROP[3], X0:CROP[2]], mask('dhoti_far')[Y0:CROP[3], X0:CROP[2]]
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    # дальняя (опорная) штанина: видимая часть за ближней — пурпур (её задней половины в рисунке нет),
    # перекрытая ближней — голубая штриховка
    an = np.array(frame('A', 'n').crop(CROP)).astype(int)
    asy = np.array(frame('A', 's').crop(CROP)).astype(int)
    synth = np.abs(asy - an).max(2) > 30            # подложка (нет в рисунке)
    vis_far = Fm & ~N & synth
    hid_far = Fm & N
    a[vis_far] = 0.45 * a[vis_far] + 0.55 * np.array([225, 0, 165])
    hatch = hid_far & (((xx + yy) // 5) % 3 == 0)
    a[hatch] = 0.4 * a[hatch] + 0.6 * np.array([40, 150, 255])
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    poly = spline(B_FRONT) + spline(B_CUFF[::-1])[1:] + spline(B_BACK)[::-1]
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon(poly, fill=(70, 40, 255, 70))
    im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    d = ImageDraw.Draw(im)
    for L in (B_FRONT, B_BACK, B_CUFF):
        d.line(spline(L), fill=(200, 20, 20), width=5, joint='curve')
    for L in TENSION:
        d.line(spline(L), fill=(20, 20, 120), width=3)
        arrow(d, L[-2], L[-1], (20, 20, 120))
    for L in DRAPE:
        d.line(spline(L), fill=(0, 120, 60), width=3)
    for L in HANG:
        d.line(spline(L), fill=(20, 20, 120), width=2)
        arrow(d, L[-2], L[-1], (20, 20, 120), 2)
    d.line([c(p) for p in CUFF_Z], fill=(20, 20, 120), width=2)
    # метки
    for txt, p, col in (('1', (735, 960), (200, 20, 20)), ('2', (612, 812), (20, 20, 120)),
                        ('3', (650, 1015), (0, 120, 60)), ('4', (690, 1180), (20, 20, 120)),
                        ('5', (612, 1300), (20, 20, 120)), ('6', (530, 1080), (190, 0, 140)),
                        ('7', (640, 1120), (30, 120, 220))):
        x, y = c(p)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(255, 255, 255), outline=col, width=3)
        d.text((x - 6, y - 10), txt, fill=col, font=fsm)
    return im


def sheet(fname, title, panels, heads, notes):
    w, h = panels[0].size
    gap, top = 8, 70
    lines = []
    for line in notes:
        if line == '':
            lines.append('')
            continue
        bold = line.startswith('#')
        for k, part in enumerate(textwrap.wrap(line.lstrip('# '), 128 if len(panels) == 3 else 175, subsequent_indent='   ')):
            lines.append(('#' if bold and k == 0 else '') + part)
    text_h = 20 + 25 * len(lines)
    out = Image.new('RGB', (len(panels) * w + (len(panels) - 1) * gap, top + h + text_h), (255, 255, 255))
    d = ImageDraw.Draw(out)
    d.text((12, 8), title, fill=(30, 30, 30), font=fbig)
    for i, (p, hd) in enumerate(zip(panels, heads)):
        out.paste(p, (i * (w + gap), top))
        d.text((i * (w + gap) + 8, top - 28), hd, fill=(60, 60, 60), font=fhead)
    y = top + h + 12
    for line in lines:
        b = line.startswith('#')
        d.text((12, y), line.lstrip('#'), fill=(30, 30, 30), font=fhead if b else font)
        y += 25
    out.save(os.path.join(OUT, fname))
    print(os.path.join(OUT, fname))


crop = lambda im: im.crop(CROP)
HEADS = ['Исходник v0.7', 'A — настройка рига и весов', 'B — схема формы для дорисовки (эскиз)']
TITLE = 'Проход ближней ноги мимо опорной (q = 0,77), крупно, 1:1 к рисунку'

COMMON = [
    '#Что удалось исправить настройкой (A)',
    'Ближняя штанина идёт за своим коленом: ткань у колена переведена на кость бедра (80 %), ниже колена свисает с колена '
    '(перенос без поворота), к краю у щиколотки снова следует голени. Передний край ближней штанины на высоте колена — '
    'впереди колена (v0.7: колено выходило за свою штанину на ≈18 px, его прикрывала выдвинутая дальняя).',
    'Компенсация v0.7 отключена: дальняя штанина больше не выдвигается ради ближнего колена (сдвиг 0 вместо 28 px).',
    'Ширина ближней штанины сохранена (126 px на высоте колена, в покое 120) — не облегающие брюки; колено не открыто. '
    'Растяжение узора в позе σ 0,81–1,20 (порог 0,8–1,2; наибольшее — под кистью руки, не видно).',
    '#Что требует дорисовки (B)',
    'Складки ближней штанины остались вертикальными складками стоящей фигуры: сетка их только переносит. Натяжения от колена '
    'к поясу и провиса под коленом нет — без нарисованной формы поза читается как сдвинутая штанина, а не как согнутая нога.',
    'За ближней штаниной открылась задняя часть дальней (опорной) штанины. Её в рисунке нет: видна подложка с угаданным прямым '
    'краем (пурпур на схеме B и на листе разметки).',
    'Лицо, голова, верх тела, палитра и пропорции не менялись; длина шага, скорость и цикл — как в v0.7. Анимация не собиралась.',
]
LEGEND_B = [
    '#Схема B (эскиз для художника, не текстура)',
    '1 — контур корректирующей формы ближней дхоти (красный): спереди натянут от пояса к колену, колено скруглено, от колена ткань '
    'падает почти отвесно к краю у щиколотки; сзади — от ягодицы по бедру, под коленом неглубокий провис.',
    '2 — складки натяжения: от колена вверх-назад к поясу и бедру (3 веером). 3 — провисающие складки под коленом (дуги). '
    '4 — свисающие складки от колена к краю. 5 — сжатие у края штанины на голени (мелкие изломы).',
    '6 — пурпур: видимая задняя часть дальней (опорной) штанины, которой нет в рисунке (сейчас подложка), — дорисовать: прямая опорная нога, вертикальные висячие складки, '
    'край у щиколотки. 7 — перекрытие (голубая штриховка): ближняя штанина поверх дальней, край ближней даёт тень на дальнюю.',
]

n = [crop(frame('v07', 'n')), crop(frame('A', 'n'))]
n.append(sketch(n[1]))
sheet('1_bez_kostei.png', TITLE + ' — без костей', n, HEADS, COMMON + [''] + LEGEND_B)
dbg = [crop(frame('v07', 'd')), crop(frame('A', 'd'))]
dbg.append(sketch(dbg[1]))
sheet('2_s_kostyami.png', TITLE + ' — с костями', dbg, HEADS,
      ['Красное — ближняя нога (бедро, колено — белый кружок, голень, стопа), синее — дальняя (опорная). '
       'Сгиб ближнего колена 42°, опорного 6°; стопа над землёй 16 px — одинаково во всех вариантах.'] + [''] + COMMON)
diag = [crop(frame('v07', 't')), crop(frame('A', 't')), crop(frame('v07', 's')), crop(frame('A', 's'))]
sheet('3_razmetka.png', 'Разметка: растяжение ткани и дорисованные участки (q = 0,77)', diag,
      ['v0.7 — растяжение', 'A — растяжение', 'v0.7 — дорисовки', 'A — дорисовки'],
      ['Растяжение: жёлтый — близко к порогу (σ > 1,1 или < 0,9), красный — растяжение > 1,2, синий — сжатие < 0,8. '
       'v0.7: σ 0,85–1,16 (жёлтое — выдвинутая дальняя штанина). A: σ 0,81–1,20, жёлтое — ниже колена и под кистью.',
       'Дорисовки (пурпур) — подложки, которых нет в рисунке. В A за ближней штаниной видна задняя часть дальней штанины '
       '(угаданный прямой край) — главное место для дорисовки; пятка дальней стопы — как и раньше.'])
