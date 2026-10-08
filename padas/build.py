"""Собирает книгу пад современников Шри Чайтаньи (ru|en/00–34.md, bn/01–34.md) в MD, DOCX и PDF.

Обычная версия — перевод со сносками; полная (-full) — перед каждым двустишием бенгальский оригинал, транслитерация
(IAST: ব = v, кроме ম্ব/ব্দ/ব্ধ/ব্জ; ঁ = m̐; ড় = ṛ; য় = y), пословный перевод, в RU — разночтения (VAR), затем перевод.
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
           17: 'Part II. Appendix: Padas Signed "Narahari" from the *Gaura-pada-tarangini*', 27: 'Part III. Nagari Padas'},
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
    d = re.sub(r'(?<!म्)ब(?!्[दधजझ])', 'व', d)          # ব = v, кроме ম্ব, ব্দ, ব্ধ, ব্জ
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
        elif all(re.match(r'^\s*[-*] ', l) for l in lines):
            blocks.extend(('bullet', re.sub(r'^\s*[-*] ', '', l)) for l in lines)
        elif re.match(r'^\*\*\d+\.\d+[a-zа-я]?\.\*\*', first):
            blocks.append(('verse', lines))
        elif re.match(r'^\d+\. ', first) and all(re.match(r'^\d+\. ', l) for l in lines):
            blocks.extend(('bullet', l) for l in lines)
        else:
            blocks.append(('p', lines))
    return blocks


_inline = kb.inline


def inline(text, html=True):
    s = _inline(text, html)
    if html:   # бенгальские слова внутри строки — бенгальским шрифтом (в Liberation Serif их нет)
        s = re.sub(r'([ঀ-৿](?:[ঀ-৿‌‍ ]*[ঀ-৿])?)',
                   r'<font name="Beng">\1</font>', s)
    return s


kb.inline = inline

from reportlab.lib.styles import ParagraphStyle
ParagraphStyle.defaults['shaping'] = 1   # сборка бенгальских лигатур и огласовок (uharfbuzz) во всех абзацах


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
