"""Компактный просмотр рабочей сводки: python3 -I tools/view.py T FROM TO [AC]
Печатает для каждого номера G-текст и (по умолчанию) двустишие A; 'C' — ещё изд. 1888."""
import os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
eds = sys.argv[4] if len(sys.argv) > 4 else 'A'
txt = open(os.path.join(HERE, 'src', f't{t:02d}-W.txt'), encoding='utf-8').read().split('\n## ')
prev = a - 1
for blk in txt:
    lines = blk.strip('# \n').split('\n')
    num = lines[0].strip()
    m = re.match(r'(\d+)', num)
    if not m or not (a <= int(m.group(1)) <= b):
        continue
    cur = int(m.group(1))
    if '?' not in num and cur > prev + 1:
        print(f'!! ПРОПУСК номеров {prev+1}–{cur-1} (искать в A/сыром G)')
    if '?' not in num: prev = max(prev, cur)
    g = re.split(r'অন্বয়|অম্বয়|অন্থয়|অদ্ধয়|অন্ধয়|অদ্বয়', lines[1][3:])[0]
    g = g if len(g) < 260 else '…' + g[-240:]
    out = [f'{num}| ' + g]
    for l in lines[2:]:
        if l[:1] in eds and l[1:2] == ':':
            out.append('   ' + l)
    print('\n'.join(out))
