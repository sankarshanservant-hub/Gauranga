"""Собирает перевод «Бхакти-ратнакары» (ru/en, тараги 01–15 — сколько готово) в MD, DOCX и PDF.
Использует функции разбора и вёрстки из ../govinda-kadacha/build.py. Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Bhakti-Ratnakara-ru', title='Бхакти-ратнакара', author='Нарахари Чакраварти (рус. пер.)', preface="""# Бхакти-ратнакара

*«Океан драгоценностей бхакти»*

*Поэма Нарахари Чакраварти (Гханашьямы Даса)*

*Перевод с бенгальского на русский*

---

## От переводчика

«Бхакти-ратнакара» — бенгальская поэма Нарахари Чакраварти (Гханашьямы Даса), вриндаванского вайшнава
XVIII в., в пятнадцати «волнах» (тарангах). В центре её — жизнь Шринивасы Ачарьи, Нароттамы Тхакура и Шьямананды,
но через их историю Нарахари рассказывает и о Госвами Вриндавана, и о многих спутниках Шри Чайтаньи, описывает
обход Враджа-мандалы (5-я волна) и Навадвипы (12-я волна), приводит множество санскритских шлок и пад.

**Источник.** Второе издание (Муршидабад, Радхараман-пресс, ред. Расабихари Санкхьятиртха, 1912–1913) по двум
сканам, для таранг 1–9 сверенное с первым изданием (Берхампур, 1888); оба — общественное достояние. Издание
Гаудия-миссии (1960) привлекалось только для сверки чтений; его примечания и переводы шлок не использовались.
Переведён **только текст поэмы**.

**Нумерация.** В старых изданиях двустишия не нумерованы, поэтому принята нумерация издания Гаудия-миссии
(общепринятая система ссылок); двустишия, которых там нет, отмечены буквой (371a), пропуски оговорены в
примечаниях.

**Принципы.** Двустишия-паяры переведены построчно, без рифмы; трипади, пады и санскритские шлоки идут под одним
номером. Испорченные места и источники цитат оговорены в примечаниях переводчика в конце каждой таранги.

---

## Оглавление

"""),
    'en': dict(out='Bhakti-Ratnakara-en', title='Bhakti-ratnakara', author='Narahari Chakravarti (Eng. tr.)', preface="""# Bhakti-ratnakara

*"The Ocean of the Jewels of Bhakti"*

*A poem by Narahari Chakravarti (Ghanashyama Dasa)*

*Translated from the Bengali*

---

## Translator's note

The *Bhakti-ratnakara* is a Bengali poem in fifteen "waves" (tarangas) by Narahari Chakravarti (Ghanashyama Dasa),
a Vaishnava of Vrindavana in the eighteenth century. At its centre are the lives of Srinivasa Acharya, Narottama
Thakura and Shyamananda, but through their story Narahari also tells of the Gosvamis of Vrindavana and of many
associates of Sri Chaitanya, describes the circuit of Vraja-mandala (the fifth wave) and of Navadvipa (the twelfth
wave), and quotes a great number of Sanskrit verses and songs.

**Source.** The second edition (Murshidabad, Radharaman Press, ed. Rasabihari Sankhyatirtha, 1912–1913) in two
scans, collated for tarangas 1–9 with the first edition (Berhampur, 1888); both are in the public domain. The
Gaudiya Mission edition (1960) was consulted only to check readings; its notes and translations of the Sanskrit
verses were not used. **Only the poem itself** is translated.

**Numbering.** The old editions do not number the couplets, so the numbering of the Gaudiya Mission edition (the
customary system of reference) is followed; couplets absent there are marked with a letter (371a), and omissions
are noted.

**Principles.** The payar couplets are translated line by line, without rhyme; tripadi stanzas, songs and Sanskrit
verses are numbered as single units. Corrupt passages and the sources of quotations are noted in the translator's
notes at the end of each taranga.

---

## Contents

"""),
}


def build(lang):
    m = META[lang]
    toc, body = [], []
    for i in range(1, 16):
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
