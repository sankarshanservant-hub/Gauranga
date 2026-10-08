"""Собирает перевод «Нароттама-виласы» (ru/en, виласы 01–12 — сколько готово) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Narottama-Vilasa-ru', title='Нароттама-виласа', author='Нарахари Чакраварти (рус. пер.)',
               preface='00.md'),
    'en': dict(out='Narottama-Vilasa-en', title='Narottama-vilasa', author='Narahari Chakravarti (Eng. tr.)',
               preface='00.md'),
}
TOC = {'ru': '## Оглавление', 'en': '## Contents'}


def build(lang):
    m = META[lang]
    pre = open(os.path.join(HERE, lang, m['preface']), encoding='utf-8').read().strip()
    toc, body = [], []
    for i in range(1, 13):
        key = f'{i:02d}'
        path = os.path.join(HERE, lang, key + '.md')
        if not os.path.exists(path):
            continue
        text = open(path, encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    md = (pre + '\n\n---\n\n' + TOC[lang] + '\n\n' + '\n'.join(toc) + '\n\n---\n\n'
          + '\n\n---\n\n'.join(body) + '\n')
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
