#!/usr/bin/env python3
"""Перевод стиха по ссылке из наших файлов (почти без затрат токенов).
  verse.py "CC Madhya 4.197-199"   — ЧЧ, перевод ВЧД (chaitanya-charitamrita/vcd/txt/CC_<Лила><NN>.txt)
  verse.py "CB Antya 3.176-178"    — ЧБ, Мадхья/Антья (chaitanya-bhagavata/src/txt/CB_<Кханда><NN>.txt)
Лилы/кханды: Adi, Madhya, Antya. ЧБ Ади — по CB_Adi_verses.json (разбор tools/cb_adi_parse.py, ~94 % стихов)."""
import re, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]

def cc(lila, ch, a, b):
    t = (R / f'chaitanya-charitamrita/vcd/txt/CC_{lila}{ch:02d}.txt').read_text(errors='replace')
    out = []
    for v in range(a, b + 1):
        m = re.search(rf'^\({v}(?:[–-]\d+)?\)(.*?)(?=^\(\d+(?:[–-]\d+)?\)|\Z)', t, re.S | re.M)
        if not m: out.append(f'({v}) — не найден'); continue
        body = re.split(r'[\u0980-\u09FF]', m.group(1))[0]  # до бенгальского текста следующего стиха
        out.append(f'({v}) ' + re.sub(r'[\s\u3164]+', ' ', body).strip())
    return out

def cb(kh, ch, a, b):
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
        m = re.search(rf'^Текст {v}(?:[–-]\d+)?\s*$(.*?)(?=^Текст \d+|\Z)', t, re.S | re.M)
        if not m: out.append(f'({v}) — не найден'); continue
        # перевод — первые подряд идущие строки кириллицей, без бенгальского и без диакритики транслитерации
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
