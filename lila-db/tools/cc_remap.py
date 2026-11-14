# Сопоставить нумерацию стихов старых файлов (vcd/txt, vcd/new, ed/vcd, ШБ.txt) с ed/vcd-rev по бенгальскому тексту.
import re, os, glob, difflib, json, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
BN = re.compile('[ঀ-৿]')
LAB = re.compile(r'^\s*\((\d+)(?:[–-](\d+))?\)(?:[\s ]|(?=[“"«])|$)')
def blocks(path):
    out = []; buf = []
    for l in open(path, encoding='utf-8'):
        if BN.search(l) and not l.lstrip().startswith('['): buf.append(l); continue
        m = LAB.match(l)
        if m:
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            t = re.sub(r'[\s৷।॥০-৯,;:!?\'‘’“”—\-]', '', ''.join(buf))
            out.append((a, b, t)); buf = []
    return out
def mapping(old, new):
    A = blocks(old); B = blocks(new)
    m = {}
    for a, b, t in A:
        best = None; br = 0
        for a2, b2, t2 in B:
            if abs(a2 - a) > 15: continue
            r = difflib.SequenceMatcher(None, t, t2).ratio() if t and t2 else (1.0 if (a2, b2) == (a, b) else 0)
            if r > br: br, best = r, (a2, b2)
        for k, n in enumerate(range(a, b + 1)):
            if best is None: m[n] = None; continue
            a2, b2 = best
            # внутри сдвоенных блоков: тот же сдвиг
            m[n] = (min(a2 + k, b2) if b - a == b2 - a2 else (a2 if k == 0 else b2), round(br, 2))
    return m
if __name__ == '__main__':
    old, new = sys.argv[1], sys.argv[2]
    m = mapping(old, new)
    ch = [(n, v) for n, v in m.items() if v is None or v[0] != n or v[1] < 0.7]
    print(len(m), 'changed/weak:', ch[:40])
