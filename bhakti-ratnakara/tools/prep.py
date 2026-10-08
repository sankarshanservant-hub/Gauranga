"""Готовит рабочие файлы для перевода «Бхакти-ратнакары» (не коммитятся: src/ в .gitignore).

python3 -I tools/prep.py           → src/tNN-G.txt  (изд. Гаудия-миссии 1960: стихи с номерами, без анвая/анувады —
                                       ТОЛЬКО для сверки чтений и нумерации),
                                     src/tNN-A.txt  (изд. 1912, 2-е изд., общественное достояние — основа),
                                     src/tNN-B.txt  (изд. 1913, другой скан того же 2-го изд.),
                                     src/tNN-C.txt  (изд. 1888, editio princeps; есть только тараги 1–9),
                                     src/tNN-W.txt  (рабочая сводка: номер GM | GM | 1912 | 1888, выравнено по сходству).
Номер двустишия в PD-текстах восстанавливается выравниванием с нумерацией изд. 1960.
"""
import os, re, sys, difflib

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, '..', 'sources', 'narahari-chakravarti', 'bhakti-ratnakara')
OUT = os.path.join(HERE, 'src')
D = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
BN = '০১২৩৪৫৬৭৮৯'

def read(name):
    return open(os.path.join(SRC, name), encoding='utf-8').read().splitlines()

# Строки колофонов (1-based) в OCR-файлах — границы таранг (найдены вручную, 2026-10-08)
COL = {
    'A': [2247, 3152, 3916, 4697, 16288, 17298, 18347, 19295, 20571, 21819, 23153, 31951, 32748, 33449, 33753],
    'B': [2250, 3164, 3921, 4710, 16297, 17306, 18355, 19303, 20567, 21812, 23128, 31863, 32654, 33343, 33644],
    'C': [2053, 2964, 3744, 4538, 15997, 17044, 18178, 19183, 20525],
}
GM_SIG = [11301, 13518, 14875, 16659, 41314, 43414, 45652, 47717, 50425, 53219, 56144, 74113, 75894, 77086, 77634]
GM_START = 7036

# ---------- изд. Гаудия-миссии 1960 ----------
def gm_units():
    lines = read('bhakti-ratnakara_bengali_Gaudiya-Mission_ed2_1960_ocr.txt')
    units = {}
    num_re = re.compile(r'[॥|৷]\s*([০-৯*]{1,4})\s*[॥|৷;]*\s*$')
    prev = GM_START - 1
    for t, sig in enumerate(GM_SIG, 1):
        seg = lines[prev:sig + 6] if t < 15 else lines[prev:sig + 6]
        prev = sig + 6
        units[t] = []
        buf, last = [], 0
        for l in seg:
            s = l.strip()
            if not s:
                continue
            buf.append(s)
            m = num_re.search(s)
            if not m:
                continue
            n = int(m.group(1).replace('*', '০').translate(D))
            if units[t] and units[t][-1][0] == n:
                buf = []; continue        # анвая/анувада к шлоке — тот же номер
            ok = last == 0 or last < n <= last + 40
            units[t].append((n if ok else -1, str(n) if ok else f'{n}?', ' / '.join(buf)))
            if ok: last = n
            buf = []
        if buf:
            units[t].append((-1, 'END', ' / '.join(buf)))
    return units

# ---------- старые издания: сплошной текст ----------
HDR = re.compile(r'(ভক্ত|তক্ত|ভক্ভ|তর্ত|ভঞ্|ভত্ত|ভভি|উকি|ছর্ত)\S*কর|তরঙ্গ\s*[|।!]?\s*\]|\[\s*\S*\s*তরঙ্গ|^\s*[\[\(]?\s*[০-৯\d]+\s*[\]\)]?\s*$')

def pd_join(lines):
    txt = ''
    for l in lines:
        s = l.strip()
        if not s or (HDR.search(s) and len(s) < 60):
            continue
        txt = txt[:-1] + s if txt.endswith('-') else txt + ' ' + s
    return txt

def pd_split(key, name):
    lines = read(name)
    out, prev = [], 0
    for c in COL[key]:
        seg = lines[prev:c + 2]
        prev = c + 2
        out.append([x.strip() for x in pd_join(seg).split('॥') if x.strip()])
    return out

def norm(s):
    s = re.sub(r'[^ঀ-৿]', '', s)
    s = re.sub('[০-৯্ঁং়ঃ]', '', s)
    return s

def align(gm, pd):
    """Для каждого стиха GM — индекс(ы) PD-двустиший, по жадному поиску в окне."""
    res, j, w = [], 0, 400
    for n, nn, t in gm:
        g = norm(t)[-60:]
        best, bi = 0, None
        for k in range(j, min(j + w, len(pd))):
            r = difflib.SequenceMatcher(None, g, norm(pd[k]), autojunk=False).ratio()
            if r > best:
                best, bi = r, k
        if bi is not None and best > 0.45:
            res.append((bi, best)); j = bi + 1; w = 12
        else:
            res.append((None, best)); w = min(w + 20, 120)
    return res

def main():
    os.makedirs(OUT, exist_ok=True)
    gm = gm_units()
    eds = {'A': 'bhakti-ratnakara_bengali_DLI-356273_ed2_1912_ocr.txt',
           'B': 'bhakti-ratnakara_bengali_Rasabihari-Sankhyatirtha_Murshidabad_ed2_1913_ocr.txt',
           'C': 'bhakti-ratnakara_bengali_DLI-356261_1888_ocr.txt'}
    pds = {k: pd_split(k, v) for k, v in eds.items()}
    for k, v in pds.items():
        print(k, 'тараг найдено:', len(v), [len(x) for x in v])
    print('G', 'тараг:', len(gm), [len(gm[t]) for t in gm])
    for t in gm:
        key = f't{t:02d}'
        with open(os.path.join(OUT, key + '-G.txt'), 'w', encoding='utf-8') as f:
            for n, nn, s in gm[t]:
                f.write(f'{nn}\t{s}\n')
        for k in pds:
            if t - 1 < len(pds[k]):
                with open(os.path.join(OUT, f'{key}-{k}.txt'), 'w', encoding='utf-8') as f:
                    for i, c in enumerate(pds[k][t - 1]):
                        f.write(f'{i}\t{c}\n')
    if len(sys.argv) > 1:
        tl = [int(x) for x in sys.argv[1:]]
    else:
        tl = list(gm)
    for t in tl:
        key = f't{t:02d}'
        g = gm[t]
        al = {}
        for k in ('A', 'C'):
            if t - 1 < len(pds[k]):
                al[k] = (pds[k][t - 1], align(g, pds[k][t - 1]))
        with open(os.path.join(OUT, key + '-W.txt'), 'w', encoding='utf-8') as f:
            for i, (n, nn, s) in enumerate(g):
                f.write(f'## {nn}\nG: {s}\n')
                for k in al:
                    pd, a = al[k]
                    bi, r = a[i]
                    f.write(f'{k}: ' + (f'[{bi}] {pd[bi]}' if bi is not None else '—') + '\n')
                f.write('\n')
        print('W', key)

if __name__ == '__main__':
    main()
