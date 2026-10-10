"""Готовит изображения сайта из исходников пользователя (site/assets/src → site/assets/img).

Тёмный фон вокруг свитков убирается в прозрачность (по яркости), чтобы свиток лежал на любом фоне,
а тень и свет давал CSS. Запуск: python3 site/tools/prep_assets.py
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'assets', 'src')
OUT = os.path.join(HERE, '..', 'assets', 'img')
os.makedirs(OUT, exist_ok=True)


def load(name):
    return Image.open(os.path.join(SRC, name)).convert('RGB')


def cutout(im, lo=38, hi=95):
    """Тёмный фон → прозрачность; бумага и бронза остаются."""
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    alpha = np.clip((lum - lo) / (hi - lo), 0, 1)
    rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
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
desk = load('bg-desk-candle.png')
save(desk.resize((1600, round(desk.height * 1600 / desk.width)), Image.LANCZOS), 'bg-desk.jpg', quality=80)
sky = load('header-navadvipa-sunset.png')
save(sky.resize((1800, round(sky.height * 1800 / sky.width)), Image.LANCZOS), 'header-sunset.jpg', quality=80)

