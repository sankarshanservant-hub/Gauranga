"""Собирает «Шри Кришна-чайтанья-чаритамриту» Мурари Гупты (ru|en/P.SS.md + skt/P.SS.md) в MD, DOCX и PDF.

Для каждого языка — две версии: только перевод и полная (санскрит, IAST, пословный перевод, перевод).
Использует разбор и вёрстку из ../govinda-kadacha/build.py.
"""
import importlib.util, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

PRAKRAMA = {
    'ru': {1: 'Пракрама первая', 2: 'Пракрама вторая', 3: 'Пракрама третья', 4: 'Пракрама четвёртая'},
    'en': {1: 'Prakrama One', 2: 'Prakrama Two', 3: 'Prakrama Three', 4: 'Prakrama Four'},
}
L = {
    'ru': dict(title='Шри Кришна-чайтанья-чаритамрита', sub='*«Нектар деяний Шри Кришны Чайтаньи» («Кадача Мурари Гупты»)*',
               author='*Мурари Гупта*', tr='*Перевод с санскрита на русский*',
               full='*Санскритский текст, транслитерация, пословный перевод и перевод*',
               verse='Шлока', wfw='Пословно', toc='Оглавление', pdfauth='Мурари Гупта (рус. пер.)'),
    'en': dict(title='Sri Krishna-chaitanya-charitamrita', sub="*\"The Nectar of Sri Krishna Chaitanya's Acts\" (Murari Gupta's Kadacha)*",
               author='*Murari Gupta*', tr='*Translated from the Sanskrit into English*',
               full='*Sanskrit text, transliteration, word-for-word and translation*',
               verse='Verse', wfw='Word for word', toc='Contents', pdfauth='Murari Gupta (Eng. tr.)'),
}
INTRO = {
    'ru': """## От переводчика

«Шри Кришна-чайтанья-чаритамрита» — санскритская поэма Мурари Гупты, земляка и спутника Шри Чайтаньи, свидетеля
его жизни в Навадвипе; в традиции её зовут «Кадачей» («записками») Мурари Гупты. Это самое раннее жизнеописание
Махапрабху; на него опирались Вриндаван Дас, Кавикарнапура, Лочана Дас и Кришнадас Кавираджа. Поэма разделена на
четыре пракрамы (части) и 78 сарг (песней).

**Источник.** Санскритский текст восстановлен по трём распознанным (OCR) копиям: двум сканам издания Харидаса Шастри
(Вриндаван) и изданию Харидаса Даса (Калькутта, 1945, бенгальское письмо); чтения выверены по метру и грамматике.
Нумерация шлок — по изданию Харидаса Шастри. Переведён только санскритский текст Мурари Гупты; переводы и
комментарии изданий не использовались. Толкование — в духе Шрилы Бхактисиддханты Сарасвати.
""",
    'en': """## Translator's Note

*Sri Krishna-chaitanya-charitamrita* is the Sanskrit poem of Murari Gupta, a fellow-countryman and companion of
Sri Chaitanya and an eyewitness of his life in Navadvipa; tradition calls it Murari Gupta's *Kadacha* ("notes"). It
is the earliest biography of Mahaprabhu, drawn upon by Vrindavana Dasa, Kavikarnapura, Lochana Dasa and Krishnadasa
Kaviraja. The poem is divided into four *prakramas* (parts) and 78 *sargas* (cantos).

**Source.** The Sanskrit text has been reconstructed from three OCR copies: two scans of the edition of Haridasa
Shastri (Vrindavana) and the edition of Haridasa Dasa (Calcutta, 1945, Bengali script); readings were checked against
metre and grammar. Verse numbering follows Haridasa Shastri's edition. Only Murari Gupta's Sanskrit text has been
translated; the translations and commentaries of the editions were not used. Interpretation follows Srila
Bhaktisiddhanta Sarasvati.
""",
}


def iast(lines):
    from indic_transliteration import sanscript
    return [sanscript.transliterate(l, 'devanagari', 'iast').replace('ṃ', 'ṁ') for l in lines]


def load_skt(s, lang):
    f = os.path.join(HERE, 'skt', s + '.md')
    res = {}
    if not os.path.exists(f):
        return res
    for part in re.split(r'^### ', open(f, encoding='utf-8').read(), flags=re.M)[1:]:
        head, _, body = part.partition('\n')
        rec, cur = {'skt': []}, None
        for line in body.split('\n'):
            if m := re.match(r'^(SKT|VAR|WFW-RU|WFW-EN|NOTE):\s*(.*)', line):
                cur = m.group(1).lower()
                if cur != 'skt':
                    rec[cur] = m.group(2).strip()
            elif cur == 'skt' and line.strip() and not line.startswith('```'):
                rec['skt'].append(line.strip())
            elif cur and cur != 'skt' and line.strip():
                rec[cur] += ' ' + line.strip()
        res[head.strip()] = rec
    return res


def with_skt(text, sk, lang):
    out = []
    for para in re.split(r'\n\s*\n', text):
        m = re.match(r'^\*\*([\d–-]+)\.\*\*', para.strip())
        rec = sk.get(m.group(1)) if m else None
        if rec and rec['skt']:
            out.append(f"### {L[lang]['verse']} {m.group(1)}")
            out.append('\n'.join(rec['skt']))
            out.append('\n'.join(f'*{l}*' for l in iast(rec['skt'])))
            w = rec.get('wfw-' + lang)
            if w:
                out.append(f"*{L[lang]['wfw']}:* " + w)
        out.append(para)
    return '\n\n'.join(out)


def sargas():
    return sorted(f[:-3] for f in os.listdir(os.path.join(HERE, 'ru')) if re.match(r'\d\.\d\d\.md$', f)
                  and os.path.exists(os.path.join(HERE, 'en', f)))


def build(lang, full=False):
    l = L[lang]
    pre = [f"# {l['title']}", l['sub'], l['author'], l['tr']] + ([l['full']] if full else [])
    toc, body, cur = [], [], None
    for s in sargas():
        p = int(s[0])
        text = open(os.path.join(HERE, lang, s + '.md'), encoding='utf-8').read().strip()
        pre_id = s.replace('.', '')
        text = re.sub(r'\[\^([^\]]+)\]', lambda m: f'[^{pre_id}-{m.group(1)}]', text)
        lines = text.split('\n')
        title = lines[0].lstrip('# ').strip()
        lines[0] = '## ' + title
        text = '\n'.join(lines)
        if p != cur:
            cur = p
            body.append(f"# {PRAKRAMA[lang][p]}")
            toc.append(f"- **{PRAKRAMA[lang][p]}**")
        toc.append(f'  - {title}')
        if full:
            text = with_skt(text, load_skt(s, lang), lang)
        body.append(text)
    md = ('\n\n'.join(pre) + '\n\n---\n\n' + INTRO[lang] + '\n---\n\n' + f"## {l['toc']}\n\n" + '\n'.join(toc)
          + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n')
    out = f"Murari-Gupta-Kadacha-{lang}" + ('-full' if full else '')
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), l['title'], l['pdfauth'])
    print(out, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in ('ru', 'en'):
        build(lang)
        build(lang, full=True)
