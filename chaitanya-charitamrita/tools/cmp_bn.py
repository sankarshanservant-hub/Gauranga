# Сверка бенгальского текста главы (ed/work/rows-<Гл>.json) с vedabase (ed/work/vb-<Гл>.json).
# Печатает расхождения слов (без учёта тире/дефисов/апострофов/пробелов вокруг тире).
import json, sys, re, os, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import normbn
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ed', 'work')
def nb(s):
    s = normbn(s); s = re.sub(r'[‌‍]', '', s); s = re.sub(r'॥[^॥]*॥', '', s)
    s = s.replace('৷', ' ').replace('।', ' ').replace('–', '-').replace("'", '’')
    s = re.sub(r'\s*—\s*', ' — ', s); s = re.sub(r'\s*-\s*', '-', s)
    s = re.sub(r'\s+([,!?])', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()
def key(w): return re.sub(r'[-—,!?;‘’“”\s]', '', w)
def diffs(chap):
    vb = json.load(open(os.path.join(R, 'vb-%s.json' % chap))); rows = json.load(open(os.path.join(R, 'rows-%s.json' % chap)))
    def vbt(n):
        for k, e in vb.items():
            a, b = (list(map(int, k.split('-'))) + [None])[:2]; b = b or a
            if a <= n <= b: return k, e['bn']
    out = []
    for r in rows:
        for i, n in enumerate(r['nums']):
            k, bl = vbt(n)
            mine = ' '.join(r['bn'][i])
            if '-' in k:   # сдвоенный у vedabase: взять нужное двустишие
                parts = re.findall(r'.*?॥\s*[০-৯]+\s*॥', ' '.join(bl), re.S)
                a = int(k.split('-')[0]); B = nb(parts[n - a]) if n - a < len(parts) else nb(' '.join(bl))
            else: B = nb(' '.join(bl))
            A = nb(mine)
            aw, bw = A.split(), B.split()
            # склейка/разбивка слов не считается, если без пробелов совпадает
            sm = difflib.SequenceMatcher(None, aw, bw)
            d = [(' '.join(aw[i1:i2]), ' '.join(bw[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']
            d = [x for x in d if key(x[0]) != key(x[1])]
            if d: out.append((n, d))
    return out
if __name__ == '__main__':
    for n, d in diffs(sys.argv[1]): print(n, ' | '.join('%s ≠ %s' % x for x in d))
