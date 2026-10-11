#!/usr/bin/env python3
"""Проверка покрытия: каждый пункт реестра facts/<тег>.md (F…, Q…, I…) упомянут в метках <!-- … --> статей
ru/<тег>.md и en/<тег>.md; меток на несуществующие пункты нет. Запуск: python3 parshadas/check.py [тег …]"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ID = re.compile(r'^([FQI]\d+[a-z]?)\.', re.M)
MARK = re.compile(r'<!--(.*?)-->', re.S)
TOKEN = re.compile(r'\b([FQI]\d+[a-z]?)\b')


def check(tag):
    errs = []
    fp = ROOT / 'facts' / f'{tag}.md'
    if not fp.exists():
        return [f'{tag}: нет facts/{tag}.md']
    ids = ID.findall(fp.read_text(encoding='utf-8'))
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errs.append(f'{tag}: повторяются номера в реестре: {" ".join(sorted(dup))}')
    ids = set(ids)
    for lang in ('ru', 'en'):
        ap = ROOT / lang / f'{tag}.md'
        if not ap.exists():
            errs.append(f'{tag}: нет {lang}/{tag}.md')
            continue
        used = set()
        for m in MARK.findall(ap.read_text(encoding='utf-8')):
            used |= set(TOKEN.findall(m))
        if miss := sorted(ids - used, key=lambda s: (s[0], int(re.sub(r'\D', '', s)))):
            errs.append(f'{tag} [{lang}]: не покрыты: {" ".join(miss)}')
        if extra := sorted(used - ids):
            errs.append(f'{tag} [{lang}]: метки без пункта в реестре: {" ".join(extra)}')
    return errs


def main():
    tags = sys.argv[1:] or sorted(p.stem for p in (ROOT / 'facts').glob('*.md'))
    errs = [e for t in tags for e in check(t)]
    print('\n'.join(errs) if errs else f'OK: {len(tags)} лиц, все пункты покрыты')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
