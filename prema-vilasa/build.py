"""Собирает перевод «Према-виласы» (ru/en, виласы 01–24 и «Полувиласа» 25) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Prema-Vilasa-ru', title='Према-виласа', author='Нитьянанда Дас (рус. пер.)', preface="""# Према-виласа

*«Игры любви»*

*Поэма Нитьянанды Даса*

*Перевод с бенгальского на русский*

---

## От переводчика

«Према-виласа» — бенгальская поэма Нитьянанды Даса (Баларамы Даса), ученика Джахнавы-деви, о жизни
Шринивасы Ачарьи, Нароттамы Тхакура и Шьямананды: их обучении во Вриндаване у Дживы Госвами, доставке
книг Госвами в Бенгалию и проповеди в Гауде, Ориссе и Вишнупуре.

**Источник.** Издание 1913 г. (Калькутта, Багбазар; общественное достояние), сверенное по двум
независимым OCR-копиям (изд. 1913 г. и его перепечатки 1999 г.). Переведён **только текст поэмы**:
предисловия и примечания издателей не переводились. Переведены все двадцать четыре виласы и заключительная «Полувиласа»
(письма Шринивасы и Дживы Госвами и стихотворный указатель содержания).

**О 24-й виласе.** Двадцать четвёртая виласа (около двух тысяч двустиший) по характеру резко отличается
от остальных. В ней собраны житие Адвайты Ачарьи (во многом совпадающее с «Адвайта-пракашей» Ишаны
Нагары), рассказы о Брахма-Харидасе, о родословии Махапрабху, о Вишварупе и Нитьянанде, о путешествии
Махапрабху в Восточную Бенгалию, о женитьбе Нитьянанды и о Вирабхадре, а большую её часть занимают
родословия и правила кулинской системы бенгальских брахманов (Адишура, Баллала Сена, Девивара,
Камсанараяна). Подлинность этой виласы оспаривается: старые рукописи поэмы её не содержат, и
Б. Маджумдар («Шри-Чайтанья-чаритер упадан») считает её позднейшим сочинением; в тексте заметны
анахронизмы (блудница «из рода моголов» при Харидасе, Камсанараяна — современник Махапрабху, смешение
логика Удаяны X в. с кулинским преобразователем) и сведения, неизвестные другим вайшнавским источникам.
Виласа переведена полностью и точно, как она есть; спорные места, расхождения с «Чайтанья-чаритамритой»,
«Чайтанья-бхагаватой» и другими источниками и признаки поздней вставки оговорены в примечаниях.

**Принципы.** Двустишия-паяры переведены построчно, без рифмы, и пронумерованы в каждой виласе
(в оригинале нумерации нет); трипади, песни и санскритские шлоки идут под одним номером. Испорченные
места оговорены в примечаниях переводчика в конце каждой виласы. Имена — по `GLOSSARY.md`.

---

## Оглавление

"""),
    'en': dict(out='Prema-Vilasa-en', title='Prema-vilasa', author='Nityananda Dasa (Eng. tr.)', preface="""# Prema-vilasa

*"The Pastimes of Love"*

*A poem by Nityananda Dasa*

*Translated from the Bengali*

---

## Translator's note

The *Prema-vilasa* is a Bengali poem by Nityananda Dasa (Balarama Dasa), a disciple of Jahnava Devi,
on the lives of Srinivasa Acharya, Narottama Thakura and Shyamananda: their training in Vrindavana under
Jiva Gosvami, the bringing of the Gosvamis' books to Bengal, and their preaching in Gauda, Orissa and
Vishnupura.

**Source.** The edition of 1913 (Calcutta, Bagbazar; public domain), collated from two independent OCR
copies (the 1913 edition and its 1999 reprint). **Only the poem itself** is translated: the editors'
prefaces and notes are not. All twenty-four vilasas are translated, together with the closing "Half-vilasa"
(the letters of Srinivasa and Jiva Gosvami and the verse index of contents).

**On the twenty-fourth vilasa.** The twenty-fourth vilasa (about two thousand couplets) differs sharply
in character from the rest. It gathers a life of Advaita Acharya (largely agreeing with Ishana Nagara's
*Advaita-prakasha*), accounts of Brahma-Haridasa, of Mahaprabhu's lineage, of Vishvarupa and Nityananda,
of Mahaprabhu's journey to East Bengal, of Nityananda's marriage and of Virabhadra, while most of it is
taken up by the genealogies and rules of the kulin system of the Bengali brahmanas (Adishura, Ballala
Sena, Devivara, Kamsanarayana). Its authenticity is disputed: the old manuscripts of the poem do not
contain it, and B. Majumdar (*Sri-Chaitanya-chariter upadan*) regards it as a late composition; the text
shows anachronisms (a "Mughal" courtesan in Haridasa's time, Kamsanarayana as Mahaprabhu's contemporary,
the conflation of the tenth-century logician Udayana with the kulin reformer) and information unknown to
other Vaishnava sources. The vilasa is translated in full and faithfully, as it stands; disputed passages,
divergences from the *Chaitanya-charitamrita*, the *Chaitanya-bhagavata* and other sources, and the signs
of late interpolation are noted in the translator's notes.

**Principles.** The payar couplets are translated line by line, without rhyme, and numbered within each
vilasa (the original has no numbering); tripadi stanzas, songs and Sanskrit verses are numbered as single
units. Corrupt passages are noted in the translator's notes at the end of each vilasa. Names follow
`GLOSSARY.md`.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 26):
        key = f'{i:02d}'
        path = os.path.join(HERE, lang, key + '.md')
        if not os.path.exists(path):
            continue
        text = open(path, encoding='utf-8').read().strip()
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
