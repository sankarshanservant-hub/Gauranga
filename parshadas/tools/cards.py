#!/usr/bin/env python3
"""Карточки паршад: проверка и выгрузка (формат — parshadas/CARDS.md).
Проверяет parshadas/cards/*.yaml: тег лица и все @-теги — в lila-db/PERSONS.md, #-теги — в PLACES.md,
события ev-… — в lila-db/events*.yaml, номера F/Q/I — в parshadas/facts/<тег>.md (реестр самого лица; чужой
реестр — как "@тег:F12"), типы связей — из списка ниже.
Собирает parshadas/export/persons.json, relations.json (рёбра графа), identities.json.
Запуск: python3 parshadas/tools/cards.py [-q]"""
import json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'parshadas'
REL_TYPES = set('''father mother spouse son daughter sibling relative grandfather grandmother uncle aunt nephew niece
in-law guru disciple siksha-guru siksha-disciple sannyasa-guru sannyasa-disciple friend companion servant served-by
met opposed ruler-of subject-of deity-served lineage-predecessor lineage-successor neighbor host guest patron
protege co-worker other'''.split())
KINDS = set('associate family guru acharya opponent ruler deity other'.split())

def tags(path, ch):
    return set(re.findall(rf'^\| ({re.escape(ch)}[\w\-]+) \|', (ROOT / path).read_text(), re.M))

PERSONS, PLACES = tags('lila-db/PERSONS.md', '@'), tags('lila-db/PLACES.md', '#')
EVENTS = {m for f in (ROOT / 'lila-db').glob('events*.yaml') for m in re.findall(r'^- id: (ev-[\w\-]+)', f.read_text(), re.M)}
_facts = {}
def fact_ids(tag):
    if tag not in _facts:
        f = P / 'facts' / f'{tag.lstrip("@")}.md'
        _facts[tag] = set(re.findall(r'^([FQI]\d+[a-z]?)\.', f.read_text(), re.M)) if f.exists() else None
    return _facts[tag]

def walk(x, path=''):
    if isinstance(x, dict):
        for k, v in x.items(): yield from walk(v, f'{path}.{k}' if path else k)
    elif isinstance(x, list):
        for i, v in enumerate(x): yield from walk(v, f'{path}[{i}]')
    else:
        yield path, x

def check(card, fname):
    errs, me = [], card.get('id', '')
    if me not in PERSONS: errs.append(f'id {me!r} нет в PERSONS.md')
    if f'{me.lstrip("@")}.yaml' != fname: errs.append(f'имя файла должно быть {me.lstrip("@")}.yaml')
    if card.get('kind') and card['kind'] not in KINDS: errs.append(f'kind {card["kind"]!r} не из {sorted(KINDS)}')
    for r in card.get('relations') or []:
        if r.get('type') not in REL_TYPES: errs.append(f'relations: тип {r.get("type")!r} не из списка (cards.py REL_TYPES)')
    for path, v in walk(card):
        if not isinstance(v, str): continue
        key = path.split('.')[-1].split('[')[0]
        for t in re.findall(r'(?<![\w:])@[a-z][\w\-]*', v):
            if t not in PERSONS: errs.append(f'{path}: тег {t} нет в PERSONS.md')
        for t in re.findall(r'(?<![\w&])#[a-z][\w\-]*', v):
            if t not in PLACES: errs.append(f'{path}: место {t} нет в PLACES.md')
        for t in re.findall(r'\bev-[\w\-]+', v):
            if t not in EVENTS: errs.append(f'{path}: событие {t} нет в lila-db/events*.yaml')
        if key == 'facts' or re.fullmatch(r'(@[\w\-]+:)?[FQI]\d+[a-z]?', v):
            m = re.fullmatch(r'(?:(@[\w\-]+):)?([FQI]\d+[a-z]?)', v)
            if not m: errs.append(f'{path}: {v!r} — ожидается F12 / Q3 / I1 / @тег:F12'); continue
            owner = m.group(1) or me; ids = fact_ids(owner)
            if ids is None: errs.append(f'{path}: нет реестра facts/{owner.lstrip("@")}.md')
            elif m.group(2) not in ids: errs.append(f'{path}: пункта {m.group(2)} нет в facts/{owner.lstrip("@")}.md')
    return errs

def main():
    quiet = '-q' in sys.argv
    files = sorted((P / 'cards').glob('*.yaml'))
    persons, rels, idents, allerr = [], [], [], []
    for f in files:
        try: card = yaml.safe_load(f.read_text()) or {}
        except yaml.YAMLError as e: allerr.append(f'{f.name}: YAML: {e}'); continue
        allerr += [f'{f.name}: {e}' for e in check(card, f.name)]
        persons.append(card)
        for r in card.get('relations') or []:
            rels.append({'from': card.get('id'), **r})
        for i in card.get('identities') or []:
            idents.append({'person': card.get('id'), **i})
    out = P / 'export'; out.mkdir(exist_ok=True)
    for name, data in (('persons', persons), ('relations', rels), ('identities', idents)):
        (out / f'{name}.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
    if allerr: print('\n'.join(allerr))
    if not quiet or allerr: print(f'{len(files)} карточек, {len(rels)} связей, {len(idents)} отождествлений; ошибок: {len(allerr)}')
    sys.exit(1 if allerr else 0)

if __name__ == '__main__':
    main()
