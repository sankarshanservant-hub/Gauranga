# Английское издание главы: ed/en/CC_<Глава>.md из
#   ed/work/rows-<Глава>.json (бенгальский и кириллическая транслитерация, уже сверенные со сканом; prep_vcd.py) и
#   ed/en/work/<Глава>.txt — наш перевод с бенгальского:
#     @title Chapter title
#     @N            (или @N-M — метка как у стиха в ed/vcd; для каждой строки транслитерации — строка пословного)
#     word-by-word for line 1 (words separated by two spaces)
#     ...
#     = verse translation (can continue on following lines)
#     @notes
#     [^N-k]: editorial note
# Использование: python3 tools/build_en.py Adi02 [...]
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyr2iast import conv
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
LILA = {'Adi': 'Ādi-līlā', 'Madhya': 'Madhya-līlā', 'Antya': 'Antya-līlā'}

def parse(path):
    title, items, notes, cur, mode = '', {}, [], None, None
    for raw in open(path, encoding='utf-8').read().split('\n'):
        l = raw.rstrip()
        if l.startswith('@title'): title = l[6:].strip(); continue
        if l.startswith('@notes'): mode = 'notes'; cur = None; continue
        m = re.match(r'^@(\d+(?:-\d+)?)\s*$', l)
        if m:
            cur = {'ww': [], 'tr': ''}; items[m.group(1)] = cur; mode = 'ww'; continue
        if mode == 'notes':
            if l.strip(): notes.append(l)
            continue
        if cur is None: continue
        if l.startswith('='): mode = 'tr'; cur['tr'] = l[1:].strip(); continue
        if mode == 'tr':
            if l.strip(): cur['tr'] += ' ' + l.strip()
            continue
        if l.strip(): cur['ww'].append(l.strip())
    return title, items, notes

def build(chap):
    lila, nn = re.match(r'([A-Za-z]+)(\d+)', chap).groups()
    rows = json.load(open(os.path.join(ROOT, 'ed', 'work', 'rows-%s.json' % chap), encoding='utf-8'))
    title, items, notes = parse(os.path.join(ROOT, 'ed', 'en', 'work', '%s.txt' % chap))
    out = ['“Śrī Caitanya-caritāmṛta”  ', LILA[lila] + '  ', 'Chapter %d  ' % int(nn), '**%s**  ' % title,
           '(translated from the Bengali for this edition)', '']
    errs, done = [], 0
    for r in rows:
        key = r['lab'].replace('–', '-')
        it = items.get(key)
        for g in r['bn']: out.append('  \n'.join(g)); out.append('')
        tl = [conv(a) for a, b in r['pairs']]
        if it is None: errs.append('%s: нет перевода' % key); ww = []
        else:
            ww = it['ww']; done += 1
            if len(ww) != len(tl): errs.append('%s: транслит. строк %d, пословного %d' % (key, len(tl), len(ww)))
        il = []
        for i, t in enumerate(tl):
            il.append(t)
            if i < len(ww): il.append(ww[i])
        out.append('  \n'.join(il)); out.append('')
        out.append('(%s) %s' % (r['lab'], it['tr'] if it else '[not yet translated]')); out.append('')
    if notes: out += ['---', ''] + [x + '\n' for x in notes]
    os.makedirs(os.path.join(ROOT, 'ed', 'en'), exist_ok=True)
    open(os.path.join(ROOT, 'ed', 'en', 'CC_%s.md' % chap), 'w', encoding='utf-8').write('\n'.join(out).rstrip() + '\n')
    print('%s EN: переведено %d из %d' % (chap, done, len(rows)))
    for e in errs[:30]: print('  !', e)

if __name__ == '__main__':
    for c in sys.argv[1:]: build(c)
