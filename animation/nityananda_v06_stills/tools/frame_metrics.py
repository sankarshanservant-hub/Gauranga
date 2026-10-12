#!/usr/bin/env python3
"""Замеры для неподвижных кадров v0.6: сгиб колен (Godot и проверочный расчёт на Python),
сколько сгиба передаёт ткань, наклон голени против низа штанины, искажение сетки σ,
площадь видимых дорисовок и искажения, положение колена относительно силуэта дхоти.

Запуск:  python3 tools/frame_metrics.py <папка сырых кадров>  → stills/frames_info.json
"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
V06 = os.path.join(HERE, '..', '..', 'nityananda_v06', 'tools')
sys.path.insert(0, V06)
import gait, sim2, gait6, tune  # noqa: E402

RAW = sys.argv[1]
PHASES = ('0.50', '0.77', '0.80', '0.98', '0.00', '0.27', '0.30', '0.48')
SCALE, OX, OY = 0.75, -210, -30
BG = np.array([254, 252, 235])

gait6.install()
sim2.setp(**dict(sim2.V03, near_center=47, far_center=-47, amp=98, heel_off=0.30, slack=0.010))
WF = tune.make_w(dict(kz0=860, kz1=1140, fw=100, b_back=0.4, b_front=0.6, drape=0.2, d0=20, d1=200,
                      s0=1080, s1=1340, cuff=0.6))
res = {}
for ph in PHASES:
    p = float(ph)
    G = gait.G
    root = np.array([0, -G['bob'] * np.cos(2 * np.pi * 2 * (p - G['bob_hi']))])
    F = {s: gait.foot(lg, (p + lg['phase']) % 1) for s, lg in gait.legs.items()}
    low = 0
    for s, lg in gait.legs.items():
        h = lg['hip'] + root; a = F[s][0]
        lmax = 2 * lg['l'] * np.cos(np.radians(G['min_flex'] / 2)); dx = a[0] - h[0]
        low = max(low, (a[1] - h[1]) - np.sqrt(max(lmax * lmax - dx * dx, 0)))
    root[1] += low
    M = {'root': (lambda r: (lambda P: P + r))(root.copy())}
    info = {}
    for s, lg in gait.legs.items():
        h = lg['hip'] + root; a = F[s][0]; k = gait.ik(h, a, lg['l'], lg['l'])
        M[s + '_leg'] = sim2.bone(lg['hip'], lg['ankle'], h, a)
        M[s + '_thigh'] = sim2.bone(lg['hip'], lg['knee'], h, k)
        M[s + '_shin'] = sim2.bone(lg['knee'], lg['ankle'], k, a)
        t1, t2 = k - h, a - k
        info[s] = dict(hip=h.tolist(), knee=k.tolist(), ankle=a.tolist(),
                       flex=float(np.degrees(np.arctan2(t1[0] * t2[1] - t1[1] * t2[0], t1 @ t2))),
                       shin_deg=float(np.degrees(np.arctan2(t2[0], t2[1]))))
    for side, layer in (('near', 'dhoti_near'), ('far', 'dhoti_far')):
        hip, ank = np.array(tune.B[side + '_hip'], float), np.array(tune.B[side + '_ankle'], float)
        ys = np.array([880., 1060., 1240.]); xs = hip[0] + (ank[0] - hip[0]) * (ys - hip[1]) / (ank[1] - hip[1])
        P = np.stack([xs, ys], 1); Wt = WF(layer, P[:, 0], P[:, 1]); ws = sum(Wt.values())
        Q = sum(Wt[b][:, None] * M[b](P) for b in Wt) / ws[:, None]
        u, v = Q[1] - Q[0], Q[2] - Q[1]
        info[side]['fabric_bend'] = float(np.degrees(np.arctan2(u[0] * v[1] - u[1] * v[0], u @ v)))
        info[side]['tube_lower_deg'] = float(np.degrees(np.arctan2(v[0], v[1])))
    g = open(f'{RAW}/k_{ph}_t.txt').read()
    m = re.search(r'near flex=(-?[\d.]+).*far flex=(-?[\d.]+).*sigma=([\d.]+)\.\.([\d.]+)', g)
    info['godot'] = dict(near_flex=float(m.group(1)), far_flex=float(m.group(2)),
                         sigma=[float(m.group(3)), float(m.group(4))])
    n = np.array(Image.open(f'{RAW}/f_{ph}_n00000001.png').convert('RGB')).astype(int)
    sy = np.array(Image.open(f'{RAW}/f_{ph}_s00000001.png').convert('RGB')).astype(int)
    st = np.array(Image.open(f'{RAW}/f_{ph}_t00000001.png').convert('RGB')).astype(int)
    info['synth_px'] = int((np.abs(sy - n).max(2) > 30).sum())
    info['stretch_px'] = int((np.abs(st - n).max(2) > 12).sum())
    fig = ndimage.binary_fill_holes(np.abs(n - BG).max(2) > 14)
    d_in = ndimage.distance_transform_edt(fig); d_out = ndimage.distance_transform_edt(~fig)
    for side in ('near', 'far'):
        x, y = info[side]['knee'][0] * SCALE + OX, info[side]['knee'][1] * SCALE + OY
        xi, yi = int(round(x)), int(round(y))
        info[side]['knee_margin'] = float((d_in[yi, xi] if fig[yi, xi] else -d_out[yi, xi]) / SCALE)
    res[ph] = info
out = os.path.join(HERE, '..', 'stills', 'frames_info.json')
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
for ph, i in res.items():
    print(ph, f"колени {i['godot']['near_flex']:.0f}°/{i['godot']['far_flex']:.0f}°, ткань {i['near']['fabric_bend']:.0f}°/{i['far']['fabric_bend']:.0f}°, "
              f"запас колена {i['near']['knee_margin']:.0f}/{i['far']['knee_margin']:.0f} px, σ {i['godot']['sigma'][0]:.2f}…{i['godot']['sigma'][1]:.2f}")
