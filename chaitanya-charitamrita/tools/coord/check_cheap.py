#!/usr/bin/env python3
# Проверка ответа «дешёвой» модели против пакета: нет ли выдуманных разделов, все ли разделы пакета переведены,
# не слишком ли длинный/короткий перевод (признак отсебятины или пропуска).
# Запуск: python3 tools/coord/check_cheap.py ed/work/packet-Madhya01/part-01.md ответ.md
import re, sys
pk = open(sys.argv[1], encoding='utf-8').read(); ans = open(sys.argv[2], encoding='utf-8').read()
want = {'apb': {}, 'anu': {}}
for m in re.finditer(r'\*\*(APB|Ану) (\d+(?:–\d+)?) \(бенгальский\):\*\* (.*)', pk):
    want['apb' if m.group(1) == 'APB' else 'anu'][m.group(2)] = m.group(3)
if '## Стих 0' in pk:
    m = re.search(r'## Стих 0.*?\*\*APB \(бенгальский\):\*\* (.*)', pk, re.S); want['apb']['0'] = m.group(1).split('\n')[0]
subs = {m.group(1) for m in re.finditer(r'## Стих (\d+(?:–\d+)?)\n(?:.*\n)*?\*\*Подзаголовок «Анубхашьи» \(бенгальский\):\*\* (?!— нет)', pk)}
parts = re.split(r'^=== .*-(apb|anu)\.md ===\s*$', ans, flags=re.M)
got = {'apb': {}, 'anu': {}}
for i in range(1, len(parts), 2):
    for m in re.finditer(r'^## (\S+)\s*\n(.*?)(?=^## |\Z)', parts[i + 1], re.M | re.S):
        got[parts[i]][m.group(1)] = re.sub(r'^> Подзаголовок:.*$', '', m.group(2), flags=re.M).strip()
bad = 0
for t in ('apb', 'anu'):
    allowed = set(want[t]) | (subs if t == 'anu' else set())
    for k in got[t]:
        if k not in allowed: bad += 1; print('!! ВЫДУМАН раздел %s %s (в пакете его нет)' % (t, k))
    for k, bn in want[t].items():
        if k not in got[t]: bad += 1; print('!! ПРОПУЩЕН раздел %s %s' % (t, k)); continue
        r = len(got[t][k]) / max(1, len(bn))
        if r > 2.2 or r < 0.5: bad += 1; print('!! %s %s: длина перевода %.1f× от бенгальского — проверить (отсебятина/пропуск)' % (t, k, r))
print('OK' if not bad else 'замечаний: %d' % bad)
