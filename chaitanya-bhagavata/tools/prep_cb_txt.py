#!/usr/bin/env python3
"""ЧБ Мадхья/Антья: src/txt/CB_<Кханда>NN.txt (формат «Текст N»: бенгальский, транслитерация, перевод, пояснение)
→ ed/CB_<Кханда>NN.md в формате ed/CB_Adi*.md: транслитерация курсивом + «**N.** перевод». Пояснения не включаются.

ВНИМАНИЕ: ed/ правят вручную (опечатки, исправления по бенгальскому). Не перезаписывать ed вслепую: собирать во
временную папку (--out DIR) и сводить с ed по стихам (см. PLAN.md, «Пересборка ed, 2026-10-24»).

Запуск: python3 chaitanya-bhagavata/tools/prep_cb_txt.py [--out DIR] [--src DIR] [CB_Madhya06 ...]

Разбор блока стиха (2026-10-24; прежняя версия теряла/склеивала строки):
  * заголовок «Текст N», «Тексты N–M», «Тексты 4.59–60», «Тексты47-48», «Текст 197 (*)»;
  * если есть бенгальский текст — транслитерация = столько же непустых строк, сколько бенгальских (санскритские
    шлоки — ещё строки со строчной буквы и с диакритикой); в главах без бенгальского (Антья 4–10) — подряд идущие
    строки со строчной буквы;
  * перевод — с первой строки после транслитерации до пустой строки или до строки с отступом после строки,
    кончающейся точкой/!/?/кавычкой (пояснение издания в Антья 4–10 идёт сразу, с отступом).
"""
import re, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
KH = {'Madhya': 'Мадхья-кханда', 'Antya': 'Антья-кханда'}
BN = re.compile(r'[ঀ-৿]')
TL = re.compile(r'[̀-ͯӣӯ]')  # комбинир. диакритика, ӣ, ӯ — признак транслитерации
HDR = re.compile(r'^[ \t]*[ТT]ексты?[ \t]*(?:\d+\.)?(\d+(?:[ \t]*[–-][ \t]*(?:\d+\.)?\d+)?)[ \t]*(?:\(\*\))?[ \t]*$', re.M)
TLW = re.compile(r'[\u0300-\u036F\u04E3\u04EF’]|й[аеуо]')  # признаки транслитерации в строке
END = ('.', '!', '?', '»', '”', '…', ')', '"', ':')


def first_letter(s):
    m = re.search(r'[A-Za-zА-Яа-яЁёЀ-ӿ]', s)
    return m.group(0) if m else ''


def is_lower(s):
    c = first_letter(s)
    return bool(c) and c.islower()


def parse_block(body):
    """→ (translit, translation) — списки строк. Построчный разбор:
    бенгальская строка ожидает строку транслитерации; строка со строчной буквы — транслитерация (сверх ожидаемых —
    только с признаками транслитерации); первая строка с прописной после транслитерации — начало перевода; перевод —
    до пустой строки, бенгальской строки или строки с отступом после конца предложения. Вводные слова перед
    цитатой (до бенгальского), подзаголовки «… — «…»», «...» и смешанные бенгальско-латинские подзаголовки
    пропускаются."""
    translit, tr = [], []
    expect, seen, sub, para = 0, False, False, 0
    for l in body.split('\n'):
        s = l.strip()
        if tr:
            if not s or BN.search(s): break
            if re.match(r'^[ \t]{2,}\S', l) and tr[-1].rstrip().endswith(END): break
            tr.append(s); continue
        if not s:
            sub, para = False, len(translit); continue
        if sub: continue
        if BN.search(s):
            if re.search('[А-Яа-яЁё]', s): sub = True; continue  # «বাংলা, транслитерация.» — подзаголовок
            expect += 1; seen = True; continue
        if s in ('...', '…') or (not first_letter(s).isupper() and re.search(r'— «(?:[А-ЯЁ]|\.\.|»)|«\.\.»', s)):
            del translit[para:]; sub = True; continue
        if is_lower(s) or (TL.search(s) and not first_letter(s).isupper()):
            if expect > 0 or not seen or TLW.search(s):
                translit.append(s); expect = max(expect - 1, 0); continue
        if not translit:  # вводные слова до цитаты («В “Бхагавад-гите” [9.17] говорится:»)
            if not first_letter(s): continue
            if not seen: continue
        tr.append(s)
    return translit, tr


def build(f):
    kh, ch = re.match(r'CB_(Madhya|Antya)(\d+)', f.stem).groups()
    t = f.read_text(errors='replace').replace('\xa0', ' ').replace('\r', '')
    title = ''
    m = re.search(r'Глава \d+\.\s*(.+)', t) or re.search(r'^\s*Глава \d+\s*\n\s*(.+(?:\n\s*[а-яё].+)?)', t, re.M)
    if m: title = re.sub(r'\s+', ' ', m.group(1)).strip()
    parts = HDR.split(t)
    out = ['“Шри Чайтанья-бхагавата”  ', f'{KH[kh]}  ', f'Глава {int(ch)}  ', f'**{title}**  ',
           '(Вриндаван Дас Тхакур; рус. пер.)', '',
           f'<!-- Стихи: транслитерация и перевод из src/txt/{f.name}; пояснения не включены. '
           'Собрано chaitanya-bhagavata/tools/prep_cb_txt.py, далее правки вручную (опечатки, по бенгальскому). -->', '']
    n = 0
    for i in range(1, len(parts), 2):
        num = re.sub(r'\s*[–-]\s*(?:\d+\.)?', '–', parts[i])
        translit, tr = parse_block(parts[i + 1])
        if not tr: print(f'  {f.stem} {num}: перевод не найден', file=sys.stderr); continue
        out += [f'*{x}*  ' for x in translit]
        out += ['', f'**{num}.** ' + ' '.join(tr), '']; n += 1
    return kh, ch, '\n'.join(out) + '\n', n


if __name__ == '__main__':
    a = sys.argv[1:]
    outdir, src = R / 'ed', R / 'src/txt'
    if '--out' in a: i = a.index('--out'); outdir = Path(a[i + 1]); del a[i:i + 2]
    if '--src' in a: i = a.index('--src'); src = Path(a[i + 1]); del a[i:i + 2]
    outdir.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob('CB_*[0-9][0-9].txt')):
        if not re.match(r'CB_(Madhya|Antya)\d+$', f.stem) or (a and f.stem not in a): continue
        kh, ch, text, n = build(f)
        (outdir / f'CB_{kh}{ch}.md').write_text(text)
        print(f.name, n)
