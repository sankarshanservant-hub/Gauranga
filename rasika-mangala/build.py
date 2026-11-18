"""Собирает литературный перевод «Расика-мангалы» Гопиджана-валлабхи Даса (ru/en, 4 вибхаги, 64 лахари) в MD, DOCX и PDF.
Вёрстка — ../govinda-kadacha/build.py; PDF — LibreOffice из DOCX (бенгальские слова в сносках — Noto Serif Bengali).
Рабочие пометки переводчика (страницы PDF, файлы порций, OCR) из сносок в книгу не идут — в исходниках они остаются.
Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys, glob, shutil, subprocess, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)
BENG_FONT = os.path.join(HERE, '..', 'fonts', 'NotoSerifBengali-Regular.ttf')

VIBH = {'ru': {1: 'Пурва-вибхага', 2: 'Дакшина-вибхага', 3: 'Пашчима-вибхага', 4: 'Уттара-вибхага'},
        'en': {1: 'Purva-vibhaga', 2: 'Dakshina-vibhaga', 3: 'Pashchima-vibhaga', 4: 'Uttara-vibhaga'}}
VIBH_SUB = {'ru': {1: 'Восточная часть', 2: 'Южная часть', 3: 'Западная часть', 4: 'Северная часть'},
            'en': {1: 'The Eastern Part', 2: 'The Southern Part', 3: 'The Western Part', 4: 'The Northern Part'}}
META = {
    'ru': dict(out='Rasika-Mangala-ru', title='Шри Расика-мангала', author='Гопиджана-валлабха Дас (рус. пер.)'),
    'en': dict(out='Rasika-Mangala-en', title='Sri Rasika-mangala', author='Gopijana-vallabha Dasa (Eng. tr.)'),
}
WORK = re.compile(r'pdf|RM-\d|OCR|файл|\bfiles?\b|колонтитул|running head|раскладк|layout|страниц|\bpages?\b|\bпеч\. с\.|printed p|под чертой|below the (?:line|rule)|после колофона|after the colophon|начинается (?:на|с новой)|begins (?:on|with a new)|кончается полным|ends with a complete|^Лахари \d+ — \d|^Lahari \d+ (?:—|comprises) \d', re.I)


def clean_note(t, lang):
    """Сноска без рабочих пометок; пустая строка — если от неё ничего не осталось."""
    t = re.sub(r'\s*\((?:печ\.|printed)[^()]*\)', '', t)
    t = re.sub(r'\s*\([^()]*(?:pdf|скан|scan|OCR|RM-\d|файл|files?\b|вырезк|cut-out|crop)[^()]*\)', '', t, flags=re.I)
    t = re.sub(r',?\s*(?:—\s*)?(?:(?:на|on) )?pdf \d+(?:[–-]\d+)?(?:\s*(?:вверху|внизу|at the top|at the bottom))?', '', t)
    t = re.sub(r'[,;]?\s*(?:сверено|checked) (?:по скану|against the scan)', '', t)
    out = []
    for sent in re.split(r'(?<=[.!?»”"])\s+(?=[А-ЯЁA-Z«“"*(])', t):
        if not WORK.search(sent):
            out.append(sent); continue
        parts = [p for p in re.split(r'(?<=[;,])\s+', sent) if not WORK.search(p)]
        if parts and not re.match(r'[a-zа-яё]', parts[0]):       # обрывок после вырезки — не берём
            out.append(' '.join(parts).rstrip(';,') + ('' if parts[-1].rstrip().endswith(('.', '»', ')')) else '.'))
    sents = out
    t = ' '.join(sents).strip()
    if lang == 'ru':
        t = re.sub(r'\b[Пп]о скану\b', lambda m: m.group(0)[0] + 'о изд. 1941 г.', t)
        t = re.sub(r'\b[Нн]а скане\b', lambda m: ('В' if m.group(0)[0] == 'Н' else 'в') + ' изд. 1941 г.', t)
        t = re.sub(r'\bСкан:', 'В изд. 1941 г.:', t).replace('чтение скана', 'чтение изд. 1941 г.')
    else:
        t = re.sub(r'\b(?:in|from|on|per) the scan\b', 'in the 1941 edition', t)
        t = re.sub(r'\b[Tt]he scan\b', lambda m: m.group(0)[0] + 'he 1941 edition', t)
    t = re.sub(r'\s{2,}', ' ', t).strip(' ;,')
    return t if re.search(r'\w', t) else ''


def prepare(text, key, lang):
    body, notes = (text.split('\n[^', 1) + [''])[:2]
    notes = ('[^' + notes) if notes else ''
    defs = re.findall(r'(?ms)^\[\^([^\]]+)\]:\s*(.*?)(?=^\[\^|\Z)', notes)
    kept = {}
    for lab, t in defs:
        c = clean_note(' '.join(t.split()), lang)
        if c:
            kept[lab] = c
    body = re.sub(r'\[\^([^\]]+)\]', lambda m: m.group(0) if m.group(1) in kept else '', body)
    order = {}
    for m in re.finditer(r'\[\^([^\]]+)\]', body):
        order.setdefault(m.group(1), len(order) + 1)
    for lab in kept:
        order.setdefault(lab, len(order) + 1)
    body = re.sub(r'\[\^([^\]]+)\]', lambda m: f'[^{key}-{order[m.group(1)]}]', body).replace('][^', '],[^')
    notes = '\n\n'.join(f'[^{key}-{order[l]}]: {kept[l]}' for l in sorted(kept, key=lambda l: order[l]))
    return body.rstrip() + '\n\n' + notes + '\n'


# сноски с бенгальскими словами: kb.parse считал бы их «бенгальским стихом» — помечаем бенгали на время разбора
_PUA = 0xF0000 - 0x0980
def parse(md):
    blocks = []
    for para in re.split(r'\n\s*\n', md):
        if para.lstrip().startswith('[^') and re.search('[ঀ-৿]', para):
            enc = re.sub('[ঀ-৿]', lambda m: chr(ord(m.group(0)) + _PUA), para)
            dec = lambda s: re.sub('[\U000F0000-\U000F007F]', lambda m: chr(ord(m.group(0)) - _PUA), s)
            for kind, data in kb.parse(enc):
                blocks.append((kind, [dec(x) for x in data] if isinstance(data, list) else dec(data)))
        else:
            blocks.extend(kb.parse(para))
    return blocks


def lo_pdf(docx, pdf):
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
    fonts = os.path.expanduser('~/.fonts'); os.makedirs(fonts, exist_ok=True)
    if not os.path.exists(os.path.join(fonts, os.path.basename(BENG_FONT))):
        shutil.copy(BENG_FONT, fonts); subprocess.run(['fc-cache', '-f'], check=False)
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', d, docx], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.move(os.path.join(d, os.path.basename(docx)[:-5] + '.pdf'), pdf)


def build(lang):
    m = META[lang]
    toc, body, cur = [], [], None
    files = sorted(glob.glob(os.path.join(HERE, lang, '[1-4]-[0-9][0-9].md')))
    for path in files:
        v, ll = map(int, os.path.basename(path)[:-3].split('-'))
        text = open(path, encoding='utf-8').read().strip()
        h = re.match(r'# [^.]+\.\s*(.+)', text)
        text = re.sub(r'^# ', '## ', text, count=1)   # полный заголовок «Вибхага. Лахари N. …» — по нему сайт связывает главы с базой лил
        text = prepare(text, f'{v}{ll:02d}', lang)
        if v != cur:
            cur = v
            body.append(f'# {VIBH[lang][v]}\n\n*{VIBH_SUB[lang][v]}*')
            toc.append(f'\n**{VIBH[lang][v]}**\n')
        toc.append(f'- {h.group(1).strip()}')
        body.append(text)
    pre = open(os.path.join(HERE, f'front-{lang}.md'), encoding='utf-8').read().rstrip()
    md = pre + '\n\n' + ('## Оглавление\n\n' if lang == 'ru' else '## Contents\n\n') + '\n'.join(toc) + \
        '\n\n---\n\n' + '\n\n'.join(body) + '\n'
    out = os.path.join(HERE, m['out'])
    open(out + '.md', 'w', encoding='utf-8').write(md)
    blocks = parse(md)
    kb.build_docx(blocks, out + '.docx')
    lo_pdf(out + '.docx', out + '.pdf')
    print(lang, 'ok', len(blocks), 'notes', md.count('\n[^'))


if __name__ == '__main__':
    langs = [a for a in sys.argv[1:] if a in ('ru', 'en')] or ['ru', 'en']
    for lang in langs:
        build(lang)
