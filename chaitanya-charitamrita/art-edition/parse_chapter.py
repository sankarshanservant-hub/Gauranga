#!/usr/bin/env python3
"""Разбор главы ЧЧ в формате ed/vcd/*.md (перевод Вриндавана Чандры даса) в структуру для вёрстки.

Каждый стих = блоки: бенгальский текст (॥ N ॥) → транслитерация с пословным (строки чередуются) → «(N) перевод».
Сдвоенные стихи — «(65–66)». Сноска [^N] — в конце файла.
"""
import re, json, sys

BENG = re.compile(r'[ঀ-৿]')


def clean(s):
    s = s.replace('　', ' ').replace('ﾠ', ' ').replace('ㅤ', ' ')
    return re.sub(r'[ \t]+', ' ', s).strip()


def parse(path, with_gloss=False):
    t = open(path, encoding='utf-8').read()
    # сноски
    notes = {}
    body = t
    for m in re.finditer(r'^\[\^(\w+)\]:\s*(.+)$', t, re.M):
        notes[m.group(1)] = m.group(2).strip()
    body = re.sub(r'^\[\^(\w+)\]:.*$', '', body, flags=re.M)
    body = re.sub(r'\n---\s*\n', '\n', body)
    blocks = [b for b in re.split(r'\n\s*\n', body.strip()) if b.strip()]
    head = [x.strip() for x in blocks[0].split('\n')]
    meta = {
        'book': head[0].strip('“”"'),
        'lila': head[1].strip(),
        'chapter': head[2].strip(),
        'title': head[3].strip('* ').strip(),
        'by': head[4].strip(),
    }
    verses = []
    bn, tl = [], []
    for b in blocks[1:]:
        lines = [clean(x) for x in b.split('\n') if x.strip()]
        m = re.match(r'^\((\d+)(?:[–-](\d+))?\)\s*(.*)$', b.strip(), re.S)
        if m:
            n1 = int(m.group(1)); n2 = int(m.group(2)) if m.group(2) else None
            tr = clean(m.group(3).replace('\n', ' '))
            fn = None
            fm = re.search(r'\[\^(\w+)\]', tr)
            if fm:
                fn = notes.get(fm.group(1)); tr = tr.replace(fm.group(0), '').strip()
            verses.append({
                'n': f'{n1}–{n2}' if n2 else str(n1), 'n1': n1,
                'bn': bn, 'tl': tl[0::2], 'gloss': tl[1::2] if with_gloss else [],
                'tr': tr, 'note': fn,
            })
            bn, tl = [], []
        elif BENG.search(b):
            bn += lines
        else:
            tl += lines
    assert not bn and not tl, 'хвост без перевода'
    return meta, verses


if __name__ == '__main__':
    meta, v = parse(sys.argv[1])
    print(meta, len(v))
    for x in v[:3]: print(json.dumps(x, ensure_ascii=False)[:400])
    bad = [x['n'] for x in v if len(x['tl']) * 2 != len(x['tl']) * 2 or not x['bn'] or not x['tl']]
    print('без bn/tl:', bad)
