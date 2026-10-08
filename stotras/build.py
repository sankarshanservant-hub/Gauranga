"""Собирает том «Гимны спутников о Шри Гауре» (ru/en: предисловие 00, стотры 01–08) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Gaura-Stotras-ru', title='Гимны спутников о Шри Гауре',
               author='Рагхунатха Дас Госвами, Рупа Госвами, Шри Чайтанья (рус. пер.)', toc='Оглавление'),
    'en': dict(out='Gaura-Stotras-en', title='Hymns of the Companions to Sri Gaura',
               author='Raghunatha Dasa Gosvami, Rupa Gosvami, Sri Chaitanya (Eng. tr.)', toc='Contents'),
}
PARTS = [f'{i:02d}' for i in range(1, 9)]


def build(lang):
    m = META[lang]
    preface = open(os.path.join(HERE, lang, '00.md'), encoding='utf-8').read().strip()
    preface = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^00-{mm.group(1)}]', preface)
    toc, body = [], []
    for key in PARTS:
        text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    md = (preface + '\n\n## ' + m['toc'] + '\n\n' + '\n'.join(toc) + '\n\n---\n\n'
          + '\n\n---\n\n'.join(body) + '\n')
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
