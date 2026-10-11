#!/usr/bin/env python3
"""Проверка походки v0.4 вне Godot (повтор формул main.gd на Python):
опережение стоп, сгиб колен, искажение сеток дхоти (σ — растяжение/сжатие треугольников)
и видимый сгиб ткани у колена. Запуск из корня проекта: python3 tools/gait_check.py
Параметры походки должны совпадать с G в main.gd (при правке main.gd обновить V04 ниже).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim2, tune
V04 = dict(sim2.V03, near_center=47, far_center=-47)
for name, params, proj_w in (('v0.3 (центры +10/−10, веса v0.3)', dict(sim2.V03), dict(kz0=880, kz1=1100, fw=1e-3, b_back=0.5, b_front=0.5, drape=0.45, d0=15, d1=100)),
                             ('v0.4 (центры +47/−47, веса v0.4)', V04, dict(kz0=860, kz1=1140, fw=100, b_back=0.4, b_front=0.6, drape=0.2, d0=20, d1=200, s0=1080, s1=1340, cuff=0.6))):
    sim2.setp(**params); fr = sim2.frames()
    nl, fl = sim2.leads(fr); w = tune.make_w(proj_w); e = tune.evaluate(fr, w); b = tune.bend(fr, w)
    nf = [i['near_flex'] for i, _ in fr]; ff = [i['far_flex'] for i, _ in fr]
    print(name)
    print(f"  центры хода (подушечка): ближняя {sim2.gait.legs['near']['center']:.0f}, дальняя {sim2.gait.legs['far']['center']:.0f} px")
    print(f"  ближняя впереди дальней до {nl:.0f} px, дальняя впереди ближней до {fl:.0f} px")
    print(f"  сгиб колена: ближнее {min(nf):.0f}–{max(nf):.0f}°, дальнее {min(ff):.0f}–{max(ff):.0f}°")
    for k, v in e.items():
        print(f"  {k}: σ {v[0]:.2f}…{v[1]:.2f}; видимый сгиб ткани у колена до {b['near' if k=='dhoti_near' else 'far']:.1f}°")
