"""Собирает «Шри Чайтанья-упанишад» с комментарием Бхактивиноды (ru/en: предисловие 00, текст 01) в MD, DOCX и PDF.
Перед сборкой подставляет санскрит из src/mula.py вместо меток `@@mula N@@` (src/fill.py).
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py (санскрит — Noto Serif Devanagari).
Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Chaitanya-Upanishad-ru', title='Шри Чайтанья-упанишад',
               author='С комментарием Бхактивиноды Тхакура (рус. пер.)'),
    'en': dict(out='Chaitanya-Upanishad-en', title='Sri Chaitanya Upanishad',
               author='With the commentary of Bhaktivinoda Thakura (Eng. tr.)'),
}
PARTS = ['01']


def build(lang):
    m = META[lang]
    preface = open(os.path.join(HERE, lang, '00.md'), encoding='utf-8').read().strip()
    preface = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^00-{mm.group(1)}]', preface)
    body = []
    for key in PARTS:
        text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        body.append(text)
    md = preface + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    subprocess.run([sys.executable, os.path.join(HERE, 'src', 'fill.py')], check=True)
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
