#!/usr/bin/env python3
"""Сборка выверенных версий главы ЧЧ (пилот: Ади 1) из ed/vcd + файлов правок.

  ed/vcd/CC_Adi01.md                 — основа (бенгальский, транслитерация, пословный, перевод ВЧД)
  review/work/Adi01-ru.txt           — правки русского: для стиха «## N» строки
        tr: <новый перевод>            (без «(N)»; нет — перевод ВЧД без изменений)
        wN: <новый пословный к N-й строке транслитерации>
        fn: <сноска>                   (может быть несколько)
  review/work/Adi01-en.txt           — английский: для каждого стиха «## N»
        w: <пословный к строке 1> / w: <к строке 2> … (по порядку строк транслитерации)
        tr: <перевод>
        fn: <сноска>
Результат: ed/vcd-rev/CC_Adi01.md (RU) и ed/en-rev/CC_Adi01.md (EN; транслитерация — IAST, обратным
преобразованием из кириллицы ed). Блок с несколькими номерами (65–66) — ключ «## 65–66».

  build_rev.py Adi01 [--check]
"""
import re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def parse_ed(path):
    """→ шапка (строки), список блоков {num, bn:[...], pairs:[(tr,wbw)], text}"""
    lines = path.read_text(encoding='utf-8').split('\n')
    head = []; i = 0
    while i < len(lines) and not re.search(r'[ঀ-৿]', lines[i]):
        head.append(lines[i]); i += 1
    blocks = []; cur = None; notes = []
    paras = '\n'.join(lines[i:]).split('\n\n')
    for p in paras:
        p = p.strip('\n')
        if not p.strip():
            continue
        if p.startswith('---'):
            continue
        if p.startswith('[^'):
            notes.append(p); continue
        if re.search(r'[ঀ-৿]', p):
            if cur is None or cur.get('text') is not None:
                cur = {'bn': [], 'pairs': [], 'text': None}; blocks.append(cur)
            cur['bn'].append(p)
        elif p.startswith('('):
            m = re.match(r'\((\d+(?:–\d+)?)\)\s*(.*)', p, re.S)
            cur['num'] = m.group(1); cur['text'] = m.group(2).strip()
        else:
            ls = [l.rstrip() for l in p.split('\n')]
            for k in range(0, len(ls), 2):
                cur['pairs'].append((ls[k].strip(), ls[k + 1].strip() if k + 1 < len(ls) else ''))
    return head, blocks, notes

def parse_edits(path):
    d = {}; cur = None
    if not path.exists():
        return d
    for l in path.read_text(encoding='utf-8').split('\n'):
        if l.startswith('## '):
            cur = d.setdefault(l[3:].strip(), {'w': [], 'wn': {}, 'tn': {}, 'bn': {}, 'fn': [], 'tr': None}); continue
        if cur is None or not l.strip() or l.startswith('#'):
            continue
        m = re.match(r'(tr|w|w\d+|t\d+|bn\d+|fn):\s?(.*)', l)
        if not m:
            raise SystemExit(f'{path.name}: строка не распознана: {l[:60]}')
        k, v = m.groups()
        if k == 'tr': cur['tr'] = v
        elif k == 'fn': cur['fn'].append(v)
        elif k == 'w': cur['w'].append(v)
        elif k.startswith('bn'): cur['bn'][int(k[2:])] = v.replace(' / ', '  \n')
        elif k.startswith('t'): cur['tn'][int(k[1:])] = v
        else: cur['wn'][int(k[1:])] = v
    return d

# кириллица ed → IAST (обратное к tools/cyr.py)
R = [('т̣х','ṭh'),('д̣х','ḍh'),('джх','jh'),('дж','j'),('кх','kh'),('гх','gh'),('чх','ch'),('тх','th'),('дх','dh'),('пх','ph'),('бх','bh'),
     ('а̄','ā'),('ӣ','ī'),('ӯ','ū'),('р̣̄','ṝ'),('р̣','ṛ'),('л̣','ḷ'),('н̇','ṅ'),('н̃','ñ'),('т̣','ṭ'),('д̣','ḍ'),('н̣','ṇ'),('ш́','ś'),('ш̣','ṣ'),('м̇','ṁ'),('х̣','ḥ'),
     ('̐','m̐'),('э','e'),
     ('а','a'),('и','i'),('у','u'),('е','e'),('о','o'),('к','k'),('г','g'),('ч','c'),('т','t'),('д','d'),('н','n'),('п','p'),('б','b'),('м','m'),('й','y'),('р','r'),('л','l'),('в','v'),('с','s'),('х','h')]
def iast(s):
    s = unicodedata.normalize('NFD', s)
    s = unicodedata.normalize('NFC', s)
    out = ''; j = 0
    while j < len(s):
        for a, b in R:
            a2 = unicodedata.normalize('NFC', a)
            if s.startswith(a2, j):
                out += b; j += len(a2); break
        else:
            out += s[j]; j += 1
    return out

def md_block(bn, pairs, num, text, fns, fnstart):
    out = []
    for b in bn:
        out.append(b); out.append('')
    pl = []
    for t, w in pairs:
        pl.append(t + '  '); pl.append(w + '  ')
    if pl:
        pl[-1] = pl[-1].rstrip()
        out.append('\n'.join(pl)); out.append('')
    marks = ''.join(f'[^{fnstart + k}]' for k in range(len(fns)))
    out.append(f'({num}) {text}{marks}'); out.append('')
    return out

def build(ch, check=False):
    head, blocks, notes = parse_ed(ROOT / f'ed/vcd/CC_{ch}.md')
    ru = parse_edits(ROOT / f'review/work/{ch}-ru.txt')
    en = parse_edits(ROOT / f'review/work/{ch}-en.txt')
    nums = [b['num'] for b in blocks]
    for k in [x for x in list(ru) + list(en) if x != '0']:
        if k not in nums:
            raise SystemExit(f'нет блока {k}')
    # RU
    out = [l for l in head if l.strip() and l.strip() != '(перевод Вриндавана Чандры даса)']
    out += ['(перевод Вриндавана Чандры даса; выверка по изд. Гаудия Матха и «Анубхашье», 2026 — проект)', '']
    fnl = []; n = 1
    oldnotes = {re.match(r'\[\^(\d+)\]', x).group(1): x.split(':', 1)[1].strip() for x in notes}
    for b in blocks:
        e = ru.get(b['num'], {'w': [], 'wn': {}, 'tn': {}, 'bn': {}, 'fn': [], 'tr': None})
        b['bn'] = [e['bn'].get(i + 1, x) for i, x in enumerate(b['bn'])]
        b['pairs'] = [(e['tn'].get(i + 1, t), w) for i, (t, w) in enumerate(b['pairs'])]
        text = e['tr'] if e['tr'] else re.sub(r'\[\^\d+\]', '', b['text'])
        fns = []
        for m in re.findall(r'\[\^(\d+)\]', b['text']):
            if not e['tr']: fns.append(oldnotes[m])
        fns += e['fn']
        pairs = [(t, e['wn'].get(i + 1, w)) for i, (t, w) in enumerate(b['pairs'])]
        b['rupairs'] = pairs
        out += md_block(b['bn'], pairs, b['num'], text, fns, n)
        fnl += [f'[^{n + k}]: {f}' for k, f in enumerate(fns)]; n += len(fns)
    if fnl:
        out += ['---', ''] + [x + '\n' for x in fnl]
    if not check:
        p = ROOT / f'ed/vcd-rev/CC_{ch}.md'; p.parent.mkdir(exist_ok=True)
        p.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')
    # EN
    lila = {'Adi': 'Ādi-līlā', 'Madhya': 'Madhya-līlā', 'Antya': 'Antya-līlā'}[re.match(r'[A-Za-z]+', ch).group()]
    num = int(re.search(r'\d+', ch).group())
    title = en.get('title', {}).get('tr') if 'title' in en else None
    out = ['“Śrī Caitanya-caritāmṛta”  ', f'{lila}  ', f'Chapter {num}  ']
    if '0' in en and en['0']['tr']:
        out.append(f"**{en['0']['tr']}**  ")
    out += ['(English translation from the Bengali, following the Gauḍīya Maṭha edition and the «Anubhāṣya», 2026 — draft)', '']
    fnl = []; n = 1; missing = []
    for b in blocks:
        e = en.get(b['num'])
        if not e or not e['tr']:
            missing.append(b['num']); continue
        if len(e['w']) != len(b['pairs']):
            raise SystemExit(f"EN {b['num']}: пословных {len(e['w'])}, строк {len(b['pairs'])}")
        pairs = [(iast(t), w) for (t, _), w in zip(b['pairs'], e['w'])]
        out += md_block(b['bn'], pairs, b['num'], e['tr'], e['fn'], n)
        fnl += [f'[^{n + k}]: {f}' for k, f in enumerate(e['fn'])]; n += len(e['fn'])
    if fnl:
        out += ['---', ''] + [x + '\n' for x in fnl]
    if not check and en:
        p = ROOT / f'ed/en-rev/CC_{ch}.md'; p.parent.mkdir(exist_ok=True)
        p.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')
    print(f'{ch}: блоков {len(blocks)}; RU правок {len([k for k in ru if ru[k]["tr"] or ru[k]["wn"] or ru[k]["fn"] or ru[k]["bn"] or ru[k]["tn"]])}; '
          f'EN готово {len(blocks) - len(missing)}' + (f'; EN нет: {missing[0]}…{missing[-1]}' if missing else ''))

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'Adi01', '--check' in sys.argv)
