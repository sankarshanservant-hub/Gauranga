"""Собирает перевод «Гаура-ганоддеша-дипики» (ru/01–03.md, en/01–03.md) в MD, DOCX и PDF.
Запуск: python3 build.py [ru|en] (по умолчанию оба; полные версии — из skt/ и skt-en/).

Использует функции разбора и вёрстки из ../govinda-kadacha/build.py.
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)
spec2 = importlib.util.spec_from_file_location('cc', os.path.join(HERE, '..', 'chaitanya-chandramrita', 'build.py'))
cc = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(cc)

OUT = 'Gaura-Ganoddesha-Dipika-ru'
PREFACE = """# Шри Гаура-ганоддеша-дипика

*«Светильник, указывающий спутников Гауры»*

*Кави Карнапура (1576)*

*Перевод с санскрита на русский*

---

## От переводчика

«Гаура-ганоддеша-дипика» — санскритское сочинение Кави Карнапуры (Парамананды Даса, Пуридаса),
младшего сына Шивананды Сена, одного из ближайших спутников Шри Чайтаньи. Книга закончена,
согласно её последней шлоке, в 1498 г. Шака (1576 г. н. э.). Она перечисляет спутников
Махапрабху, Нитьянанды и Адвайты и указывает, кем каждый из них был в играх Кришны во Врадже
(а также в Двараке, Матхуре, Айодхье и на небесах). Это главный источник гаудия-вайшнавской
традиции о «прежних обликах» спутников Чайтаньи.

**Источник.** Санскритский текст взят из издания Gaudiya Vedanta Publications (2008); его
текстовый слой в шрифтовой кодировке Kruti Dev перекодирован в Юникод. Переведён **только
санскритский текст Кави Карнапуры**; хинди-перевод и комментарий издания не использовались и
не воспроизводятся. Нумерация шлок — по этому изданию (в нём шлоки 10–22 и 194–207 объединены
в группы). Места, где текст требовал пояснений, оговорены в примечаниях.

**Сверка.** После первого перевода санскритский текст был выверен: ошибки перекодировки исправлены по метру,
грамматике и изображениям страниц издания (так же проверены места, казавшиеся неполными, — почти все они
оказались целыми в самом издании). Перевод каждой шлоки заново сверен с выверенным текстом: из 203 шлок и групп
167 переведены верно, в 26 внесены мелкие уточнения, в 10 исправлены ошибки — в том числе в отождествлениях
(Шанкара Гхош и Шанкара Пандит вместо «Шанкха», Арджуна → гопи Арджунийа, Халаюдха = Прабала, Гунамала =
Дамаянти, Васудха и Джахнава = Варуни и Ревати) и в цепочке преемственности Мадхвы (шл. 22).

---

## Оглавление

"""

PREFACE_FULL = PREFACE.replace('*Перевод с санскрита на русский*',
    '*Перевод с санскрита на русский*\n\n*Санскритский текст, транслитерация и пословный перевод*').replace('## Оглавление',
    """**Полная версия.** Для каждой шлоки даны санскритский текст деванагари (выверенный: ошибки перекодировки
из шрифта Kruti Dev исправлены по метру, грамматике и изображениям страниц издания), транслитерация IAST,
пословный перевод и перевод.

---

## Оглавление""")


PREFACE_EN = """# Sri Gaura-ganoddesha-dipika

*"The Lamp that Points Out the Associates of Gaura"*

*Kavi Karnapura (1576)*

*Translated from the Sanskrit*

---

## Translator's note

The *Gaura-ganoddesha-dipika* is a Sanskrit work by Kavi Karnapura (Paramananda Dasa, Puridasa), the
youngest son of Shivananda Sena, one of the closest associates of Sri Chaitanya. According to its last
verse, the book was completed in Shaka 1498 (1576 CE). It enumerates the associates of Mahaprabhu, of
Nityananda and of Advaita, and states who each of them was in Krishna's pastimes in Vraja (and also in
Dvaraka, Mathura, Ayodhya and the heavens). It is the principal source of the Gaudiya Vaishnava tradition
on the "former identities" of Chaitanya's associates.

**Source.** The Sanskrit text is taken from the edition of Gaudiya Vedanta Publications (2008); its text
layer, in the Kruti Dev font encoding, was converted into Unicode. **Only Kavi Karnapura's Sanskrit text
has been translated**; the edition's Hindi translation and commentary were not used and are not
reproduced. The verse numbering follows that edition (in it verses 10–22 and 194–207 are combined into
groups). Places where the text needed explanation are noted in the footnotes.

**Verification.** After the first translation the Sanskrit text was checked: conversion errors were
corrected by metre, grammar and the page images of the edition (passages that seemed incomplete were
checked in the same way, and almost all of them proved to be whole in the edition itself). The
translation of every verse was then compared afresh with the corrected text, and errors were corrected —
among them in the identifications (Shankara Ghosha and Shankara Pandita rather than "Shankha," Arjuna →
the gopi Arjuniya, Halayudha = Prabala, Gunamala = Damayanti, Vasudha and Jahnava = Varuni and Revati) and in
the chain of succession from Madhva (v. 22). The English translation was made from the Sanskrit, in
agreement with the Russian translation (same numbering and notes).

---

## Contents

"""

PREFACE_EN_FULL = PREFACE_EN.replace('*Translated from the Sanskrit*',
    '*Translated from the Sanskrit*\n\n*Sanskrit text, transliteration and word-for-word translation*').replace('## Contents',
    """**Full version.** For each verse the Sanskrit text in Devanagari is given (corrected: errors of the
conversion from the Kruti Dev font have been fixed by metre, grammar and the page images of the edition),
followed by an IAST transliteration, a word-for-word translation and the translation.

---

## Contents""")

LANGS = {
    'ru': dict(out=OUT, preface=PREFACE, preface_full=PREFACE_FULL, wfw='skt', lab=('Шлока', 'Пословно', ''),
               title='Шри Гаура-ганоддеша-дипика', author='Кави Карнапура (рус. пер.)'),
    'en': dict(out='Gaura-Ganoddesha-Dipika-en', preface=PREFACE_EN, preface_full=PREFACE_EN_FULL, wfw='skt-en',
               lab=('Verse', 'Word for word', ''), title='Sri Gaura-ganoddesha-dipika', author='Kavi Karnapura (Eng. tr.)'),
}


def load_skt(lang):
    sk = cc.load_skt(os.path.join(HERE, 'skt'))
    if lang != 'ru':
        tr = cc.load_skt(os.path.join(HERE, LANGS[lang]['wfw']))
        for k, rec in sk.items():
            rec['wfw'] = tr.get(k, {}).get('wfw', '')
    return sk


def build(out, preface, full=False, lang='ru'):
    m = LANGS[lang]
    toc, body = [], []
    for i in (1, 2, 3):
        text = open(os.path.join(HERE, lang, f'{i:02d}.md'), encoding='utf-8').read().strip()
        text = kb.re.sub(r'\[\^([^\]]+)\]', lambda m: f'[^{i:02d}-{m.group(1)}]', text)
        title = text.splitlines()[0].lstrip('# ').strip()
        sub = kb.re.search(r'^\*([^*\[].+)\*$', text, kb.re.M)
        toc.append(f'- {title} — {sub.group(1)}' if sub else f'- {title}')
        if full:
            text = cc.with_skt(text, load_skt(lang), lab=m['lab'])
        body.append(text)
    md = preface + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), m['title'], m['author'])
    print(out, 'ok', len(blocks))


if __name__ == '__main__':
    import sys
    for lang in (sys.argv[1:] or ['ru', 'en']):
        m = LANGS[lang]
        build(m['out'], m['preface'], lang=lang)
        if os.path.isdir(os.path.join(HERE, m['wfw'])) and any(f.startswith('s0') for f in os.listdir(os.path.join(HERE, m['wfw']))):
            build(m['out'] + '-full', m['preface_full'], full=True, lang=lang)
