"""Собирает перевод «Чайтанья-мангалы» Лочана Даса (ru|en/NN.md) в MD, DOCX и PDF.
Использует разбор и вёрстку из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en]."""
import glob, importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Lochana-Chaitanya-Mangala-ru', title='Шри Чайтанья-мангала', author='Лочан Дас (рус. пер.)',
               preface="""# Шри Чайтанья-мангала

*Лочан Дас Тхакур*

*По изданию Шрилы Бхактисиддханты Сарасвати (Шри Чайтанья Матх, 1922)*

*Перевод с бенгальского на русский*

---

## От переводчика

«Шри Чайтанья-мангала» — бенгальская песенная поэма Лочана Даса, ученика Нарахари Саркара Тхакура из Шрикханды,
написанная в 1560-е годы. Она следует санскритской «Кадаче» Мурари Гупты, дополняя её преданиями школы Шрикханды,
и делится на четыре кханды: Сутра, Ади, Мадхья и Шеша. Перевод сделан по изданию Шрилы Бхактисиддханты Сарасвати
(1922); испорченные места текста восстановлены по изданию 1983 г. (Вриндаван) и 1903 г. Нумерация двустиший — как в
издании Бхактисиддханты. Его прозаические изложения содержания разделов переведены и даны курсивом в начале разделов.
Текст Лочана Даса передан без поправок; где он расходится с позднейшим гаудия-вайшнавским богословием, это оговорено
в примечаниях.

---

## Оглавление

"""),
    'en': dict(out='Lochana-Chaitanya-Mangala-en', title='Sri Chaitanya-mangala', author='Lochana Dasa (Eng. tr.)',
               preface="""# Sri Chaitanya-mangala

*Lochana Dasa Thakura*

*Following the edition of Srila Bhaktisiddhanta Sarasvati (Sri Chaitanya Math, 1922)*

*Translated from the Bengali*

---

## Translator's note

*Sri Chaitanya-mangala* is a Bengali song-poem by Lochana Dasa, a disciple of Narahari Sarakara Thakura of
Shrikhanda, composed in the 1560s. It follows Murari Gupta's Sanskrit *Kadacha*, enlarging it with the traditions of
the Shrikhanda school, and is divided into four khandas: Sutra, Adi, Madhya and Shesha. The translation follows the
edition of Srila Bhaktisiddhanta Sarasvati (1922); corrupt places have been restored from the editions of 1983
(Vrindavana) and 1903. The couplets are numbered as in Bhaktisiddhanta's edition. His prose summaries of the sections
are translated and given in italics at the head of the sections. Lochana Dasa's text is rendered without correction;
where it differs from later Gaudiya Vaishnava theology, this is noted in the footnotes.

---

## Contents

"""),
}


def bn2lat(s):
    from indic_transliteration import sanscript
    s = s.replace('\u09df', '\u09af\u09bc').replace('\u09dc', '\u09a1\u09bc').replace('\u09dd', '\u09a2\u09bc').replace('ৎ', 'ত্')
    d = ''.join(chr(ord(c) - 0x80) if '\u0980' <= c <= '\u09ff' else c for c in s)
    return sanscript.transliterate(d, 'devanagari', 'iast').replace('r̤', 'ṛ').replace('||', '॥').replace('|', '।')


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
    out, i = [], 0
    for para in re.split(r'\n\s*\n', text):
        m = re.match(r'^\*\*(\d+[a-zа-я]?)\.\*\*', para.strip())
        if m and i < len(recs) and recs[i]['n'] == m.group(1):
            r = recs[i]; i += 1
            if r['bn']:
                out.append('\n'.join(r['bn']))
                out.append('\n'.join(f'*{bn2lat(l)}*' for l in r['bn']))
                w = r.get('wfw-' + lang)
                if w: out.append(('*Пословно:* ' if lang == 'ru' else '*Word for word:* ') + w)
        out.append(para)
    return '\n\n'.join(out)


def build(lang, full=False):
    m = META[lang]
    toc, body = [], []
    for path in sorted(glob.glob(os.path.join(HERE, lang, '[0-9][0-9].md'))):
        key = os.path.basename(path)[:2]
        text = open(path, encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        if full:
            text = with_bn(text, load_bn(key), lang)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    pre = m['preface']
    out = m['out']
    if full:
        out += '-full'
        pre = pre.replace('---', ('*Бенгальский текст, транслитерация, пословный перевод и перевод*' if lang == 'ru' else '*Bengali text, transliteration, word-for-word and translation*') + '\n\n---', 1)
    md = pre + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), m['title'], m['author'])
    print(out, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
        build(lang, full=True)
