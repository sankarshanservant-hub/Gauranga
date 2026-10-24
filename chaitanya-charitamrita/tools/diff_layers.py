#!/usr/bin/env python3
"""Сведение двух слоёв перевода ВЧД «Чайтанья-чаритамриты».
  ed/vcd/CC_<Лила><NN>.md   — выправленное издание (стих: «(N) перевод» одной строкой; сноски «[^N]»)
  vcd/txt/CC_<Лила><NN>.txt — исходная выгрузка .doc (её читает parshadas/tools/verse.py)

Для сравнения текст нормализуется: пробелы/неразрывные пробелы/переносы строк, кавычки «»“”„" → ", ё → е,
знак ударения, метки сносок ed «[^N]». Сами правки при переносе берутся как есть (из ed, без меток сносок).
Стихи сопоставляются по номеру; где нумерация слоёв расходится (ВЧД шёл по другому изданию: лишний или
сдвоенный стих), пара подбирается по сходству текста среди соседних номеров (±3).

Каждое расхождение (пословный фрагмент) получает вид:
  punct   — только пунктуация/тире/дефисы/пробелы внутри слова;
  small   — опечатка, падежное окончание, написание имени (1–3 слова, похожие);
  ref     — оформление ссылки на источник «[ШБ 1.1.2]» → «(Шримад-Бхагаватам, 1.1.2)» (в txt не переносится);
  comment — в txt вставка современного комментария (Шридхар Махарадж и др.), в ed удалена (не переносится);
  ed-extra / txt-extra — текст есть только в одном слое (потеря или добавка);
  big     — большая замена (исправление смысла по бенгальскому, перефразировка) — разбирается вручную.

  diff_layers.py [Adi14 Madhya10 …]      — отчёт по расхождениям (все главы с обоими слоями)
  diff_layers.py --summary              — только счётчики по видам
  diff_layers.py --apply-txt LIST       — перенести ed → txt фрагменты из списка (строки «Adi14 24» —
                                          все фрагменты стиха, кроме ref/comment; «Adi14 24 punct,small» —
                                          только этих видов); переносы строк txt сохраняются
Стихотворные версии vcd/txt/*poetry*.txt — отдельный стихотворный перевод (свой текст), с прозой не совпадают;
скрипт их не сравнивает."""
import re, sys, difflib, collections
from pathlib import Path

R = Path(__file__).resolve().parents[1]
ED, TXT = R / 'ed/vcd', R / 'vcd/txt'
STOP = re.compile(r'[ঀ-৿ᅠﾠㅤ]')
NUM = r'\(([0-9]+(?:[–-][0-9]+)?)\)'
FN = re.compile(r'\[\^[0-9]+\]')
PUN = re.compile(r'[\s\.,;:!?\-–—…"\'()\[\]/]')


def norm(s):
    s = FN.sub('', s)
    s = s.replace(' ', ' ').replace('　', ' ').replace(' ', ' ')
    s = re.sub(r'[«»“”„"]', '"', s).replace('ё', 'е').replace('Ё', 'Е').replace('́', '')
    return re.sub(r'\s+', ' ', s).strip()


def first(k):
    return int(re.match(r'[0-9]+', k).group())


def ed_verses(ch, text=None):
    if text is None:
        f = ED / f'CC_{ch}.md'
        if not f.exists():
            return {}
        text = f.read_text()
    out = {}
    for ln in text.splitlines():
        m = re.match(rf'^{NUM}\s*(.*)$', ln)
        if m:
            out[m.group(1).replace('-', '–')] = m.group(2).rstrip()
    return out


def txt_verses(ch, t=None):
    """{номер: (текст, [(start, end) — участки строк в файле])}, текст файла.
    Перевод — от «(N)» до пустой строки / строки из U+3000 / следующего «(N)»; бенгальский текст и
    мусорные разделители (U+1160, U+FFA0, U+3164) обрезают его, как в verse.py."""
    if t is None:
        t = (TXT / f'CC_{ch}.txt').read_text()
    lines = t.split('\n')
    offs, pos = [], 0
    for ln in lines:
        offs.append(pos)
        pos += len(ln) + 1
    out, i = {}, 0
    while i < len(lines):
        m = re.match(rf'^{NUM}[\s ]*', lines[i])
        if not m:
            i += 1
            continue
        key = m.group(1).replace('-', '–')
        spans = [(offs[i] + m.end(), offs[i] + len(lines[i]))]
        j = i + 1
        while j < len(lines):
            ln = lines[j]
            if not ln.strip() or re.match(rf'^{NUM}', ln):
                break
            spans.append((offs[j], offs[j] + len(ln)))
            j += 1
        ns = []  # обрезать по бенгальскому/разделителю
        for a, b in spans:
            k = STOP.search(t, a, b)
            if k:
                if k.start() > a:
                    ns.append((a, k.start()))
                break
            ns.append((a, b))
        body = '\n'.join(t[a:b] for a, b in ns)
        if key not in out:
            out[key] = (body, ns)
        i = j
    return out, t


def sim(a, b):
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


def pairs(ch):
    """[(ключ ed, ключ txt, текст ed, текст txt)]; ключ None — стиха нет в слое."""
    ed = ed_verses(ch)
    tv, _ = txt_verses(ch)
    tkeys = sorted(tv, key=first)
    used, out = set(), []
    for k in sorted(ed, key=first):
        ne = norm(ed[k])
        best = k if k in tv else None
        s0 = sim(ne, norm(tv[best][0])) if best else 0
        if s0 < 0.5:
            n = first(k)
            cands = [x for x in tkeys if abs(first(x) - n) <= 3 and x not in used]
            sc = sorted(((sim(ne, norm(tv[x][0])), x) for x in cands), reverse=True)
            if sc and sc[0][0] >= 0.5 and sc[0][0] > s0 + 0.1:
                best = sc[0][1]
        if best is not None:
            used.add(best)
        out.append((k, best, ed[k], tv[best][0] if best else None))
    for x in tkeys:
        if x not in used:
            out.append((None, x, None, tv[x][0]))
    return out


def bare(ws):
    return PUN.sub('', ' '.join(ws)).lower()


def kind(o, n):
    so, sn = ' '.join(o), ' '.join(n)
    if bare(o) == bare(n):
        return 'punct'
    if (re.search(r'\((ШБ|Бг|Брс|БРС)|\[', so) or
            re.search(r'Шримад-Бхагаватам,|Бхагавад-гита,|Бхакти-расамрита-синдху,', sn) and
            not re.search(r'Шримад-Бхагаватам|Бхагавад-гита|Бхакти-расамрита', so)) and len(o) <= 4 and len(n) <= 4:
        return 'ref'
    if len(o) > 6 and re.search(r'Махарадж|Прабхупад', so) and not re.search(r'Махарадж', sn):
        return 'comment'
    if abs(len(o) - len(n)) <= 1 and 0 < len(o) <= 3 and 0 < len(n) <= 3 and sim(bare(o), bare(n)) >= 0.6:
        return 'small'
    if not o:
        return 'ed-extra'
    if not n:
        return 'txt-extra'
    return 'big'


def hunks(x, e):
    """Пословные фрагменты: (i1, i2, j1, j2, вид) по словам txt (wx) и ed (we)."""
    wx, we = x.split(), FN.sub('', e).split()
    sm = difflib.SequenceMatcher(a=[norm(w) for w in wx], b=[norm(w) for w in we], autojunk=False)
    res = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal':
            res.append((i1, i2, j1, j2, kind([norm(w) for w in wx[i1:i2]], [norm(w) for w in we[j1:j2]])))
    return wx, we, res


def chapters(args):
    return args or sorted(p.stem[3:] for p in ED.glob('CC_*.md'))


def report(chs, summary=False):
    cnt, nverse = collections.Counter(), 0
    for ch in chs:
        for ke, kx, e, x in pairs(ch):
            if e is None or x is None:
                cnt['numbering'] += 1
                if not summary:
                    print(f'{ch} {ke or "—"}/{kx or "—"}\tНУМЕРАЦИЯ: стих только в {"txt" if e is None else "ed"}')
                continue
            if norm(e) == norm(x):
                continue
            wx, we, hs = hunks(x, e)
            if not hs:
                continue
            nverse += 1
            lab = ke if ke == kx else f'{ke} (txt {kx})'
            if not summary:
                print(f'{ch} {lab}')
            for i1, i2, j1, j2, kd in hs:
                cnt[kd] += 1
                if not summary:
                    print(f'   {kd:9} …{" ".join(wx[max(0, i1 - 3):i1])} [txt: {" ".join(wx[i1:i2])} | '
                          f'ed: {" ".join(we[j1:j2])}] {" ".join(wx[i2:i2 + 3])}…')
    print(f'# стихов с расхождениями: {nverse}; фрагментов по видам: {dict(cnt)}', file=sys.stderr)


def apply_txt(listfile):
    todo = collections.defaultdict(dict)
    for ln in Path(listfile).read_text().splitlines():
        ln = ln.split('#')[0].strip()
        if not ln:
            continue
        p = ln.split()
        kinds = set(p[2].split(',')) if len(p) > 2 else None
        todo[p[0]][p[1].replace('-', '–')] = kinds
    for ch, verses in todo.items():
        tv, t = txt_verses(ch)
        pr = {ke: (kx, e) for ke, kx, e, x in pairs(ch) if ke and kx}
        repl, nv = [], 0
        for k, kinds in verses.items():
            kx, e = pr[k]
            body, spans = tv[kx]
            toks = []
            for a, b in spans:
                for m in re.finditer(r'[^\s 　]+', t[a:b]):
                    toks.append((a + m.start(), a + m.end()))
            wx, we, hs = hunks(body, e)
            assert len(toks) == len(wx), (ch, k)
            n0 = len(repl)
            for i1, i2, j1, j2, kd in hs:
                if kinds is None and kd in ('ref', 'comment'):
                    continue
                if kinds and kd not in kinds:
                    continue
                nw = ' '.join(we[j1:j2])
                if i1 < i2:
                    repl.append((toks[i1][0], toks[i2 - 1][1], nw))
                elif i1 < len(toks):
                    repl.append((toks[i1][0], toks[i1][0], nw + ' '))
                else:
                    repl.append((toks[-1][1], toks[-1][1], ' ' + nw))
            nv += len(repl) > n0
        for a, b, s in sorted(repl, reverse=True):
            t = t[:a] + s + t[b:]
        (TXT / f'CC_{ch}.txt').write_text(t)
        print(f'{ch}: стихов {nv}, замен {len(repl)}')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--apply-txt':
        apply_txt(a[1])
    else:
        report(chapters([x for x in a if not x.startswith('--')]), '--summary' in a)
