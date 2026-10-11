"""Собирает перевод «Анурага-валли» (ru/en, манджари 01–08) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Anuragavalli-ru', title='Анурага-валли', author='Манохара Дас (рус. пер.)', preface="""# Анурага-валли

*«Лиана анураги»*

*Поэма Манохары Даса*

*Перевод с бенгальского на русский*

---

## От переводчика

«Анурага-валли» — бенгальская поэма в восьми «манджари» («соцветиях») о Шринивасе Ачарье, его гуру Гопале Бхатте
Госвами и ветви Шринивасы. Манджари 1 — мангалачарана и жизнь Гопалы Бхатты (встреча с Махапрабху в Шрирангаме,
приход во Вриндаван, явление Шри Радха-раманы); 2 — юность Шринивасы, Пури и Гададхара Пандит, «загадка» для
Гададхары Даса и заступничество Вишнуприи; 3 — Гауда, Абхирама и путь во Вриндаван, посвящение у Гопалы Бхатты;
4 — Божества Вриндавана, учение у Шри Дживы, Кашишвара и Божество Гауранги у Говинды, Локанатха и Нароттама;
5 — паломничество по Враджу и звание «Ачарья»; 6 — возвращение в Гауду с книгами, второе и третье путешествия во
Вриндаван, Шьямананда, Рамачандра и Говинда Кавираджи; 7 — перечень ветвей Шринивасы; 8 — четыре сампрадаи,
толкование Хари-намы и преемство самого автора.

**Автор и дата.** Манохара Дас — ученик Рамашараны Чаттараджа (из Баганаколы близ Катоа), сына Кришнадаса Чаттараджа;
его преемство: Гопала Бхатта — Шринивас Ачарья — Рамачаран Чакраварти — Рамашарана Чаттарадж (8.61–68). По повелению
гуру он ушёл во Вриндаван и жил у Радха-кунды; там же, узнав об уходе гуру, сложил десять санскритских шлок о нём
(8.86). Поэма закончена во Вриндаване в 1753 г. самвата, 1618 г. шака — в светлую половину месяца чайтра 1696 г.
Автор не был свидетелем описываемого: он опирается на предание («слышал из уст махантов»), на рукописи и, в
значительной мере, на тот же круг рассказов, что «Према-виласа» и «Карнананда». В нашей базе лил «Анурага-валли» —
источник уровня C.

**Особенности и расхождения.** Многое известно только по «Анурага-валли»: правило двух наставников во Вриндаване
(«западные» — к Гопале Бхатте, гаудии — к Рагхунатхе Бхатте); явление Радха-раманы рукой Шри Рупы; загадка Гададхары
Пандита, оскорбление Гададхары Даса и заступничество Вишнуприи; годичное испытание Нароттамы и обет Локанатхи;
толкование шлоки о кадамбе; встреча с Виттхаланатхой; ложь Шринивасы о женитьбе и прощение Гопалы Бхатты; Шринивас как
адхикари Радха-раманы. Похищение книг в Вишнупуре автор не упоминает. Все расхождения с «Према-виласой»,
«Карнанандой», «Нароттама-виласой», «Бхакти-ратнакарой» и «Чайтанья-чаритамритой» оговорены в примечаниях.
В восьмой манджари автор называет линию Махапрабху «нимананди» (от имени Нимай); переведено как у автора, с
примечанием: гаудия-вайшнавы во главе со Шрилой Бхактисиддхантой Сарасвати называют свою сампрадаю
Брахма-Мадхва-Гаудия.

**Источник.** 2-е издание: Калькутта, Патрика-пресс, изд. Шри Тадиткантхи Бишвас, Гаурабда 426 (1912);
общественное достояние (Internet Archive, `AnuragValli`). Переведён **только текст поэмы**: предисловие, подстрочные
примечания и приложение редактора (бенгальские переводы шлок) не переводились.

**Принципы.** Двустишия-паяры переведены построчно, без рифмы, и пронумерованы в каждой манджари; песни (пады) и
санскритские шлоки идут под одним номером; раги и подзаголовки не нумеруются; *[с. N]* — страница издания.
Испорченные и неясные места оговорены в примечаниях. Имена — по глоссариям «Према-виласы», «Карнананды» и
`GLOSSARY.md`.

---

## Оглавление

"""),
    'en': dict(out='Anuragavalli-en', title='Anuraga-valli', author='Manohara Dasa (Eng. tr.)', preface="""# Anuraga-valli

*"The Creeper of Anuraga"*

*A poem by Manohara Dasa*

*Translated from the Bengali*

---

## Translator's note

The *Anuraga-valli* is a Bengali poem in eight "manjaris" ("clusters of blossoms") on Srinivasa Acharya, his guru
Gopala Bhatta Gosvami and Srinivasa's branch. Manjari 1 gives the mangalacharana and the life of Gopala Bhatta (his
meeting with Mahaprabhu at Srirangam, his coming to Vrindavana, the appearance of Sri Radha-ramana); 2 — Srinivasa's
youth, Puri and Gadadhara Pandita, the "riddle" for Gadadhara Dasa and Vishnupriya's intercession; 3 — Gauda,
Abhirama and the road to Vrindavana, initiation by Gopala Bhatta; 4 — the Deities of Vrindavana, study with Sri Jiva,
Kashishvara and Gauranga's Deity beside Govinda, Lokanatha and Narottama; 5 — the pilgrimage through Vraja and the
title "Acharya"; 6 — the return to Gauda with the books, the second and third journeys to Vrindavana, Shyamananda,
Ramachandra and Govinda Kaviraja; 7 — the list of Srinivasa's branches; 8 — the four sampradayas, the explanation of
the Hari-nama and the author's own succession.

**Author and date.** Manohara Dasa was a disciple of Ramasharana Chattaraja (of Baganakola near Katwa), son of
Krishnadasa Chattaraja; his line is Gopala Bhatta — Srinivasa Acharya — Ramacharana Chakravarti — Ramasharana
Chattaraja (8.61–68). At his guru's order he went to Vrindavana and lived at Radha-kunda; there, on learning of his
guru's passing, he composed ten Sanskrit shlokas about him (8.86). The poem was completed in Vrindavana in Samvat 1753,
Shaka 1618 — in the bright half of Chaitra, 1696 CE. The author did not witness the events he describes: he relies on
tradition ("heard from the lips of the mahantas"), on manuscripts and, to a large extent, on the same body of stories
as the *Prema-vilasa* and the *Karnananda*. In our lila database the *Anuraga-valli* is a level-C source.

**Peculiarities and divergences.** Much is known only from the *Anuraga-valli*: the rule of the two teachers in
Vrindavana ("westerners" to Gopala Bhatta, Gaudiyas to Raghunatha Bhatta); the manifestation of Radha-ramana by Sri
Rupa's hand; Gadadhara Pandita's riddle, the offense to Gadadhara Dasa and Vishnupriya's intercession; Narottama's
year-long test and Lokanatha's vow; the explanation of the kadamba verse; the meeting with Vitthalanatha; Srinivasa's
untruth about his marriage and Gopala Bhatta's forgiveness; Srinivasa as adhikari of Radha-ramana. The theft of the
books in Vishnupura is not mentioned. All divergences from the *Prema-vilasa*, the *Karnananda*, the
*Narottama-vilasa*, the *Bhakti-ratnakara* and the *Chaitanya-charitamrita* are noted. In the eighth manjari the author
calls Mahaprabhu's line "Nimanandi" (from the name Nimai); this is translated as the author has it, with a note: the
Gaudiya Vaishnavas, headed by Srila Bhaktisiddhanta Sarasvati, call their sampradaya the Brahma-Madhva-Gaudiya.

**Source.** The 2nd edition: Calcutta, Patrika Press, published by Sri Taditkanti Bishvas, Gaurabda 426 (1912); public
domain (Internet Archive, `AnuragValli`). **Only the poem itself** is translated: the editor's preface, footnotes and
appendix (Bengali renderings of the shlokas) are not.

**Principles.** The payar couplets are translated line by line, without rhyme, and numbered within each manjari;
songs (padas) and Sanskrit shlokas are numbered as single units; ragas and subheadings are not numbered; *[p. N]* is
the page of the edition. Corrupt and unclear passages are noted. Names follow the glossaries of the *Prema-vilasa*,
the *Karnananda* and `GLOSSARY.md`.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 9):
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
