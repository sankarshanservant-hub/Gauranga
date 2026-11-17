"""Собирает литературный перевод «Вайшнава-лиламриты» (ru/en, главы 01–09) в MD, DOCX и PDF.
Полное издание (ория + транслитерация + пословный) — отдельно, позже.
Использует разбор и вёрстку из ../govinda-kadacha/build.py; орийские слова в сносках набираются шрифтом
Noto Sans Oriya (../fonts). Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)
ORYA_FONT = os.path.join(HERE, '..', 'fonts', 'NotoSansOriya-Regular.ttf')

# --- орийское письмо в PDF: регистрируем шрифт и оборачиваем орийские отрезки ---
_orig_inline = kb.inline
_ORYA = re.compile('[\u0B00-\u0B7F][\u0B00-\u0B7F\u200c\u200d ]*[\u0B00-\u0B7F]|[\u0B00-\u0B7F]')
_LONE = re.compile('(?<![\u0B00-\u0B7F])([\u0B01-\u0B03\u0B3C\u0B3E-\u0B57\u0B62\u0B63])')  # одиночная матра «ି» → «◌ି»
def inline(text, html=True):
    s = _orig_inline(text, html)
    if not html:
        return s
    lone = []
    s = _LONE.sub(lambda m: (lone.append(m.group(1)), f'\x00{len(lone) - 1}\x00')[1], s)
    s = _ORYA.sub(lambda m: f'<font name="Orya">{m.group(0)}</font>', s)
    s = re.sub('\x00(\\d+)\x00', lambda m: f'<font name="Orya">-{lone[int(m.group(1))]}</font>', s)
    # орийское слово в самом начале абзаца (сразу после метки сноски) reportlab не шейпит — отделяем пробелом
    return ' ' + s if s.startswith('<font name="Orya">') else s
kb.inline = inline
_orig_pdf = kb.build_pdf
def build_pdf(blocks, path, title, author):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import ParagraphStyle
    pdfmetrics.registerFont(TTFont('Orya', ORYA_FONT))
    _init = ParagraphStyle.__init__
    def init(self, *a, **k):          # включаем шейпинг (лигатуры ория) во всех стилях
        _init(self, *a, **k); self.shaping = 1
    ParagraphStyle.__init__ = init
    try:
        _orig_pdf(blocks, path, title, author)
    finally:
        ParagraphStyle.__init__ = _init
kb.build_pdf = build_pdf

META = {
    'ru': dict(out='Vaishnava-Lilamrita-ru', title='Вайшнава-лиламрита', author='Мадхава Паттанаяк (рус. пер.)',
               preface=open(os.path.join(HERE, 'front-ru.md'), encoding='utf-8').read()),
    'en': dict(out='Vaishnava-Lilamrita-en', title='Vaishnava-lilamrita', author='Madhava Pattanayaka (Eng. tr.)',
               preface=open(os.path.join(HERE, 'front-en.md'), encoding='utf-8').read()),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 10):
        key = f'{i:02d}'
        path = os.path.join(HERE, lang, key + '.md')
        if not os.path.exists(path):
            continue
        text = open(path, encoding='utf-8').read().strip()
        # служебная строка о файле full/CC.md в книге не нужна
        text = re.sub(r'(?m)^\*(Перевод с ория|Translated from O).*\n?', '', text)
        text = re.sub(r'(?m)^\[\^intro-1\]:.*\n?', '', text)   # сведения сноски — в предисловии
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    md = m['preface'].rstrip() + '\n\n' + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
