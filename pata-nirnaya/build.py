"""Книги RU/EN (MD, DOCX, PDF): python3 build.py [ru|en]. Вёрстка — как в ../rasika-mangala/build.py."""
import importlib.util, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rm', os.path.join(HERE, '..', 'rasika-mangala', 'build.py'))
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
PARTS = {'shakha-nirnayamrita': ['SNA'], 'pata-nirnaya': ['PN', 'PP', 'ASN']}[os.path.basename(HERE)]
NAME = {'shakha-nirnayamrita': 'Shakha-Nirnayamrita', 'pata-nirnaya': 'Pata-Nirnaya'}[os.path.basename(HERE)]
def build(lang):
    body = []
    for k in PARTS:
        t = re.sub(r'^# ', '## ', open(os.path.join(HERE, lang, k + '.md'), encoding='utf-8').read().strip(), count=1)
        body.append(rm.prepare(t, k, lang))
    md = open(os.path.join(HERE, f'front-{lang}.md'), encoding='utf-8').read().rstrip() + '\n\n---\n\n' + '\n\n'.join(body) + '\n'
    out = os.path.join(HERE, f'{NAME}-{lang}')
    open(out + '.md', 'w', encoding='utf-8').write(md)
    rm.kb.build_docx(rm.parse(md), out + '.docx'); rm.lo_pdf(out + '.docx', out + '.pdf')
    print(lang, 'ok')
if __name__ == '__main__':
    for l in [a for a in sys.argv[1:] if a in ('ru', 'en')] or ['ru', 'en']: build(l)
