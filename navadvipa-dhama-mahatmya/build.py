"""Собирает «Навадвипа-дхама-махатмью» и «Навадвипа-бхава-тарангу» (изд. Шри Чайтанья Сарасват Матха: RU 2001,
EN 2015) в MD, DOCX и PDF. Использует функции разбора и вёрстки из ../govinda-kadacha/build.py.
Запуск: python3 build.py [ru|en].
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

META = {
    'ru': dict(out='Navadvipa-Dhama-Mahatmya-ru', title='Навадвипа-дхама-махатмья',
               author='Шрила Бхактивинода Тхакур', front=['00-biography'], back=[], preface="""# Шри Навадвипа-дхама-махатмья

*и*

# Шри Навадвипа-бхава-таранга

*Шрила Бхактивинода Тхакур*

*Перевод Шри Чайтанья Сарасват Гаудия Матха*

---

## Об этом издании

«Шри Навадвипа-дхама-махатмья» («Слава Шри Навадвипа-дхамы», 1890) — бенгальская поэма Шрилы Бхактивиноды Тхакура:
Шри Нитьянанда Прабху ведёт Шри Дживу Госвами по девяти островам Навадвипы и на каждом месте открывает ему лилы
Шри Чайтаньи Махапрабху и Его спутников, игры прежних юг и тайну дхамы, неотличной от Вриндавана.
«Шри Навадвипа-бхава-таранга» («Волны экстаза Навадвипы», 1899) — парикрама самого Бхактивиноды: что он видит
духовным зрением на каждом месте дхамы.

Русский текст — перевод, изданный Шри Чайтанья Сарасват Гаудия Матхом (М.: Философская книга, 2001; пер. Д. Рогозы
с английского). Здесь он разбит по стихам с той же нумерацией, что и английский перевод Шри Чайтанья Сарасват
Матха 2015 г. (сделанный с бенгальского издания 1988 г.); стихи, которых в издании 2001 г. нет, переведены по
изданию 2015 г. и отмечены в сносках.

---

## Оглавление

"""),
    'en': dict(out='Navadvipa-Dhama-Mahatmya-en', title='Sri Navadvipa-dhama-mahatmya',
               author='Srila Bhakti Vinod Thakur',
               front=['00-translators-note', '00-publishers-notes', '00-ahvana', '00-preface', '00-vandana'],
               back=['20-gaura-krishna-tattva', '21-land-of-sweetness', '22-ten-offences', '23-glossary'],
               preface="""# Śrī Navadvīpa-dhāma-māhātmya

*and*

# Śrī Navadvīpa-bhāva-taraṅga

*Śrīla Bhakti Vinod Ṭhākur*

*Śrī Chaitanya Sāraswat Maṭh*

---

## About this edition

The text is that of Śrī Chaitanya Sāraswat Maṭh’s English edition of 2015 (translated from the Bengali edition of
1988). Here only the English prose translation of each verse is given, with the verse numbers of that edition;
where the edition gives one translation for two verses, the number is a range (e.g. 15–16).

---

## Contents

"""),
}


def read(lang, key):
    path = os.path.join(HERE, lang, key + '.md')
    if not os.path.exists(path): return None
    text = open(path, encoding='utf-8').read().strip()
    # уникальные метки сносок в сводном файле
    return re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)


def build(lang):
    m = META[lang]
    keys = m['front'] + [f'{i:02d}' for i in range(1, 20)] + m['back']
    toc, body = [], []
    for key in keys:
        text = read(lang, key)
        if text is None: continue
        if not text.startswith('#'): continue
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        # заголовки разделов внутри вводных статей — на уровень ниже заголовка статьи
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
