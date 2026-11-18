"""Собирает литературный перевод «Джаганнатха-чаритамриты» Дивакара Даса (ru/en, главы 01–07, 23) в MD, DOCX и PDF.
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
    'ru': dict(out='Jagannatha-Charitamrita-ru', title='Джаганнатха-чаритамрита', author='Дивакар Дас (рус. пер.)',
               preface=open(os.path.join(HERE, 'front-ru.md'), encoding='utf-8').read()),
    'en': dict(out='Jagannatha-Charitamrita-en', title='Jagannatha-charitamrita', author='Divakara Dasa (Eng. tr.)',
               preface=open(os.path.join(HERE, 'front-en.md'), encoding='utf-8').read()),
}
CHAPTERS = [1, 2, 3, 4, 5, 6, 7, 23]



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
    for i in CHAPTERS:
        key = f'{i:02d}'
        path = os.path.join(HERE, lang, key + '.md')
        if not os.path.exists(path):
            continue
        text = open(path, encoding='utf-8').read().strip()
        # служебная строка о файле full/CC.md в книге не нужна (сноска на ней — переносим на заголовок раздела)
        mm = re.search(r'(?m)^\*(?:Перевод с ория|Translated from O).*?\*((?:\[\^[^\]]+\])*)\s*$', text)
        if mm:
            text = text[:mm.start()] + text[mm.end():]
            if mm.group(1):
                # знак сноски в заголовке не набирается — ставим его после первого стиха
                text = re.sub(r'(?m)^(\*\*\d+\.\d+\.\*\*.*?)(\s*)$', lambda x: x.group(1) + mm.group(1) + x.group(2), text, count=1)
        # рабочие заметки переводчика о страницах PDF (сноски intro-…) в книгу не идут — суть их в предисловии
        text = re.sub(r'\[\^intro-[^\]]+\](?!:)', '', text)
        text = re.sub(r'(?m)^\[\^intro-[^\]]+\]:.*\n?', '', text)
        text = renumber(text, key).replace('][^', '],[^')     # две сноски подряд: «1,2»
        sub = re.search(r'(?m)^## (.+)$', text)
        toc.append(f"- {'Глава' if lang == 'ru' else 'Chapter'} {i}" + (f'. {sub.group(1).strip()}' if sub else ''))
        body.append(text)
    md = m['preface'].rstrip() + '\n\n' + ('## Оглавление\n\n' if lang == 'ru' else '## Contents\n\n') + \
        '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    out_dir, out = HERE, m['out']
    open(os.path.join(out_dir, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(out_dir, out + '.docx'))
    lo_pdf(os.path.join(out_dir, out + '.docx'), os.path.join(out_dir, out + '.pdf'))
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    args = sys.argv[1:]
    langs = [a for a in args if a in ('ru', 'en')] or ['ru', 'en']
    for lang in langs:
        build(lang)
