# Порция 16: сплошная сверка «Падакалпатару» (tesseract-OCR pk_v1…v4) по подписям поэтов-современников.
# python3 -I sweep_pk.py [vol ...]  — печатает места, где в строке есть имя поэта-современника (с вариантами OCR),
# а в окне пады (≈20 строк до подписи) — слова гаура-лилы; номер ПК — по ближайшим надёжным меткам «॥N॥M॥» (≈, интервал),
# PDF-страница — по разделителям «=== vN pNNNN»; пометка NEW — номер(а) интервала не упомянуты ни в CATALOG.md, ни в padas/ru/*.md.
import re, sys, glob
R = '/home/user/Gauranga/'
T = R + 'sources/padas/tesseract/'
BD = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
START = {1: 0, 2: 612, 3: 1578, 4: 2385}
POETS = {
    'VG': r'বা[সশ][ুূু্থ]+\s*(?:দেব)?\s*[-]?\s*ঘো[ষয]|বা[সশ](?:ু|ূ|্থ|্ু|্ত)(?:দেব)?\b|বাসুদেব|বাস্থদেব|বাসুঘোষ|বাস্থঘোষ|\bবাসু\b|বাস্থ',
    'GG': r'গোবিন্দ\s*[-]?\s*ঘো[ষয]|গোবিন্দঘো',
    'MG': r'মাধ[বো]\s*[-]?\s*ঘো[ষয]',
    'NH': r'নরহরি|নরহরী|নরহুরি',
    'MU': r'মুরারি|মুরারী|মূরারি|মুরারি',
    'SS': r'শিবানন্দ|শিবাই|সেন শিব',
    'VV': r'বংশী|বংশি|বংশীবদন|বংশীদাস|বং[শস]ী',
    'RM': r'রামানন্দ',
    'PA': r'পরমানন্দ|পরমানন্ব',
    'GD': r'গৌরী\s*দাস|গৌরিদাস|গোৌরীদাস|গৌরীদা',
    'KR': r'কৃষ্ণ\s*দাস|কৃষ্ণদাস|কষ্ণদাস|কৃফদাস|কুষ্ণদাস',
    'CS': r'চন্দ্রশেখর|চন্দ্র শেখর|চন্দ্রশেখর',
    'RC': r'রামচন্দ্র|রামচন্দ্‌র',
    'BD': r'বলরাম|বলরা[মষ]|বলাই দাস',
    'NN': r'নয়নানন্দ|নয়নানন্দ|নয়নানন্ব|নয়নানন্দ|নয়ানন্দ|নয়নান',
    'YD': r'য[দছহ][ুূ]\s*(?:নাথ|নন্দন|নন্বন)|য[দছহ][ুূ]নাথ|য[দছহ][ুূ]নন্দন|\bয[দছহ][ুূ]\b',
    'AN': r'অনন্ত',
    'KD': r'কানু\s*দাস|কানুরাম|কানুদাস|কান্থ\s*দাস|কানু\b',
    'MD': r'মাধবী|মাধবি দাস',
    'CD': r'চৈতন্[যত্]\s*দাস|চৈতন্যদাস|চৈতন্তদাস|চৈতন্তু দাস',
    'SG': r'শঙ্কর|শংকর',
    'VD': r'বাসুদেব দত্ত|দত্ত',
    'PD': r'পরমেশ্বর',
}
G = re.compile('গৌর|গোরা|গোৌর|শচী|নদীয়া|নদিয়া|নদীয়া|চৈতন্|নিতাই|নিত্যানন্দ|বিশ্বম্ভর|নিমাই|গদাধর|অদ্বৈত|সন্ন্যাস|সন্্যাস|'
               'নীলাচল|শ্রীবাস|গোরাচাঁদ|গৌরাঙ্গ|গোৌরাঙ্গ|শান্তিপুর|সুরধুনী|নবদ্বীপ|নদীয়া|কীর্তন|কীর্ত্তন|প্রভু|পহু|পহুঁ')
END = re.compile(r'॥\s*[০-৯]|[০-৯]\s*॥|[০-৯]{3,4}\s*[|।]')
mark = re.compile(r'[॥|]\s*([০-৯]{1,3}\s*[॥।1\)|/]+\s*[০-৯]{1,4}|[০-৯]{2,7})\s*[॥।|]?')
known = set()
for f in [R + 'padas/CATALOG.md'] + glob.glob(R + 'padas/ru/*.md'):
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'ПК\s*[\*≈~]*\s*(\d{1,4})', t):
        known.add(int(m.group(1)))
    if f.endswith('CATALOG.md'):
        for r in t.split('\n'):
            c = r.split('|')
            if r.startswith('| ') and len(c) > 5:
                for m in re.finditer(r'(\d{1,4})', c[4]):
                    known.add(int(m.group(1)))


def labels(lines, start):
    out = []
    prev = start
    for i, l in enumerate(lines):
        ms = list(mark.finditer(l))
        if not ms:
            continue
        s = re.split(r'[\s॥।1\)|/]+', ms[-1].group(1))[-1].translate(BD)
        for k in (4, 3, 2, 1):
            if len(s) >= k:
                v = int(s[-k:])
                if prev < v <= prev + 25:
                    out.append((i, v)); prev = v
                    break
    return out


vols = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4]
for vol in vols:
    lines = open(T + f'pk_v{vol}.txt', encoding='utf-8').read().split('\n')
    pages = []
    pg = 0
    for l in lines:
        if l.startswith('=== v'):
            pg = int(l.split('p')[-1])
        pages.append(pg)
    lab = labels(lines, START[vol])
    li = [a for a, b in lab]
    import bisect
    seen = set()
    for i, l in enumerate(lines):
        for k, pat in POETS.items():
            if not re.search(pat, l):
                continue
            j = bisect.bisect_left(li, i)
            nxt = lab[j] if j < len(lab) else (len(lines), 9999)
            prv = lab[j - 1] if j > 0 else (0, START[vol])
            if not any(END.search(x) for x in lines[i:i + 4]):   # подпись — в последних строках пады (рядом метка конца)
                continue
            lo, hi = prv[1] + 1, nxt[1]
            win = '\n'.join(lines[max(prv[0] + 1, i - 22):i + 1])
            if not G.search(win):
                continue
            key = (k, lo, hi)
            if key in seen:
                continue
            seen.add(key)
            new = all(n not in known for n in range(lo, hi + 1))
            num = str(hi) if lo == hi else f'{lo}-{hi}'
            print(f"v{vol} p{pages[i]:03d} L{i + 1:<6d} {k} PK {num:10s} {'NEW' if new else '   '} | {l.strip()[:80]}")
