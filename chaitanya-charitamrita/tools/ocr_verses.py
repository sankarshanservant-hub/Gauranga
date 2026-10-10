# Текст стихов из OCR скана (tesseract --psm 3 tsv): для каждого «॥ N ॥» — строка с номером и предыдущие строки стиха
# того же блока (того же кегля). Сравнение с бенгальским главы: python3 ocr_verses.py <dir с tN.tsv> P1 P2 <Глава>
import csv, sys, os, re, json, difflib
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import normbn
BD = '০১২৩৪৫৬৭৮৯'
def bn2i(s): return int(''.join(str(BD.index(c)) for c in s))
def lines_of(path):
    R = [r for r in csv.DictReader(open(path, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE) if r['level'] == '5' and r['text'].strip()]
    L = defaultdict(list)
    for r in R: L[(r['block_num'], r['par_num'], r['line_num'])].append(r)
    out = []
    for k, ws in L.items():
        top = min(int(w['top']) for w in ws); bot = max(int(w['top']) + int(w['height']) for w in ws)
        out.append({'k': k, 'top': top, 'h': bot - top, 'left': min(int(w['left']) for w in ws),
                    'right': max(int(w['left']) + int(w['width']) for w in ws), 'text': ' '.join(w['text'] for w in ws)})
    return out
def verses(d, p1, p2):
    res = {}
    for p in range(p1, p2 + 1):
        f = os.path.join(d, 't%d.tsv' % p)
        if not os.path.exists(f): continue
        Ls = lines_of(f)
        for i, l in enumerate(Ls):
            t = l['text'].strip()
            m = re.search(r'(?:[॥।|1!lI]\s*|\s)([০-৯]{1,3})\s*[॥।|1!lI*\s]*$', t)
            if m and len(t) > 15 and not re.match(r'^[০-৯]', t):
                n = bn2i(m.group(1))
                # предыдущие строки того же столбца, близко сверху
                prev = [x for x in Ls if x is not l and abs((x['left'] + x['right']) / 2 - (l['left'] + l['right']) / 2) < 300
                        and 0 < l['top'] - x['top'] < 4.6 * l['h']]
                prev.sort(key=lambda x: x['top'])
                if n not in res or res[n][3] < l['h']: res[n] = (p, [x['text'] for x in prev], l['text'], l['h'])
    return res
def key(s):
    s = normbn(s); s = re.sub(r'[‌‍]', '', s); s = re.sub(r'[॥।৷|‘’\'“”"*_,.;!?:()—–-]', ' ', s)
    s = re.sub(r'[০-৯]', ' ', s)
    return s.split()
if __name__ == '__main__':
    d, p1, p2, chap = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    V = verses(d, p1, p2)
    R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ed', 'work')
    rows = json.load(open(os.path.join(R, 'rows-%s.json' % chap)))
    json.dump({n: v for n, v in sorted(V.items())}, open(os.path.join(R, 'ocr-%s.json' % chap), 'w'), ensure_ascii=False, indent=0)
    for r in rows:
        for i, n in enumerate(r['nums']):
            if n not in V: print(n, 'нет в OCR'); continue
            p, prev, last, _ = V[n]
            k = len(r['bn'][i]) - 1          # сколько строк стиха над строкой с номером
            o = ' '.join((prev[-k:] if k else []) + [last])
            a, b = key(' '.join(r['bn'][i])), key(o)
            sm = difflib.SequenceMatcher(None, a, b)
            bad = []
            for t, i1, i2, j1, j2 in sm.get_opcodes():
                if t == 'equal': continue
                A, B = ' '.join(a[i1:i2]), ' '.join(b[j1:j2])
                if difflib.SequenceMatcher(None, A, B).ratio() < 0.6 or abs(len(A) - len(B)) > 4: bad.append('%s ≠ %s' % (A, B))
            if bad: print(n, 'с.%d' % p, ' | '.join(bad)); sys.stdout.flush()
