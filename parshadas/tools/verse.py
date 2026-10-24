#!/usr/bin/env python3
"""Перевод стиха по ссылке из наших файлов (почти без затрат токенов).
  verse.py "CC Madhya 4.197-199"   — ЧЧ, перевод ВЧД (chaitanya-charitamrita/vcd/txt/CC_<Лила><NN>.txt)
  verse.py "CB Antya 3.176-178"    — ЧБ, по нашему изданию chaitanya-bhagavata/ed/CB_<Кханда><NN>.md
Лилы/кханды: Adi, Madhya, Antya. ЧБ — по ed/ (там ручные правки; Мадхья/Антья пересобраны 2026-10-24); запасной
путь, если стиха в ed нет: Ади — CB_Adi_verses.json, Мадхья/Антья — src/txt/CB_<Кханда><NN>.txt."""
import re, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]

def cc(lila, ch, a, b):
    t = (R / f'chaitanya-charitamrita/vcd/txt/CC_{lila}{ch:02d}.txt').read_text(errors='replace')
    out = []
    for v in range(a, b + 1):
        m = re.search(rf'^\({v}(?:[–-]\d+)?\)(.*?)(?=^\(\d+(?:[–-]\d+)?\)|\Z)', t, re.S | re.M)
        grp = ''
        if not m:  # стих внутри группы «(54–55)»
            for g in re.finditer(r'^\((\d+)[–-](\d+)\)(.*?)(?=^\(\d+(?:[–-]\d+)?\)|\Z)', t, re.S | re.M):
                if int(g.group(1)) <= v <= int(g.group(2)):
                    m, grp = g, f'[{g.group(1)}–{g.group(2)}] '
                    break
        if not m: out.append(f'({v}) — не найден'); continue
        body = m.group(3) if grp else m.group(1)
        body = re.split(r'[\u0980-\u09FF]', body)[0]  # до бенгальского текста следующего стиха
        body = re.split(r'[\u1160\uFFA0\u3164]', body)[0]  # до приклеенного подзаголовка («ᅠ ᅠ 9 ветвь — …»)
        out.append(f'({v}) {grp}' + re.sub(r'\s+', ' ', body).strip())
    return out

def cb_ed(kh, ch, a, b):
    """Издание ed/CB_<Кханда><NN>.md: «**N.** перевод» (группы — «**12–14.**»)."""
    f = R / f'chaitanya-bhagavata/ed/CB_{kh}{ch:02d}.md'
    if not f.exists(): return None
    t = f.read_text(errors='replace')
    out = []
    for v in range(a, b + 1):
        m, grp = re.search(rf'^\*\*{v}\.\*\* (.*)$', t, re.M), ''
        if not m:
            for g in re.finditer(r'^\*\*(\d+)[–-](\d+)\.\*\* (.*)$', t, re.M):
                if int(g.group(1)) <= v <= int(g.group(2)):
                    m, grp = g, f'[{g.group(1)}–{g.group(2)}] '
                    break
        out.append(f'({v}) {grp}' + (m.group(m.lastindex).strip() if m else '— не найден'))
    return out

def cb(kh, ch, a, b):
    # все кханды — по изданию ed/ (разбор CB_Adi_verses.json и src/txt ошибался: транслитерация вместо перевода,
    # склейка с пояснением — Антья 4.171, 4.178, 8.125)
    r = cb_ed(kh, ch, a, b)
    if r and not any(x.endswith('— не найден') for x in r): return r
    if kh == 'Adi':  # разобрано tools/cb_adi_parse.py из двухколоночной выгрузки CB_Adi_all.txt
        import json
        d = json.loads((R / 'chaitanya-bhagavata/src/txt/CB_Adi_verses.json').read_text())
        out = []
        for v in range(a, b + 1):
            s = d.get(f'{ch}.{v}', '')
            sure = s.rstrip().endswith(('.', '!', '?', '»', '”', ']', ')')) and len(s) < 450
            out.append(f'({v}) ' + (s if s else '— не найден (искать в CB_Adi_all.txt)')
                       + ('' if not s or sure else '  ⚠ проверить по CB_Adi_all.txt (разбор неуверенный)'))
        return out
    t = (R / f'chaitanya-bhagavata/src/txt/CB_{kh}{ch:02d}.txt').read_text(errors='replace')
    out = []
    for v in range(a, b + 1):
        m = re.search(rf'^Тексты? (?:{ch}\.)?{v}(?:[–-]\d+)?\s*$(.*?)(?=^Тексты? \d+|\Z)', t, re.S | re.M)
        grp = ''
        if not m:  # стих внутри группы «Текст 12–14»
            for g in re.finditer(r'^Тексты? (?:\d+\.)?(\d+)[–-](?:\d+\.)?(\d+)\s*$(.*?)(?=^Тексты? \d+|\Z)', t, re.S | re.M):  # бывает «Тексты 5.231–233»
                if int(g.group(1)) <= v <= int(g.group(2)):
                    m, grp = g, f'[{g.group(1)}–{g.group(2)}] '
                    break
            m = m and type('M', (), {'group': lambda self, i, _g=m: _g.group(3) if i == 1 else _g.group(i)})()
        if not m: out.append(f'({v}) — не найден'); continue
        # перевод идёт после бенгальских строк и стольких же строк транслитерации (в транслитерации бывает строка
        # без диакритики, а в переводе — слово с диакритикой, поэтому по одному виду строки их не различить)
        ls = [l.strip() for l in m.group(1).splitlines()]
        bn = [i for i, s in enumerate(ls) if re.search(r'[\u0980-\u09FF]', s)]
        if bn:
            run = [bn[0]]  # первая группа бенгальских строк (в блоке бывает несколько стихов)
            for i in bn[1:]:
                if i != run[-1] + 1: break
                run.append(i)
            bn = run
            rest = [s for s in ls[bn[-1] + 1:]]
            k, i = len(bn), 0
            while i < len(rest) and k:  # пропустить транслитерацию
                if rest[i]: k -= 1
                i += 1
            tr = []
            for s in rest[i:]:
                if not s:
                    if tr: break
                    continue
                tr.append(s)
            if tr:
                out.append(f'({v}) {grp}' + ' '.join(tr)); continue
        # запасной путь: первые подряд идущие строки кириллицей, без бенгальского и без диакритики транслитерации
        tr, started = [], False
        for l in m.group(1).splitlines():
            s = l.strip()
            ok = bool(s) and re.search('[А-Яа-яЁё]{3}', s) and not re.search(r'[\u0980-\u09FF\u0300-\u036F]', s)
            if ok:
                tr.append(s); started = True
            elif started:
                break
        out.append(f'({v}) ' + ' '.join(tr))
    return out

for ref in sys.argv[1:]:
    m = re.match(r'(CC|CB)\s+(Adi|Madhya|Antya)\s+(\d+)\.(\d+)(?:[–-](\d+))?', ref)
    if not m: print(ref, '— формат: "CC Adi 5.205-207"'); continue
    src, lila, ch, a, b = m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), int(m.group(5) or m.group(4))
    print(f'## {ref}'); print('\n'.join((cc if src == 'CC' else cb)(lila, ch, a, b)))
