"""Собирает перевод «Карнананды» (ru/en, нирьясы 01–07) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Karnananda-ru', title='Карнананда', author='Ядунандана Дас (рус. пер.)', preface="""# Карнананда

*«Радость для ушей»*

*Поэма Ядунанданы Даса*

*Перевод с бенгальского на русский*

---

## От переводчика

«Карнананда» — бенгальская поэма в семи «нирьясах» («выжимках») о Шринивасе Ачарье и его ветви. Автор,
Ядунандана Дас, вайдья из деревни Малихати, был учеником Хемалаты Тхакурани, дочери Шринивасы; большая часть
книги передаёт то, что он слышал из её уст. Нирьясы 1–2 — перечень ветвей и подветвей Шринивасы (его семьи и
учеников); 3 — трёхдневное самадхи Шринивасы и находка кольца Шри Радхи Рамачандрой Кавираджей; 4 — наставления
Рамачандры царю Вире Хамбиру (по существу — переложение «Чайтанья-чаритамриты» и гимнов Госвами); 5 — письма Шрилы
Дживы Госвами и встреча Махапрабху с Гопалой Бхаттой в Шрирангаме; 6 — обет Шринивасы, его посвящение и уход из
Вриндавана с книгами; 7 — разрешение сомнения о кончине Кришнадаса Кавираджи и Рагхунатхи Даса.

**Датировка и достоверность.** Колофон (6.167–170) называет 1529 г. эры шака (1607 г. н. э.), полнолуние вайшакхи,
Будхуипару. Эта дата плохо согласуется с содержанием: в книге — взрослые внуки Шринивасы и их ученики, прямая
отсылка к «Према-виласе» как к готовой книге, спор о «Гопала-чампу»; перечень «кавирадж и чакраварти» добавлен
после колофона. Поэтому в нашей базе лил «Карнананда» отнесена к источникам уровня C, а поздние части — ниже.
Главные расхождения с «Према-виласой», «Бхакти-ратнакарой» и «Чайтанья-чаритамритой» оговорены в примечаниях:
кража книг Госвами во время паломничества Шринивасы в Пури (а не по пути из Вриндавана с Нароттамой и
Шьяманандой); Вира Хамбир получает имя «Гопаладас» от Дживы; Махапрабху в Шрирангаме гостит у Трималлы Бхатты и сам
предсказывает Гопале Бхатте приход Шринивасы; Кришнадас Кавираджа после «смерти от горя» возвращается в тело. Учение
о паракии и внутреннем смысле «Гопала-чампу» передано точно, с пояснениями по Шриле Бхактисиддханте Сарасвати.

**Источник.** Издание Рамнараяна Видьяратны (Бахарампур, конец XIX в.; общественное достояние; DLI
`in.ernet.dli.2015.510314`), сверенное со вторым набором того же издателя (1892). Переведён **только текст поэмы**:
посвящение, предисловие и подстрочные примечания издателя, указатель и список опечаток не переводились.

**Принципы.** Двустишия-паяры переведены построчно, без рифмы, и пронумерованы в каждой нирьясе; песни (пады),
санскритские шлоки и письма идут под одним номером. Испорченные места оговорены в примечаниях. Имена — по
глоссарию «Према-виласы» и `GLOSSARY.md`.

---

## Оглавление

"""),
    'en': dict(out='Karnananda-en', title='Karnananda', author='Yadunandana Dasa (Eng. tr.)', preface="""# Karnananda

*"Joy for the Ears"*

*A poem by Yadunandana Dasa*

*Translated from the Bengali*

---

## Translator's note

The *Karnananda* is a Bengali poem in seven "niryasas" ("extracts") on Srinivasa Acharya and his branch. The author,
Yadunandana Dasa, a Vaidya of the village of Malihati, was a disciple of Hemalata Thakurani, Srinivasa's daughter;
most of the book relates what he heard from her lips. Niryasas 1–2 list the branches and sub-branches of Srinivasa
(his family and disciples); 3 tells of Srinivasa's three-day samadhi and the finding of Sri Radha's nose-ring by
Ramachandra Kaviraja; 4 gives Ramachandra's instructions to King Vira Hambira (in substance a rendering of the
*Chaitanya-charitamrita* and the Gosvamis' hymns); 5 gives Srila Jiva Gosvami's letters and Mahaprabhu's meeting with
Gopala Bhatta at Shrirangam; 6 Srinivasa's vow, initiation and departure from Vrindavana with the books; 7 the
resolution of a doubt about the passing of Krishnadasa Kaviraja and Raghunatha Dasa.

**Dating and reliability.** The colophon (6.167–170) gives Shaka 1529 (1607 CE), the full moon of Vaishakha, at
Budhuipara. This date agrees poorly with the contents: the book mentions Srinivasa's grown grandsons and their
disciples, refers to the *Prema-vilasa* as a finished book, and records the dispute over the *Gopala-champu*; the list
of "Kavirajas and Chakravartis" is added after the colophon. In our lila database the *Karnananda* is therefore
classed as a level-C source, its later parts lower. The main divergences from the *Prema-vilasa*, the
*Bhakti-ratnakara* and the *Chaitanya-charitamrita* are noted: the theft of the Gosvamis' books during Srinivasa's
pilgrimage to Puri (not on the way from Vrindavana with Narottama and Shyamananda); Vira Hambira receiving the name
"Gopaladasa" from Jiva; Mahaprabhu staying at Shrirangam with Trimalla Bhatta and Himself foretelling Srinivasa's
coming to Gopala Bhatta; Krishnadasa Kaviraja returning to his body after his "death from grief". The teaching on
parakiya and the inner meaning of the *Gopala-champu* is rendered faithfully, with notes following Srila Bhaktisiddhanta
Sarasvati.

**Source.** The edition of Ramnarayan Vidyaratna (Baharampur, late 19th c.; public domain; DLI
`in.ernet.dli.2015.510314`), checked against the same publisher's second setting (1892). **Only the poem itself** is
translated: the editor's dedication, preface and footnotes, the index and the errata are not.

**Principles.** The payar couplets are translated line by line, without rhyme, and numbered within each niryasa;
songs (padas), Sanskrit verses and letters are numbered as single units. Corrupt passages are noted. Names follow the
*Prema-vilasa* glossary and `GLOSSARY.md`.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 8):
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
