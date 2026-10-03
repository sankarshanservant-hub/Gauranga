"""Собирает русский перевод «Гаура-ганоддеша-дипики» (ru/01–03.md) в MD, DOCX и PDF.

Использует функции разбора и вёрстки из ../govinda-kadacha/build.py.
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

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

if __name__ == '__main__':
    toc, body = [], []
    for i in (1, 2, 3):
        text = open(os.path.join(HERE, 'ru', f'{i:02d}.md'), encoding='utf-8').read().strip()
        text = kb.re.sub(r'\[\^([^\]]+)\]', lambda m: f'[^{i:02d}-{m.group(1)}]', text)
        title = text.splitlines()[0].lstrip('# ').strip()
        sub = kb.re.search(r'^\*([^*\[].+)\*$', text, kb.re.M)
        toc.append(f'- {title} — {sub.group(1)}' if sub else f'- {title}')
        body.append(text)
    md = PREFACE + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    open(os.path.join(HERE, OUT + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, OUT + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, OUT + '.pdf'), 'Шри Гаура-ганоддеша-дипика', 'Кави Карнапура (рус. пер.)')
    print('ok', len(blocks))
