"""Анализ походки: опережение стоп, сгиб коленей и искажение сеток дхоти (порт скиннинга main.gd)."""
import json, sys, numpy as np
from PIL import Image
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait
from gait import V, rot, ik

V03 = dict(slack=0.003, near_center=10, far_center=-10, bob=1.5, bob_hi=0.0, min_flex=5, toe_up=5,
           heel_up=14, swing_pitch=30, pitch_peak=0.22, flat_at=0.65, clear=12, amp=70, duty=0.6)

def setp(**kw):
    gait.G.update(kw); gait.legs.clear()
    for s_ in ('near', 'far'):
        lg = {k: V(gait.B[f'{s_}_{k}']) for k in ('hip', 'ankle', 'heel', 'ball', 'toe')}
        lg['l'] = np.linalg.norm(lg['hip'] - lg['ankle']) / 2 * (1 + gait.G['slack'])
        lg['knee'] = ik(lg['hip'], lg['ankle'], lg['l'], lg['l'])
        lg['center'] = lg['ball'][0] + gait.G[s_ + '_center']; lg['phase'] = 0. if s_ == 'near' else .5
        gait.legs[s_] = lg

def bone(ra, rb, ca, cb):
    ang = np.arctan2(*(cb - ca)[::-1]) - np.arctan2(*(rb - ra)[::-1])
    c, s = np.cos(ang), np.sin(ang); R = np.array([[c, -s], [s, c]])
    return lambda P: (P - ra) @ R.T + ca

def frames(n=36):
    G = gait.G; out = []
    for i in range(n):
        p = i / n
        root = V((0, -G['bob'] * np.cos(2 * np.pi * 2 * (p - G['bob_hi']))))
        F = {s: gait.foot(lg, (p + lg['phase']) % 1) for s, lg in gait.legs.items()}
        low = 0
        for s, lg in gait.legs.items():
            h = lg['hip'] + root; a = F[s][0]
            lmax = 2 * lg['l'] * np.cos(np.radians(G['min_flex'] / 2)); dx = a[0] - h[0]
            low = max(low, (a[1] - h[1]) - np.sqrt(max(lmax * lmax - dx * dx, 0)))
        root[1] += low
        M = {'root': (lambda r: (lambda P: P + r))(root.copy())}; info = {'p': p}
        for s, lg in gait.legs.items():
            h = lg['hip'] + root; a = F[s][0]; k = ik(h, a, lg['l'], lg['l'])
            M[s + '_leg'] = bone(lg['hip'], lg['ankle'], h, a)
            M[s + '_thigh'] = bone(lg['hip'], lg['knee'], h, k)
            M[s + '_shin'] = bone(lg['knee'], lg['ankle'], k, a)
            th = F[s][1]
            info[s + '_ball'] = a[0] + rot(lg['ball'] - lg['ankle'], th)[0]
            info[s + '_toe'] = a[0] + rot(lg['toe'] - lg['ankle'], th)[0]
            info[s + '_ankle'] = a[0]
            t1, t2 = k - h, a - k
            info[s + '_flex'] = np.degrees(np.arctan2(t1[0] * t2[1] - t1[1] * t2[0], t1 @ t2))
        out.append((info, M))
    return out

def mesh_metrics(proj, fr, layers=('dhoti_near', 'dhoti_far')):
    rig = json.load(open(proj + '/rig.json')); res = {}
    for L in rig['layers']:
        if L['name'] not in layers: continue
        m = L['mesh']; P = np.array(m['verts'], float).reshape(-1, 2); T = np.array(m['tris']).reshape(-1, 3)
        tex = np.array(Image.open(proj + '/' + L['texture']))[..., 3]; ox, oy = L['origin']
        c = P[T].mean(1).astype(int); vis = tex[np.clip(c[:, 1] - oy, 0, tex.shape[0] - 1), np.clip(c[:, 0] - ox, 0, tex.shape[1] - 1)] > 0
        W = {b: np.array(w) for b, w in m['weights'].items()}; ws = sum(W.values())
        smin, smax = [], []
        for info, M in fr:
            Q = sum(W[b][:, None] * M[b](P) for b in W) / ws[:, None]
            a0, a1, a2 = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]; b0, b1, b2 = Q[T[:, 0]], Q[T[:, 1]], Q[T[:, 2]]
            A = np.stack([a1 - a0, a2 - a0], -1); B = np.stack([b1 - b0, b2 - b0], -1)
            J = B @ np.linalg.inv(A); sv = np.linalg.svd(J, compute_uv=False)
            det = np.linalg.det(J)
            sv = sv[vis]; smin.append(np.where(det[vis] < 0, -1, sv[:, 1])); smax.append(sv[:, 0])
        smin = np.array(smin); smax = np.array(smax)
        res[L['name']] = dict(min_sigma=float(smin.min()), max_sigma=float(smax.max()),
                              frac_squeezed=float((smin < 0.85).mean()), frac_stretched=float((smax > 1.15).mean()),
                              worst_frame_min=int(smin.min(1).argmin()), worst_frame_max=int(smax.max(1).argmax()))
    return res

def leads(fr):
    d = np.array([i['near_ball'] - i['far_ball'] for i, _ in fr])
    return d.max(), -d.min()

if __name__ == '__main__':
    setp(**V03); fr = frames()
    nl, fl = leads(fr)
    print(f"v0.3: центр ближней стопы {gait.legs['near']['center']:.0f}, дальней {gait.legs['far']['center']:.0f}; "
          f"ближняя впереди дальней максимум на {nl:.0f} px, дальняя впереди ближней на {fl:.0f} px")
    print(mesh_metrics(sys.argv[1], fr))

def where(proj, fr, layer, weights=None, k=6):
    rig = json.load(open(proj + '/rig.json'))
    L = [l for l in rig['layers'] if l['name'] == layer][0]
    m = L['mesh']; P = np.array(m['verts'], float).reshape(-1, 2); T = np.array(m['tris']).reshape(-1, 3)
    tex = np.array(Image.open(proj + '/' + L['texture']))[..., 3]; ox, oy = L['origin']
    c = P[T].mean(1); ci = c.astype(int)
    vis = tex[np.clip(ci[:, 1] - oy, 0, tex.shape[0] - 1), np.clip(ci[:, 0] - ox, 0, tex.shape[1] - 1)] > 0
    W = weights(layer, P[:, 0], P[:, 1]) if weights else {b: np.array(w) for b, w in m['weights'].items()}
    ws = sum(W.values()); rows = []
    for fi, (info, M) in enumerate(fr):
        Q = sum(W[b][:, None] * M[b](P) for b in W) / ws[:, None]
        a0, a1, a2 = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]; b0, b1, b2 = Q[T[:, 0]], Q[T[:, 1]], Q[T[:, 2]]
        J = np.stack([b1 - b0, b2 - b0], -1) @ np.linalg.inv(np.stack([a1 - a0, a2 - a0], -1))
        sv = np.linalg.svd(J, compute_uv=False)
        for t in np.flatnonzero(vis & ((sv[:, 0] > 1.25) | (sv[:, 1] < 0.8))):
            rows.append((fi, int(c[t, 0]), int(c[t, 1]), round(float(sv[t, 1]), 2), round(float(sv[t, 0]), 2)))
    return rows
