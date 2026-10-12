#!/usr/bin/env python3
"""Разбор цикла ходьбы по фазам из журнала Godot (main.gd --logcontact --logknees, режим forward).

Проверяет фактические точки контакта стопы с землёй в мировых координатах:
пятку при постановке, всю подошву в основной опоре, переднюю часть стопы при отталкивании —
а не только подушечку. Плюс сгиб колена по фазам, зазор над землёй в переносе, момент прохода
переносимой стопы мимо опорной, движение переносимой стопы назад (рывок), резкость сгиба колена.

Запуск:  python3 tools/phase_check.py <журнал> [подпись]
"""
import re
import sys

import numpy as np

GROUND = {'near': 1414.0, 'far': 1404.0}     # линии земли стоп (y холста)
DUTY, HEEL_PHASE, HEEL_OFF = 0.6, 0.08, 0.42
PTS = ('heel', 'mid', 'ball', 'toe')
TOUCH = 0.6                                    # px: точка касается земли
NEAR_GROUND = 3.0                              # px: «почти касается»


def load(path):
    rows, knees = [], []
    for line in open(path):
        if line.startswith('CONTACT'):
            d = {'t': float(re.search(r't=([\d.]+)', line).group(1)),
                 'p': float(re.search(r' p=([\d.]+)', line).group(1))}
            for side in ('near', 'far'):
                for nm in PTS:
                    x, y = re.search(rf'{side}_{nm}=(-?[\d.]+),(-?[\d.]+)', line).groups()
                    d[f'{side}_{nm}'] = (float(x), float(y))
            rows.append(d)
        elif line.startswith('KNEES'):
            m = re.search(r'near flex=(-?[\d.]+) clear=(-?[\d.]+) far flex=(-?[\d.]+) clear=(-?[\d.]+)', line)
            knees.append(tuple(map(float, m.groups())))
    return rows[1:], knees[1:]       # первый кадр — до старта


def phase_name(q):
    if q < HEEL_PHASE:
        return 'постановка (пятка)'
    if q < HEEL_OFF:
        return 'опора (вся подошва)'
    if q < DUTY:
        return 'отталкивание (передняя часть)'
    s = (q - DUTY) / (1 - DUTY)
    return 'перенос: начало' if s < 0.33 else ('перенос: середина' if s < 0.67 else 'перенос: подготовка к постановке')


def main():
    path = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else path
    rows, knees = load(path)
    n = len(rows)
    print(f'== {label}: {n} кадров ==')
    report = {}
    for si, side in enumerate(('near', 'far')):
        g = GROUND[side]
        off = 0.0 if side == 'near' else 0.5
        X = {nm: np.array([r[f'{side}_{nm}'][0] for r in rows]) for nm in PTS}
        Y = {nm: np.array([r[f'{side}_{nm}'][1] for r in rows]) for nm in PTS}
        q = np.array([(r['p'] + off) % 1.0 for r in rows])
        flex = np.array([k[0 if side == 'near' else 2] for k in knees])
        # 1) скольжение точек, касающихся земли (соседние кадры, обе точки на земле)
        slide = {}
        for nm in PTS:
            on = Y[nm] >= g - TOUCH
            dx = np.abs(np.diff(X[nm]))
            both = on[1:] & on[:-1]
            slide[nm] = float(dx[both].max()) if both.any() else None
        # 2) «волочение»: точка почти у земли, но движется
        drag = []
        for nm in PTS:
            near = (Y[nm] >= g - NEAR_GROUND) & (Y[nm] < g - TOUCH)
            v = np.abs(np.gradient(X[nm]))
            k = near & (v > 1.0)
            if k.any():
                drag.append((nm, int(k.sum()), float(v[k].max()), sorted(set(phase_name(x) for x in q[k]))))
        # 3) переносимая стопа движется назад в мире (рывок)
        sw = q >= DUTY
        vx = np.gradient(X['ball'])
        back = sw & (vx < -0.05)
        # 4) зазор в переносе
        low = np.min([g - Y[nm] for nm in PTS], axis=0)
        print(f'\n[{"ближняя" if side == "near" else "дальняя"} стопа]')
        print('  скольжение точек на земле (наиб. сдвиг за кадр 1/60 с, px холста): ' +
              ', '.join(f'{nm} {"—" if v is None else f"{v:.2f}"}' for nm, v in slide.items()))
        if drag:
            for nm, cnt, vmax, ph in drag:
                print(f'  ВОЛОЧЕНИЕ: {nm} у земли (<{NEAR_GROUND:.0f} px) и движется: {cnt} кадров, до {vmax:.1f} px/кадр; фазы: {", ".join(ph)}')
        else:
            print('  волочения у земли нет')
        print(f'  переносимая стопа назад в мире: {int(back.sum())} кадров, до {(-vx[back]).max() if back.any() else 0:.2f} px/кадр')
        swl = low[sw]
        print(f'  зазор подошвы в переносе: мин {swl.min():.1f}, макс {swl.max():.1f} px')
        # по фазам
        names = ['постановка (пятка)', 'опора (вся подошва)', 'отталкивание (передняя часть)',
                 'перенос: начало', 'перенос: середина', 'перенос: подготовка к постановке']
        print('  сгиб колена по фазам (мин–макс°), зазор (px):')
        for nm in names:
            k = np.array([phase_name(x) == nm for x in q])
            if k.any():
                print(f'    {nm:34s} колено {flex[k].min():4.0f}–{flex[k].max():4.0f}°   зазор {low[k].min():5.1f}–{low[k].max():5.1f}')
        # резкость сгиба: наибольшее изменение скорости сгиба за кадр
        acc = np.abs(np.diff(flex, 2))
        print(f'  наибольший скачок скорости сгиба колена: {acc.max():.2f}°/кадр² (фаза {phase_name(q[1:-1][acc.argmax()])})')
        report[side] = dict(X=X, Y=Y, q=q, low=low)
    # 5) проход переносимой стопы мимо опорной
    print('\n[проход мимо опорной стопы]')
    for side, other in (('near', 'far'), ('far', 'near')):
        r, o = report[side], report[other]
        sw = r['q'] >= DUTY
        rel = r['X']['ball'] - o['X']['ball']
        cross = np.flatnonzero(sw[1:] & sw[:-1] & (np.sign(rel[1:]) != np.sign(rel[:-1])))
        for c in cross:
            s = (r['q'][c] - DUTY) / (1 - DUTY)
            print(f'  {"ближняя" if side == "near" else "дальняя"} проходит мимо опорной при s={s:.2f} переноса; зазор {r["low"][c]:.1f} px')


if __name__ == '__main__':
    main()
