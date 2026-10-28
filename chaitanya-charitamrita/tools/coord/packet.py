#!/usr/bin/env python3
# Пакет для перевода главы «простой» моделью: по каждому стиху — бенгальский стих и перевод ВЧД (ed/vcd/CC_<Гл>.md)
# + бенгальский текст подзаголовка и обоих комментариев к этому стиху, вырезанный из второго OCR (CCBSST, современный
# набор того же издания — почти без ошибок). Модели остаётся только перевести данный ей текст.
# Запуск: python3 tools/coord/packet.py Madhya01 [стихов в части, по умолчанию 25]
# Выход: ed/work/packet-<Гл>/part-01.md, part-02.md … + остатки (что не удалось отнести к стиху) — leftovers.md
import os, re, sys
CC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
W = os.environ.get('CC_WORK') or (os.path.abspath(os.path.join(CC, '..', '..', 'cc-work')) if os.path.isdir(os.path.join(CC, '..', '..', 'cc-work')) else '/tmp/cc-work')
chap = sys.argv[1]; per = int(sys.argv[2]) if len(sys.argv) > 2 else 25
BD = '০১২৩৪৫৬৭৮৯'
b2i = lambda s: int(''.join(str(BD.index(c)) for c in s))
NUM = r'[০-৯]{1,3}(?:\s*[-–]\s*[০-৯]{1,3})?'

def key(s):
    a = [b2i(x) for x in re.findall(r'[০-৯]+', s)]
    return '%d' % a[0] if len(a) == 1 else '%d–%d' % (a[0], a[-1])

# ---- 1. CCBSST: блоки, разделённые пустыми строками
raw = open(os.path.join(W, 'bsst', chap + '.txt'), encoding='utf-8').read()
blocks = [b.strip('\n') for b in re.split(r'\n\s*\n', raw) if b.strip()]
def junk(l):
    l = l.strip()
    letters = len(re.findall(r'[অ-হড়-য়]', l))
    return letters < 3 or re.fullmatch(r'[\s০-৯]+', l) or re.search(r'চৈতন্যচরিতামৃত\s*$|^মধ্যলীলা|^আদিলীলা|^অন্ত্যলীলা|লীলা\s*[-—–]+\s*[^\s]+\s*পরিচ্ছেদ', l)

sub, apb, anu, left = {}, {}, {}, []
mode, lastc, cur = None, None, {'apb': None, 'anu': None}
pending_sub = []
SUBEND = r'(__|—|\$__|৪__|£__|[৪£\$]\s*_+)\s*$'
def is_verse_line(l): return bool(re.search(r'[৷|]\s*$', l.strip())) and not re.search(r'।\s*$', l.strip())
def add_comm(md, s):
    d = apb if md == 'apb' else anu
    m = re.match(r'^(' + NUM + r')\s*[।|]\s*(.*)$', s)
    if m:
        k = key(m.group(1)); prev = cur[md]
        inline = re.search(r'[০-৯]+\s*[।|1]', m.group(2))            # «৩। যশোদার স্বপ্ন, ৪। জন্মোৎসব…» — перечень внутри текста
        mono = prev is None or int(k.split('–')[-1]) >= int(prev.split('–')[0]) - 5   # допускаем небольшой откат (колонки CCBSST идут не строго по порядку)
        if not inline and mono and int(k.split('–')[-1]) <= 999:
            cur[md] = k; d.setdefault(k, []).append(m.group(2)); return
        left.append('[%s: номер %s не принят (после %s) — продолжение предыдущего?] %s' % (md, k, prev, s[:80]))
    if cur[md]: d[cur[md]].append(s)
    else: left.append('[%s без номера] %s' % (md, s))
# построчно: CCBSST перемешивает колонки, в одном блоке бывают и стихи, и комментарий
LINES = [l.rstrip() for b in blocks for l in (b.split('\n') + ['']) ]
VEND = re.compile(r'॥\s*(' + NUM + r')\s*॥')
skip_idx = set()
for i, l in enumerate(LINES):                      # первая строка двустишия — та, за которой (через ≤1 строку) идёт ॥N॥
    if VEND.search(l):
        for j in (i - 1, i - 2, i - 3):
            if j >= 0 and LINES[j].strip() and not VEND.search(LINES[j]) and len(LINES[j].strip()) < 75 \
               and not re.search(r'।\s*$', LINES[j]) and not re.search(SUBEND, LINES[j]) and not re.match(r'^(অমৃতপ্রবাহ|অনুভাষ্য)', LINES[j].strip()):
                skip_idx.add(j)
            else: break
for i, l in enumerate(LINES):
    st = l.strip()
    if not st or junk(st): continue
    if st.startswith('কথাসার'): mode = 'kathasara'; apb.setdefault('0', []).append(st); continue
    if re.match(r'^অমৃতপ্রবাহ\s*ভাষ্য\s*$', st): mode = lastc = 'apb'; continue
    if re.match(r'^অনুভাষ্য\s*$', st): mode = lastc = 'anu'; continue
    if re.match(r'^অমৃতানুকণা', st): mode = 'skip'; continue   # добавления редакторов 2004 г. — не переводим
    m = VEND.search(st)
    if m:
        if pending_sub: sub[key(m.group(1))] = ' '.join(pending_sub); pending_sub = []
        if mode == 'kathasara': mode = None
        mode = 'verse' if mode in (None, 'verse', 'kathasara') else mode
        continue
    if i in skip_idx: continue
    if re.search(SUBEND, st) and '।' not in st:
        pending_sub.append(re.sub(r'\s*[\$৪£]?\s*(__|—|_)+\s*$', ' —', st)); continue
    if mode == 'kathasara': apb['0'].append(st); continue
    if mode == 'skip': continue
    if mode in (None, 'verse'):
        if lastc: mode = lastc
        else: left.append('[?] ' + st); continue
    add_comm(mode, st)

def text(parts):  # склеить строки, сняв переносы «ভক্তি- / সিদ্ধান্ত»
    t = ' '.join(p.strip() for p in parts if p.strip())
    return re.sub(r'-\s+(?=[ঀ-৿])', '', t)

# ---- 2. Наши стихи (бенгальский + перевод ВЧД) из ed/vcd
md = open(os.path.join(CC, 'ed', 'vcd', 'CC_%s.md' % chap), encoding='utf-8').read()
verses = []
for p in re.split(r'\n\s*\n', md):
    if re.search(r'॥\s*[০-৯]+\s*॥', p) and re.search(r'[ঀ-৿]', p) and not re.search(r'[А-Яа-я]', p):
        verses.append({'bn': [l.strip() for l in p.split('\n') if l.strip()], 'tr': None})
    m = re.match(r'^\((\d+(?:–\d+)?)\) (.*)', p, re.S)
    if m and verses and verses[-1]['tr'] is None:
        verses[-1]['lab'] = m.group(1); verses[-1]['tr'] = re.sub(r'\[\^[^\]]+\]', '', m.group(2)).strip()
verses = [v for v in verses if v.get('lab')]

used = set()
def comm_for(lab, d):
    a, b = (lab.split('–') + [lab])[:2]
    out = []
    for k in d:
        last = int(k.split('–')[-1]); first = int(k.split('–')[0])
        if int(a) <= last <= int(b) and k not in used:
            out.append((k, text(d[k]))); used.add((id(d), k))
    return out

# запасной источник: OCR нашего скана (ed/bn/<Гл>-ocr.md) — абзацы «N।», которых нет в CCBSST
ocr_par, pg = {}, {}
page = None; curn = None
for l in open(os.path.join(CC, 'ed', 'bn', chap + '-ocr.md'), encoding='utf-8'):
    mp = re.match(r'^## стр\. (\d+)', l)
    if mp: page = mp.group(1); curn = None; continue
    m = re.match(r'^\s*(' + NUM + r')\s*[।|]\s*(.*)$', l.strip())
    if m and not re.search(r'[০-৯]+\s*[।|1]', m.group(2)):
        curn = key(m.group(1)); ocr_par.setdefault(curn, []).append(m.group(2)); pg.setdefault(curn, page); continue
    if curn and l.strip() and not l.startswith('#'): ocr_par[curn].append(l.strip())
od = os.path.join(CC, 'ed', 'work', 'packet-' + chap); os.makedirs(od, exist_ok=True)
for f in os.listdir(od): os.remove(os.path.join(od, f))
taken = {'apb': set(), 'anu': set()}
parts = [verses[i:i + per] for i in range(0, len(verses), per)]
for pi, pv in enumerate(parts, 1):
    L = ['# Пакет %s, часть %d из %d (стихи %s–%s)' % (chap, pi, len(parts), pv[0]['lab'], pv[-1]['lab']), '']
    if pi == 1 and '0' in apb:
        L += ['## Стих 0 (краткое содержание главы — только «Амрита-праваха-бхашья»)', '', '**APB (бенгальский):** ' + text(apb['0']), '']
        taken['apb'].add('0')
    for v in pv:
        lab = v['lab']; a, b = (lab.split('–') + [lab])[:2]
        L += ['## Стих %s' % lab, '', '**Стих (бенгальский):**', ''] + ['    ' + x for x in v['bn']] + ['',
              '**Перевод ВЧД:** ' + (v['tr'] or '—')]
        ss = [sub[k] for k in sub if a and int(a) <= int(k.split('–')[-1]) <= int(b)]
        L.append('**Подзаголовок «Анубхашьи» (бенгальский):** ' + (' / '.join(ss) if ss else '— нет'))
        for nm, d, tag in (('APB', apb, 'apb'), ('Ану', anu, 'anu')):
            ks = [k for k in d if k != '0' and int(a) <= int(k.split('–')[-1]) <= int(b) and k not in taken[tag]]
            if ks:
                for k in sorted(ks, key=lambda k: (int(k.split('–')[-1]), '–' in k)):
                    L.append('**%s %s (бенгальский):** %s' % (nm, k, text(d[k]))); taken[tag].add(k)
            else:
                L.append('**%s (бенгальский):** — нет' % nm)
        have = {k for k in list(apb) + list(anu)}
        for k in ocr_par:
            if k not in have and int(a) <= int(k.split('–')[-1]) <= int(b):
                L.append('**Комментарий %s — ТОЛЬКО ЧЕРНОВОЙ OCR старого скана (APB или Ану — определить по картинке с. %s; текст с ошибками распознавания):** %s'
                         % (k, pg.get(k), text(ocr_par[k])[:3000]))
        L.append('')
    open(os.path.join(od, 'part-%02d.md' % pi), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
rest = ['# Остатки %s — не отнесены к стиху (проверить по скану)' % chap, '']
for nm, d, tag in (('APB', apb, 'apb'), ('Ану', anu, 'anu')):
    for k in d:
        if k not in taken[tag]: rest.append('**%s %s:** %s' % (nm, k, text(d[k])))
rest += [''] + left
open(os.path.join(od, 'leftovers.md'), 'w', encoding='utf-8').write('\n'.join(rest) + '\n')
print('%s: стихов %d, частей %d; APB разделов %d, Ану %d, подзаголовков %d; остатков: %d раздел(ов), %d строк(и) -> %s'
      % (chap, len(verses), len(parts), len(apb), len(anu), len(sub),
         sum(1 for t in ('apb', 'anu') for k in (apb if t == 'apb' else anu) if k not in taken[t]), len(left), od))
