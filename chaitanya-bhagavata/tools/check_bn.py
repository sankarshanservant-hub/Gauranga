#!/usr/bin/env python3
"""Проверка bn/CB_X.md: номера стихов (подряд, как в ed/), пустые стихи, латиница/цифры/мусор распознавания.
Запуск: python3 chaitanya-bhagavata/tools/check_bn.py CB_Adi01 [CB_Adi02 …] | --all"""
import glob, os, re, sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
LAB = re.compile(r'^\*\*(\d+)(?:[–-](\d+))?\.?\*\*', re.M)


def nums(path):
    t = open(path, encoding='utf-8').read()
    out = []
    for m in LAB.finditer(t):
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        out.append((a, b, m.end(), m.start()))
    return t, out


def check(name):
    bn = os.path.join(HERE, 'bn', name + '.md'); ed = os.path.join(HERE, 'ed', name + '.md')
    if not os.path.exists(bn): return [f'{name}: нет bn-файла']
    t, B = nums(bn); _, E = nums(ed)
    errs = []
    sb = {n for a, b, *_ in B for n in range(a, b + 1)}; se = {n for a, b, *_ in E for n in range(a, b + 1)}
    if sb != se:
        errs.append(f'{name}: номера не совпадают с ed — нет в bn: {sorted(se - sb)[:15]}, лишние: {sorted(sb - se)[:15]}')
    prev = 0
    for i, (a, b, end, _st) in enumerate(B):
        if a != prev + 1: errs.append(f'{name}: после {prev} идёт {a}')
        prev = b
        nxt = B[i + 1][3] if i + 1 < len(B) else len(t)  # начало следующей метки (в т. ч. группы **27–28.**)
        body = re.sub(r'<!--.*?-->', '', t[end:nxt], flags=re.S).strip()
        if not body: errs.append(f'{name} {a}: пустой стих'); continue
        bad = re.findall(r'[A-Za-z0-9০-৯॥|_~{}\[\]<>=+*]', body.replace('⟨?⟩', ''))
        if bad: errs.append(f'{name} {a}: посторонние знаки {"".join(sorted(set(bad)))}')
    q = t.count('⟨?⟩')
    print(f'{name}: стихов {len(sb)} (ed {len(se)}), ⟨?⟩ {q}, замечаний {len(errs)}')
    return errs


if __name__ == '__main__':
    names = [os.path.basename(f)[:-3] for f in sorted(glob.glob(os.path.join(HERE, 'bn', 'CB_*.md')))] if '--all' in sys.argv else sys.argv[1:]
    E = [e for n in names for e in check(n)]
    print('\n'.join(E[:200]))
    sys.exit(1 if E else 0)
