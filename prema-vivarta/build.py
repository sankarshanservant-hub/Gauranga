"""Собирает перевод «Према-виварты» (ru/en, главы 01–20) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Prema-Vivarta-ru', title='Према-виварта', author='Джагадананда Пандит (рус. пер.)', preface="""# Шри Шри Према-виварта

*«Превращения любви»*

*Поэма, приписываемая Джагадананде Пандиту*

*Перевод с бенгальского на русский*

---

## От переводчика

**Книга.** «Према-виварта» («Превращения любви», или «Игры виварты любви») — бенгальская поэма в двадцати главах,
написанная от лица Джагадананды Пандита, спутника Шри Чайтаньи Махапрабху. Это не связное жизнеописание: автор
говорит, что записывает лилы Господа «как вспомнятся, хотя бы и не по порядку» (гл. 15). Воспоминания —
детская ссора и примирение с Нимаем, попугай, поющий «Гаура», шутки Господа о «царице Двараки», разбитый кувшин
сандалового масла, путь во Вриндаван, утренняя прогулка к пастухам Гадигачхи, экадаши в Пури — перемежаются
наставлениями: о Шри Чайтанье как едином облике Радхи и Кришны, о неотличии Навадвипы от Вриндавана, о
юкта-вайрагье, о поведении домохозяина и отрёкшегося, об обличении «сахаджиев», о трёх видах преданности, о
святом имени. Последние две главы — «Нама-рахасья-патала» (беседа Санаткумары и Нарады о десяти оскорблениях
Имени) и подборка стихов шастр о славе Имени — изложены как беседы Махапрабху с преданными в Пури.

**Джагадананда Пандит.** По «Чайтанья-чаритамрите», Джагадананда — «жизнь Господа», известный как проявление
Сатьябхамы (Ади 10.21; ср. «Гаура-ганоддеша-дипику», 51); его любовь, как у Сатьябхамы, — «строптивая» (вамья),
полная любовных ссор с Господом (Антья 7.138). Антья 12–13 рассказывает о самых известных его лилах: он привозит
из Бенгалии сандаловое масло, а когда Господь отказывается им пользоваться, разбивает кувшин и лежит в обиде, пока
Господь не приходит к нему пообедать; шьёт Господу подушку, которую Тот не принимает; уходит во Вриндаван и в
гневе едва не ударяет горшком Санатану, увидев на нём красную ткань санньяси. Господь посылал его в Навадвипу к
Шачи-мате. «Према-виварта» во многом говорит тем же голосом — голосом ревнивой, обидчивой любви, «Джагая-задиры».

**Об авторстве.** Традиция и Гаудия Матх принимают поэму как сочинение Джагадананды: впервые её издал
Шрила Бхактивинода Тхакур (1905/1906), затем — Гаудия Матх (1337 г. бенг. эры, ок. 1930). Историк Биманбихари
Маджумдар («Шри-Чайтанья-чаритер упадан») сомневался в авторстве Джагадананды из-за языка поэмы, её богословия
и упоминаний «Маяпура» и считал вопрос требующим разбора старых рукописей. Мы приводим это мнение как мнение
историка; в примечаниях отмечено, какие сведения известны только по «Према-виварте» и где она расходится с
«Чайтанья-чаритамритой». В базе лил поэма отнесена к источникам уровня B с оговоркой о спорной атрибуции.

**Издание.** Перевод сделан по седьмому изданию Шри Чайтанья Матха (Шридхам Маяпур; ред. Бхакти Вилас Тиртха
Махарадж; 1972, перепечатка 1983), сверено с изданием Шри Чайтанья Гаудия Матха (2005). Переведён **только текст
поэмы**: вступление и оглавление редактора, подзаголовки внутри глав (вставки редактора) и его примечания не
переводились. Названия глав даны по оглавлению издания. В седьмом издании заголовок двадцатой главы ошибочно
напечатан как «двадцать первая»; нумерация глав — по оглавлению.

**Принципы.** Двустишия (паяр) переведены построчно, без рифмы, и пронумерованы в каждой главе (в издании
нумерации нет); строфа трипади (две строки по три стопы) и санскритская шлока идут под одним номером, шлоки — курсивом,
припев — без номера. В квадратных скобках курсивом — страницы седьмого издания. Ссылки на «Чайтанья-чаритамриту»
даны по главам, номера стихов — по нашему тексту ЧЧ. Места, допускающие мирское или майявадское прочтение
(«преображение» в Неизменном, паракия, «аропа» в поклонении Божеству, «нирвана», «подобный Кришне»), поясняются
в примечаниях в согласии с учением Шрилы Бхактисиддханты Сарасвати.

---

## Оглавление

"""),
    'en': dict(out='Prema-Vivarta-en', title='Prema-vivarta', author='Jagadananda Pandita (Eng. tr.)', preface="""# Sri Sri Prema-vivarta

*"The Transformations of Love"*

*A poem attributed to Jagadananda Pandita*

*Translated from the Bengali*

---

## Translator's note

**The book.** The *Prema-vivarta* ("The Transformations of Love", or "The Play of Love's Vivarta") is a Bengali
poem in twenty chapters written in the voice of Jagadananda Pandita, a companion of Sri Chaitanya Mahaprabhu. It
is not a connected biography: the author says that he writes down the Lord's lilas "as they come to mind, though
not in order" (ch. 15). Recollections — a childhood quarrel and reconciliation with Nimai, the parrot singing
"Gaura", the Lord's jests about the "queen of Dvaraka", the broken pot of sandalwood oil, the journey to
Vrindavana, a morning outing to the cowherds of Gadigachha, an Ekadashi in Puri — alternate with teaching: on Sri
Chaitanya as the one form of Radha and Krishna, on the non-difference of Navadvipa and Vrindavana, on
yukta-vairagya, on the conduct of householder and renunciant, against the "sahajiyas", on the three kinds of
devotion, on the holy name. The last two chapters — the "Nama-rahasya-patala" (the conversation of Sanatkumara
and Narada on the ten offences to the Name) and a collection of scriptural verses on the glory of the Name — are
set out as Mahaprabhu's talks with the devotees in Puri.

**Jagadananda Pandita.** According to the *Chaitanya-charitamrita*, Jagadananda is "the Lord's very life", known
as a manifestation of Satyabhama (Adi 10.21; cf. *Gaura-ganoddesha-dipika* 51); his love, like Satyabhama's, is
"contrary" (*vamya*), full of loving quarrels with the Lord (Antya 7.138). Antya 12–13 tells his best-known lilas:
he brings sandalwood oil from Bengal and, when the Lord refuses to use it, breaks the pot and lies sulking until
the Lord comes to dine with him; he makes the Lord a pillow, which He does not accept; he goes to Vrindavana and in
anger nearly strikes Sanatana with a pot on seeing him wear a sannyasi's red cloth. The Lord used to send him to
Navadvipa to Mother Shachi. The *Prema-vivarta* largely speaks in the same voice — the voice of jealous, touchy
love, of "Jagai the quarrelsome".

**On authorship.** Tradition and the Gaudiya Math accept the poem as Jagadananda's work: it was first published
by Srila Bhaktivinoda Thakura (1905/1906), then by the Gaudiya Math (Bengali year 1337, c. 1930). The historian
Bimanbehari Majumdar (*Sri-Chaitanya-chariter upadan*) doubted Jagadananda's authorship on account of the poem's
language, its theology and its references to "Mayapura", and held that the question required a study of old
manuscripts. We give this as a historian's opinion; the notes mark what is known only from the *Prema-vivarta*
and where it differs from the *Chaitanya-charitamrita*. In our lila database the poem is classed as a level-B
source with a reservation about its disputed attribution.

**Edition.** The translation follows the seventh edition of the Sri Chaitanya Math (Sridham Mayapur; ed. Bhakti
Vilasa Tirtha Maharaja; 1972, reprinted 1983), checked against the edition of the Sri Chaitanya Gaudiya Math
(2005). **Only the text of the poem** is translated: the editor's introduction and table of contents, the
sub-headings within the chapters (the editor's insertions) and his notes are not. Chapter titles follow the
edition's table of contents. In the seventh edition the heading of the twentieth chapter is misprinted as
"twenty-first"; the numbering of chapters follows the table of contents.

**Principles.** The couplets (payar) are translated line by line, without rhyme, and numbered within each chapter
(the edition has no numbering); a tripadi stanza and a Sanskrit verse each form a single unit, the verses in
italics; a refrain is unnumbered. Page numbers of the seventh edition are given in square brackets in italics.
References to the *Chaitanya-charitamrita* are by chapter, verse numbers following our CC text. Passages that
might allow a worldly or Mayavadi reading ("transformation" in the Changeless, parakiya, "aropa" in Deity worship,
"nirvana", "like Krishna") are explained in the notes in accordance with the teaching of Srila Bhaktisiddhanta
Sarasvati.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 21):
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
