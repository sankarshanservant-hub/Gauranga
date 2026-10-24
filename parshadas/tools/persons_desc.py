#!/usr/bin/env python3
"""Короткая справка о лице из его карточки (parshadas/cards/<тег>.yaml) — для lila-db/PERSONS.md и сайта.

В столбце «Также / кто это» PERSONS.md поддерживается отрезок `{карточка: …}`: отождествление, гуру, родина,
явление и уход, самадхи. Остальной текст столбца не трогается; отрезок пересобирается при каждом запуске
(его вызывает cards.py), так что править его руками не нужно — правится карточка.
Запуск отдельно: python3 parshadas/tools/persons_desc.py [--check]  (--check — только показать, что изменится)"""
import re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
PERSONS = ROOT / 'lila-db' / 'PERSONS.md'
PLACES = ROOT / 'lila-db' / 'PLACES.md'
SEG = re.compile(r'\s*(?:·\s*)?\{карточка: [^{}]*\}')
IN_RU = {'krishna-lila': 'в Кришна-лиле', 'rama-lila': 'в Рама-лиле', 'other-avatara': 'в лиле аватары',
         'tattva': 'по таттве', 'other': ''}

def names(path, ch):
    out = {}
    for l in path.read_text().splitlines():
        m = re.match(rf'^\| ({re.escape(ch)}[\w\-]+) \| ([^|]+) \|', l)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out

def short(s, n=70):
    s = re.sub(r'\s*\([^()]*\)', '', str(s or ''))
    s = re.split(r'\s*[(;]|\s+≠\s+|\s+—\s+только', s)[0].strip(' ,.')
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + '…'

def summary(card, P, L):
    parts = []
    ids = [i for i in card.get('identities') or [] if i.get('in') in IN_RU and i.get('as')]
    ids.sort(key=lambda i: (i.get('in') != 'krishna-lila', i.get('level') or 'Z'))
    if ids:
        i = ids[0]
        src = f' ({short(i["source"], 20)})' if i.get('source') else ''
        more = ' и др.' if len(ids) > 1 else ''
        parts.append(f'{IN_RU[i["in"]]} — {short(i["as"], 50)}{src}{more}'.strip(' —'))
    gurus = [r['who'] for r in card.get('relations') or [] if r.get('type') in ('guru', 'sannyasa-guru')]
    if gurus:
        parts.append('гуру — ' + ', '.join(P.get(g, g) for g in dict.fromkeys(gurus)))
    orig = [p.rstrip('?') for p in (card.get('origin') or {}).get('places') or []]
    if orig:
        parts.append('происхождение — ' + L.get(orig[0], orig[0]))
    life = card.get('life') or {}
    for k, lab in (('appearance', 'явление'), ('disappearance', 'уход')):
        t = (life.get(k) or {}).get('tithi')
        if t:
            parts.append(f'{lab} — {short(t)}')
    sam = [s.get('place', '').rstrip('?') for s in life.get('samadhi') or [] if s.get('place')]
    if sam:
        parts.append('самадхи — ' + ', '.join(L.get(s, s) for s in sam))
    return '; '.join(parts)

def update(check=False):
    P, L = names(PERSONS, '@'), names(PLACES, '#')
    cards = {}
    for f in sorted((ROOT / 'parshadas' / 'cards').glob('*.yaml')):
        c = yaml.safe_load(f.read_text()) or {}
        if c.get('id'):
            cards[c['id']] = c
    lines, changed = PERSONS.read_text().split('\n'), 0
    for n, l in enumerate(lines):
        m = re.match(r'^(\| (@[\w\-]+) \|[^|]*\|[^|]*\|)([^|]*)\|\s*$', l)
        if not m or m.group(2) not in cards:
            continue
        s = summary(cards[m.group(2)], P, L)
        rest = SEG.sub('', m.group(3)).strip()
        col = ' · '.join(x for x in (rest, f'{{карточка: {s}}}' if s else '') if x)
        new = f'{m.group(1)} {col} |'
        if new != l:
            changed += 1
            if check:
                print(new)
            lines[n] = new
    if not check and changed:
        PERSONS.write_text('\n'.join(lines))
    return changed

def info(card, P, L):
    """Сводка для сайта (lila-db/export/persons.json)."""
    return {'summary': summary(card, P, L)}

if __name__ == '__main__':
    n = update('--check' in sys.argv)
    print(f'PERSONS.md: обновлено строк — {n}')
