# Перевести ссылки записей ЧЧ в lila-db на выверенное издание ed/vcd-rev (номера — по изданию Гаудия Матха).
import re, os, glob, difflib, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cc_remap import blocks
CC = 'chaitanya-charitamrita/'
def chap_of(path):
    b = os.path.basename(path)
    if b == 'ШБ.txt': return 'Antya12'
    m = re.match(r'CC_([A-Za-z]+\d\d)', b); return m.group(1) if m else None
_cache = {}
def align(old, new):
    if (old, new) in _cache: return _cache[(old, new)]
    A = blocks(old); B = blocks(new); mp = {}
    for i, (a, b, t) in enumerate(A):
        best, br = None, -1
        for j, (a2, b2, t2) in enumerate(B):
            if abs(a2 - a) > 15: continue
            r = difflib.SequenceMatcher(None, t, t2).ratio() if t and t2 else 0
            r += 0.05 if (a2, b2) == (a, b) else 0
            if r > br: br, best = r, j
        mp[i] = (best, br)
    _cache[(old, new)] = (A, B, mp); return A, B, mp
def old_index(A, lab, start=0):
    # как build.find: '25' — первое вхождение от start; '2:25' — второе вхождение в файле
    pos = []
    for i, (a, b, t) in enumerate(A):
        for n in range(a, b + 1): pos.append((str(n), i))
        if b > a: pos.append(('%d–%d' % (a, b), i))
    if ':' in lab:
        k, v = lab.split(':', 1); idx = [i for l, i in pos if l == v]
        return idx[int(k) - 1] if len(idx) >= int(k) else None
    return next((i for l, i in pos if l == lab and i >= start), None)
log = []
for yf in sorted(glob.glob('lila-db/lilas/cc*.yaml')):
    txt = open(yf, encoding='utf-8').read()
    out = []; changed = 0
    def fix_verses(m):
        global changed
        f, fr, to = m.group(1), m.group(2), m.group(3)
        ch = chap_of(f); new = CC + 'ed/vcd-rev/CC_%s.md' % ch
        old = os.path.join(f)
        A, B, mp = align(old, new)
        i = old_index(A, fr); j = old_index(A, to, i or 0) if i is not None else None
        if i is None or j is None: log.append(('!! не найден', yf, f, fr, to)); return m.group(0)
        bi, ri = mp[i]; bj, rj = mp[j]
        if bi is None or bj is None: log.append(('!! нет пары', yf, f, fr, to)); return m.group(0)
        # номер внутри сдвоенного блока старого файла
        a, b, _ = A[i]; n_fr = int(fr.split(':')[-1].split('–')[0]); off_i = n_fr - a
        a2, b2, _ = B[bi]; nfr = min(a2 + off_i, b2) if (b - a) == (b2 - a2) else a2
        a, b, _ = A[j]; n_to = int(to.split(':')[-1].split('–')[-1]); off_j = n_to - a
        a3, b3, _ = B[bj]; nto = min(a3 + off_j, b3) if (b - a) == (b3 - a3) else b3
        if min(ri, rj) < 0.7 and 'ed/vcd/' not in f: log.append(('? слабое', yf, f, fr, to, '->', nfr, nto, round(min(ri, rj), 2)))
        if (str(nfr), str(nto)) != (fr, to): log.append(('~', yf, ch, fr, to, '->', nfr, nto))
        return '{file: "%s", from: "%d", to: "%d"}' % (new, nfr, nto)
    t2 = re.sub(r'\{file: "(chaitanya-charitamrita/[^"]+)", from: "([^"]+)", to: "([^"]+)"\}', fix_verses, txt)
    t2 = re.sub(r'^(  file: )"chaitanya-charitamrita/[^"]*?(CC_[A-Za-z]+\d\d|ШБ)[^"]*"', lambda m: '%s"%sed/vcd-rev/CC_%s.md"' % (m.group(1), CC, 'Antya12' if m.group(2) == 'ШБ' else m.group(2)[3:]), t2, flags=re.M)
    if t2 != txt: open(yf, 'w', encoding='utf-8').write(t2)
for x in log: print(*x)
