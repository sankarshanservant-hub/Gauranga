"""Собирает книгу пад современников Шри Чайтаньи (ru|en/00–34.md, bn/01–34.md) в MD, DOCX и PDF.

Обычная версия — перевод со сносками; полная (-full) — перед каждым двустишием бенгальский оригинал, транслитерация
(IAST: ব = b, ব-фала после согласной — v; ঁ = m̐; ড় = ṛ; ং = ṃ; য় = y), пословный перевод, в RU — разночтения (VAR), затем перевод.
Движок вёрстки — ../govinda-kadacha/build.py (свой разбор блоков и встроенный бенгальский шрифт в PDF).
Запуск: python3 build.py [ru|en] (по умолчанию оба, обе версии).
"""
import glob, importlib.util, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

PARTS = {
    'ru': {1: 'Часть I. Пады современников', 17: 'Часть II. Приложение: пады с подписью «Нарахари» из «Гаура-пада-тарангини»',
           27: 'Часть III. Нагари-пады'},
    'en': {1: 'Part I. Padas of the Contemporaries',
           17: 'Part II. Appendix: Padas Signed "Narahari" from the Gaura-pada-tarangini', 27: 'Part III. Nagari Padas'},
}
META = {
    'ru': dict(out='Padas-ru', title='Пады современников Шри Чайтаньи', author='Пер. с бенгальского', chap='Глава',
               toc='Оглавление', full='*Бенгальский текст, транслитерация, пословный перевод, разночтения и перевод*',
               wfw='*Пословно:* ', var='Разночтения: ',
               head="""# Пады современников Шри Чайтаньи

*Песни спутников Шри Чайтаньи Махапрабху о Его лилах*

*Перевод с бенгальского на русский*
"""),
    'en': dict(out='Padas-en', title="Padas of Sri Chaitanya's Contemporaries", author='Translated from the Bengali',
               chap='Chapter', toc='Contents', full='*Bengali text, transliteration, word-for-word and translation*',
               wfw='*Word for word:* ', var=None,
               head="""# Padas of Sri Chaitanya's Contemporaries

*Songs of Sri Chaitanya Mahaprabhu's companions about His lilas*

*Translated from the Bengali*
"""),
}

BENG = re.compile(r'[ঀ-৿]')


def bn2lat(s):
    """Бенгальское письмо → IAST по правилу книги (как в EN-сносках)."""
    from indic_transliteration import sanscript
    s = s.replace('‌', '').replace('‍', '')
    s = s.replace('য়', 'য়').replace('ড়', 'ড়').replace('ঢ়', 'ঢ়')
    s = s.replace('ৎ', 'ত্‌')
    d = ''.join(chr(ord(c) - 0x80) if 'ঀ' <= c <= '৿' else c for c in s)
    d = re.sub(r'(?<=[\u0915-\u0939\u093c])्ब', '्व', d)   # ব = b; ব-фала после согласной — v (স্ব sv, দ্ব dv)
    d = d.replace('म्व', 'म्ब').replace('ब्व', 'ब्ब')      # ম্ব mb, ব্ব bb
    d = d.replace('ँ', '')                    # ঁ → m̐
    o = sanscript.transliterate(d, 'devanagari', 'iast')
    o = o.replace('', 'm̐').replace('‌', '').replace('r̤', 'ṛ').replace('ẏ', 'y')
    return unicodedata.normalize('NFC', o.replace('॥', '||').replace('।', '|'))


def load_bn(key):
    f = os.path.join(HERE, 'bn', key + '.md')
    out = []
    if not os.path.exists(f):
        return out
    for part in re.split(r'^### ', open(f, encoding='utf-8').read(), flags=re.M)[1:]:
        head, _, body = part.partition('\n')
        rec, cur = {'n': head.strip(), 'bn': []}, None
        for line in body.split('\n'):
            if m := re.match(r'^(BN|VAR|WFW-RU|WFW-EN|NOTE):\s*(.*)', line):
                cur = m.group(1).lower()
                if cur != 'bn': rec[cur] = m.group(2).strip()
            elif cur == 'bn' and line.strip() and not line.startswith('#'):
                rec['bn'].append(line.strip())
            elif cur and cur != 'bn' and line.strip() and not line.startswith('#'):
                rec[cur] += ' ' + line.strip()
        out.append(rec)
    return out


def with_bn(text, recs, lang):
    m_ = META[lang]
    out, i = [], 0
    for para in re.split(r'\n\s*\n', text):
        m = re.match(r'^\*\*(\d+\.\d+[a-zа-я]?)\.\*\*', para.strip())
        if m:
            if i >= len(recs) or recs[i]['n'] != m.group(1):
                raise SystemExit(f'bn не совпадает с переводом: {m.group(1)} / {recs[i]["n"] if i < len(recs) else "—"}')
            r = recs[i]; i += 1
            if r['bn']:
                out.append('\n'.join(r['bn']))
                out.append('\n'.join(f'*{bn2lat(l)}*' for l in r['bn']))
                w = r.get('wfw-' + lang)
                if w: out.append(m_['wfw'] + w)
                if m_['var'] and r.get('var'):
                    out.append('>> ' + m_['var'] + r['var'])
        out.append(para)
    if i != len(recs):
        raise SystemExit(f'не все записи bn использованы: {i} из {len(recs)}')
    return '\n\n'.join(out)


def parse(md):
    """Как kb.parse, но: бенгальский блок — только строки оригинала (бенгальское письмо преобладает),
    сноски и абзацы с бенгальскими словами остаются текстом; метки двустиший — N.M."""
    blocks = []
    for para in re.split(r'\n\s*\n', md):
        lines = [l.rstrip() for l in para.strip('\n').splitlines() if l.strip()]
        if not lines:
            continue
        first = lines[0]
        letters = re.findall(r'[^\W\d_]', para)
        beng_share = len(BENG.findall(para)) / max(1, len(letters))
        if m := re.match(r'^(#{1,4}) (.+)', first):
            blocks.append(('h%d' % min(len(m.group(1)), 3), m.group(2)))
            if len(lines) > 1:
                blocks.extend(parse('\n'.join(lines[1:])))
        elif first.strip() == '---':
            blocks.append(('hr', ''))
        elif re.match(r'^\[\^[^\]]+\]:', first):
            notes, cur = [], None
            for l in lines:
                if mm := re.match(r'^\[\^([^\]]+)\]:\s*(.*)', l):
                    cur = [mm.group(1).split('-', 1)[-1], mm.group(2)]
                    notes.append(cur)
                elif cur:
                    cur[1] += ' ' + l.strip()
            blocks.extend(('note', n) for n in notes)
        elif all(l.startswith('>>') for l in lines):
            blocks.append(('comment', [l.lstrip('>').strip() for l in lines]))
        elif all(l.startswith('>') for l in lines):
            blocks.append(('quote', [l.lstrip('>').strip() for l in lines]))
        elif beng_share > 0.6 and not first.startswith('**'):
            blocks.append(('beng', lines))
        elif re.match(r'^\s*[-*] |^\d+\. ', first) and all(re.match(r'^\s*[-*] |^\d+\. |^\s+\S', l) for l in lines):
            items = []
            for l in lines:                                   # пункты списка с продолжением на следующих строках
                if re.match(r'^\s*[-*] |^\d+\. ', l):
                    items.append(re.sub(r'^\s*[-*] ', '', l))
                else:
                    items[-1] += ' ' + l.strip()
            blocks.extend(('bullet', x) for x in items)
        elif re.match(r'^\*\*\d+\.\d+[a-zа-я]?\.\*\*', first):
            blocks.append(('verse', lines))
        elif len(lines) > 1 and all(re.match(r'^\*[^*].*\*$', l) for l in lines):
            blocks.append(('p', lines))                 # строки транслитерации — построчно
        else:
            blocks.append(('p', [' '.join(l.strip() for l in lines)]))   # проза: жёсткие переносы исходника снимаются
    return blocks


_inline = kb.inline


def inline(text, html=True):
    s = _inline(text, html)
    if html:   # бенгальские слова внутри строки — бенгальским шрифтом (в Liberation Serif их нет)
        s = re.sub(r'([ঀ-৿](?:[ঀ-৿‌‍ ]*[ঀ-৿])?)',
                   r'<font name="Beng">\1</font>', s)
    return s


kb.inline = inline


def docx_runs(par, text, size=None):
    """Как kb.docx_runs, но бенгальские вставки внутри строки — отдельными прогонами со шрифтом Noto Serif Bengali."""
    from docx.shared import Pt
    from docx.oxml.ns import qn
    for part in re.split(r'(<b>.*?</b>|<i>.*?</i>|<super>.*?</super>)', inline(text, html=False)):
        if not part:
            continue
        m = re.match(r'<(b|i|super)>(.*)</\1>', part)
        body = m.group(2) if m else part
        for seg in re.split(r'([\u0980-\u09ff](?:[\u0980-\u09ff\u200c\u200d ]*[\u0980-\u09ff])?)', body):
            if not seg:
                continue
            r = par.add_run(seg)
            if m:
                r.bold = m.group(1) == 'b'
                r.italic = m.group(1) == 'i'
                r.font.superscript = m.group(1) == 'super'
            if size:
                r.font.size = Pt(size)
            if BENG.search(seg):
                fonts = r._element.get_or_add_rPr().get_or_add_rFonts()
                for k in ('w:ascii', 'w:hAnsi', 'w:cs'):
                    fonts.set(qn(k), 'Noto Serif Bengali')


kb.docx_runs = docx_runs

from reportlab.lib.styles import ParagraphStyle
ParagraphStyle.defaults['shaping'] = 1   # сборка бенгальских лигатур и огласовок (uharfbuzz) во всех абзацах

# reportlab формирует «слово» целиком шрифтом первого фрагмента: «গোরা или গোরা…» дали бы квадраты.
# Режем слово по сменам шрифта и формируем каждую часть своим шрифтом.
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
    res = _tt.makeShapedFragWord(w)([width] + out)
    return res


_rp.shapeFragWord = _shape_mixed


def chapter(lang, key):
    text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
    return text


def build(lang, full=False):
    m = META[lang]
    keys = sorted(os.path.basename(p)[:2] for p in glob.glob(os.path.join(HERE, lang, '[0-9][0-9].md')))
    toc, body = [], []
    pre = chapter(lang, '00')
    toc.append('- ' + pre.splitlines()[0].lstrip('# ').strip())
    body.append(pre)
    for key in keys:
        if key == '00':
            continue
        n = int(key)
        if n in PARTS[lang]:
            toc.append(f'- **{PARTS[lang][n]}**')
            body.append(f'# {PARTS[lang][n]}')
        text = chapter(lang, key)
        title = text.splitlines()[0].lstrip('# ').strip()
        text = f'# {m["chap"]} {n}. {title}' + text[text.index('\n'):]
        if full:
            text = with_bn(text, load_bn(key), lang)
        toc.append(f'  - {m["chap"]} {n}. {title}')
        body.append(text)
    head = m['head'] + ('\n' + m['full'] + '\n' if full else '')
    md = head + '\n---\n\n## ' + m['toc'] + '\n\n' + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    out = m['out'] + ('-full' if full else '')
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), m['title'], m['author'])
    print(out, 'ok', len(blocks), 'блоков')


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
        build(lang, full=True)
