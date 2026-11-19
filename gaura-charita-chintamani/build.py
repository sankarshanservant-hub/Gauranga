"""Книги RU/EN «Гаура-чарита-чинтамани» (MD, DOCX, PDF): python3 build.py [ru|en]. Вёрстка — как в ../rasika-mangala/build.py."""
import importlib.util, os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rm', os.path.join(HERE, '..', 'rasika-mangala', 'build.py'))
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
rm.ED = {'ru': ('изд. 1947 г.',), 'en': '1947 edition'}   # изд. Харидаса Даса
def parse(md):
    # строфы «**К.N.**» — тоже стихи (с переносами строк), а не абзацы прозы
    return [('verse', d) if k == 'p' and re.match(r'^\*\*\d+\.\d+[a-zа-я]?\.\*\*', d[0]) else (k, d) for k, d in rm.parse(md)]
def build(lang):
    toc, body = [], []
    for p in sorted(glob.glob(os.path.join(HERE, lang, '[0-9][0-9].md'))):
        k = os.path.basename(p)[:2]
        t = open(p, encoding='utf-8').read().strip()
        t = re.sub(r'^# ', '## ', t, count=1)
        toc.append('- ' + re.match(r'## (.+)', t).group(1).split('[^')[0].strip())
        body.append(rm.prepare(t, k, lang))
    md = open(os.path.join(HERE, f'front-{lang}.md'), encoding='utf-8').read().rstrip() + '\n\n' + \
        ('## Оглавление' if lang == 'ru' else '## Contents') + '\n\n' + '\n'.join(toc) + '\n\n---\n\n' + '\n\n'.join(body) + '\n'
    out = os.path.join(HERE, f'Gaura-Charita-Chintamani-{lang}')
    open(out + '.md', 'w', encoding='utf-8').write(md)
    rm.kb.build_docx(parse(md), out + '.docx'); rm.lo_pdf(out + '.docx', out + '.pdf')
    print(lang, 'ok')
if __name__ == '__main__':
    for l in [a for a in sys.argv[1:] if a in ('ru', 'en')] or ['ru', 'en']: build(l)
