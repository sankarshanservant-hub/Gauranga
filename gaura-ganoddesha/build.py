"""Собирает русский перевод «Гаура-ганоддеша-дипики» (ru/01–03.md) в MD, DOCX и PDF.

Использует функции разбора и вёрстки из ../govinda-kadacha/build.py.
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)
spec2 = importlib.util.spec_from_file_location('cc', os.path.join(HERE, '..', 'chaitanya-chandramrita', 'build.py'))
cc = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(cc)

OUT = 'Gaura-Ganoddesha-Dipika-ru'
PREFACE = """# Шри Гаура-ганоддеша-дипика

*«Светильник, указывающий спутников Гауры»*

*Кави Карнапура (1576)*

*Перевод с санскрита на русский*

---

## От переводчика

«Гаура-ганоддеша-дипика» — санскритское сочинение Кави Карнапуры (Парамананды Даса, Пуридаса),
младшего сына Шивананды Сена, одного из ближайших спутников Шри Чайтаньи. Книга закончена,
согласно её последней шлоке, в 1498 г. Шака (1576 г. н. э.). Она перечисляет спутников
Махапрабху, Нитьянанды и Адвайты и указывает, кем каждый из них был в играх Кришны во Врадже
(а также в Двараке, Матхуре, Айодхье и на небесах). Это главный источник гаудия-вайшнавской
традиции о «прежних обликах» спутников Чайтаньи.

**Источник.** Санскритский текст взят из издания Gaudiya Vedanta Publications (2008); его
текстовый слой в шрифтовой кодировке Kruti Dev перекодирован в Юникод. Переведён **только
санскритский текст Кави Карнапуры**; хинди-перевод и комментарий издания не использовались и
не воспроизводятся. Нумерация шлок — по этому изданию (в нём шлоки 10–22 и 194–207 объединены
в группы). Места, где извлечённый текст неполон, оговорены в примечаниях.

---

## Оглавление

"""

PREFACE_FULL = PREFACE.replace('*Перевод с санскрита на русский*',
    '*Перевод с санскрита на русский*\n\n*Санскритский текст, транслитерация и пословный перевод*').replace('## Оглавление',
    """**Полная версия.** Для каждой шлоки даны санскритский текст деванагари (выверенный: ошибки перекодировки
из шрифта Kruti Dev исправлены по метру, грамматике и изображениям страниц издания), транслитерация IAST,
пословный перевод и перевод.

---

## Оглавление""")


def build(out, preface, full=False):
    toc, body = [], []
    for i in (1, 2, 3):
        text = open(os.path.join(HERE, 'ru', f'{i:02d}.md'), encoding='utf-8').read().strip()
        text = kb.re.sub(r'\[\^([^\]]+)\]', lambda m: f'[^{i:02d}-{m.group(1)}]', text)
        title = text.splitlines()[0].lstrip('# ').strip()
        sub = kb.re.search(r'^\*([^*\[].+)\*$', text, kb.re.M)
        toc.append(f'- {title} — {sub.group(1)}' if sub else f'- {title}')
        if full:
            text = cc.with_skt(text, cc.load_skt(os.path.join(HERE, 'skt')))
        body.append(text)
    md = preface + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), 'Шри Гаура-ганоддеша-дипика', 'Кави Карнапура (рус. пер.)')
    print(out, 'ok', len(blocks))


if __name__ == '__main__':
    build(OUT, PREFACE)
    if os.path.isdir(os.path.join(HERE, 'skt')) and any(f.startswith('s0') for f in os.listdir(os.path.join(HERE, 'skt'))):
        build(OUT + '-full', PREFACE_FULL, full=True)
