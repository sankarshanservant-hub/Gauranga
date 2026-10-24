#!/usr/bin/env python3
"""Проверка поглавных md ЧБ (ed/CB_*.md): сбои сборки по стихам.
  A — перевод начинается со строчной буквы или с диакритики транслитерации (приклеена транслитерация?);
  B — пустой перевод;
  C — пропуски и повторы номеров стихов (с учётом групп «N–M»);
  D — (справочно) в переводе есть диакритика транслитерации (часто законно: «Слово дад̣ха̄на…»; при -v — список).
Запуск: python3 chaitanya-bhagavata/tools/check_ed.py [DIR] [-v] [--only Madhya|Antya|Adi]
Код выхода 1, если есть A–C."""
import re, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
TL = re.compile(r'[̀-ͯӣӯ]')
args = sys.argv[1:]
verbose = '-v' in args
only = args[args.index('--only') + 1] if '--only' in args else ''
args = [a for i, a in enumerate(args) if not a.startswith('-') and (i == 0 or args[i - 1] != '--only')]
d = Path(args[0]) if args else R / 'ed'
cnt = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
for f in sorted(d.glob('CB_*[0-9][0-9].md')):
    if only and only not in f.stem: continue
    prev, seen = 0, set()
    for ln, l in enumerate(f.read_text().splitlines(), 1):
        m = re.match(r'^\*\*(\d+)(?:[–-](\d+))?\.\*\*\s*(.*)$', l)
        if not m: continue
        a, b, tr = int(m.group(1)), int(m.group(2) or m.group(1)), m.group(3).strip()
        ref = f'{f.stem} {m.group(1)}' + (f'–{m.group(2)}' if m.group(2) else '')
        if a != prev + 1:
            cnt['C'] += 1
            print(f'C {ref}: после {prev} идёт {a}' + (' (повтор)' if a <= prev else ' (пропуск)'))
        prev = max(prev, b)
        if not tr:
            cnt['B'] += 1; print(f'B {ref}: пустой перевод'); continue
        w = tr.split()[0]
        c = re.search(r'[A-Za-zА-Яа-яЁёЀ-ӿ]', tr)
        if (c and c.group(0).islower()) or TL.search(w):
            cnt['A'] += 1; print(f'A {ref}: {tr[:90]}')
        elif TL.search(tr):
            cnt['D'] += 1
            if verbose: print(f'D {ref}: …{tr[max(0, TL.search(tr).start() - 40):][:90]}')
print(f'Итого: A (строчная/диакритика в начале) {cnt["A"]}, B (пустой) {cnt["B"]}, '
      f'C (пропуски/повторы номеров) {cnt["C"]}; справочно D (диакритика внутри перевода) {cnt["D"]}')
sys.exit(1 if cnt['A'] + cnt['B'] + cnt['C'] else 0)
