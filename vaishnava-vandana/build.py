"""Собирает «Вайшнава-ванданы» (ru/en, части 01–03 + указатель лиц) в MD, DOCX и PDF; генерирует INDEX.md из index.tsv.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

PARTS = ['01', '02', '03']

META = {
    'ru': dict(out='Vaishnava-Vandana-ru', title='Вайшнава-ванданы',
               author='Джива Госвами (приписывается), Девакинандана Дас; рус. пер.', preface="""# Вайшнава-ванданы

*«Восхваления вайшнавов»: перечни спутников Шри Чайтаньи*

*Санскритская вандана, приписываемая Дживе Госвами; «Вайшнава-вандана» и «Вайшнавабхидхана» Девакинанданы Даса*

*Перевод с санскрита и бенгали на русский*

---

## От переводчика

**Что такое вайшнава-вандана.** Так называются стихотворные перечни вайшнавов — прежде всего спутников
Шри Чайтаньи Махапрабху, Нитьянанды и Адвайты, — которые преданные читали по утрам: «Кто, встав на рассвете,
читает вайшнава-вандану, тот никогда не узнает мук». В отличие от житий, ванданы не рассказывают историю,
а называют имена — иногда одним словом, иногда с короткой характеристикой: кто каким был в Кришна-лиле, чем
прославился, кого Господь особо любил. Поэтому они хорошо дополняют «Гаура-ганоддеша-дипику» Кави Карнапуры
(1576), где спутники Господа сопоставлены с их обликами во Врадже, и списки «ветвей древа преданности» в
«Чайтанья-чаритамрите» (Ади 9–12). Некоторые сведения известны только по ванданам: о брахмачари среди
спутников в Навадвипе, о многих санньяси, окружавших Господа, о подвигах спутников Нитьянанды.

**Часть 1. Санскритская вандана, приписываемая Дживе Госвами** (153 шлоки). Автор несколько раз называет себя
«Дживой» и подписывается в конце: «я, Джива, закончил»; колофон называет вандану «следующей сампрадае Мадхвы».
В перечне трудов Дживы в «Бхакти-ратнакаре» её нет; известны лишь две рукописи, и атрибуция остаётся спорной.
Б. Маджумдар, издавший текст в приложении к своей книге «Шри-Чайтанья-чаритер упадан» (1938/39; 2-е изд. 1959),
склонялся к тому, что она принадлежит самому Дживе, а бенгальские ванданы составлены вслед за ней. Отдельного
издания, перешедшего в общественное достояние, у этого текста нет; переведён только старый санскритский текст
по двум независимым OCR-копиям двух изданий Маджумдара, без его примечаний. Испорченные места оговорены в сносках.

**Часть 2. Девакинандана Дас, «Вайшнава-вандана»** (147 двустиший) — самая распространённая бенгальская
вандана. Девакинандана — ученик Пурушоттамы Даса, сына Садашивы Кавираджи из спутников Нитьянанды, и,
следовательно, писал ещё в XVI в. Перевод сделан по изданию Атулакришны Госвами (Калькутта, 1910), где
вандана Девакинанданы напечатана вместе с другими. Нумерация двустиший совпадает с нумерацией Маджумдара;
два двустишия, взятые издателем в скобки, отмечены номерами 16a и 42a. Строки раг и припевы (дхуя) не нумеруются.
«Большая» вандана Девакинанданы, по Маджумдару, сохранилась лишь в рукописи и в изданиях, перешедших в общественное
достояние, не найдена.

**Часть 3. Девакинандана Кавираджа, «Вайшнавабхидхана»** — санскритский перечень имён (53 шлоки), почти
дословно повторяющий порядок бенгальской ванданы; из того же издания 1910 г.

**Не переведены** две другие ванданы издания 1910 г. — «Первая вандана» о спутниках Нитьянанды и вандана в
трипади, приписанные Вриндавану Дасу (см. `CATALOG.md`).

**Принципы.** Переведён только текст ванданы — без оригинала и пословного перевода. Русский и английский
переводы сделаны параллельно, с единой нумерацией и одинаковыми сносками. В сносках кратко сказано, кто этот
спутник (по «Гаура-ганоддеше» — ГГД, по нашему переводу; «Чайтанья-чаритамрите» — ЧЧ; «Чайтанья-бхагавате» —
ЧБ), и отмечены расхождения между ванданами, с ГГД и с выводами Маджумдара. Где вандана расходится с принятым
у гаудия-вайшнавов (например, иное отождествление спутника), перевод точен, а пояснение дано в сноске.
В конце книги — **сводный указатель лиц**: где каждый спутник упомянут в трёх текстах и в ГГД.

---

## Оглавление

"""),
    'en': dict(out='Vaishnava-Vandana-en', title='The Vaishnava-vandanas',
               author='Jiva Gosvami (attributed), Devakinandana Dasa; Eng. tr.', preface="""# The Vaishnava-vandanas

*"Praises of the Vaishnavas": lists of the associates of Sri Chaitanya*

*The Sanskrit vandana attributed to Jiva Gosvami; the* Vaishnava-vandana *and* Vaishnavabhidhana *of Devakinandana Dasa*

*Translated from the Sanskrit and Bengali*

---

## Translator's note

**What a Vaishnava-vandana is.** This is the name of verse lists of Vaishnavas — above all the associates
of Sri Chaitanya Mahaprabhu, Nityananda and Advaita — which devotees recited in the morning: "Whoever, rising
at dawn, reads the Vaishnava-vandana will never know torment." Unlike the biographies, the vandanas tell no
story; they give names — sometimes a single word, sometimes a short characterisation: who someone was in
Krishna-lila, what he was famous for, whom the Lord especially loved. They therefore complement Kavi
Karnapura's *Gaura-ganoddesha-dipika* (1576), which matches the Lord's associates with their forms in Vraja,
and the lists of the "branches of the tree of devotion" in the *Chaitanya-charitamrita* (Adi 9–12). Some
facts are known only from the vandanas: about brahmacharis among the associates at Navadvipa, about many
sannyasis around the Lord, about the deeds of Nityananda's associates.

**Part 1. The Sanskrit vandana attributed to Jiva Gosvami** (153 verses). The author several times calls himself
"Jiva" and signs at the end: "I, Jiva, have completed it"; the colophon calls the vandana "following the
sampradaya of Madhva". It is not in the list of Jiva's works in the *Bhakti-ratnakara*; only two manuscripts
are known, and the attribution remains disputed. B. Majumdar, who published the text in an appendix to his
book *Sri-Chaitanya-chariter upadan* (1938/39; 2nd ed. 1959), inclined to think it was Jiva's own and that
the Bengali vandanas followed it. There is no public-domain edition of this text; only the old Sanskrit text
has been translated, from two independent OCR copies of Majumdar's two editions, without his notes. Corrupt
places are noted in the footnotes.

**Part 2. Devakinandana Dasa, the Vaishnava-vandana** (147 couplets) — the most widespread Bengali vandana.
Devakinandana was a disciple of Purushottama Dasa, the son of Sadashiva Kaviraja among Nityananda's associates,
and so wrote in the sixteenth century. The translation follows the edition of Atulakrishna Gosvami (Calcutta,
1910), where Devakinandana's vandana is printed together with others. The numbering of couplets agrees with
Majumdar's; two couplets bracketed by the editor are numbered 16a and 42a. Raga lines and refrains (dhuya)
are not numbered. Devakinandana's "great" vandana, according to Majumdar, survives only in manuscript and has
not been found in a public-domain edition.

**Part 3. Devakinandana Kaviraja, the Vaishnavabhidhana** — a Sanskrit list of names (53 verses), following
almost exactly the order of the Bengali vandana; from the same 1910 edition.

**Not translated** are two other vandanas of the 1910 edition — the "First vandana" on Nityananda's associates
and a vandana in tripadi, both attributed to Vrindavana Dasa (see `CATALOG.md`).

**Principles.** Only the text of the vandanas is translated — without the original or a word-for-word
rendering. The Russian and English translations were made in parallel, with the same numbering and the same
notes. The notes say briefly who each associate is (according to the *Gaura-ganoddesha* — GGD, by our
numbering; the *Chaitanya-charitamrita* — CC; the *Chaitanya-bhagavata* — CB) and mark divergences between
the vandanas, from GGD and from Majumdar's conclusions. Where a vandana differs from what Gaudiya Vaishnavas
accept (for example, a different identification of an associate), the translation is exact and the
explanation is given in a note. At the end of the book there is a **consolidated index of persons**: where
each associate is mentioned in the three texts and in GGD.

---

## Contents

"""),
}

IDX = {
    'ru': dict(h='# Указатель лиц', intro='*Где упомянут каждый спутник: ч. 1 — вандана, приписываемая Дживе (шлоки); ч. 2 — Девакинандана (двустишия); ч. 3 — «Вайшнавабхидхана» (шлоки); ГГД — «Гаура-ганоддеша-дипика» (шлоки по нашему переводу). Тег — код лица в базе лил (`lila-db/PERSONS.md`); «—» — тег не заведён (лицо не отождествлено). «(?)» — отождествление предположительно. Порядок — по первому упоминанию.*',
               cols=['Имя', 'Тег', 'Ч. 1', 'Ч. 2', 'Ч. 3', 'ГГД']),
    'en': dict(h='# Index of persons', intro='*Where each associate is mentioned: Part 1 — the vandana attributed to Jiva (verses); Part 2 — Devakinandana (couplets); Part 3 — the* Vaishnavabhidhana *(verses); GGD — the* Gaura-ganoddesha-dipika *(verses by our numbering). Tag — the person code in the lila database (`lila-db/PERSONS.md`); "—" — no tag (person not identified). "(?)" — tentative identification. Order — by first mention.*',
               cols=['Name', 'Tag', 'Pt. 1', 'Pt. 2', 'Pt. 3', 'GGD']),
}


def index_md(lang):
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'index.tsv'), encoding='utf-8')][1:]
    m = IDX[lang]
    out = [m['h'], '', m['intro'], '', '| ' + ' | '.join(m['cols']) + ' |', '|' + '---|' * 6]
    for tag, ru, en, j, d, a, g in rows:
        out.append(f"| {ru if lang == 'ru' else en} | {tag if tag != '—' else '—'} | {j} | {d} | {a} | {g} |")
    return '\n'.join(out) + '\n'


def write_index():
    """INDEX.md — двуязычный сводный указатель (из index.tsv)."""
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'index.tsv'), encoding='utf-8')][1:]
    out = ['# Сводный указатель лиц «Вайшнава-вандан» / Index of persons', '',
           'Генерируется из `index.tsv` скриптом `build.py`. Ч. 1 — вандана, приписываемая Дживе (шлоки); ч. 2 — Девакинандана '
           '(двустишия, нумерация как у Маджумдара); ч. 3 — «Вайшнавабхидхана»; ГГД — «Гаура-ганоддеша-дипика» по `../gaura-ganoddesha/ru/`. '
           f'Всего {len(rows)} строк, из них с тегом — {sum(1 for r in rows if r[0].startswith("@"))}.', '',
           '| RU | EN | Тег | Ч. 1 | Ч. 2 | Ч. 3 | ГГД |', '|---|---|---|---|---|---|---|']
    for tag, ru, en, j, d, a, g in rows:
        out.append(f'| {ru} | {en} | {tag} | {j} | {d} | {a} | {g} |')
    open(os.path.join(HERE, 'INDEX.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


def build(lang):
    m = META[lang]
    toc, body = [], []
    for key in PARTS:
        text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    idx = index_md(lang)
    toc.append('- ' + idx.splitlines()[0].lstrip('# ').strip())
    body.append(idx.strip())
    md = m['preface'] + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    write_index()
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
