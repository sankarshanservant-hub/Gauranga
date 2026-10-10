#!/usr/bin/env python3
"""Сборка слоёв и сеток для теста ходьбы Нитьянанды (v0.2) из одного цельного рисунка.

Запуск (из корня проекта Godot):
    python3 -I tools/build_rig.py source/Nityananda_Standing_Accepted_Working.png .

Исходный PNG не изменяется. Результат:
    assets/layer_<имя>.png        — RGBA-текстуры слоёв (кремовый фон → прозрачность)
    assets/layer_<имя>_diag.png   — те же текстуры, синтезированные подложки подкрашены пурпурным
    rig.json                      — кости (покой), слои, сетки, веса
    diagnostics/*                 — проверка неподвижной сборки

Подход: рисунок разбит на области заливки между контурами (компоненты связности).
Каждая область отнесена к слою по опорным точкам (SEEDS). Контур принадлежит верхнему
из соседних слоёв. Под краями подвижных слоёв нижний слой получает «подложку» —
продолжение своих областей заливки (ближайший цвет + контур по границе областей).
Подложка — адаптация, не авторский рисунок; в diag-текстурах она подкрашена.
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

SRC, OUT = sys.argv[1], sys.argv[2]
BG = np.array([254, 252, 235], np.float32)

# Порядок слоёв снизу вверх.
LAYERS = ['shawl', 'far_foot', 'dhoti_far', 'near_foot', 'dhoti_near', 'torso', 'arm']
Z = {n: i for i, n in enumerate(LAYERS)}

# Внутренние точки областей заливки → слой (координаты исходного холста 1054×1492).
SEEDS = {
    'torso': [(562, 71), (510, 103), (518, 124), (548, 124), (531, 151), (589, 188),
              (647, 399), (641, 541)],
    'shawl': [(601, 365), (567, 574), (527, 306), (461, 420), (605, 446), (445, 577),
              (481, 674), (384, 800), (511, 681), (488, 804), (443, 787), (397, 1098),
              (370, 905), (376, 969), (376, 1024), (380, 1051)],
    'arm': [(528, 380), (575, 748), (578, 815)],
    'dhoti_near': [(644, 582), (602, 584), (530, 1249), (503, 1084), (589, 643)],
    'dhoti_far': [(596, 1249), (626, 1064), (610, 1010)],
    'near_foot': [(495, 1380)],
    'far_foot': [(592, 1364)],
}

# Подложки: подвижный верхний слой -> ширина полосы (px) от краёв нижних слоёв.
# Под таким слоем строится одна общая подложка: каждый пиксель продолжает ближайшую
# область заливки из слоёв НИЖЕ него и принадлежит тому слою, чья это область.
OCCLUDERS = {'arm': 200, 'dhoti_near': 400, 'near_foot': 120, 'dhoti_far': 120}
# Предел продолжения нижнего слоя под верхним, px (без записи — без предела).
REACH = {
    ('dhoti_near', 'dhoti_far'): 200, ('dhoti_near', 'shawl'): 70,
    ('dhoti_near', 'near_foot'): 40, ('dhoti_near', 'far_foot'): 40,
    ('near_foot', 'far_foot'): 40, ('near_foot', 'dhoti_far'): 40, ('near_foot', 'shawl'): 10,
    ('dhoti_far', 'far_foot'): 40, ('dhoti_far', 'shawl'): 60,
}
# Допустимые области продолжения (многоугольники холста). Скрытая часть дальней штанины
# за ближней: её задний край задан вручную — от видимого края у щели между штанинами
# (567,1250) вверх под ближнюю дхоти. Это дорисовка-предположение, не авторский контур.
ALLOW = {('dhoti_near', 'dhoti_far'): [(567, 1252), (552, 1130), (540, 1000), (532, 870),
                                       (530, 740), (540, 600), (730, 600), (730, 1252)]}
# Узор подложки: области слоя под верхним слоем продолжаются узором указанной области
# (дальняя штанина сзади — основная ткань с точками, а не гладкая полоса).
PATTERN_AS = {('dhoti_near', 'dhoti_far'): (596, 1249)}
LINE_BY_LAYER = {'arm'}
# Шнур уходит за предплечье у запястья; его продолжение под рукой (до края руки) —
# дорисовка по кривизне видимого конца. Конец, направление, поворот (°/шаг 2 px).
CORD_END, CORD_DIR, CORD_TURN, CORD_STEPS = (576.0, 719.0), (-0.75, 0.66), 1.3, 45
# Анизотропия (масштаб по y, x): шаль продолжается под дхоти вбок, а не вниз ниже своего края.
ANISO = {('dhoti_near', 'shawl'): (3.0, 1.0), ('dhoti_far', 'shawl'): (3.0, 1.0)}
# Области, которые не продолжаем под другими слоями (тонкий шнур — дорисовка его пути неизвестна).
NO_EXTEND_SEEDS = [(647, 399)]

# Пятка дальней стопы закрыта подъёмом ближней. Её дорисовка — копия пятки ближней стопы
# того же рисунка со сдвигом (задняя линия щиколотки 470→560, подошва 1414→1403).
FAR_HEEL_SHIFT = (90, -11)
FAR_HEEL_SRC_XMAX = 525
FAR_SOLE_YMAX = 1407

# Кости в покое (координаты холста). Колени скрыты дхоти и вычисляются в Godot.
BONES = {
    'near_hip': [579, 610], 'near_ankle': [492, 1360],
    'near_heel': [470, 1414], 'near_ball': [578, 1414], 'near_toe': [614, 1406],
    'far_hip': [618, 611], 'far_ankle': [585, 1358],
    'far_heel': [560, 1403], 'far_ball': [672, 1404], 'far_toe': [708, 1393],
    'shoulder': [528, 340], 'elbow': [530, 552], 'wrist': [566, 759],
    'shawl_attach': [520, 307], 'shawl_mid': [430, 870],
    'head_anchor': [566, 240], 'pelvis_root': [599, 593],
}

MESH_CELL = {'shawl': 14, 'dhoti_far': 12, 'dhoti_near': 12, 'arm': 10}
RIGID = {'torso': 'root', 'near_foot': 'near_foot', 'far_foot': 'far_foot'}


def smooth(v, a, b):
    t = np.clip((v - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def weights_for(layer, x, y):
    """Веса вершин по положению в покое."""
    if layer == 'shawl':
        ua = smooth(y, 560, 1000)
        ub = smooth(y, 850, 1150)
        return {'root': 1 - ua, 'shawl_a': ua * (1 - ub), 'shawl_b': ua * ub}
    if layer in ('dhoti_near', 'dhoti_far'):
        side = 'near' if layer == 'dhoti_near' else 'far'
        # Ткань следует за линией бедро→щиколотка (без колена: широкая дхоти не повторяет
        # сгиб колена); у самого края штанины добавляется поворот голени.
        t = smooth(y, 640, 920)
        s = smooth(y, 1180, 1300)
        if side == 'near':
            # задняя драпировка (левее линии ноги) следует за ногой слабее
            hip, ank = BONES['near_hip'], BONES['near_ankle']
            lx = hip[0] + (ank[0] - hip[0]) * np.clip((y - hip[1]) / (ank[1] - hip[1]), 0, 1)
            t = t * (1 - 0.45 * smooth(lx - x, 15, 100))
        return {'root': 1 - t, side + '_leg': t * (1 - s), side + '_shin': t * s}
    if layer == 'arm':
        e = smooth(y, 505, 605)
        return {'arm_upper': 1 - e, 'arm_fore': e}
    raise ValueError(layer)


def main():
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'diagnostics'), exist_ok=True)
    im8 = np.array(Image.open(SRC).convert('RGB'))
    im = im8.astype(np.float32)
    H, W, _ = im.shape
    Lum = im.mean(2)
    Lbg = BG.mean()

    fill = Lum > 70
    n, lab = cv2.connectedComponents(fill.astype(np.uint8), connectivity=4)
    area = np.bincount(lab.ravel(), minlength=n)
    mean = np.stack([np.bincount(lab.ravel(), weights=im[..., c].ravel(), minlength=n)
                     for c in range(3)], 1) / np.maximum(area, 1)[:, None]
    med = mean.copy()
    for i in range(1, n):
        if area[i] >= 300:
            med[i] = np.median(im[lab == i], 0)

    comp_layer = np.full(n, -2, int)          # -1 фон, -2 не назначено
    for i in range(1, n):
        c = mean[i]
        if c[0] - c[2] > 12 and np.abs(c - BG).max() <= 14:
            comp_layer[i] = -1
    for name, pts in SEEDS.items():
        for (x, y) in pts:
            i = lab[y, x]
            assert fill[y, x] and i > 0, (name, x, y)
            assert comp_layer[i] in (-2, Z[name]), ('конфликт', name, x, y, comp_layer[i])
            comp_layer[i] = Z[name]
    big = area >= 300
    unassigned = [i for i in range(1, n) if big[i] and comp_layer[i] == -2]
    assert not unassigned, ('крупные области без слоя', unassigned)

    pix_layer = comp_layer[lab]
    bigm = fill & big[lab] & (pix_layer >= 0)
    dist_big, (iy, ix) = ndimage.distance_transform_edt(~bigm, return_indices=True)
    nearest_layer = pix_layer[iy, ix]

    owner = np.full((H, W), -1, int)
    m = fill & (pix_layer >= 0) & big[lab]
    owner[m] = pix_layer[m]
    m = fill & ~big[lab] & (comp_layer[lab] != -1)       # мелкие области (глаз, камень тюрбана…)
    owner[m] = nearest_layer[m]

    # Тёмные пиксели (контуры, волосы): верхний из слоёв, чья заливка ближе 3.5 px.
    dark = ~fill
    best = np.full((H, W), -1, int)
    any_near = np.zeros((H, W), bool)
    for li, name in enumerate(LAYERS):
        lm = (owner == li) & fill
        d = ndimage.distance_transform_edt(~lm)
        near = dark & (d <= 3.5)
        best[near] = np.maximum(best[near], li)
        any_near |= near
    owner[dark & any_near] = best[dark & any_near]
    rest = dark & ~any_near
    yy, xx = np.mgrid[0:H, 0:W]
    hair = rest & (yy < 450)
    owner[hair] = Z['torso']
    other = rest & ~hair
    owner[other] = nearest_layer[other]

    # Светлая кромка сглаживания чужого контура внутри нижней заливки отходит к верхнему
    # слою — иначе при сдвиге верхнего слоя на нижнем остаётся «тень» его контура.
    med_l = med.mean(1)
    for hi in range(len(LAYERS) - 1, 0, -1):
        dh = ndimage.distance_transform_edt(~(dark & (owner == hi)))
        fr = fill & (owner >= 0) & (owner < hi) & (dh <= 1.5) & (Lum < med_l[lab] - 8)
        owner[fr] = hi

    # Сглаженный край у фона: снимаем примесь крема, цвет — к контуру.
    bgpix = fill & (comp_layer[lab] == -1)
    a = np.clip(1.0 - Lum / Lbg, 0, 1)
    a[a < 0.06] = 0
    aa = bgpix & (a > 0)
    opaque = owner >= 0
    _, (jy, jx) = ndimage.distance_transform_edt(~opaque, return_indices=True)
    owner_aa = owner[jy, jx]
    owner[aa] = owner_aa[aa]
    alpha = np.where(opaque, 1.0, 0.0)
    alpha[aa] = a[aa]
    color = im.copy()
    with np.errstate(divide='ignore', invalid='ignore'):
        unm = (im - (1 - a)[..., None] * BG) / np.maximum(a, 1e-3)[..., None]
    color[aa] = np.clip(unm[aa], 0, 255)
    color[alpha == 0] = 0

    pure_bg = bgpix & ~aa

    # --- текстуры слоёв с подложками ---
    layer_rgba = {}
    for li, name in enumerate(LAYERS):
        rgba = np.zeros((H, W, 4), np.float32)
        own = owner == li
        rgba[own, :3] = color[own]
        rgba[own, 3] = alpha[own]
        layer_rgba[name] = rgba
    under_mask = {name: np.zeros((H, W), bool) for name in LAYERS}
    is_bgid = comp_layer == -1
    no_ext = np.zeros(n, bool)
    for (x, y) in NO_EXTEND_SEEDS:
        no_ext[lab[y, x]] = True
    src_ok = fill & big[lab] & ~no_ext[lab]
    bg_id = int(np.flatnonzero(is_bgid)[0])
    interior = ndimage.binary_erosion(fill & big[lab], iterations=3) & (alpha >= 1)

    def pattern_fill(ty, tx, cid):
        """Цвет подложки: узор той же области заливки, взятый со сдвигом (точки на дхоти,
        ровный цвет шали); если подходящего сдвига нет — медианный цвет области."""
        out = med[cid].copy()
        todo = ~is_bgid[cid]
        for r in (40, 70, 100, 140, 180, 230, 290):
            for ang in range(0, 360, 30):
                if not todo.any():
                    return out
                ox = int(round(r * np.cos(np.radians(ang))))
                oy = int(round(r * np.sin(np.radians(ang))))
                sx_, sy_ = tx + ox, ty + oy
                ok = todo & (sx_ >= 0) & (sx_ < W) & (sy_ >= 0) & (sy_ < H)
                i_ = np.flatnonzero(ok)
                good = interior[sy_[i_], sx_[i_]] & (lab[sy_[i_], sx_[i_]] == cid[i_])
                i_ = i_[good]
                out[i_] = im[sy_[i_], sx_[i_]]
                todo[i_] = False
        return out
    eff = owner.copy()          # владелец с учётом уже построенных подложек
    for occ_name in sorted(OCCLUDERS, key=lambda k: -Z[k]):
        band = OCCLUDERS[occ_name]
        zo = Z[occ_name]
        lower = (eff >= 0) & (eff < zo)
        d_low = ndimage.distance_transform_edt(~lower)
        target = (eff == zo) & (layer_rgba[occ_name][..., 3] >= 1) & (d_low <= band)
        filled = np.zeros((H, W), bool)
        if occ_name == 'near_foot':
            # пятка дальней стопы: копия пятки ближней стопы со сдвигом
            dx, dy = FAR_HEEL_SHIFT
            ty, tx = np.nonzero(target)
            sx, sy = tx - dx, ty - dy
            ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H) & (sx <= FAR_HEEL_SRC_XMAX) & (ty <= FAR_SOLE_YMAX)
            ok[ok] &= (owner[sy[ok], sx[ok]] == Z['near_foot']) & (alpha[sy[ok], sx[ok]] > 0)
            ff = layer_rgba['far_foot']
            ff[ty[ok], tx[ok], :3] = color[sy[ok], sx[ok]]
            ff[ty[ok], tx[ok], 3] = alpha[sy[ok], sx[ok]]
            under_mask['far_foot'][ty[ok], tx[ok]] = True
            eff[ty[ok], tx[ok]] = np.where(alpha[sy[ok], sx[ok]] >= 1, Z['far_foot'], eff[ty[ok], tx[ok]])
            filled[ty[ok], tx[ok]] = True
        rest_t = target & ~filled
        # Ближайшая область среди нижних слоёв, но каждый слой продолжается под верхним
        # не дальше своего предела (REACH); дальше — прозрачно (фон).
        best_d = np.full((H, W), np.inf)
        ids = np.full((H, W), -1, int)
        for gi in range(zo):
            src = ndimage.binary_erosion(src_ok & (owner == gi), iterations=1)
            if not src.any():
                continue
            samp = ANISO.get((occ_name, LAYERS[gi]), (1.0, 1.0))
            d, (sy, sx) = ndimage.distance_transform_edt(~src, sampling=samp, return_indices=True)
            d = np.where(d <= REACH.get((occ_name, LAYERS[gi]), 1e9), d, np.inf)
            if (occ_name, LAYERS[gi]) in ALLOW:
                am = np.zeros((H, W), np.uint8)
                cv2.fillPoly(am, [np.array(ALLOW[(occ_name, LAYERS[gi])], np.int32)], 1)
                d = np.where(am > 0, d, np.inf)
            upd = rest_t & (d < best_d)
            best_d[upd] = d[upd]
            ids[upd] = lab[sy[upd], sx[upd]]
            if (occ_name, LAYERS[gi]) in PATTERN_AS:
                px_, py_ = PATTERN_AS[(occ_name, LAYERS[gi])]
                ids[upd] = lab[py_, px_]
        d_bg = ndimage.distance_transform_edt(~pure_bg)
        to_bg = rest_t & ((d_bg < best_d) | (ids < 0))
        ids[to_bg] = bg_id
        # контур по границам областей; снаружи фигуры (прозрачно) — тоже граница с фоном.
        # Под рукой внутренних контуров не рисуем (только край с фоном): стыки мелких областей
        # шали и пояса иначе дают «лесенку» и прямоугольные рамки; открываются узкие полосы.
        if occ_name in LINE_BY_LAYER:
            key = np.where(ids >= 0, 10, -1)
            key[ids == bg_id] = 1
        else:
            key = ids.copy()
        key_b = key.copy()
        key_b[~rest_t & (alpha == 0)] = 1 if occ_name in LINE_BY_LAYER else bg_id
        bnd = np.zeros((H, W), bool)
        for sh in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nb = np.roll(key_b, sh, axis=(0, 1))
            bnd |= rest_t & (nb >= 0) & (nb != key)
        dline = ndimage.distance_transform_edt(~bnd)
        la = np.clip(2.0 - dline, 0, 1)
        ty, tx = np.nonzero(rest_t)
        cid = ids[ty, tx]
        # слой пикселя подложки: слой ближайшей области; для фона — слой ближайшей заливки
        lay = comp_layer[cid].copy()
        if (lay < 0).any():
            nb_l = np.where((owner >= 0) & (owner < zo) & fill, owner, -1)
            _, (qy, qx) = ndimage.distance_transform_edt(nb_l < 0, return_indices=True)
            fb = nb_l[qy, qx][ty, tx]
            lay[lay < 0] = fb[lay < 0]
        fc = pattern_fill(ty, tx, cid)
        fa = np.where(is_bgid[cid], 0.0, 1.0)
        l_ = la[ty, tx]
        out_a = l_ + fa * (1 - l_)
        out_c = (fc * (fa * (1 - l_))[:, None]) / np.maximum(out_a, 1e-6)[:, None]
        for li, name in enumerate(LAYERS):
            k = (lay == li) & (out_a > 0)
            if not k.any():
                continue
            rgba = layer_rgba[name]
            rgba[ty[k], tx[k], :3] = out_c[k]
            rgba[ty[k], tx[k], 3] = out_a[k]
            under_mask[name][ty[k], tx[k]] = True
            full = k & (out_a >= 1)
            eff[ty[full], tx[full]] = li

    # --- продолжение шнура под рукой (в слой корпуса) ---
    cord_id = lab[NO_EXTEND_SEEDS[0][1], NO_EXTEND_SEEDS[0][0]]
    cord_col = med[cord_id]
    pts = []
    p_ = np.array(CORD_END, float)
    d_ = np.array(CORD_DIR, float)
    d_ /= np.linalg.norm(d_)
    th_ = np.radians(CORD_TURN)
    rot = np.array([[np.cos(th_), -np.sin(th_)], [np.sin(th_), np.cos(th_)]])
    for _ in range(CORD_STEPS):
        pts.append(p_.copy())
        p_ = p_ + 2 * d_
        d_ = rot @ d_
    SS = 4
    x0c, y0c = 440, 680
    wc, hc = 200, 140
    pl = (np.array(pts) - [x0c, y0c]) * SS
    pl = pl.round().astype(np.int32).reshape(-1, 1, 2)
    m_out = np.zeros((hc * SS, wc * SS), np.uint8)
    m_core = np.zeros_like(m_out)
    cv2.polylines(m_out, [pl], False, 255, thickness=8 * SS, lineType=cv2.LINE_AA)
    cv2.polylines(m_core, [pl], False, 255, thickness=4 * SS, lineType=cv2.LINE_AA)
    a_out = cv2.resize(m_out, (wc, hc), interpolation=cv2.INTER_AREA) / 255.0
    a_core = cv2.resize(m_core, (wc, hc), interpolation=cv2.INTER_AREA) / 255.0
    region = (owner[y0c:y0c + hc, x0c:x0c + wc] == Z['arm'])
    tl = layer_rgba['torso'][y0c:y0c + hc, x0c:x0c + wc]
    a_out *= region
    a_core *= region
    base_a = tl[..., 3:4]
    col = tl[..., :3] * base_a
    col = col * (1 - a_out[..., None])                       # чёрный контур поверх
    al = base_a[..., 0] + a_out * (1 - base_a[..., 0])
    col = col * (1 - a_core[..., None]) + cord_col * a_core[..., None]
    al = al * (1 - a_core) + a_core
    tl[..., :3] = np.where(al[..., None] > 0, col / np.maximum(al, 1e-6)[..., None], 0)
    tl[..., 3] = al
    under_mask['torso'][y0c:y0c + hc, x0c:x0c + wc] |= (a_out > 0.05)

    # --- обрезка, сетки, запись ---
    rig = {'version': '0.2', 'status': 'TECHNICAL_TEST', 'canvas': [W, H],
           'source': 'source/Nityananda_Standing_Accepted_Working.png',
           'bones_rest': BONES, 'layers': []}
    for li, name in enumerate(LAYERS):
        rgba = layer_rgba[name]
        al = rgba[..., 3]
        ys, xs = np.nonzero(al > 0)
        pad = 16
        x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
        x1, y1 = min(xs.max() + pad + 1, W), min(ys.max() + pad + 1, H)
        crop = rgba[y0:y1, x0:x1]
        img = np.clip(np.round(crop), 0, 255).astype(np.uint8)
        img[..., 3] = np.clip(np.round(crop[..., 3] * 255), 0, 255).astype(np.uint8)
        img[img[..., 3] == 0, :3] = 0
        Image.fromarray(img, 'RGBA').save(os.path.join(OUT, 'assets', f'layer_{name}.png'))
        diag = img.copy()
        um = under_mask[name][y0:y1, x0:x1]
        diag[um, :3] = (0.45 * diag[um, :3] + 0.55 * np.array([255, 0, 200])).astype(np.uint8)
        Image.fromarray(diag, 'RGBA').save(os.path.join(OUT, 'assets', f'layer_{name}_diag.png'))
        entry = {'name': name, 'z': li, 'texture': f'assets/layer_{name}.png',
                 'texture_diag': f'assets/layer_{name}_diag.png',
                 'origin': [int(x0), int(y0)], 'size': [int(x1 - x0), int(y1 - y0)],
                 'synth_pixels': int(um.sum())}
        if name in RIGID:
            entry['rigid'] = RIGID[name]
        else:
            cell = MESH_CELL[name]
            occ = cv2.dilate((crop[..., 3] > 0).astype(np.uint8), np.ones((5, 5), np.uint8))
            h, w = occ.shape
            nx, ny = (w + cell - 1) // cell, (h + cell - 1) // cell
            vid = {}
            verts, tris = [], []

            def v(i, j):
                k = (i, j)
                if k not in vid:
                    vid[k] = len(verts)
                    verts.append((x0 + i * cell, y0 + j * cell))
                return vid[k]
            for j in range(ny):
                for i in range(nx):
                    if occ[j * cell:(j + 1) * cell + 1, i * cell:(i + 1) * cell + 1].any():
                        a_, b_, c_, d_ = v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)
                        tris += [a_, b_, c_, a_, c_, d_]
            vx = np.array([p[0] for p in verts], float)
            vy = np.array([p[1] for p in verts], float)
            wts = weights_for(name, vx, vy)
            entry['mesh'] = {
                'verts': [int(t) for p in verts for t in p],
                'tris': tris,
                'weights': {b: [round(float(t), 4) for t in arr]
                            for b, arr in wts.items() if np.asarray(arr).max() > 1e-4},
            }
        rig['layers'].append(entry)
    with open(os.path.join(OUT, 'rig.json'), 'w') as f:
        json.dump(rig, f, separators=(',', ':'))

    # --- проверка неподвижной сборки (порядок слоёв, нормальное наложение) ---
    comp = np.ones((H, W, 3), np.float32) * BG
    for name in LAYERS:
        rgba = layer_rgba[name]
        a_ = rgba[..., 3:4]
        comp = rgba[..., :3] * a_ + comp * (1 - a_)
    diff = np.abs(comp - im).max(2)
    stats = {
        'max_abs_diff': float(diff.max()),
        'mean_abs_diff': float(np.abs(comp - im).mean()),
        'pixels_diff_gt_2': int((diff > 2).sum()),
        'pixels_diff_gt_8': int((diff > 8).sum()),
        'pixels_diff_gt_24': int((diff > 24).sum()),
        'figure_pixels': int((alpha > 0).sum()),
        'synthesized_underlay_pixels': {k: int(v.sum()) for k, v in under_mask.items()},
        'note': 'Сравнение программной композиции слоёв в покое с исходным PNG на кремовом фоне; '
                'не проверка рендера Godot и не проверка движения.',
    }
    with open(os.path.join(OUT, 'diagnostics', 'rest_compare.json'), 'w') as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
    dvis = np.clip(diff * 8, 0, 255).astype(np.uint8)
    side = np.concatenate([im8, np.clip(comp, 0, 255).astype(np.uint8),
                           np.stack([dvis] * 3, -1)], 1)
    Image.fromarray(side).save(os.path.join(OUT, 'diagnostics', 'rest_side_by_side.png'))
    # карта слоёв
    pal = np.array([[60, 140, 255], [255, 170, 60], [140, 60, 200], [255, 220, 80],
                    [90, 40, 160], [240, 120, 120], [80, 200, 120]], np.float32)
    lm = np.ones((H, W, 3), np.float32) * 255
    for li in range(len(LAYERS)):
        m_ = owner == li
        lm[m_] = 0.35 * im[m_] + 0.65 * pal[li]
    for name in LAYERS:
        u = under_mask[name]
        lm[u & ((xx + yy) % 6 < 2)] = (255, 0, 200)
    Image.fromarray(lm.astype(np.uint8)).save(os.path.join(OUT, 'diagnostics', 'layer_map.png'))
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == '__main__':
    main()
