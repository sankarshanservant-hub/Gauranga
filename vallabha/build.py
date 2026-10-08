"""Собирает книгу «Шри Чайтанья в текстах других традиций» (ru/en: 00 — предисловие, 01 — варты,
02 — «Валлабха-дигвиджая» Ядунатхи, 03 — «Бхактамалы» Набхадаса, Дхрувадаса, Рагхавдаса, 04 — кавитты Приядаса)
в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py (как nityananda-vamsha/build.py);
деванагари внутри строк (цитаты оригинала в примечаниях) набирается шрифтом Noto Serif Devanagari.
Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Other-Traditions-ru', title='Шри Чайтанья в текстах других традиций',
               author='Валлабхские варты, «Бхактамалы», Приядас (рус. пер.)', toc='Оглавление'),
    'en': dict(out='Other-Traditions-en', title='Sri Chaitanya in the Texts of Other Traditions',
               author='Vallabha vartas, the Bhaktamals, Priyadas (Eng. tr.)', toc='Contents'),
}
KEYS = ['00', '01', '02', '03', '04']

# --- деванагари: при разборе прячем её в область частного использования, чтобы kb.parse не принял абзац
# с цитатой за «блок оригинала»; после разбора возвращаем.
DEVA = re.compile(r'[ऀ-ॿ]')
OFF = 0xF000 - 0x0900


def hide(s):
    return ''.join(chr(ord(c) + OFF) if 'ऀ' <= c <= 'ॿ' else c for c in s)


def unhide(x):
    if isinstance(x, str):
        return ''.join(chr(ord(c) - OFF) if '' <= c <= '' else c for c in x)
    if isinstance(x, (list, tuple)):
        return type(x)(unhide(i) for i in x)
    return x


def parse(md):
    out = []
    for kind, data in kb.parse(hide(md)):
        data = unhide(data)
        if kind in ('p', 'verse', 'quote') and isinstance(data, list):
            data = [' '.join(l.strip() for l in data)]        # проза: жёсткие переносы исходника снимаются
        out.append((kind, data))
    return out


_inline = kb.inline


def inline(text, html=True):
    s = _inline(text, html)
    if html:
        s = re.sub(r'([ऀ-ॿ](?:[ऀ-ॿ‌‍ ]*[ऀ-ॿ])?)',
                   r'<font name="Deva">\1</font>', s)
    return s


kb.inline = inline


def docx_runs(par, text, size=None):
    """Как kb.docx_runs, но деванагари внутри строки — отдельными прогонами со шрифтом Noto Serif Devanagari."""
    from docx.shared import Pt
    from docx.oxml.ns import qn
    for part in re.split(r'(<b>.*?</b>|<i>.*?</i>|<super>.*?</super>)', inline(text, html=False)):
        if not part:
            continue
        m = re.match(r'<(b|i|super)>(.*)</\1>', part)
        body = m.group(2) if m else part
        for seg in re.split(r'([ऀ-ॿ](?:[ऀ-ॿ‌‍ ]*[ऀ-ॿ])?)', body):
            if not seg:
                continue
            r = par.add_run(seg)
            if m:
                r.bold = m.group(1) == 'b'
                r.italic = m.group(1) == 'i'
                r.font.superscript = m.group(1) == 'super'
            if size:
                r.font.size = Pt(size)
            if DEVA.search(seg):
                fonts = r._element.get_or_add_rPr().get_or_add_rFonts()
                for k in ('w:ascii', 'w:hAnsi', 'w:cs'):
                    fonts.set(qn(k), 'Noto Serif Devanagari')


kb.docx_runs = docx_runs

from reportlab.lib.styles import ParagraphStyle
ParagraphStyle.defaults['shaping'] = 1   # сборка лигатур деванагари (uharfbuzz)

# reportlab формирует «слово» шрифтом первого фрагмента; режем слово по сменам шрифта (как padas/build.py).
import reportlab.platypus.paragraph as _rp
from reportlab.pdfbase import ttfonts as _tt
from reportlab.pdfbase.pdfmetrics import stringWidth as _sw
_orig_shape = _tt.shapeFragWord


def _shape_mixed(w, *a, **k):
    if isinstance(w, _tt.ShapedFragWord):
        return w
    pieces = w[1:]
    if len({f.fontName for f, s in pieces if not hasattr(f, 'cbDefn')}) <= 1:
        return _orig_shape(w, *a, **k)
    groups = []
    for f, s in pieces:
        fn = None if hasattr(f, 'cbDefn') else f.fontName
        if groups and (fn is None or fn == groups[-1][0]):
            groups[-1][1].append((f, s))
        else:
            groups.append([fn, [(f, s)]])
    out, width = [], 0
    for fn, ps in groups:
        sub = w.__class__([sum(_sw(s, f.fontName, f.fontSize) for f, s in ps if not hasattr(f, 'cbDefn'))] + ps)
        r = _orig_shape(sub, *a, **k)
        width += r[0]
        out.extend(r[1:])
    return _tt.makeShapedFragWord(w)([width] + out)


_rp.shapeFragWord = _shape_mixed


def chapter(lang, key):
    text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
    return re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)


def build(lang):
    m = META[lang]
    pre = chapter(lang, '00')
    toc, body = [], []
    for key in KEYS[1:]:
        text = chapter(lang, key)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        for l in text.splitlines():
            if l.startswith('## ') and l[3:5].strip()[:1].isdigit():
                toc.append('  - ' + l[3:].strip())
        body.append(text)
    md = pre + '\n\n---\n\n## ' + m['toc'] + '\n\n' + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
