"""Собирает перевод «Нитьянанда-вамша-вистары» (ru/en, главы 01–10) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Nityananda-Vamsha-Vistara-ru', title='Шри Нитьянанда-вамша-вистара',
               author='Вриндаван Дас (приписывается; рус. пер.)', preface="""# Шри Нитьянанда-вамша-вистара

*«Распространение рода Нитьянанды»*

*Поэма, приписываемая Вриндавану Дасу Тхакуру*

*Перевод с бенгальского на русский*

---

## От переводчика

«Нитьянанда-вамша-вистара» — бенгальская поэма о семье Нитьянанды Прабху: его женитьбе на Васудхе
и Джахнаве по велению Махапрабху, рождении Вирачандры (Вирабхадры), путешествиях Джахнавы во Вриндаван,
проповеди Вирачандры в Бенгалии и его паломничестве во Вриндаван. Поэма приписывается Вриндавану Дасу
Тхакуру, автору «Чайтанья-бхагаваты»; большинство исследователей считают эту атрибуцию сомнительной
и относят поэму к более позднему времени (на это указывают, в частности, хронологические несообразности —
встречи Вирачандры с лицами, жившими раньше). Перевод сделан для ознакомления с текстом, без суждения
о его подлинности.

**Источник.** Издание Кишори Даса Бабаджи (Халисахар, 2-е изд., 1991), известное по двум независимым
OCR-копиям на archive.org; копии разобраны по колонкам и сверены построчно. Переведён **только текст
поэмы**: предисловие, примечания и приложения издателя (в том числе санскритская стотра Абхирамы
Госвами и мангала-шлоки перед началом поэмы) не переводились. Пометки *[с. N]* — страницы PDF-скана.

**Принципы.** Двустишия-паяры переведены построчно, без рифмы, и пронумерованы в каждой главе
(в оригинале нумерации нет); строфы-трипади и санскритские шлоки идут под одним номером. Испорченные
места оговорены в примечаниях переводчика в конце каждой главы. Глава 4 и глава 5 в издании носят почти
одинаковое название (обе о путешествии Джахнавы во Вриндаван). Имена — по `GLOSSARY.md`.

---

## Оглавление

"""),
    'en': dict(out='Nityananda-Vamsha-Vistara-en', title='Sri Nityananda-vamsha-vistara',
               author='Vrindavana Dasa (attributed; Eng. tr.)', preface="""# Sri Nityananda-vamsha-vistara

*"The Expansion of Nityananda's Line"*

*A poem attributed to Vrindavana Dasa Thakura*

*Translated from the Bengali*

---

## Translator's note

The *Nityananda-vamsha-vistara* is a Bengali poem about the family of Nityananda Prabhu: his marriage
to Vasudha and Jahnava at Mahaprabhu's command, the birth of Virachandra (Virabhadra), Jahnava's journeys
to Vrindavana, Virachandra's preaching in Bengal and his pilgrimage to Vrindavana. It is attributed to
Vrindavana Dasa Thakura, author of the *Chaitanya-bhagavata*; most scholars consider the attribution
doubtful and date the poem later (it contains chronological inconsistencies, such as Virachandra
meeting persons of an earlier generation). The translation is offered for acquaintance with the text,
without judgement on its authenticity.

**Source.** The edition of Kishori Dasa Babaji (Halisahar, 2nd ed., 1991), known from two independent
OCR copies on archive.org; the copies were separated into columns and collated line by line. **Only the
poem itself** is translated: the editor's preface, notes and appendices (including Abhirama Gosvami's
Sanskrit stotra and the mangala verses printed before the poem) are not. Markers *[p. N]* give the pages
of the PDF scan.

**Principles.** The payar couplets are translated line by line, without rhyme, and numbered within each
chapter (the original has no numbering); tripadi stanzas and Sanskrit verses are numbered as single units.
Corrupt passages are noted in the translator's notes at the end of each chapter. Chapters 4 and 5 bear
almost the same title in the edition (both concern Jahnava's journey to Vrindavana). Names follow
`GLOSSARY.md`.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 11):
        key = f'{i:02d}'
        text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    md = m['preface'] + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
