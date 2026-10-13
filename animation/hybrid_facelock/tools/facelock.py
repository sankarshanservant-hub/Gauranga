#!/usr/bin/env python3
"""Гибрид, шаг 1: закрепление лица в сгенерированном ролике.

Тело, ткань и волосы — из сгенерированного видео; голова (тюрбан, лицо, ухо, верх волос у головы)
каждый кадр подставляется из утверждённого исходного рисунка. Положение головы отслеживается по кадрам
(ECC, поворот + сдвиг относительно первого кадра) и сглаживается во времени; масштаб — постоянный,
по совмещению исходника с первым кадром.

Запуск:  python3 -I tools/facelock.py <исходный PNG> <папка кадров ролика> <выходная папка>
"""
import json
import os
import sys

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d

SRC, FR, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
frames = sorted(f for f in os.listdir(FR) if f.endswith('.png'))
src = cv2.imread(SRC)
f0 = cv2.imread(os.path.join(FR, frames[0]))
H, W = f0.shape[:2]

# Область головы в исходнике (координаты холста 1054×1492): тюрбан, лицо, ухо, верх волос у головы.
# Перед лицом и над тюрбаном область заходит на фон — фон исходника закрывает остатки сгенерированной головы.
HEAD_POLY = np.array([(470, 40), (640, 30), (690, 90), (700, 175), (680, 230), (640, 250),
                      (600, 262), (556, 262), (520, 246), (488, 205), (466, 140)], np.float32)
FEATHER_BACK = 7      # px кадра: мягкий стык с волосами и шеей
GRAD = lambda g: cv2.GaussianBlur(g, (0, 0), 1.5)


def gray(im):
    return GRAD(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0)


# 1. исходник → первый кадр (аффинно, уточнение ECC по всей фигуре)
s0 = 0.570
A = np.array([[s0, 0, -2.4], [0, s0, -1.3]], np.float32)
src_in_f0 = cv2.warpAffine(src, A, (W, H), borderValue=tuple(int(v) for v in src[5, 5]))
_, A_d = cv2.findTransformECC(gray(src_in_f0), gray(f0), np.eye(2, 3, dtype=np.float32), cv2.MOTION_AFFINE,
                              (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
A_d3 = np.vstack([A_d, [0, 0, 1]])
# ECC: f0(x) ≈ src_in_f0(W x) → src_in_f0 → f0 через обратную
A_src_f0 = (np.linalg.inv(A_d3) @ np.vstack([A, [0, 0, 1]]))[:2]

# 2. маска головы в координатах первого кадра
poly_f0 = cv2.transform(HEAD_POLY[None], A_src_f0)[0]
m0 = np.zeros((H, W), np.uint8)
cv2.fillPoly(m0, [poly_f0.round().astype(np.int32)], 255)
x, y, w, h = cv2.boundingRect(poly_f0.round().astype(np.int32))
roi = (max(x - 30, 0), max(y - 30, 0), min(x + w + 30, W), min(y + h + 30, H))
head0 = cv2.warpAffine(src, A_src_f0, (W, H), flags=cv2.INTER_AREA, borderValue=tuple(int(v) for v in src[5, 5]))

# 3. слежение за головой: поворот + сдвиг каждого кадра относительно первого (ECC в окне головы)
g0 = gray(f0)
tm = np.zeros((H, W), np.uint8)
tm[roi[1]:roi[3], roi[0]:roi[2]] = 255
tm = cv2.bitwise_and(tm, cv2.dilate(m0, np.ones((15, 15), np.uint8)))
def head_centroid(im):
    # грубое положение головы: центр тюрбана (синее в верхней части) и лица (кожа выше шеи)
    im = im.astype(int)
    b, g_, r = im[..., 0], im[..., 1], im[..., 2]
    lim = int(roi[3])
    blue = (b > 150) & (r < 140) & (b - g_ > 60)
    skin = (r > 200) & (g_ > 160) & (b < 200) & (r - b > 30)
    blue[lim:] = False
    skin[lim:] = False
    ys, xs = np.nonzero(blue)
    ys2, xs2 = np.nonzero(skin)
    return np.array([(xs.mean() + xs2.mean()) / 2, (ys.mean() + ys2.mean()) / 2])


c0 = head_centroid(f0)
track, cc = [], []
for fn in frames:
    im = cv2.imread(os.path.join(FR, fn))
    g = gray(im)
    d = head_centroid(im) - c0
    Wp = np.array([[1, 0, d[0]], [0, 1, d[1]]], np.float32)
    try:
        c, Wp = cv2.findTransformECC(g0, g, Wp, cv2.MOTION_EUCLIDEAN,
                                     (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-5), tm, 5)
    except cv2.error:
        c = float('nan')
    ang = np.degrees(np.arctan2(Wp[1, 0], Wp[0, 0]))
    track.append([ang, Wp[0, 2], Wp[1, 2]])
    cc.append(float(c))
track = np.array(track)
smooth = np.stack([gaussian_filter1d(track[:, k], 1.5, mode='nearest') for k in range(3)], 1)

# 4. сборка: голова из исходника поверх кадра
feather = cv2.GaussianBlur(m0.astype(np.float32) / 255, (0, 0), FEATHER_BACK / 2)
log = []
for i, fn in enumerate(frames):
    fr = cv2.imread(os.path.join(FR, fn)).astype(np.float32)
    ang, tx, ty = smooth[i]
    a = np.radians(ang)
    Wt = np.array([[np.cos(a), -np.sin(a), tx], [np.sin(a), np.cos(a), ty]], np.float32)
    # ECC: кадр_t(Wt·x) ≈ кадр_0(x) — точка x первого кадра переходит в Wt·x
    hd = cv2.warpAffine(head0, Wt, (W, H), flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    al = cv2.warpAffine(feather, Wt, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    out = hd * al + fr * (1 - al)
    cv2.imwrite(os.path.join(OUT, fn), out.clip(0, 255).astype(np.uint8))
    log.append({'frame': fn, 'ecc': cc[i], 'raw_deg_dx_dy': [round(float(v), 2) for v in track[i]],
                'used_deg_dx_dy': [round(float(v), 2) for v in smooth[i]]})
json.dump({'src_to_frame0_affine': A_src_f0.round(5).tolist(), 'frames': log},
          open(os.path.join(OUT, 'track.json'), 'w'), ensure_ascii=False, indent=0)
print('кадров', len(frames), 'ECC min %.3f median %.3f' % (np.nanmin(cc), np.nanmedian(cc)))
