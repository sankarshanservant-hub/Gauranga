#!/usr/bin/env python3
"""Нитьянанда, тест повторно используемых действий v1: сборка частей.

Переиспользует слои проекта v0.7 (../../nityananda_v07/assets, rig.json) и исходный рабочий рисунок.
Из них делит: голову (лицо, тюрбан, ухо, волосы) — отдельный блок; полосу шали над плечом — поверх руки;
руку — на плечо и предплечье с круглыми накладками в локте; кисть исходника заменяется кистью с хватом.
Новые рисунки (технические черновики, не авторские): кисть с хватом, сосуд, накладки локтя,
подложки под головой (шея, шаль под волосами). Всё новое и всё подложенное — в diag-текстурах пурпуром
и отдельными PNG в missing/ (координаты холста исходника, смещение, маска).

Запуск (из папки project):  python3 -I tools/build_parts.py
"""
import json
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, '..')
V07 = os.path.join(PROJ, '..', '..', 'nityananda_v07')
SRC = os.path.join(V07, 'source', 'Nityananda_Standing_Accepted_Working.png')
OUT_A = os.path.join(PROJ, 'assets')
OUT_M = os.path.join(PROJ, '..', 'missing')
os.makedirs(OUT_A, exist_ok=True)
os.makedirs(OUT_M, exist_ok=True)

src = np.array(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W, _ = src.shape
rig07 = json.load(open(os.path.join(V07, 'rig.json')))


def load_layer(L, diag=False):
    im = np.array(Image.open(os.path.join(V07, L['texture_diag' if diag else 'texture']))).astype(np.float32)
    out = np.zeros((H, W, 4), np.float32)
    x0, y0 = L['origin']
    h, w = im.shape[:2]
    out[y0:y0 + h, x0:x0 + w] = im
    out[..., 3] /= 255.0
    return out


LAY = {L['name']: load_layer(L) for L in rig07['layers']}
SYN = {}
for L in rig07['layers']:
    d = load_layer(L, True)
    SYN[L['name']] = (np.abs(d[..., :3] - LAY[L['name']][..., :3]).max(2) > 8) & (LAY[L['name']][..., 3] > 0)

# ---------------- опорные точки (холст исходника) ----------------
P = {
    'shoulder': (528.0, 340.0), 'elbow': (530.0, 552.0), 'wrist': (563.0, 752.0),
    'head_pivot': (560.0, 240.0),      # наклон головы: около уха, шея остаётся на корпусе
    'neck_front_jaw': (588.0, 226.0),
}
# голова: всё из слоя корпуса внутри многоугольника (линия разреза по шее: от угла челюсти вниз-назад под волосы)
HEAD_POLY = [(372, 20), (720, 20), (720, 226), (588, 226), (548, 260), (540, 281), (530, 283), (455, 372),
             (440, 392), (372, 402)]
# подложка шеи над разрезом (закрыта головой в покое; открывается при наклоне)
NECK_UL = [(589, 227), (589, 194), (566, 186), (546, 196), (530, 226), (528, 262), (538, 284), (548, 260)]
# полоса шали над плечом — поверх плеча руки и волос
BAND_YMAX = 350
BAND_X = (430, 612)
ELBOW_R = 25.5          # радиус накладки локтя (половина ширины руки на уровне локтя: 506–555)
LINE_W = 3.2            # толщина контура рисунка, px
WRIST_CUT = 14.0        # px от центра браслета вдоль предплечья: ниже — кисть исходника (заменяется)

skin = np.median(src[640:660, 515:540].reshape(-1, 3), 0)          # кожа руки
dark = np.array([28.0, 22.0, 34.0])                                   # контур
lum = src.mean(2)


def poly_mask(pts, dil=0):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 1)
    if dil:
        m = cv2.dilate(m, np.ones((dil, dil), np.uint8))
    return m > 0


def save_rgba(arr, path, crop=True):
    a = np.clip(arr, 0, None).copy()
    al = a[..., 3]
    if crop:
        ys, xs = np.nonzero(al > 0)
        x0, y0, x1, y1 = max(xs.min() - 4, 0), max(ys.min() - 4, 0), min(xs.max() + 5, W), min(ys.max() + 5, H)
    else:
        x0, y0, x1, y1 = 0, 0, W, H
    c = a[y0:y1, x0:x1]
    img = np.zeros(c.shape, np.uint8)
    img[..., :3] = np.clip(np.round(c[..., :3]), 0, 255)
    img[..., 3] = np.clip(np.round(c[..., 3] * 255), 0, 255)
    img[img[..., 3] == 0, :3] = 0
    Image.fromarray(img, 'RGBA').save(path)
    return [int(x0), int(y0)], [int(x1 - x0), int(y1 - y0)]


def over(dst, top):
    a = top[..., 3:4]
    out = dst.copy()
    out[..., 3:4] = a + dst[..., 3:4] * (1 - a)
    out[..., :3] = (top[..., :3] * a + dst[..., :3] * dst[..., 3:4] * (1 - a)) / np.maximum(out[..., 3:4], 1e-6)
    return out


def tint(rgba, mask):
    d = rgba.copy()
    d[mask, :3] = 0.45 * d[mask, :3] + 0.55 * np.array([255, 0, 200])
    return d


# ---------------- голова ----------------
torso = LAY['torso']
head_m = poly_mask(HEAD_POLY) & (torso[..., 3] > 0)
head = torso * head_m[..., None]
body_torso = torso * (~head_m)[..., None]
syn_torso = SYN['torso'] & ~head_m

# подложка шеи: кожа + продолжение передней линии шеи вверх под челюсть
neck_m = poly_mask(NECK_UL) & ~(body_torso[..., 3] >= 1)
neck_ul = np.zeros((H, W, 4), np.float32)
neck_ul[neck_m, :3] = np.median(src[240:270, 560:580].reshape(-1, 3), 0)
neck_ul[neck_m, 3] = 1
yy, xx = np.mgrid[0:H, 0:W]
nl = neck_m & (np.abs(xx - 585.5) <= LINE_W / 2) & (yy < 228)
neck_ul[nl, :3] = dark

# шаль под волосами: продолжение областей шали (ближайшая область заливки, её медианный цвет, контур по границам)
fill = lum > 70
n_lab, lab = cv2.connectedComponents(fill.astype(np.uint8), connectivity=4)
shawl = LAY['shawl']
band_m = (shawl[..., 3] > 0) & (yy < BAND_YMAX) & (xx >= BAND_X[0]) & (xx <= BAND_X[1]) & ~SYN['shawl']   # только видимая шаль, без подложки под рукой
src_shawl = fill & (shawl[..., 3] >= 1) & ~SYN['shawl']
from scipy import ndimage  # noqa: E402
d_sh, (iy, ix) = ndimage.distance_transform_edt(~src_shawl, return_indices=True)
other_fig = ((shawl[..., 3] > 0) | (body_torso[..., 3] > 0)) & ~head_m
under_hair = head_m & (ndimage.distance_transform_edt(~other_fig) < 45) & ~neck_m & (d_sh < 60)
ids = lab[iy, ix]
med = {}
for cid in np.unique(ids[under_hair]):
    med[cid] = np.median(src[lab == cid], 0)
hair_ul = np.zeros((H, W, 4), np.float32)
ty, tx = np.nonzero(under_hair)
hair_ul[ty, tx, :3] = np.array([med[c] for c in ids[ty, tx]])
hair_ul[ty, tx, 3] = 1
key = np.where(under_hair, ids, -1)
bnd = np.zeros((H, W), bool)
for sh in ((0, 1), (1, 0)):
    nb = np.roll(key, sh, axis=(0, 1))
    bnd |= under_hair & (nb >= 0) & (nb != key)
bl = np.clip(LINE_W / 2 + 0.5 - ndimage.distance_transform_edt(~bnd), 0, 1)
hair_ul[..., :3] = hair_ul[..., :3] * (1 - bl[..., None]) + dark * bl[..., None]

# ---------------- шаль: полоса над плечом отдельно ----------------
band = shawl * band_m[..., None]
shawl_rest = shawl * (~band_m)[..., None]

# ---------------- корпус (неподвижный) ----------------
body = np.zeros((H, W, 4), np.float32)
body_syn = np.zeros((H, W), bool)
for name, lay, syn in (('shawl', shawl_rest, SYN['shawl'] & ~band_m), ('far_foot', LAY['far_foot'], SYN['far_foot']),
                       ('dhoti_far', LAY['dhoti_far'], SYN['dhoti_far']), ('near_foot', LAY['near_foot'], SYN['near_foot']),
                       ('dhoti_near', LAY['dhoti_near'], SYN['dhoti_near'])):
    body = over(body, lay)
    body_syn = np.where(lay[..., 3] > 0.5, syn, body_syn)
body = over(body, hair_ul)
body_syn |= under_hair
body = over(body, neck_ul)
body_syn |= neck_m
body = over(body, body_torso)
body_syn = np.where(body_torso[..., 3] > 0.5, syn_torso, body_syn)

# ---------------- рука ----------------
arm = LAY['arm']
S, E, Wr = (np.array(P[k]) for k in ('shoulder', 'elbow', 'wrist'))
u_up = (E - S) / np.linalg.norm(E - S)
u_fo = (Wr - E) / np.linalg.norm(Wr - E)
nb_ = u_up + u_fo
nb_ /= np.linalg.norm(nb_)
rel = np.stack([xx - E[0], yy - E[1]], -1)
side = rel @ nb_                       # <0 — плечо, >0 — предплечье
along_fo = rel @ u_fo
hand_cut = along_fo > np.linalg.norm(Wr - E) + WRIST_CUT
arm_a = arm[..., 3] > 0
up_m = arm_a & (side <= 0)
fo_m = arm_a & (side > 0) & ~hand_cut


def disc(center, r, half_sign, axis):
    """Накладка сустава: круг кожи с контуром, только по одну сторону разреза."""
    d = np.hypot(xx - center[0], yy - center[1])
    a = np.clip(r + 0.5 - d, 0, 1)
    ring = np.clip(1 - np.abs(d - (r - LINE_W / 2)) + LINE_W / 2 - 0.5, 0, 1) * (d <= r + 0.5)
    s = (np.stack([xx - center[0], yy - center[1]], -1) @ axis) * half_sign > 0
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = skin * (1 - ring[..., None]) + dark * ring[..., None]
    out[..., 3] = a * s
    return out, (a > 0) & s


cap_up, cap_up_m = disc(E, ELBOW_R, +1, nb_)     # для плеча: полукруг по стороне предплечья
cap_fo, cap_fo_m = disc(E, ELBOW_R, -1, nb_)     # для предплечья: полукруг по стороне плеча
upper = over(cap_up, arm * up_m[..., None])
fore = over(cap_fo, arm * fo_m[..., None])
upper_syn = cap_up_m & ~up_m
fore_syn = cap_fo_m & ~fo_m


def fill_only(rgba, ring_px=5, keep=None):
    """Заливка без внешнего контура: для второго прохода (заливки поверх контуров соседних частей)."""
    m = rgba[..., 3] > 0.02
    dist = ndimage.distance_transform_edt(m)
    off_skin = np.abs(rgba[..., :3] - skin).max(2) > 28
    out = rgba.copy()
    rm = (dist <= ring_px) & off_skin & (rgba[..., :3].mean(2) < skin.mean() + 5)
    rm |= (dist <= 1.2) & m
    if keep is not None:
        rm &= ~keep          # браслет — целиком, с контуром (он лежит поверх кисти)
    out[rm, 3] = 0
    return out


# ---------------- кисть с хватом и сосуд (новый рисунок, технический черновик) ----------------
SS = 4
v_fo = np.array([-u_fo[1], u_fo[0]])          # поперёк кисти; «вниз» сосуда


def L2C(u, v):
    p = Wr + u * u_fo + v * v_fo
    return (float(p[0]) * SS, float(p[1]) * SS)


def spline_closed(pts, n=10):
    Pp = np.array(pts, float)
    out = []
    for i in range(len(Pp)):
        p0, p1, p2, p3 = Pp[i - 1], Pp[i], Pp[(i + 1) % len(Pp)], Pp[(i + 2) % len(Pp)]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return out


def draw_shape(dr_fill, dr_line, pts_uv, fillc, smooth=True, line=True):
    pts = spline_closed(pts_uv) if smooth else pts_uv
    poly = [L2C(u, v) for u, v in pts]
    dr_fill.polygon(poly, fill=fillc)
    if line:
        dr_line.line(poly + [poly[0]], fill=(0, 0, 0, 255), width=int(LINE_W * SS), joint='curve')


def render_layers(shapes):
    """shapes: [(points_uv, fill_rgb, smooth)], рисуются по порядку; возвращает RGBA холста (с контуром) и только заливку."""
    img = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    fill_img = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    for pts, col, sm, strokes in shapes:
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        lf = ImageDraw.Draw(layer)
        fl = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ff = ImageDraw.Draw(fl)
        c = tuple(int(v) for v in col) + (255,)
        draw_shape(lf, lf, pts, c, sm)
        draw_shape(ff, ff, pts, c, sm, line=False)
        for st in strokes:      # внутренние открытые штрихи (между пальцами)
            lf.line([L2C(u, v) for u, v in st], fill=(0, 0, 0, 255), width=int(LINE_W * SS * 0.8))
            ff.line([L2C(u, v) for u, v in st], fill=(0, 0, 0, 255), width=int(LINE_W * SS * 0.8))
        img = Image.alpha_composite(img, layer)
        fill_img = Image.alpha_composite(fill_img, fl)

    def to_arr(im):
        a = np.array(im.resize((W, H), Image.LANCZOS)).astype(np.float32)
        a[..., 3] /= 255.0
        blk = a[..., :3].max(2) < 1
        a[blk, :3] = dark
        # чёрные штрихи PIL → цвет контура рисунка
        nearblack = a[..., :3].mean(2) < 60
        a[nearblack, :3] = dark
        return a
    return to_arr(img), to_arr(fill_img)


BRASS = np.array([200, 150, 64.0])
# Сосуд (ось вдоль v, верх = −v): венчик, горлышко, тулово, дно. Без узора, плоский цвет.
VC = 46.0     # центр тулова по u
vessel_pts = [(VC - 22, -54), (VC + 22, -54), (VC + 23, -48), (VC + 15, -45), (VC + 15, -34), (VC + 30, -24),
              (VC + 37, -4), (VC + 35, 22), (VC + 24, 40), (VC + 18, 46), (VC - 18, 46), (VC - 24, 40),
              (VC - 35, 22), (VC - 37, -4), (VC - 30, -24), (VC - 15, -34), (VC - 15, -45), (VC - 23, -48)]
vessel, vessel_fill = render_layers([(vessel_pts, BRASS, False, [])])
# сглаженный контур сосуда: повторно со сплайном
vessel, vessel_fill = render_layers([(vessel_pts, BRASS, True, [])])

# Кисть: тыльная сторона к зрителю, четыре пальца обхватывают тулово спереди, большой палец сверху.
FW = 10.5
v0 = -20.0
fingers = []
for i in range(4):
    a_, b_ = v0 + i * FW, v0 + (i + 1) * FW
    m_ = (a_ + b_) / 2
    tip = 76 - abs(i - 1.2) * 2.5           # средние пальцы чуть длиннее
    fingers.append(([(44, a_ + 0.6), (tip - 4, a_ + 0.3), (tip, m_), (tip - 4, b_ - 0.3), (44, b_ - 0.6)], skin, True, []))
back = ([(-16, -17.5), (14, -20), (40, -21.5), (53, -19), (57, 0), (54, 21), (40, 23), (14, 20), (-16, 17.5)], skin, True,
        [[(53, -9.5), (60, -9.0)], [(54, 1.0), (61, 1.0)], [(53, 11.5), (60, 11.8)]])
thumb = ([(14, -16), (36, -23), (56, -28), (63, -25), (58, -20), (36, -14), (18, -10)], skin, True, [])
hand, hand_fill = render_layers(fingers + [back, thumb])

# ---------------- запись ----------------
parts = {}


def part(name, rgba, syn_mask, pivot, z, note, fill_rgba=None):
    org, size = save_rgba(rgba, os.path.join(OUT_A, f'{name}.png'))
    save_rgba_at(tint(rgba, syn_mask & (rgba[..., 3] > 0)), os.path.join(OUT_A, f'{name}_diag.png'), org, size)
    e = {'texture': f'assets/{name}.png', 'texture_diag': f'assets/{name}_diag.png', 'origin': org, 'size': size,
         'pivot': [float(pivot[0]), float(pivot[1])], 'z': z, 'note': note,
         'synth_pixels': int((syn_mask & (rgba[..., 3] > 0)).sum())}
    if fill_rgba is not None:
        save_rgba_at(fill_rgba, os.path.join(OUT_A, f'{name}_fill.png'), org, size)
        e['texture_fill'] = f'assets/{name}_fill.png'
    parts[name] = e


def save_rgba_at(rgba, path, org, size):
    x0, y0 = org
    c = rgba[y0:y0 + size[1], x0:x0 + size[0]]
    img = np.zeros(c.shape, np.uint8)
    img[..., :3] = np.clip(np.round(c[..., :3]), 0, 255)
    img[..., 3] = np.clip(np.round(c[..., 3] * 255), 0, 255)
    img[img[..., 3] == 0, :3] = 0
    Image.fromarray(img, 'RGBA').save(path)


ALL = np.ones((H, W), bool)
part('body', body, body_syn, (599, 593), 0, 'неподвижный корпус: шаль, дхоти, стопы, торс с шеей (слои v0.7) + подложки')
part('head', head, SYN['torso'] & head_m, P['head_pivot'], 1, 'голова с волосами и тюрбаном — один жёсткий блок')
part('upper_arm', upper, upper_syn, P['shoulder'], 2, 'плечо; накладка локтя — новый рисунок', fill_only(upper))
part('band', band, SYN['shawl'] & band_m, P['shoulder'], 3, 'полоса шали над плечом — поверх плеча и волос')
bangle = np.abs(along_fo - np.linalg.norm(Wr - E)) <= 16
part('forearm', fore, fore_syn, P['elbow'], 4, 'предплечье с браслетом; накладка локтя — новый рисунок', fill_only(fore, keep=bangle))
part('vessel', vessel, ALL, P['wrist'], 5, 'тестовый сосуд — новый рисунок (технический черновик)')
part('hand_grip', hand, ALL, P['wrist'], 6, 'кисть с хватом — новый рисунок (технический черновик)', hand_fill)

# недостающие рисунки: отдельные PNG + маски, координаты холста исходника
missing = {}
for name, rgba, m, why in (
        ('neck_under_head', neck_ul, neck_m, 'шея над линией разреза: закрыта головой, открывается при наклоне'),
        ('shawl_under_hair', hair_ul, under_hair, 'шаль и шея под волосами: открываются, когда волосы смещаются с головой'),
        ('elbow_cap_upper', cap_up * cap_up_m[..., None], cap_up_m & ~up_m, 'накладка локтя на плече (сторона предплечья)'),
        ('elbow_cap_forearm', cap_fo * cap_fo_m[..., None], cap_fo_m & ~fo_m, 'накладка локтя на предплечье (сторона плеча)'),
        ('body_behind_arm', body * (body_syn & (arm[..., 3] > 0))[..., None], body_syn & (arm[..., 3] > 0),
         'корпус, шаль, шнур и дхоти за рукой (подложки v0.7): открываются при подъёме руки'),
        ('hand_grip', hand, hand[..., 3] > 0, 'кисть с хватом — технический черновик, нужна доработка художником'),
        ('vessel', vessel, vessel[..., 3] > 0, 'тестовый сосуд — технический черновик')):
    rgba = rgba.copy()
    rgba[~m, 3] = 0
    if not m.any():
        continue
    org, size = save_rgba(rgba, os.path.join(OUT_M, f'{name}.png'))
    mk = np.zeros((H, W, 4), np.float32)
    mk[m] = [255, 255, 255, 1]
    save_rgba_at(mk, os.path.join(OUT_M, f'{name}_mask.png'), org, size)
    missing[name] = {'png': f'{name}.png', 'mask': f'{name}_mask.png', 'offset': org, 'size': size, 'what': why,
                     'pixels': int(m.sum())}
json.dump({'canvas': [W, H], 'coords': 'пиксели холста исходного рисунка (1054×1492), начало — левый верхний угол',
           'parts': missing}, open(os.path.join(OUT_M, 'missing.json'), 'w'), ensure_ascii=False, indent=1)

# крепление сосуда к кисти: в покое оба нарисованы в координатах холста; сосуд — дочерний кисти (общая точка Wr)
grip = {'vessel_parent': 'hand_grip', 'vessel_offset': [0, 0], 'note': 'сосуд жёстко привязан к кисти; хват один',
        'hand_axis_rest': [float(u_fo[0]), float(u_fo[1])], 'vessel_up_rest': [float(-v_fo[0]), float(-v_fo[1])]}
manifest = {'version': 'actions_v1', 'status': 'TECHNICAL_TEST', 'canvas': [W, H], 'source': 'Nityananda_Standing_Accepted_Working.png (v0.7)',
            'points': P, 'parts': parts, 'grip': grip,
            'z_order_bottom_to_top': ['body', 'head', 'upper_arm(line)', 'forearm(line)', 'vessel', 'hand_grip(line)',
                                      'upper_arm(fill)', 'hand_grip(fill)', 'forearm(fill)', 'band']}
json.dump(manifest, open(os.path.join(PROJ, 'parts.json'), 'w'), ensure_ascii=False, indent=1)

# проверка покоя: сборка частей (без кисти и сосуда) против исходника
comp = np.ones((H, W, 3), np.float32) * src[5, 5]
rest = np.zeros((H, W, 4), np.float32)
for r in (body, head, upper, fore, band):
    rest = over(rest, r)
comp = rest[..., :3] * rest[..., 3:4] + comp * (1 - rest[..., 3:4])
diff = np.abs(comp - src).max(2)
hand_zone = hand_cut & (arm[..., 3] > 0)
dz = diff.copy()
dz[cv2.dilate(hand_zone.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0] = 0
st = {'mean_abs_diff_excl_hand': float(dz.mean()), 'pixels_diff_gt_24_excl_hand': int((dz > 24).sum()),
      'note': 'покой без кисти и сосуда против исходника (кисть исходника заменена — исключена из сравнения)'}
os.makedirs(os.path.join(PROJ, 'diagnostics'), exist_ok=True)
json.dump(st, open(os.path.join(PROJ, 'diagnostics', 'rest_compare.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(st, ensure_ascii=False))
print({k: v['synth_pixels'] for k, v in parts.items()})
