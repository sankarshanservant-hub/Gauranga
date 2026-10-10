"""Готовит изображения сайта из исходников пользователя (site/assets/src → site/assets/img).

Тёмный фон вокруг свитков убирается в прозрачность (по яркости), чтобы свиток лежал на любом фоне,
а тень и свет давал CSS. Запуск: python3 site/tools/prep_assets.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'assets', 'src')
OUT = os.path.join(HERE, '..', 'assets', 'img')
os.makedirs(OUT, exist_ok=True)


def load(name):
    return Image.open(os.path.join(SRC, name)).convert('RGB')


def cutout(im, thr=34):
    """Тёмный фон → прозрачность. Фоном считается только тёмная область, связанная с краем картинки
    (заливка от краёв), поэтому сам свиток и бронза остаются полностью непрозрачными; мягкий переход —
    лишь по контуру (1–2 px)."""
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    cand = Image.fromarray(np.where(lum < thr, 0, 255).astype(np.uint8), 'L').copy()
    w, h = cand.size
    px = cand.load()
    step = 4
    seeds = [(x, 0) for x in range(0, w, step)] + [(x, h - 1) for x in range(0, w, step)] + \
            [(0, y) for y in range(0, h, step)] + [(w - 1, y) for y in range(0, h, step)]
    for xy in seeds:
        if px[xy] == 0:
            ImageDraw.floodfill(cand, xy, 128)
    alpha = np.where(np.asarray(cand) == 128, 0, 255).astype(np.uint8)
    alpha = np.asarray(Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(1.2)))
    rgba = np.dstack([a.astype(np.uint8), alpha])
    return Image.fromarray(rgba, 'RGBA')


def save(im, name, **kw):
    path = os.path.join(OUT, name)
    im.save(path, **kw)
    print(name, im.size, os.path.getsize(path) // 1024, 'КБ')


H = 560  # высота ленты в файле (px)

# Горизонтальная лента: полотно стыкуется само с собой по краям — повторяем как есть
plain = load('ribbon-plain.png')
plain = plain.resize((round(plain.width * H / plain.height), H), Image.LANCZOS)
save(cutout(plain), 'ribbon-tile.webp', quality=84)

# Начало ленты со скалкой: подгоняем высоту бумаги к полотну (бумага 72–632 → 64–644 у полотна);
# после подгонки картинка совпадает с полотном уже за скалкой (≈ x 400–600 при высоте 560) — режем там
rod = load('ribbon-rod-left.png')
k = (644 - 64) / (632 - 72)
rod = rod.resize((round(rod.width * k), round(rod.height * k)), Image.LANCZOS)
top = round(72 * k) - 64
rod = rod.crop((0, top, rod.width, top + 724))
rod = rod.resize((round(rod.width * H / 724), H), Image.LANCZOS).crop((0, 0, 520, H))
save(cutout(rod), 'ribbon-start.webp', quality=84)
save(cutout(rod.transpose(Image.FLIP_LEFT_RIGHT)), 'ribbon-end.webp', quality=84)

# Вертикальный свиток (окно чтения): ширина 640
W = 640
vt = load('vscroll-top.png')
vt = vt.resize((W, round(vt.height * W / vt.width)), Image.LANCZOS)
save(cutout(vt.crop((0, 0, W, 300))), 'vscroll-top.webp', quality=82)
vm = load('vscroll-middle.png')
vm = vm.resize((W, round(vm.height * W / vm.width)), Image.LANCZOS)
save(cutout(vm), 'vscroll-middle.webp', quality=82)  # стыкуется сама с собой — целиком
vb = load('vscroll-bottom.png')
k = (876 - 92) / (848 - 90)  # подогнать ширину бумаги к верхней части
vb = vb.resize((round(vb.width * k), round(vb.height * k)), Image.LANCZOS)
left = round(90 * k) - 92
vb = vb.crop((left, 0, left + 971, vb.height))
vb = vb.resize((W, round(vb.height * W / 971)), Image.LANCZOS)
save(cutout(vb.crop((0, vb.height - 260, W, vb.height))), 'vscroll-bottom.webp', quality=82)

# Фоны
desk = load('bg-desk-books.png')  # без свечи (2026-10-10); прежний вариант — bg-desk-candle.png
save(desk.resize((1600, round(desk.height * 1600 / desk.width)), Image.LANCZOS), 'bg-desk.jpg', quality=80)
sky = load('header-navadvipa-sunset.png')
save(sky.resize((1800, round(sky.height * 1800 / sky.width)), Image.LANCZOS), 'header-sunset.jpg', quality=80)


# Иллюстрации лил: src/lila/<id>.png (виньетка на белом) → img/<id>.webp с прозрачным фоном.
# Фон — светлая малонасыщенная область, связанная с краем картинки (заливка от краёв), вместе со светлой
# «бумажной» бахромой кисти; край затем чуть подрезается и смягчается (1–2 px). Живопись остаётся непрозрачной,
# со своими естественными краями; белые облака внутри не трогаются (они не связаны с краем через светлый фон).
def white_to_alpha(im, thr=140, sat=45, erode=9):
    a = np.asarray(im.convert('RGB'))
    ai = a.astype(int)
    light = (ai.min(axis=2) > thr) & ((ai.max(axis=2) - ai.min(axis=2)) < sat)
    cand = Image.fromarray(np.where(light, 0, 255).astype(np.uint8), 'L').copy()
    w, h = cand.size
    px = cand.load()
    seeds = [(x, 0) for x in range(0, w, 3)] + [(x, h - 1) for x in range(0, w, 3)] + \
            [(0, y) for y in range(0, h, 3)] + [(w - 1, y) for y in range(0, h, 3)]
    for xy in seeds:
        if px[xy] == 0:
            ImageDraw.floodfill(cand, xy, 128)
    alpha = Image.fromarray(np.where(np.asarray(cand) == 128, 0, 255).astype(np.uint8), 'L')
    alpha = alpha.filter(ImageFilter.MinFilter(erode)).filter(ImageFilter.GaussianBlur(1.6))
    return Image.fromarray(np.dstack([a, np.asarray(alpha)]), 'RGBA')


LILA = os.path.join(SRC, 'lila')
for f in sorted(os.listdir(LILA)) if os.path.isdir(LILA) else []:
    if not f.lower().endswith('.png'):
        continue
    im = Image.open(os.path.join(LILA, f))
    if im.mode == 'RGBA' and np.asarray(im)[:, :, 3].min() < 250:
        cut = im                                # уже с прозрачностью
    else:
        cut = white_to_alpha(im)
    cut.thumbnail((900, 900), Image.LANCZOS)
    save(cut, f[:-4] + '.webp', quality=86)
