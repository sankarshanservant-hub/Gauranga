"""Сравнение вариантов переноса до правки сцены (повтор формул main.gd)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait, sim2, tune, gait6
from gait import rot
W4 = dict(kz0=860, kz1=1140, fw=100, b_back=0.4, b_front=0.6, drape=0.2, d0=20, d1=200, s0=1080, s1=1340, cuff=0.6)
C = dict(sim2.V03, near_center=47, far_center=-47, amp=98)
ORIG_FOOT, ORIG_STANCE = gait.foot, gait.stance

def run(label, new=False, n=87, **kw):
    if new: gait6.install()
    else: gait.foot, gait.stance = ORIG_FOOT, ORIG_STANCE
    sim2.setp(**dict(C, **kw)); fr = sim2.frames(n)
    G = gait.G; vstep = 2 * G['amp'] / G['duty'] / n      # сдвиг корпуса за кадр
    out = {}
    for side, lg in gait.legs.items():
        flex = np.array([i[side + '_flex'] for i, _ in fr])
        q = np.array([(i / n + lg['phase']) % 1 for i in range(n)])
        pts = []
        for qi in q:
            a, th = gait.foot(lg, qi)
            pts.append([a + rot(lg[k] - lg['ankle'], th) for k in ('heel', 'ball', 'toe')])
        pts = np.array(pts)                                  # n×3×2
        wx = pts[..., 0] + (np.arange(n) * vstep)[:, None]
        g = lg['ball'][1]; h = g - pts[..., 1]               # высота над землёй
        vel = np.abs(np.gradient(wx, axis=0))
        sw = q >= G['duty']
        drag = ((h < 3) & (h > 0.6) & (vel > 1.0) & sw[:, None]).sum()
        slide = (vel * (h <= 0.6)).max()
        back = (-np.gradient(wx[:, 1])[sw]).max()
        acc = np.abs(np.diff(np.r_[flex, flex[:2]], 2)).max()
        st = flex[~sw]; sws = flex[sw]
        out[side] = (st.min(), st.max(), sws.max(), sws[-max(2, n // 30):].min(), h[sw].min(axis=1)[3:-3].min(), drag, slide, back, acc)
    e = tune.evaluate(fr, tune.make_w(W4))
    ry = []
    print(f'{label}')
    for side, v in out.items():
        print(f'  {side:4s}: опора {v[0]:.0f}–{v[1]:.0f}°, перенос макс {v[2]:.0f}°, перед постановкой {v[3]:.0f}°, '
              f'мин. зазор в середине переноса {v[4]:.1f}px, волочение {v[5]} кадро-точек, скольжение на земле {v[6]:.2f}px/кадр, '
              f'назад {max(v[7],0):.2f}px/кадр, скачок сгиба {v[8]:.2f}°/кадр²')
    print('  ткань σ: ' + ', '.join(f'{k} {a:.2f}…{b:.2f}' for k, (a, b, *_ ) in e.items()))

if __name__ == '__main__':
    run('C v0.5 (исходный)')
    run('новый перенос (непрерывный наклон, отрыв/постановка на месте), зазор 12', new=True)
    run('то же, зазор 15', new=True, clear=15)
    run('то же, зазор 12, запас длины ноги 0.008', new=True, slack=0.008)
    run('то же, зазор 15, запас 0.008', new=True, clear=15, slack=0.008)
