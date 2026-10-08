"""Собирает перевод «Шри Гаура-кришнодаи» Говинда-девы (ru/en, сарги 01–18) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
Включаются только уже переведённые сарги (файлы ru/NN.md, en/NN.md).
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Gaura-Krishnodaya-ru', title='Шри Гаура-кришнодая',
               author='Говинда-дева (рус. пер.)', preface="""# Шри Гаура-кришнодая

*«Восход Гаура-Кришны»*

*Санскритская поэма Говинда-девы (1758)*

*Перевод с санскрита на русский*

---

## От переводчика

«Шри Шри Гаура-кришнодая» — санскритская махакавья в восемнадцати саргах (около 1100 шлок) о жизни Шри
Чайтаньи Махапрабху — от причин Его нисшествия до ухода. Автор, Говинда-дева (Говинда Кави), — поэт из
Ориссы, принадлежавший, по словам издателя, к семейству (линии) Вакрешвары Пандита, спутника Махапрабху;
поэма завершена в 1680 г. Шака (1758 г. н. э.), в месяц ашвина. В колофоне каждой сарги автор называет себя
«пчелой, опьянённой мёдом лотосов-стоп Шри Гауранги».

**Значение поэмы.** Говинда-дева пишет через два с лишним века после Махапрабху и почти во всём следует
«Шри Чайтанья-чаритамрите» Кришнадаса Кавираджа — он сам называет её источником («нектар деяний», 1.4).
Поэтому как исторический источник поэма вторична. Её ценность — в поэтическом пересказе на языке
классической кавьи, в любви, с которой описаны игры Господа, и в немногих собственных добавлениях:
пролог на небесах (Земля у Брахмы, Брахма у Молочного океана), отождествления спутников (Вишну — Вишварупа,
Тумбуру — Рамананда), рассказ о том, как Младенец не брал грудь, пока Адвайта не посвятил Шачи в мантру,
подробные описания праздников Пури. Такие места оговорены в сносках.

**Издание.** Перевод сделан по изданию Шрилы Бхактисиддханты Сарасвати (Шри Вималапрасад Сиддханта
Сарасвати; первое издание — 427 г. эры Чайтаньи, 1913 г.), 4-е изд., Майяпур, Шри Чайтанья-матх, 2002
(скан — archive.org, `sri-gaura-krsnodayah`). Рукопись, как пишет Бхактисиддханта в кратком предисловии,
была найдена в княжестве Наягарх (Орисса) и передана ему Рай-сахибом Гаурашьямом Маханти; издатель хвалит
поэму за ясный санскрит и обилие поэтических украшений. Комментария и примечаний к тексту в издании нет;
переведена только поэма, предисловие издателя не переводилось.

**Принципы.** Перевод прозаический, по шлокам; номера — как в издании (благословляющая шлока Рупы Госвами
перед первой саргой обозначена 0). Пометки *[с. N]* — страницы PDF-скана. Текст набран бенгальским шрифтом
и известен нам по OCR, сверенному со сканом; испорченные места оговорены. В сносках — параллели с
«Чайтанья-чаритамритой» (ЧЧ), «Чайтанья-бхагаватой» (ЧБ), «Гаура-ганоддеша-дипикой» (ГГД) и богословские
пояснения в духе учения Шрилы Бхактисиддханты Сарасвати; там, где автор расходится с ЧЧ или с
гаудия-вайшнавским богословием, текст переведён как есть, а расхождение оговорено.

---

## Оглавление

"""),
    'en': dict(out='Gaura-Krishnodaya-en', title='Sri Gaura-krishnodaya',
               author='Govinda-deva (Eng. tr.)', preface="""# Sri Gaura-krishnodaya

*"The Rising of Gaura-Krishna"*

*A Sanskrit poem by Govinda-deva (1758)*

*Translated from the Sanskrit*

---

## Translator's note

The *Sri Sri Gaura-krishnodaya* is a Sanskrit mahakavya in eighteen cantos (about 1,100 verses) on the life of
Sri Chaitanya Mahaprabhu — from the causes of His descent to His departure. Its author, Govinda-deva
(Govinda Kavi), was a poet of Orissa who, according to the editor, belonged to the family (line) of
Vakreshvara Pandita, an associate of Mahaprabhu; the poem was completed in Shaka 1680 (1758 CE), in the
month of Ashvina. In the colophon of each canto the author calls himself "a bee intoxicated by the honey of
the lotus feet of Sri Gauranga."

**The value of the poem.** Govinda-deva writes more than two centuries after Mahaprabhu and follows Krishnadasa
Kaviraja's *Sri Chaitanya-charitamrita* almost throughout — he himself names it as his source ("the nectar of
His deeds," 1.4). As a historical source, therefore, the poem is secondary. Its value lies in its poetic
retelling in the language of classical kavya, in the love with which the Lord's pastimes are described, and in
a few additions of its own: a prologue in heaven (the Earth before Brahma, Brahma at the Milk Ocean),
identifications of the associates (Vishnu as Vishvarupa, Tumburu as Ramananda), the story of how the Infant
would not take the breast until Advaita initiated Shachi into the mantra, and detailed descriptions of the
festivals of Puri. Such passages are noted in the footnotes.

**The edition.** The translation follows the edition of Srila Bhaktisiddhanta Sarasvati (Sri Vimalaprasada
Siddhanta Sarasvati; first edition in the year 427 of the Chaitanya era, 1913), 4th ed., Mayapur, Sri
Chaitanya Math, 2002 (scan at archive.org, `sri-gaura-krsnodayah`). The manuscript, as Bhaktisiddhanta writes
in his brief preface, was found in the princely state of Nayagarh (Orissa) and given to him by Rai Sahib
Gaurashyama Mahanti; the editor praises the poem for its lucid Sanskrit and wealth of poetic ornament. The
edition contains no commentary or notes; only the poem is translated, and the editor's preface is not.

**Principles.** The translation is in prose, verse by verse; the numbers are those of the edition (Rupa
Gosvami's benedictory verse before the first canto is marked 0). The markers *[p. N]* give the pages of the
PDF scan. The text is printed in Bengali script and is known to us through OCR checked against the scan;
corrupt passages are noted. The footnotes give parallels with the *Chaitanya-charitamrita* (CC), the
*Chaitanya-bhagavata* (CB) and the *Gaura-ganoddesha-dipika* (GGD), and theological explanations in the
spirit of the teaching of Srila Bhaktisiddhanta Sarasvati; where the author departs from the CC or from Gaudiya
Vaishnava theology, the text is translated as it stands and the divergence is noted.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 19):
        key = f'{i:02d}'
        p = os.path.join(HERE, lang, key + '.md')
        if not os.path.exists(p):
            continue
        text = open(p, encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    md = m['preface'] + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, m['out'] + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, m['out'] + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, m['out'] + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks), 'sargas:', len(body))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
