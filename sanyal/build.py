"""Собирает русский перевод книги Саньяла «Sree Krishna Chaitanya» (1933) в MD, DOCX и PDF.
Вёрстка — ../govinda-kadacha/build.py, PDF — LibreOffice (как в ../rasika-mangala/build.py). Запуск: python3 build.py."""
import importlib.util, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rm', os.path.join(HERE, '..', 'rasika-mangala', 'build.py'))
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
FRONT = ['00-title', '00-publisher', '00-preface', '00-contents', '00-foreword']
VOL1 = [f'I-{i:02d}' for i in range(1, 10)]
VOL2 = ['II-00'] + [f'II-{i:02d}' for i in range(1, 25)]


def sec(name):
    t = open(os.path.join(HERE, 'ru', name + '.md'), encoding='utf-8').read()
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    defs = re.findall(r'(?m)^\[\^[^\]]+\]:.*$', t)                # сноски посреди текста — в конец раздела
    t = re.sub(r'(?m)^\[\^[^\]]+\]:.*\n?', '', t)
    t = re.sub(r'\n{3,}', '\n\n', t).strip() + ('\n\n' + '\n'.join(defs) if defs else '')
    return rm.prepare(t, name.replace('-', ''), 'ru')


def build():
    parts = [open(os.path.join(HERE, 'front-ru.md'), encoding='utf-8').read().rstrip()]
    toc = ['## Оглавление', '']
    for title, names in (('Шри Кришна Чайтанья', FRONT), ('Том I. Введение', VOL1), ('Том II', VOL2)):
        parts.append(f'# {title}')
        toc.append(f'**{title}**\n')
        for n in names:
            s = sec(n)
            parts.append(s)
            h = re.findall(r'(?m)^## (.+)$', s)
            toc += [f'- {x}' for x in h]
        toc.append('')
    md = parts[0] + '\n\n' + '\n'.join(toc) + '\n\n---\n\n' + '\n\n'.join(parts[1:]) + '\n'
    out = os.path.join(HERE, 'Sanyal-Sree-Krishna-Chaitanya-ru')
    open(out + '.md', 'w', encoding='utf-8').write(md)
    rm.kb.build_docx(rm.parse(md), out + '.docx')
    rm.lo_pdf(out + '.docx', out + '.pdf')
    print('ok', len(md.split()), 'слов')


if __name__ == '__main__':
    build()
