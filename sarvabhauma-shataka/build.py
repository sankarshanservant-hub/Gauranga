"""Собирает литературный перевод «Сарвабхаума-шатаки» (ru/en) в MD, DOCX и PDF.
Вёрстка — ../govinda-kadacha/build.py, PDF — LibreOffice (как в ../rasika-mangala/build.py). Запуск: python3 build.py [ru|en]."""
import importlib.util, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rm', os.path.join(HERE, '..', 'rasika-mangala', 'build.py'))
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
OUT = {'ru': 'Sarvabhauma-Shataka-ru', 'en': 'Sarvabhauma-Shataka-en'}


def build(lang):
    text = open(os.path.join(HERE, lang, '01.md'), encoding='utf-8').read().strip()
    text = re.sub(r'^# .*\n+\*[^\n]*\*(\[\^[^\]]+\])?\s*\n', lambda m: '', text, count=1)   # титул — в предисловии
    src = re.search(r'\[\^(source-1)\]', open(os.path.join(HERE, lang, '01.md'), encoding='utf-8').read().split('\n\n')[1])
    if src and f'[^{src.group(1)}]' not in text.split('\n[^')[0]:
        text = re.sub(r'(?m)^(\*\*1\.\*\*.*?)$', lambda m: m.group(1) + f'[^{src.group(1)}]', text, count=1)
    head = '## Шатака' if lang == 'ru' else '## The Shataka'
    text = rm.prepare(head + '\n\n' + text, '1', lang)
    md = open(os.path.join(HERE, f'front-{lang}.md'), encoding='utf-8').read().rstrip() + '\n\n---\n\n' + text
    out = os.path.join(HERE, OUT[lang])
    open(out + '.md', 'w', encoding='utf-8').write(md)
    rm.kb.build_docx(rm.parse(md), out + '.docx')
    rm.lo_pdf(out + '.docx', out + '.pdf')
    print(lang, 'ok', md.count('\n[^'), 'сносок')


if __name__ == '__main__':
    for lang in [a for a in sys.argv[1:] if a in ('ru', 'en')] or ['ru', 'en']:
        build(lang)
