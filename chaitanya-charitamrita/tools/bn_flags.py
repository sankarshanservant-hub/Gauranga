# Сверка бенгальского текста стихов главы со сканом: каждая строка стиха ищется в OCR страниц (tsv, psm 3),
# строки с неточным совпадением (после отсева типичных ошибок OCR) вырезаются из изображения страницы
# и собираются в листы для просмотра глазами.
# Использование: python3 tools/bn_flags.py <Глава> <папка со сканом: pN.pgm, tN.tsv> P1 P2 [второй OCR: CCBSST djvu.txt]
# Результат: ed/work/bnflags-<Глава>.txt (стих.строка | стр. | наш текст | OCR), <папка>/sheets/<Глава>-K.png
import sys, os, json, difflib, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocr_verses import lines_of, key, verses as ocr_markers
from PIL import Image, ImageDraw
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OCR_FIX = (('ঘ', 'য'), ('রু', 'কৃ'), ('ক্ক', 'কৃ'), ('ক্ষ্ণ', 'কৃষ্ণ'), ('ষ্ক', 'ষ্ণ'), ('ত্ব', 'ত্ত্ব'), ('ব্ব', 'র্ব্ব'),
           ('ম্ম', 'র্ম্ম'), ('র্য', 'র্য্য'), ('্্', '্'), ('ূ', 'ু'), ('ী', 'ি'))
def canon(w):
    for a, b in OCR_FIX: w = w.replace(a, b)
    return w
def diffs_of(a, b):
    bad = []
    for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if t == 'equal': continue
        A, B = ' '.join(a[i1:i2]), ' '.join(b[j1:j2])
        if re.fullmatch(r'[\d১-৯০]*', B) and not A: continue
        if not A or not B or difflib.SequenceMatcher(None, A, B).ratio() < 0.9 or A[-1] != B[-1]: bad.append((A, B))
    return bad

def second_ocr(txt_path):
    """строки второго OCR (CCBSST djvu.txt) в виде списков токенов"""
    if not txt_path or not os.path.exists(txt_path): return None
    return [[canon(x) for x in key(l)] for l in open(txt_path, encoding='utf-8').read().split('\n') if l.strip()]

def best_window(toks, lines2, k):
    best, bw = 0, []
    for i in range(len(lines2)):
        w = sum(lines2[i:i + k + 1], [])
        q = difflib.SequenceMatcher(None, ' '.join(toks), ' '.join(w), autojunk=False).quick_ratio()
        if q > best: best, bw = q, w
    return bw

def main(chap, d, p1, p2, txt2=None):
    L2 = second_ocr(txt2)
    rows = json.load(open(os.path.join(ROOT, 'ed', 'work', 'rows-%s.json' % chap), encoding='utf-8'))
    pages = {p: lines_of(os.path.join(d, 't%d.tsv' % p)) for p in range(p1, p2 + 1) if os.path.exists(os.path.join(d, 't%d.tsv' % p))}
    big = [l['h'] for Ls in pages.values() for l in Ls]
    hmin = sorted(big)[len(big) // 2] * 0.9 if big else 22     # стихи набраны крупнее комментария
    out, crops = [], []
    M = ocr_markers(d, p1, p2)           # n -> (стр., строки выше, строка с номером, высота)
    for r in rows:
        for gi, g in enumerate(r['bn']):
            n = r['nums'][gi]
            if n in M:                    # стих найден по номеру: сравнить его строки целиком
                p, prev, last, h = M[n]
                k = len(g) - 1
                ocr = ' '.join((prev[-k:] if k else []) + [last])
                L = [x for x in pages[p] if x['text'] == last][0]
                top = L['top'] - int(k * h * 1.75) - 8; bot = L['top'] + h + 8
                left, right = L['left'], L['right']
            else:                         # номер не найден: ближайшая по тексту строка (крупный кегль)
                best = (0, None, None)
                for pp, Ls in pages.items():
                    for l in Ls:
                        if l['h'] < hmin: continue
                        q = difflib.SequenceMatcher(None, g[-1], l['text']).ratio()
                        if q > best[0]: best = (q, pp, l)
                q, p, L = best
                if L is None: out.append('%d | ? | не найден в скане' % n); continue
                ocr = L['text']; k = len(g) - 1
                top = L['top'] - int(k * L['h'] * 1.75) - 8; bot = L['top'] + L['h'] + 8
                left, right = L['left'], L['right']
            a = [canon(x) for x in key(' '.join(g))]; b = [canon(x) for x in key(ocr)]
            bad = diffs_of(a, b)
            if bad and L2 is not None:     # голосование: оставить только то, в чём второй OCR согласен с первым
                b2 = best_window(a, L2, len(g) - 1)
                bad2 = diffs_of(a, b2)
                keep = []
                for A, B in bad:
                    for A2, B2 in bad2:
                        if (set(A.split()) & set(A2.split()) or (not A and not A2)) and \
                           difflib.SequenceMatcher(None, B, B2).ratio() >= 0.75: keep.append((A, B)); break
                bad = keep
            if not bad: continue
            out.append('%d | с.%d | %s | OCR: %s | %s' % (n, p, ' / '.join(g), ocr, '; '.join('%s≠%s' % x for x in bad)))
            im = Image.open(os.path.join(d, 'p%d.pgm' % p)); W, H = im.size
            x0, x1 = (0, W // 2 + 10) if left < W // 2 - 100 else (W // 2 - 10, W)
            if right - left > W * 0.6 or (left < W // 2 - 100 and right > W // 2 + 100): x0, x1 = 0, W
            c = im.crop((x0, max(0, top), x1, min(H, bot))).convert('L')
            lab = Image.new('L', (c.size[0] + 70, c.size[1]), 255); lab.paste(c, (70, 0))
            ImageDraw.Draw(lab).text((4, c.size[1] // 2 - 6), str(n), fill=0)
            crops.append(lab)
    open(os.path.join(ROOT, 'ed', 'work', 'bnflags-%s.txt' % chap), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    sd = os.path.join(d, 'sheets'); os.makedirs(sd, exist_ok=True)
    for k in range(0, len(crops), 8):
        part = crops[k:k + 8]; Wm = max(c.size[0] for c in part)
        o = Image.new('L', (Wm, sum(c.size[1] for c in part)), 255); y = 0
        for c in part: o.paste(c, (0, y)); y += c.size[1]
        o.save(os.path.join(sd, '%s-%d.png' % (chap, k // 8)))
    print('%s: строк на просмотр %d, листов %d -> %s' % (chap, len(out), (len(crops) + 7) // 8, sd))
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else None)
