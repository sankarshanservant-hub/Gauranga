import json, itertools, sys, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import sim2
from PIL import Image
import os
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = {'near_hip': (579, 610), 'near_ankle': (492, 1360), 'far_hip': (618, 611), 'far_ankle': (585, 1358)}
def ss(v, a, b):
    t = np.clip((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def make_w(P):
    def w(layer, x, y):
        side = 'near' if layer == 'dhoti_near' else 'far'
        hip, ank = B[side + '_hip'], B[side + '_ankle']
        lx = hip[0] + (ank[0] - hip[0]) * np.clip((y - hip[1]) / (ank[1] - hip[1]), 0, 1)
        dl = x - lx
        t = ss(y, 640, 920); s = P.get('cuff', 1.0) * ss(y, P.get('s0', 1180), P.get('s1', 1300)); kz = ss(y, P['kz0'], P['kz1'])
        front = ss(dl, -P['fw'], P['fw'])
        b = P['b_back'] + (P['b_front'] - P['b_back']) * front
        if side == 'near':
            t = t * (1 - P['drape'] * ss(-dl, P['d0'], P['d1']))
        return {'root': 1 - t, side + '_leg': t * (1 - b) * (1 - s), side + '_thigh': t * b * (1 - kz) * (1 - s),
                side + '_shin': t * (b * kz * (1 - s) + s)}
    return w
rig = json.load(open(PROJ + '/rig.json')); MESH = {}
for L in rig['layers']:
    if L['name'] in ('dhoti_near', 'dhoti_far'):
        m = L['mesh']; P_ = np.array(m['verts'], float).reshape(-1, 2); T = np.array(m['tris']).reshape(-1, 3)
        tex = np.array(Image.open(PROJ + '/' + L['texture']))[..., 3]; ox, oy = L['origin']
        c = P_[T].mean(1).astype(int)
        vis = tex[np.clip(c[:, 1] - oy, 0, tex.shape[0] - 1), np.clip(c[:, 0] - ox, 0, tex.shape[1] - 1)] > 0
        MESH[L['name']] = (P_, T, vis)
def evaluate(fr, wf):
    out = {}
    for name, (P_, T, vis) in MESH.items():
        W = wf(name, P_[:, 0], P_[:, 1]); ws = sum(W.values())
        mn, mx = [], []
        A = np.stack([P_[T[:, 1]] - P_[T[:, 0]], P_[T[:, 2]] - P_[T[:, 0]]], -1); Ai = np.linalg.inv(A)
        for info, M in fr:
            Q = sum(W[b][:, None] * M[b](P_) for b in W) / ws[:, None]
            Bm = np.stack([Q[T[:, 1]] - Q[T[:, 0]], Q[T[:, 2]] - Q[T[:, 0]]], -1)
            sv = np.linalg.svd(Bm @ Ai, compute_uv=False)[vis]
            mn.append(sv[:, 1]); mx.append(sv[:, 0])
        mn = np.array(mn); mx = np.array(mx)
        out[name] = (mn.min(), mx.max(), (mn < 0.85).mean() * 100, (mx > 1.2).mean() * 100)
    return out
def setcenters(nc, fc):
    sim2.setp(**dict(sim2.V03, near_center=nc, far_center=fc)); return sim2.frames()

def bend(fr, wf):
    out = {}
    for side, layer in (('near', 'dhoti_near'), ('far', 'dhoti_far')):
        hip, ank = np.array(B[side + '_hip'], float), np.array(B[side + '_ankle'], float)
        ys = np.array([880., 1060., 1240.]); xs = hip[0] + (ank[0] - hip[0]) * (ys - hip[1]) / (ank[1] - hip[1])
        P = np.stack([xs, ys], 1); W = wf(layer, P[:, 0], P[:, 1]); ws = sum(W.values()); mx = 0
        for info, M in fr:
            Q = sum(W[b][:, None] * M[b](P) for b in W) / ws[:, None]
            u, v = Q[1] - Q[0], Q[2] - Q[1]; mx = max(mx, np.degrees(np.arctan2(u[0] * v[1] - u[1] * v[0], u @ v)))
        out[side] = mx
    return out
