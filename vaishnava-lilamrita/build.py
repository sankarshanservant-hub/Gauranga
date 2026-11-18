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


def lo_pdf(docx, pdf):
    """PDF через LibreOffice из DOCX: reportlab неверно раскладывает ория рядом с кириллицей (наложения, квадраты).
    В DOCX включаем «не растягивать строки с ручным переносом» (иначе стихи растягиваются по ширине)."""
    import shutil, subprocess, tempfile, zipfile
    tmp = docx + '.tmp'
    with zipfile.ZipFile(docx) as zi, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            data = zi.read(it.filename)
            if it.filename == 'word/settings.xml':
                x = data.decode('utf-8')
                if 'doNotExpandShiftReturn' not in x:
                    x = (x.replace('<w:compat>', '<w:compat><w:doNotExpandShiftReturn/>', 1) if '<w:compat>' in x
                         else x.replace('</w:settings>', '<w:compat><w:doNotExpandShiftReturn/></w:compat></w:settings>'))
                data = x.encode('utf-8')
            zo.writestr(it, data)
    os.replace(tmp, docx)
    fonts = os.path.expanduser('~/.fonts')
    os.makedirs(fonts, exist_ok=True)
    if not os.path.exists(os.path.join(fonts, os.path.basename(ORYA_FONT))):
        shutil.copy(ORYA_FONT, fonts); subprocess.run(['fc-cache', '-f'], check=False)
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', d, docx], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.move(os.path.join(d, os.path.basename(docx)[:-5] + '.pdf'), pdf)


def renumber(text, key):
    """Сноски главы: словесные метки → номера по порядку первой ссылки ([^bhela-42] → [^01-1])."""
    order = {}
    for mm in re.finditer(r'\[\^([^\]]+)\](?!:)', text):
        order.setdefault(mm.group(1), len(order) + 1)
    for mm in re.finditer(r'(?m)^\[\^([^\]]+)\]:', text):     # определение без ссылки — в конец
        order.setdefault(mm.group(1), len(order) + 1)
    return re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{order[mm.group(1)]}]', text)


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
        text = renumber(text, key).replace('][^', '],[^')     # две сноски подряд: «1,2»
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    md = m['preface'].rstrip() + '\n\n' + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    lo_pdf(os.path.join(HERE, m['out'] + '.docx'), os.path.join(HERE, m['out'] + '.pdf'))
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
