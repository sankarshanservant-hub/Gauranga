"""Собирает переводы материалов по «Чайтанья-мангале» Джаянанды (ru/en, файлы NN-*.md) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import glob, importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Jayananda-Chaitanya-Mangala-ru', title='Джаянанда. Чайтанья-мангала: фрагменты и свидетельства',
               author='Джаянанда; Н. Васу; Дж. Саркар (рус. пер.)', preface="""# Джаянанда. «Чайтанья-мангала»

*Сохранившиеся фрагменты поэмы и ранние свидетельства о ней*

*Перевод с бенгальского (и английского) на русский*

---

## От переводчика

«Чайтанья-мангала» Джаянанды — бенгальская поэма о жизни Шри Чайтаньи, написанная, по-видимому,
в середине XVI века в жанре мангала-кавьи, для пения по деревням. Она расходится с другими жизнеописаниями
во многих подробностях; особенно известен её рассказ о кончине Махапрабху. Полный текст поэмы (изд. 1905 и
1971 гг.) в открытом доступе отсутствует, поэтому здесь собрано всё, что удалось достать:

1. **Пятнадцать фрагментов** самой поэмы — по изданию 1971 г. (с. 10–222), в наборе проекта Эксетерского
   университета «Famine and Dearth». Переведён только текст поэмы.
2. **Статья Нагендранатха Васу** «Поэт Джаянанда и „Чайтанья-мангала“» (1897) — первое описание рукописи
   с обширными цитатами, в том числе с плачем Вишнуприи по двенадцати месяцам и заключительным пересказом
   жизни Чайтаньи.
3. **Его же заметка** 1898 г. о подлинности поэмы.
4. **Отрывок из книги Джадунатха Саркара** (1922) — английский перевод сцены кончины Чайтаньи по Джаянанде.

Статьи Васу и книга Саркара — общественное достояние. Стихи переведены построчно, без рифмы; испорченные
места оговорены в примечаниях переводчика; примечания Васу помечены особо. Имена — по `GLOSSARY.md`.

---

## Оглавление

"""),
    'en': dict(out='Jayananda-Chaitanya-Mangala-en', title='Jayananda. Chaitanya-mangala: Fragments and Testimonies',
               author='Jayananda; N. Vasu; J. Sarkar (Eng. tr.)', preface="""# Jayananda. Chaitanya-mangala

*The surviving fragments of the poem and early testimonies about it*

*Translated from the Bengali*

---

## Translator's note

Jayananda's *Chaitanya-mangala* is a Bengali poem on the life of Sri Chaitanya, apparently composed in the
middle of the sixteenth century in the mangala-kavya genre, to be sung in the villages. It differs from the
other biographies in many details; its account of Mahaprabhu's passing is especially well known. The full
text (editions of 1905 and 1971) is not freely available, so everything that could be obtained is gathered here:

1. **Fifteen fragments** of the poem itself, from the 1971 edition (pp. 10–222), as transcribed by the
   University of Exeter project "Famine and Dearth". Only the poem text is translated.
2. **Nagendranath Vasu's article** "The Poet Jayananda and the Chaitanya-mangala" (1897), the first
   description of the manuscript, with extensive quotations, including Vishnupriya's lament of the twelve
   months and the closing summary of Chaitanya's life.
3. **His note** of 1898 on the authenticity of the poem.
4. **An excerpt from Jadunath Sarkar** (1922): his English translation of the scene of Chaitanya's passing
   according to Jayananda, reproduced as published.
5. **Quotations from the poem in later authors**: 88 passages gathered from D. C. Sen (1914), Girijashankar
   Raychaudhuri (1946), B. B. Majumdar (1939/1959), Sukumar Sen (1940) and others; only Jayananda's verse is
   translated, arranged by khanda.

Vasu's articles and Sarkar's book are in the public domain. Verse is translated line by line, without rhyme;
corrupt passages are discussed in the translator's notes; Vasu's own notes are marked as such. Names follow
`GLOSSARY.md`.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for path in sorted(glob.glob(os.path.join(HERE, lang, '[0-9][0-9]-*.md'))):
        key = os.path.basename(path)[:2]
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
