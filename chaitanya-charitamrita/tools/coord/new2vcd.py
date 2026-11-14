#!/usr/bin/env python3
# Антья 16–19 (у ВЧД нет; наш перевод «в его стиле», vcd/new/CC_<Гл>.md — уже в целевом формате, бенгальский выверен
# по скану, vcd/new/work/overrides.txt) -> vcd/txt/CC_<Гл>.txt в виде выгрузки ВЧД, чтобы дальше работал обычный
# конвейер (tools/prep_vcd.py + ed/fixes/<Гл>.txt). Сноски vcd/new переносятся правками `@N note: => …`
# в ed/fixes/<Гл>.txt (если их там ещё нет). Запуск: python3 tools/coord/new2vcd.py Antya16
import os, re, sys
CC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ch = sys.argv[1]
src = os.path.join(CC, 'vcd', 'new', 'CC_%s.md' % ch)
dst = os.path.join(CC, 'vcd', 'txt', 'CC_%s.txt' % ch)
fx = os.path.join(CC, 'ed', 'fixes', '%s.txt' % ch)
t = open(src, encoding='utf-8').read()
body, _, notes = t.partition('\n---\n')
N = dict(re.findall(r'^\[\^(\w+)\]:\s*(.*)$', notes, re.M))
out, refs = [], []
for l in body.split('\n'):
    l = l.rstrip()
    m = re.match(r'^\((\d+)(?:[–-]\d+)?\)', l)
    for k in re.findall(r'\[\^(\w+)\]', l):
        refs.append((m.group(1) if m else '?', N[k]))
    l = re.sub(r'\[\^\w+\]', '', l)
    if l.startswith('**') and l.endswith('**'): l = l[2:-2]
    out.append(l)
open(dst, 'w', encoding='utf-8').write('\n'.join(out).rstrip() + '\n')
old = open(fx, encoding='utf-8').read() if os.path.exists(fx) else ''
add = ['@%s note: => %s  # сноска перевода 2026 (vcd/new)' % (n, s) for n, s in refs if ('@%s note:' % n) not in old]
if add:
    if not old: old = '# Ручные правки главы %s. Формат: @стих поле: было => стало  # причина\n' % ch
    open(fx, 'w', encoding='utf-8').write(old.rstrip('\n') + '\n' + '\n'.join(add) + '\n')
print('%s: -> %s; сносок перенесено в ed/fixes: %d' % (ch, os.path.relpath(dst, CC), len(add)))
