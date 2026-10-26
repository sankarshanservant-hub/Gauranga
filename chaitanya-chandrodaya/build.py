"""Собирает перевод «Шри Чайтанья-чандродаи» (акты 01–10) в MD, DOCX и PDF — русский (ru/) и английский (en/).
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en] (по умолчанию оба).
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

PREFACE_RU = """# Шри Чайтанья-чандродая

*«Восход луны Чайтаньи»*

*Драма в десяти актах Кави Карнапуры (Парамананды Сены)*

*Перевод с санскрита и пракрита на русский*

---

## От переводчика

«Шри Чайтанья-чандродая» (*Śrī-caitanya-candrodaya-nāṭaka*) — санскритская драма Кави Карнапуры, младшего сына
Шивананды Сены, написанная, по традиции, в 1572 г. (1494 г. эры Шака) по просьбе царя Ориссы Пратапарудры
(в прологе распорядитель говорит о его повелении поставить пьесу перед Джаганнатхой). Это одно из самых ранних
жизнеописаний Шри Чайтаньи: автор лично видел Махапрабху ребёнком, а Кришнадаса Кавираджа в «Чайтанья-чаритамрите»
прямо опирается на неё и цитирует её. Драма охватывает всю лилу Махапрабху — от нисшествия и игр в Навадвипе
до санньясы, жизни в Пури, путешествий на юг и во Вриндавану и ежегодных праздников колесниц; события перемежаются
сценами с аллегорическими лицами (Майтри, Према-бхакти, Вирага, Кали, Адхарма) и пьесой в пьесе (акт 3 —
«Дана-кели», разыгранная спутниками Господа в Навадвипе).

**Источник.** Электронный текст Gaudiya Grantha Mandira, составленный по изданиям М. Гухи (Навадвипа, 2-е изд., 1971)
и Р. Мишры (Варанаси, 1966). Сомнительные места сверены с изданием *Kāvyamālā* № 87 (Бомбей, Нирная-сагар, 1917);
пропуски электронного текста восполнены по нему (в квадратных скобках или с примечанием), важные разночтения
указаны в примечаниях. Анонимные заметки издания Гухи и примечания издателей не переводились.

**Принципы.** Переведены проза, стихи и ремарки; пракритные реплики (их говорят женщины, слуги, видушака)
переведены с пракрита с опорой на санскритскую чхаю; где говорящий на пракрите переходит на санскрит, это
отмечено, как в оригинале. Стихи даны прозой и пронумерованы внутри каждого акта.
Нумерация электронного текста местами сбита (пропущенные или повторённые номера, ненумерованные цитаты); в таких
случаях номера выровнены, по возможности по *Kāvyamālā*, что оговорено в примечаниях. Примечания переводчика
(реалии, игра слов, источники цитат, разночтения) — в конце каждого акта. Английские переводы не использовались.

**Английская версия** (`Chaitanya-Chandrodaya-en`) сделана с того же санскрита и пракрита параллельно с русским
переводом: нумерация стихов и примечания в обоих языках совпадают. Стихи драмы, приводимые в «Чайтанья-чаритамрите»,
сверены по смыслу с нашим переводом ЧЧ. Вслед за Шрилой Бхактисиддхантой Сарасвати описанные здесь игры Радхи и
Кришны и Шри Чайтаньи — неземные (*aprākṛta*): любовь гопи — према, а не мирская страсть, а Божества — сам Господь,
а не изваяния.

---

## Оглавление

"""


PREFACE_EN = """# Sri Chaitanya-chandrodaya

*"The Rising of the Moon of Chaitanya"*

*A drama in ten acts by Kavi Karnapura (Paramananda Sena)*

*Translated from the Sanskrit and Prakrit into English*

---

## Translator's Preface

The *Sri Chaitanya-chandrodaya* (*Śrī-caitanya-candrodaya-nāṭaka*) is a Sanskrit drama by Kavi Karnapura, the youngest
son of Shivananda Sena, written, according to tradition, in 1572 (Shaka 1494) at the request of Prataparudra, the
king of Orissa (in the prologue the stage-director speaks of his command to stage the play before Jagannatha). It is
one of the earliest lives of Sri Chaitanya: the author saw Mahaprabhu with his own eyes as a child, and Krishnadasa
Kaviraja in the *Chaitanya-charitamrita* relies on it directly and quotes it. The drama covers the whole lila of
Mahaprabhu — from His descent and His pastimes in Navadvipa to His sannyasa, His life in Puri, His journeys to the
south and to Vrindavana, and the yearly chariot festivals; the events are interwoven with scenes of allegorical
characters (Maitri, Prema-bhakti, Viraga, Kali, Adharma) and with a play within the play (Act 3, the "Dana-keli",
performed by the Lord's associates in Navadvipa).

**Source.** The electronic text of the Gaudiya Grantha Mandira, compiled from the editions of M. Guha (Navadvipa,
2nd ed., 1971) and R. Mishra (Varanasi, 1966). Doubtful passages have been checked against the *Kāvyamālā*
edition No. 87 (Bombay, Nirnaya-sagar, 1917); gaps in the electronic text have been filled from it (in square
brackets or with a note), and important variant readings are indicated in the notes. The anonymous notes of
Guha's edition and the editors' notes have not been translated.

**Principles.** The prose, the verses and the stage directions are translated; the Prakrit speeches (spoken by
women, servants and the vidushaka) are translated from the Prakrit with the help of the Sanskrit *chāyā*; where a
character who normally speaks Prakrit changes to Sanskrit, this is marked, as in the original. The verses are given
in prose and numbered within each act. The numbering of the electronic text is in places confused (missing or
repeated numbers, unnumbered quotations); in such cases the numbers have been aligned, where possible following the
*Kāvyamālā*, and this is noted. The translator's notes (realia, plays on words, sources of quotations, variant
readings) are given at the end of each act. Modern English translations of the drama have not been used.

**The English version** was made from the Sanskrit and Prakrit of the same source, in parallel with the Russian
translation of the project: the numbering of the verses and the notes coincide in both languages. Verses of the
drama quoted in the *Chaitanya-charitamrita* have been compared in sense with our translation of the CC. Following
Srila Bhaktisiddhanta Sarasvati, the pastimes of Radha and Krishna and of Sri Chaitanya described here are
transcendental (*aprākṛta*); the love of the gopis is prema, not worldly passion, and the Deities are the Lord
Himself, not images.

---

## Contents

"""

META = {
    'ru': dict(out='Chaitanya-Chandrodaya-ru', pre=PREFACE_RU, title='Шри Чайтанья-чандродая',
               author='Кави Карнапура (рус. пер.)'),
    'en': dict(out='Chaitanya-Chandrodaya-en', pre=PREFACE_EN, title='Sri Chaitanya-chandrodaya',
               author='Kavi Karnapura (English tr.)'),
}


def build(lang):
    m = META[lang]
    OUT = m['out']
    toc, body = [], []
    for i in range(1, 11):
        key = f'{i:02d}'
        text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        body.append(text)
    md = m['pre'] + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, OUT + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, OUT + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, OUT + '.pdf'), m['title'], m['author'])
    print(lang, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        build(lang)
