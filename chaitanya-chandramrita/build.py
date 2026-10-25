"""Собирает перевод «Шри Чайтанья-чандрамриты» (ru/01–04.md, en/01–04.md) в MD, DOCX и PDF.
Запуск: python3 build.py [ru|en] (по умолчанию оба).

Использует функции разбора и вёрстки из ../govinda-kadacha/build.py.
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

OUT = 'Chaitanya-Chandramrita-ru'
PREFACE = """# Шри Чайтанья-чандрамрита

*«Нектар луны Чайтаньи»*

*Прабодхананда Сарасвати*

*Перевод с санскрита на русский*

---

## От переводчика

«Шри Чайтанья-чандрамрита» — санскритский сборник из ста с лишним шлок, прославляющих Шри
Чайтанью Махапрабху. Автор — Прабодхананда Сарасвати, современник Махапрабху, позднее живший
во Вриндаване (традиция считает его дядей и наставником Гопалы Бхатты Госвами). Книга
делится на двенадцать разделов: хвала, поклонение, благословение, величие преданных Гауры,
порицание непреданных, смирение, верность предмету поклонения, наставление миру,
превосходство Чайтаньи, величие его воплощения, красота и танец Гауры и, наконец, скорбь
о его уходе.

**Источник.** Санскритский текст взят из издания: «Шри Чайтанья-чандрамритам татха Шри
Сангита-мадхавам», Матхура, 1951 (изд. Бабы Кришнадаса, с хинди-переводом Госвами Кришна
Чайтаньи; скан eGangotri на archive.org). Нумерация шлок — по этому изданию (142 шлоки и
одна шлока в скобках без номера). Плохо распознанные места сверены с бенгальским изданием
с переводом Бхактисиддханты Сарасвати (там 143 шлоки: одна шлока стоит в другом месте,
поэтому начиная с 7-го раздела номера там на единицу больше). Переведён **только санскритский
текст Прабодхананды**. Хинди- и бенгальские переводы и комментарии изданий помогали
разобрать испорченные места, но не воспроизводятся. Английский перевод Б. Б. Саркара
(1935), лежащий в репозитории, содержит только английский текст без санскрита, поэтому
источником не служил.

**Сверка.** После первого перевода санскритский текст был построчно восстановлен по обоим изданиям
(с проверкой метра и опорой на пословный разбор Бхактисиддханты), и перевод каждой шлоки заново
сверен с ним. Из 143 шлок (включая шлоку в скобках) 90 оказались переведены верно, в 38 внесены
мелкие уточнения, в 15 исправлены смысловые ошибки, возникшие в основном из-за испорченного OCR.
Восстановленный санскритский текст с транслитерацией и пословным переводом дан в полной версии.

---

## Оглавление

"""

PREFACE_B = PREFACE.replace('*Перевод с санскрита на русский*',
    '*Перевод с санскрита на русский*\n\n*Санскритский текст, транслитерация, пословный перевод и «Гаудия-бхашья» Бхактисиддханты Сарасвати (перевод с бенгальского)*').replace(
    '## Оглавление', """**Устройство полной версии.** Для каждой шлоки даны: санскритский текст деванагари, восстановленный
по изданию 1951 г. и бенгальскому изданию Бхактисиддханты (при расхождении предпочтено чтение
Бхактисиддханты; это наша выверенная редакция, а не перепечатка какого-либо одного издания);
транслитерация IAST; пословный перевод — полный перевод анвайи (пословного разбора) Бхактисиддханты
в его порядке слов (в квадратных скобках — подразумеваемые слова, добавленные им); перевод.

После каждой шлоки дан перевод «Гаудия-бхашьи» Бхактисиддханты Сарасвати
(1874–1937) — его бенгальского перевода-толкования из издания Гаудия Матха (Калькутта, 1-е изд.).
Для каждой шлоки переведены заголовок-резюме и связное толкование (*anuvāda*); из пословного
разбора (*anvaya*) добавлены лишь толкования, которых нет в связном тексте. Бенгальский текст
известен по OCR-копии; нечитаемые места отмечены «[…]». Номера шлок — по изданию 1951 г.;
в бенгальском издании шлока 17 повторена ещё раз под № 75, поэтому начиная с № 75 его номера
на единицу больше.

---

## Оглавление""")


def load_bhashya(d='bss'):
    """{номер по изд. 1951: (тема, [абзацы])} из bss/b0*.md или bss-en/b0*.md (нумерация бенгальского изд.)."""
    res = {}
    for f in sorted(os.listdir(os.path.join(HERE, d))):
        if not kb.re.match(r'b0\d\.md$', f):
            continue
        text = open(os.path.join(HERE, d, f), encoding='utf-8').read()
        for part in kb.re.split(r'^### ', text, flags=kb.re.M)[1:]:
            head, _, body = part.partition('\n')
            head = head.strip()
            if not head.isdigit():
                res[head] = (None, [p.strip() for p in kb.re.split(r'\n\s*\n', body) if p.strip()])
                continue
            n = int(head)
            lines = body.strip().split('\n')
            tema = lines[0].split(':', 1)[1].strip() if lines and lines[0].startswith(('ТЕМА', 'THEME')) else None
            rest = '\n'.join(lines[1:] if tema is not None else lines)
            paras = [p.strip() for p in kb.re.split(r'\n\s*\n', rest) if p.strip()]
            key = n if n <= 74 else ('17b' if n == 75 else n - 1)
            res[key] = (tema, paras)
    return res


DROP_ANVAYA_NOTES = False


ANVAYA_NOTE = ('Из пословного толкования', 'From the word-for-word gloss')


def with_bhashya(text, bh, lang='ru'):
    out = []
    for para in kb.re.split(r'\n\s*\n', text):
        out.append(para)
        m = kb.re.match(r'^\*\*(\d+)\.\*\*', para.strip())
        if not m:
            continue
        n = int(m.group(1))
        for key in ([n, '17b'] if n == 17 else [n]):
            if key not in bh:
                continue
            tema, paras = bh[key]
            if lang == 'en':
                lab = '**Gaudiya-bhashya' + (' (Bengali ed., No. 75 — the verse repeated)' if key == '17b' else '') + '.**'
            else:
                lab = '**Гаудия-бхашья' + (' (бенг. изд., № 75 — повтор шлоки)' if key == '17b' else '') + '.**'
            out.append('>> ' + lab + (f" *{tema.replace('*', '')}*" if tema else ''))
            for p in paras:
                if DROP_ANVAYA_NOTES:
                    p = '\n'.join(l for l in p.split('\n') if not l.startswith(ANVAYA_NOTE))
                if p.strip():
                    out.append('\n'.join('>> ' + l for l in p.split('\n')))
    return '\n\n'.join(out)


def load_skt(d=None):
    """{номер: {'skt': [строки], 'wfw': str, 'var': str}} из skt/s0*.md."""
    res = {}
    d = d or os.path.join(HERE, 'skt')
    if not os.path.isdir(d):
        return res
    for f in sorted(os.listdir(d)):
        if not kb.re.match(r's0\d\.md$', f):
            continue
        for part in kb.re.split(r'^### ', open(os.path.join(d, f), encoding='utf-8').read(), flags=kb.re.M)[1:]:
            head, _, body = part.partition('\n')
            rec, cur = {'skt': []}, None
            for line in body.split('\n'):
                if m := kb.re.match(r'^(SKT|VAR|WFW|CHECK|FIX|NOTE|RU):\s*(.*)', line):
                    cur = m.group(1).lower()
                    if cur != 'skt':
                        rec[cur] = m.group(2).strip()
                elif cur == 'skt' and line.strip() and not line.startswith('```'):
                    rec['skt'].append(line.strip())
                elif cur and cur != 'skt' and line.strip():
                    rec[cur] += ' ' + line.strip()
            res[head.strip()] = rec
    return res


def load_anvaya(d='bss'):
    """{номер: {'anvaya': str, 'diff': [строки]}} из bss/a0*.md или bss-en/a0*.md (основная нумерация)."""
    res = {}
    d = os.path.join(HERE, d)
    for f in sorted(os.listdir(d)):
        if not kb.re.match(r'a0\d\.md$', f):
            continue
        for part in kb.re.split(r'^### ', open(os.path.join(d, f), encoding='utf-8').read(), flags=kb.re.M)[1:]:
            head, _, body = part.partition('\n')
            rec, cur = {'anvaya': '', 'diff': []}, None
            for line in body.split('\n'):
                if m := kb.re.match(r'^(ANVAYA|DIFF):\s*(.*)', line):
                    cur = m.group(1).lower()
                    if cur == 'anvaya':
                        rec['anvaya'] = m.group(2).strip()
                    elif m.group(2).strip() and m.group(2).strip().lower() not in ('нет', 'нет.'):
                        rec['diff'].append(m.group(2).strip())
                elif cur == 'anvaya' and line.strip():
                    rec['anvaya'] += ' ' + line.strip()
                elif cur == 'diff' and line.strip().startswith('-'):
                    rec['diff'].append(line.strip()[1:].strip())
            res[head.strip()] = rec
    return res


def iast(lines):
    from indic_transliteration import sanscript
    return [sanscript.transliterate(l, 'devanagari', 'iast').replace('ṃ', 'ṁ') for l in lines]


def with_skt(text, sk, an=None, lab=('Шлока', 'Пословно', 'Пословно (анвайя Бхактисиддханты)')):
    an = an or {}
    out = []
    for para in kb.re.split(r'\n\s*\n', text):
        m = kb.re.match(r'^\*\*([\d–-]+)\.\*\*', para.strip())
        keys = []
        if m:
            keys = [m.group(1)]
        elif para.strip().startswith(('(Поклоняюсь Шри Кришне Чайтанье', '(I bow to Sri Krishna Chaitanya')):
            keys = ['13a']
        for k in keys:
            rec = sk.get(k)
            if not rec or not rec['skt']:
                continue
            out.append(f'### {lab[0]} {k}')
            out.append('\n'.join(rec['skt']))
            out.append('\n'.join(f'*{l}*' for l in iast(rec['skt'])))
            if an.get(k, {}).get('anvaya'):
                out.append(f'*{lab[2]}:* ' + an[k]['anvaya'])
            elif rec.get('wfw'):
                out.append(f'*{lab[1]}:* ' + rec['wfw'])
        out.append(para)
    return '\n\n'.join(out)


def build(out, preface, bh=None, sk=None, an=None, lang='ru'):
    m = LANGS[lang]
    toc, body = [], []
    intro = m['intro']
    files = [intro] if bh is not None and os.path.exists(os.path.join(HERE, lang, intro + '.md')) else []
    files += [f'{i:02d}' for i in (1, 2, 3, 4)]
    for key in files:
        text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
        text = kb.re.sub(r'\[\^([^\]]+)\]', lambda m: f'[^{key[:2]}-{m.group(1)}]', text)
        title = text.splitlines()[0].lstrip('# ').strip()
        sub = kb.re.search(r'^\*([^*\[].+)\*$', text, kb.re.M)
        toc.append(f'- {title} — {sub.group(1)}' if sub and key != intro else f'- {title}')
        if bh is not None:
            text = with_bhashya(text, bh, lang)
            if sk:
                text = with_skt(text, sk, an, lab=m['lab'])
            if key == '04' and 'END' in bh:
                text = text.split('\n\n[^')[0] + '\n\n' + '\n\n'.join('>> ' + p for p in bh['END'][1]) + \
                    ('\n\n[^' + text.split('\n\n[^', 1)[1] if '\n\n[^' in text else '')
        body.append(text)
    md = preface + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), m['title'], m['author'])
    print(out, 'ok', len(blocks))


def diff_report(an):
    """Сводка расхождений нашего перевода с толкованием Бхактисиддханты → bss/RASHOZHDENIYA.md."""
    if not an:
        return
    keys = sorted(an, key=lambda k: int(kb.re.match(r'\d+', k).group()))
    rows = [(k, d) for k in keys for d in an[k]['diff']]
    nsense = len({k for k, d in rows if '[смысл]' in d})
    lines = ['# Расхождения перевода с толкованием Бхактисиддханты', '',
             'Сравнение русского перевода (ru/01–04.md) с анвайей и анувада «Гаудия-бхашьи». '
             '[смысл] — меняет смысл, [оттенок] — нюанс. Расхождения [смысл] в переводе исправлены по Бхактисиддханте (17 шлок); «наш перевод» ниже — прежняя редакция.', '',
             f'Всего замечаний: {len(rows)}; шлок с расхождениями по смыслу: {nsense}.', '',
             '**Шлоки с расхождениями по смыслу:** ' + ', '.join(k for k in keys if any('[смысл]' in d for d in an[k]['diff'])) + '.', '']
    for k in keys:
        if an[k]['diff']:
            lines.append(f'## Шлока {k}')
            lines += [f'- {d}' for d in an[k]['diff']]
            lines.append('')
    open(os.path.join(HERE, 'bss', 'RASHOZHDENIYA.md'), 'w', encoding='utf-8').write('\n'.join(lines))
    blocks = kb.parse('\n'.join(lines))
    kb.build_pdf(blocks, os.path.join(HERE, 'bss', 'RASHOZHDENIYA.pdf'), 'Расхождения с Бхактисиддхантой', '')
    kb.build_docx(blocks, os.path.join(HERE, 'bss', 'RASHOZHDENIYA.docx'))
    print('diff report:', len(rows), 'items,', nsense, 'verses [смысл]')


PREFACE_EN = """# Sri Chaitanya-chandramrita

*"The Nectar of the Moon Chaitanya"*

*Prabodhananda Sarasvati*

*Translated from the Sanskrit*

---

## Translator's note

The *Sri Chaitanya-chandramrita* is a Sanskrit collection of a little over a hundred verses glorifying Sri
Chaitanya Mahaprabhu. Its author is Prabodhananda Sarasvati, a contemporary of Mahaprabhu who later lived in
Vrindavana (tradition regards him as the uncle and teacher of Gopala Bhatta Gosvami). The book is divided
into twelve sections: praise, obeisance, benediction, the glory of Gaura's devotees, censure of the
non-devotees, humility, fidelity to the object of worship, instruction to the world, the supremacy of
Chaitanya, the glory of His descent, the beauty and dance of Gaura, and finally lament over His
disappearance.

**Source.** The Sanskrit text is taken from the edition *Sri Chaitanya-chandramritam tatha Sri
Sangita-madhavam*, Mathura, 1951 (ed. Baba Krishnadasa, with a Hindi translation by Gosvami Krishna
Chaitanya; eGangotri scan at archive.org). The verse numbering follows that edition (142 verses and one
verse in brackets without a number). Poorly recognized passages have been checked against the Bengali
edition with the translation of Bhaktisiddhanta Sarasvati (which has 143 verses: one verse stands in a
different place, so from the seventh section on its numbers are one higher). **Only Prabodhananda's
Sanskrit text has been translated.** The Hindi and Bengali translations and commentaries of the editions
helped to make out corrupt passages but are not reproduced.

**Verification.** After the first translation the Sanskrit text was restored line by line from both
editions (checking the metre and relying on Bhaktisiddhanta's word-for-word analysis), and the translation
of every verse was compared afresh with it; places where the translation departed from Bhaktisiddhanta's
interpretation in meaning were corrected according to him. The English translation was made from the
Sanskrit, in agreement with the Russian translation (same numbering and notes).

---

## Contents

"""

PREFACE_EN_FULL = PREFACE_EN.replace('*Translated from the Sanskrit*',
    '*Translated from the Sanskrit*\n\n*Sanskrit text, transliteration, word-for-word translation and the "Gaudiya-bhashya" of Bhaktisiddhanta Sarasvati (translated from the Bengali)*').replace('## Contents',
    """**Full version.** For each verse are given: the Sanskrit text in Devanagari, restored from the 1951 edition
and Bhaktisiddhanta's Bengali edition (where they differ, Bhaktisiddhanta's reading is preferred; this is our
own corrected text, not a reprint of any single edition); an IAST transliteration; a word-for-word
translation — the complete translation of Bhaktisiddhanta's *anvaya* (word-for-word analysis) in his word
order (words he supplies as implied are in square brackets); and the translation.

After each verse follows a translation of the "Gaudiya-bhashya" of Bhaktisiddhanta Sarasvati (1874–1937) —
his Bengali translation and commentary from the Gaudiya Math edition (Calcutta, 1st ed.); his preface to that
edition is given at the beginning of the book. For each verse the summary heading and the continuous
commentary (*anuvada*) are translated; glosses from the word-for-word analysis that are not in the continuous
text appear in the *anvaya* above. The Bengali text is known from an OCR copy; illegible places are marked
"[…]". The verse numbers follow the 1951 edition; in the Bengali edition verse 17 is repeated once more as
No. 75, so from No. 75 on its numbers are one higher. The commentary and the *anvaya* were translated into
English from the Bengali, in agreement with the Russian translation.

---

## Contents""")

LANGS = {
    'ru': dict(intro='00-vvedenie', lab=('Шлока', 'Пословно', 'Пословно (анвайя Бхактисиддханты)'),
               title='Шри Чайтанья-чандрамрита', author='Прабодхананда Сарасвати (рус. пер.)'),
    'en': dict(intro='00-introduction', lab=('Verse', 'Word for word', "Word for word (Bhaktisiddhanta's anvaya)"),
               title='Sri Chaitanya-chandramrita', author='Prabodhananda Sarasvati (Eng. tr.)'),
}


def load_skt_en():
    sk = load_skt()
    tr = load_skt(os.path.join(HERE, 'skt-en'))
    for k, rec in sk.items():
        rec['wfw'] = tr.get(k, {}).get('wfw', '')
    return sk


if __name__ == '__main__':
    import sys
    langs = sys.argv[1:] or ['ru', 'en']
    if 'ru' in langs:
        build(OUT, PREFACE)
        if os.path.isdir(os.path.join(HERE, 'bss')):
            an = load_anvaya()
            DROP_ANVAYA_NOTES = bool(an)
            build(OUT + '-full', PREFACE_B, load_bhashya(), load_skt(), an)
            diff_report(an)
    if 'en' in langs:
        build('Chaitanya-Chandramrita-en', PREFACE_EN, lang='en')
        if os.path.isdir(os.path.join(HERE, 'skt-en')):
            bh_en = load_bhashya('bss-en') if os.path.isdir(os.path.join(HERE, 'bss-en')) else {}
            an_en = load_anvaya('bss-en') if bh_en else None
            DROP_ANVAYA_NOTES = bool(an_en)
            build('Chaitanya-Chandramrita-en-full', PREFACE_EN_FULL, bh_en, load_skt_en(), an_en, lang='en')
