"""Перенос стопы v0.6 на Python (повтор main.gd) для расчёта до правки сцены.
Подключается к sim2/gait: заменяет gait.foot."""
import numpy as np
import gait
from gait import V, rot

P6 = dict(land_hold=0.10, clear_pow=1.0)


def hermite(p0, p1, m0, m1, u):
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * m1


def pitch_curve(q):
    """Наклон стопы по всей фазе (рад): непрерывная кривая через опорные точки — без остановки
    при отрыве от земли. Значения в точках те же, что в v0.5: 0 → 14° (отрыв) → 30° → 0 → −5°."""
    G = gait.G
    d = G['duty']
    sw = 1 - d
    k = [(G['heel_off'], 0.0), (d, G['heel_up']), (d + G['pitch_peak'] * sw, G['swing_pitch']),
         (d + G['flat_at'] * sw, 0.0), (1.0, -G['toe_up'])]
    xs = np.array([a for a, _ in k]); ys = np.radians([b for _, b in k])
    sec = np.diff(ys) / np.diff(xs)
    sl = np.zeros(len(xs))
    for i in range(1, len(xs) - 1):          # монотонный кубический (Фритч–Карлсон)
        if sec[i - 1] * sec[i] > 0:
            sl[i] = 2 / (1 / sec[i - 1] + 1 / sec[i])
    i = np.searchsorted(xs, q) - 1
    i = int(np.clip(i, 0, len(xs) - 2))
    h = xs[i + 1] - xs[i]; u = (q - xs[i]) / h
    return hermite(ys[i], ys[i + 1], sl[i] * h, sl[i + 1] * h, u)


def stance(lg, p):
    G = gait.G
    A, d = G['amp'], G['duty']
    ball = V((lg['center'] + A - 2 * A * p / d, lg['ball'][1]))
    if p < G['heel_phase']:
        th = -np.radians(G['toe_up']) * (1 - gait.ss(0, G['heel_phase'], p))
        heel = ball - (lg['ball'] - lg['heel'])
        return heel + rot(lg['ankle'] - lg['heel'], th), th
    th = pitch_curve(p) if p > G['heel_off'] else 0.
    return ball + rot(lg['ankle'] - lg['ball'], th), th


def foot(lg, p):
    G = gait.G
    d = G['duty']
    if p < d:
        return stance(lg, p)
    s = (p - d) / (1 - d)
    a0, _ = stance(lg, d - 1e-9)
    a1, _ = stance(lg, 0.0)
    m = -2 * G['amp'] * (1 - d) / d            # ход опорной стопы за перенос (в долях s)
    # Траектория ведётся по пятке: от её положения при отрыве носка до точки постановки.
    # В конце переноса (land_hold) пятка в мире неподвижна и только опускается — без подката.
    th = pitch_curve(d + s * (1 - d))
    th0 = pitch_curve(d)
    h0 = a0 + rot(lg['heel'] - lg['ankle'], th0)
    h1 = a1 + rot(lg['heel'] - lg['ankle'], -np.radians(G['toe_up']))
    s1 = 1 - P6['land_hold']
    if s > s1:
        hx = h1[0] - m * (1 - s)
    else:
        u = s / s1
        hx = hermite(h0[0], h1[0] - m * (1 - s1), m * s1, m * s1, u)
    x = hx - rot(lg['heel'] - lg['ankle'], th)[0]
    c = G['clear'] * (np.sin(np.pi * s) ** 0.85 if s < 0.5 else np.sin(np.pi * s))   # как в main.gd v0.6
    y = min(lg['ball'][1] - c - rot(q - lg['ankle'], th)[1] for q in (lg['heel'], lg['ball'], lg['toe']))
    return V((x, y)), th


def install():
    gait.foot = foot
    gait.stance = stance
