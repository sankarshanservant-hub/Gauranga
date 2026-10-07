"""Fuzzy grep Bengali OCR: fgrep.py [-C n] [-t thr] 'query' files..."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bnorm import grams
args = sys.argv[1:]
C, thr = 0, 0.6
while args and args[0].startswith('-'):
    if args[0] == '-C':
        C = int(args[1]); args = args[2:]
    elif args[0] == '-t':
        thr = float(args[1]); args = args[2:]
q = grams(args[0])
for f in args[1:]:
    lines = open(f, encoding='utf-8', errors='replace').read().split('\n')
    for i, l in enumerate(lines):
        # compare with line + next line joined (pada lines may wrap)
        g = grams(l + ' ' + (lines[i + 1] if i + 1 < len(lines) else ''))
        if not q or not g:
            continue
        s = len(q & g) / len(q)
        if s >= thr:
            print(f'{os.path.basename(f)}:{i+1}: [{s:.2f}] ' + l.strip())
            if C:
                for j in range(max(0, i - C), min(len(lines), i + C + 1)):
                    if lines[j].strip():
                        print('    ' + lines[j].strip())
