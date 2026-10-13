#!/usr/bin/env python3
"""Диагностическое сравнение ключевых поз: исходный рисунок · исходная поза · конечная поза; с костями; дорисовки.
Запуск: python3 tools/pose_sheet.py <папка кадров c_*_{n,d,s}00000001.png>  (кадры — см. README_RU.md)"""
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

R = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'stills')
SRC = os.path.join(HERE, '..', '..', 'nityananda_v07', 'source', 'Nityananda_Standing_Accepted_Working.png')
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font, fb, fh = ImageFont.truetype(F, 16), ImageFont.truetype(FB, 22), ImageFont.truetype(FB, 17)
fr = lambda a, m: Image.open(f'{R}/c_{a}_{m}00000001.png').convert('RGB')
orig = Image.open(SRC).convert('RGB').crop((340, 20, 860, 780))      # та же рамка, что у кадров (масштаб 1)


def sheet(fname, title, panels, heads, notes):
    w, h = panels[0].size
    top, gap = 64, 8
    lines = []
    for n in notes:
        lines += textwrap.wrap(n, 140, subsequent_indent='   ') or ['']
    out = Image.new('RGB', (len(panels) * (w + gap) - gap, top + h + 18 + 23 * len(lines)), 'white')
    d = ImageDraw.Draw(out)
    d.text((10, 8), title, fill=(30, 30, 30), font=fb)
    for i, (p, hd) in enumerate(zip(panels, heads)):
        out.paste(p, (i * (w + gap), top))
        d.text((i * (w + gap) + 6, top - 26), hd, fill=(60, 60, 60), font=fh)
    y = top + h + 10
    for l in lines:
        d.text((10, y), l, fill=(30, 30, 30), font=font)
        y += 23
    out.save(os.path.join(OUT, fname))
    print(fname)


sheet('1_poses_clean.png', 'Ключевые позы без разметки (Godot 4.3, масштаб 1:1 к рисунку)',
      [orig, fr('start', 'n'), fr('end', 'n')],
      ['исходный рисунок (v0.7)', 'исходная поза: держит сосуд', 'конечная: сосуд у груди, голова склонена'],
      ['Кисть с хватом и сосуд — технические черновики (новый рисунок), не авторские. Ноги, лицо, тюрбан, волосы, палитра, '
       'длина рук — из рисунка без изменений. Исходная поза: локоть согнут на 40° (с одним хватом при прямой руке сосуд был бы '
       'наклонён на ~50°). Конечная: плечо отведено назад на 24°, локоть 119°, запястье +15°, голова от 0 до 8° вокруг точки у уха.'])
sheet('2_poses_diagnostic.png', 'Диагностика ключевых поз: кости и дорисованные участки',
      [fr('start', 'd'), fr('end', 'd'), fr('start', 's'), fr('end', 's')],
      ['исходная — кости', 'конечная — кости', 'исходная — дорисовки', 'конечная — дорисовки'],
      ['Кости: красное — плечо → локоть → запястье (белые кружки — шарниры), оранжевое — ось кисти, коричневое — ось сосуда, '
       'синее — точка наклона головы и ось головы. Наклон сосуда: исходная 10,6°, конечная 0,5° от вертикали.',
       'Пурпур — всё, чего нет в исходном рисунке: кисть с хватом, сосуд, накладки локтя, шаль под волосами и под куполом плеча, '
       'шея над линией разреза, подложки v0.7 за рукой (шаль, торс, шнур, дхоти). В конечной позе открыты: шаль за плечом '
       '(между волосами и полосой шали), полоса за бывшим положением предплечья (дхоти и шаль, подложка v0.7 — видна мелкая '
       '«ступенчатая» текстура), шея под волосами.'])
