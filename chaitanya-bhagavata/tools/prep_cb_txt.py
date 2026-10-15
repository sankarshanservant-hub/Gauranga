#!/usr/bin/env python3
"""ЧБ Мадхья/Антья: src/txt/CB_<Кханда>NN.txt (формат «Текст N»: бенгальский, транслитерация, перевод, пояснение)
→ ed/CB_<Кханда>NN.md в формате ed/CB_Adi*.md: транслитерация курсивом + «**N.** перевод». Пояснения не включаются.
Запуск: python3 chaitanya-bhagavata/tools/prep_cb_txt.py"""
import re
from pathlib import Path
R = Path(__file__).resolve().parents[1]
KH = {'Madhya': 'Мадхья-кханда', 'Antya': 'Антья-кханда'}
for f in sorted((R / 'src/txt').glob('CB_*[0-9][0-9].txt')):
    kh, ch = re.match(r'CB_(Madhya|Antya)(\d+)', f.stem).groups()
    t = f.read_text(errors='replace').replace(' ', ' ')
    title = ''
    m = re.search(r'Глава \d+\.\s*(.+)', t) or re.search(r'^\s*Глава \d+\s*\n\s*(.+(?:\n\s*[а-яё].+)?)', t, re.M)
    if m: title = re.sub(r'\s+', ' ', m.group(1)).strip()
    parts = re.split(r'^Тексты? (\d+(?:\s*[–-]\s*\d+)?)\s*$', t, flags=re.M)
    out = ['“Шри Чайтанья-бхагавата”  ', f'{KH[kh]}  ', f'Глава {int(ch)}  ', f'**{title}**  ',
           '(Вриндаван Дас Тхакур; рус. пер.)', '',
           f'<!-- Стихи: транслитерация и перевод из src/txt/{f.name} без правок; пояснения не включены. '
           'Собрано chaitanya-bhagavata/tools/prep_cb_txt.py. -->', '']
    n = 0
    for i in range(1, len(parts), 2):
        num = re.sub(r'\s*[–-]\s*', '–', parts[i]); body = parts[i + 1].splitlines()
        tr, translit, started = [], [], False
        for l in body:
            s = l.strip()
            if not s:
                if started: break
                continue
            if re.search(r'[ঀ-৿]', s): continue
            if re.search(r'[̀-ͯ]', s) and not started: translit.append(s); continue
            if re.search('[А-Яа-яЁё]{3}', s): tr.append(s); started = True
            elif started: break
        if not tr: continue
        out += [f'*{x}*  ' for x in translit]
        out += ['', f'**{num}.** ' + ' '.join(tr), '']; n += 1
    (R / 'ed' / f'CB_{kh}{ch}.md').write_text('\n'.join(out) + '\n')
    print(f.name, n)
