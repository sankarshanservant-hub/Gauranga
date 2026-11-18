"""Делит набранный текст Саньяла на фрагменты для перевода (≈2000 слов, по границам абзацев).
python3 -I sanyal/tools/split.py <выходная папка>
Разделы — по строкам набранного текста sources/sanyal/Sanyal_vol1-2_retyped.txt (см. SECTIONS);
абзацы, разорванные переносом страницы (несколько пустых строк, предложение не кончено), склеиваются."""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'sources/sanyal/Sanyal_vol1-2_retyped.txt')
# (код, название, первая строка, последняя строка) — 1-based
SECTIONS = [('00-title', 'Титул', 1, 31), ('00-publisher', 'Publisher preface', 32, 129),
            ('00-preface', 'Preface', 130, 190), ('00-contents', 'Contents', 191, 605),
            ('00-foreword', 'Foreword (Bhaktisiddhanta Sarasvati)', 606, 1379)]
I = [1382, 2052, 2713, 3419, 4499, 6018, 6446, 7059, 8122, 8958]
for k in range(9):
    SECTIONS.append((f'I-{k + 1:02d}', f'Vol. I, ch. {k + 1}', I[k], I[k + 1] - 1))
II = [9277, 10018, 10688, 11373, 11843, 12586, 13098, 13971, 14511, 15108, 15696, 16254, 17018, 18384, 19158,
      19966, 20446, 21046, 21839, 22884, 23950, 24666, 25493, 26258]
SECTIONS.append(('II-00', 'Auspicatory Observance', 8958, 9276))
L = open(SRC, encoding='utf-8').read().split('\n')
II.append(len(L) + 1)
for k in range(24):
    SECTIONS.append((f'II-{k + 1:02d}', f'Vol. II, ch. {k + 1}', II[k], II[k + 1] - 1))
LIMIT = 2000


def paragraphs(lines):
    out, cur, blanks = [], [], 0
    for ln in lines + ['']:
        if ln.strip():
            if cur and blanks >= 2 and not re.search(r'[.!?:;»”"\')\]]\s*$', cur[-1]):
                pass                         # перенос страницы посреди абзаца — продолжаем
            elif cur and blanks:
                out.append(' '.join(x.strip() for x in cur)); cur = []
            cur.append(ln); blanks = 0
        else:
            blanks += 1
    if cur:
        out.append(' '.join(x.strip() for x in cur))
    return [re.sub(r'\s+', ' ', p).strip() for p in out if p.strip()]


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    index = []
    for code, title, a, b in SECTIONS:
        ps = paragraphs(L[a - 1:b])
        frags, cur, n = [], [], 0
        for p in ps:
            w = len(p.split())
            if cur and n + w > LIMIT:
                frags.append(cur); cur, n = [], 0
            cur.append(p); n += w
        if cur:
            frags.append(cur)
        if len(frags) > 1 and sum(len(x.split()) for x in frags[-1]) < 500:   # короткий хвост — к предыдущему
            tail = frags.pop(); frags[-1] += tail   # не «frags[-2] += frags.pop()»: индекс -2 вычисляется до pop
        start = 1
        for i, fr in enumerate(frags, 1):
            name = f'SN-{code}-{i:02d}.txt'
            words = sum(len(x.split()) for x in fr)
            with open(os.path.join(outdir, name), 'w', encoding='utf-8') as f:
                f.write(f'# {name[:-4]} — {title}, фрагмент {i} из {len(frags)}; абзацы {start}–{start + len(fr) - 1}'
                        f' (раздела); строки исходника {a}–{b}; {words} слов, {len(fr)} абзацев\n\n')
                for j, p in enumerate(fr, start):
                    f.write(f'[{j}] {p}\n\n')
            index.append((name[:-4], title, i, len(frags), start, start + len(fr) - 1, words))
            start += len(fr)
    with open(os.path.join(outdir, 'INDEX.md'), 'w', encoding='utf-8') as f:
        f.write('| Фрагмент | Раздел | № | Абзацы | Слов |\n|---|---|---|---|---|\n')
        for nm, t, i, k, s, e, w in index:
            f.write(f'| {nm} | {t} | {i}/{k} | {s}–{e} | {w} |\n')
    print(len(index), 'фрагментов,', sum(x[6] for x in index), 'слов')


if __name__ == '__main__':
    main(sys.argv[1])
