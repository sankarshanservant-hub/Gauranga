"""Собирает файлы статей о спутниках для чтения/печати: <Name>-<lang>.md, .docx и .pdf (движок ../govinda-kadacha/build.py).
Исходники — parshadas/<lang>/<тег>.md; служебные метки <!-- F… --> снимаются.
Имя файла берётся из уже собранного RU-файла с тем же тегом (<Name>-ru.md, строка «· @тег»), иначе — из заголовка EN.
Запуск: python3 parshadas/build_en.py [en|ru] [тег ...]
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)


def names_by_tag():
    out = {}
    for f in os.listdir(HERE):
        m = re.match(r'(.+)-ru\.md$', f)
        if not m:
            continue
        head = open(os.path.join(HERE, f), encoding='utf-8').read(600)
        t = re.search(r'·\s*(@[\w-]+)', head)
        if t:
            out[t.group(1)[1:]] = m.group(1)
    return out


def clean(md):
    md = re.sub(r'[ \t]*<!--.*?-->', '', md, flags=re.S)
    return re.sub(r'\n{3,}', '\n\n', md)


def for_engine(md):
    """Для движка: id сносок с префиксом ([^1] → [^a-1]) и абзацы прозы в одну строку (без жёстких переносов)."""
    md = re.sub(r'\[\^([^\]]+)\]', lambda m: f'[^a-{m.group(1)}]', md)
    out = []
    paras = []
    for para in re.split(r'\n\s*\n', md):          # заголовок, за которым сразу идёт текст, — отдельным абзацем
        ls = para.strip('\n').splitlines()
        while ls and ls[0].startswith('#') and len(ls) > 1:
            paras.append(ls[0]); ls = ls[1:]
            if ls and ls[0].startswith('*') and ls[0].endswith('*') and not ls[0].startswith('**'):
                paras.append(ls[0]); ls = ls[1:]
        paras.append('\n'.join(ls))
    for para in paras:
        lines = [l.rstrip() for l in para.strip('\n').splitlines() if l.strip()]
        if not lines:
            continue
        special = lines[0].startswith(('#', '|', '>', '[^', '- ', '* ', '---')) or all(l.lstrip().startswith('|') for l in lines)
        if special and not lines[0].startswith('[^'):
            out.append('\n'.join(lines))
        elif lines[0].startswith('[^'):            # сноски: каждая с новой строки, продолжения склеить
            notes = []
            for l in lines:
                if re.match(r'^\[\^[^\]]+\]:', l) or not notes:
                    notes.append(l)
                else:
                    notes[-1] += ' ' + l.strip()
            out.append('\n'.join(notes))
        else:
            out.append(' '.join(l.strip() for l in lines))
    return '\n\n'.join(out) + '\n'


def build(lang, tags=None):
    names = names_by_tag()
    src = os.path.join(HERE, lang)
    done = []
    for f in sorted(os.listdir(src)):
        if not f.endswith('.md'):
            continue
        tag = f[:-3]
        if tags and tag not in tags:
            continue
        md = clean(open(os.path.join(src, f), encoding='utf-8').read())
        name = names.get(tag)
        if not name:
            title = re.search(r'^#\s+(.+)$', md, re.M).group(1)
            name = re.sub(r'[^A-Za-z0-9]+', '-', re.sub(r'^(Sri|Srila|Shri)\s+', '', title)).strip('-')
        base = os.path.join(HERE, f'{name}-{lang}')
        open(base + '.md', 'w', encoding='utf-8').write(md)
        blocks = kb.parse(for_engine(md))
        title = re.search(r'^#\s+(.+)$', md, re.M).group(1)
        kb.build_docx(blocks, base + '.docx')
        kb.build_pdf(blocks, base + '.pdf', title, '')
        done.append(name)
    return done


if __name__ == '__main__':
    lang = sys.argv[1] if len(sys.argv) > 1 else 'en'
    res = build(lang, set(sys.argv[2:]) or None)
    print(f'{lang}: {len(res)} files')
