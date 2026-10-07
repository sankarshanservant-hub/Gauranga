"""Проверяет базу лил и собирает: TIMELINE.md (для чтения), export/lilas.json и export/events.json (для сайта,
приложения и поиска; см. query.py). Запуск: python3 build.py"""
import glob, json, os, re, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
BIRTH = 1486


def read(path):
    return open(os.path.join(HERE, path), encoding='utf-8').read()


def table_col(path, pat):
    return set(re.findall(pat, read(path), re.M))


def section_codes(path, title):
    """Коды из первого столбца таблицы в разделе '## title…'."""
    t = read(path)
    m = re.search(r'^## ' + re.escape(title) + r'.*?$(.*?)(?=^## |\Z)', t, re.M | re.S)
    return set(re.findall(r'^\| ([a-z0-9-]+) \|', m.group(1), re.M)) - {'Код'} if m else set()


PERSONS = table_col('PERSONS.md', r'^\| (@[a-z0-9-]+) \|')
PLACES = table_col('PLACES.md', r'^\| (#[a-z0-9-]+) \|')
SOURCES = {c: a for c, a in re.findall(r'^\| ([a-z0-9-]+) \|[^|]*\|[^|]*\| ([A-D]) \|', read('SOURCES.md'), re.M)}
PERIODS, PERIOD_YEARS = {}, {}
for code, name, rest in re.findall(r'^\| (P\d\d|PX) \| ([^|]+) \|(.*)$', read('PERIODS.md'), re.M):
    PERIODS[code] = name.strip()
    y = re.findall(r'(\d{4})–(\d{4})', rest.split('|')[-2] if rest.count('|') >= 2 else '')
    if y: PERIOD_YEARS[code] = [int(y[0][0]), int(y[0][1])]
KINDS = {'lila', 'pre-advent', 'prophecy', 'vision', 'teaching', 'miracle', 'post-advent', 'author'}
THEMES = section_codes('THEMES.md', 'Темы')
BHAVAS = section_codes('THEMES.md', 'Бхава')
TEACHINGS = section_codes('THEMES.md', 'Темы учения')
CONF = {'точно', 'вероятно', 'оценка', ''}
LISTS = ('persons', 'places', 'themes', 'bhava', 'teaching', 'scriptures')


def check_common(e, where, errors):
    if e.get('period') not in PERIODS: errors.append(f"{where}: неизвестный период {e.get('period')}")
    for k in LISTS:
        if k in e and not isinstance(e[k], list): errors.append(f'{where}: {k} должен быть списком')
    for t in e.get('persons') or []:
        if t not in PERSONS: errors.append(f'{where}: тег {t} не в PERSONS.md')
    for t in e.get('places') or []:
        if t not in PLACES: errors.append(f'{where}: тег {t} не в PLACES.md')
    for k, reg in (('themes', THEMES), ('bhava', BHAVAS), ('teaching', TEACHINGS)):
        for t in e.get(k) or []:
            if t not in reg: errors.append(f'{where}: {k}: {t} нет в THEMES.md')
    for k in ('years', 'age'):
        v = e.get(k)
        if v not in (None, '', []) and not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) for x in v)):
            errors.append(f'{where}: {k} — [от, до] целыми числами')
    if e.get('date_conf', '') not in CONF: errors.append(f"{where}: date_conf — точно/вероятно/оценка")


def load_events(errors):
    data = yaml.safe_load(read('events.yaml')) or []
    ev = {}
    for e in data:
        where = f"events.yaml:{e.get('id')}"
        for k in ('id', 'title', 'period'):
            if k not in e: errors.append(f'{where}: нет поля {k}')
        if e.get('id') in ev: errors.append(f'{where}: повтор id')
        check_common(e, where, errors)
        ev[e.get('id')] = e
    return ev


def load(errors, events):
    entries, ids = [], set()
    for f in sorted(glob.glob(os.path.join(HERE, 'lilas', '*.yaml'))):
        data = yaml.safe_load(open(f, encoding='utf-8')) or []
        for e in data:
            where = f"{os.path.basename(f)}:{e.get('id')}"
            for k in ('id', 'source', 'ref', 'period', 'title', 'summary', 'persons', 'places', 'kind', 'authority'):
                if k not in e: errors.append(f'{where}: нет поля {k}')
            if e.get('id') in ids: errors.append(f'{where}: повтор id')
            ids.add(e.get('id'))
            if e.get('source') not in SOURCES: errors.append(f"{where}: неизвестный источник {e.get('source')}")
            if e.get('kind') not in KINDS: errors.append(f"{where}: неизвестный kind {e.get('kind')}")
            if e.get('authority') not in ('A', 'B', 'C', 'D'): errors.append(f'{where}: authority A/B/C/D')
            if e.get('event') and e['event'] not in events: errors.append(f"{where}: событие {e['event']} нет в events.yaml")
            check_common(e, where, errors)
            entries.append(e)
    return entries


def resolve(e, ev):
    """Итоговые годы/возраст: своё значение → событие → период."""
    r = dict(e)
    for k in ('years', 'age', 'date_conf', 'date_basis', 'calendar', 'cc', 'cb'):
        if not r.get(k) and ev and ev.get(k): r[k] = ev[k]
    if not r.get('years') and r.get('period') in PERIOD_YEARS:
        r['years'] = PERIOD_YEARS[r['period']]
        if not r.get('date_conf'): r['date_conf'] = 'оценка'
        r['years_from'] = 'period'
    if not r.get('age') and r.get('years') and r['years'][0] >= BIRTH:
        r['age'] = [max(0, r['years'][0] - BIRTH), r['years'][1] - BIRTH]
    return r


def build():
    errors = []
    events = load_events(errors)
    entries = load(errors, events)
    for x in errors: print('ОШИБКА', x)
    order = list(PERIODS)
    key = lambda e: (order.index(e['period']) if e.get('period') in order else 99, e.get('order') or 0, e.get('source', ''), e['id'])
    entries.sort(key=key)
    full = [resolve(e, events.get(e.get('event'))) for e in entries]
    # засвидетельствованность события = число разных источников
    by_event = {}
    for e in full:
        if e.get('event'): by_event.setdefault(e['event'], []).append(e)
    for e in full:
        srcs = {x['source'] for x in by_event.get(e.get('event'), [e])}
        e['attestation'] = len(srcs)
    os.makedirs(os.path.join(HERE, 'export'), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, 'export', 'lilas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    evout = []
    for eid, ev in events.items():
        ev = resolve(dict(ev), None)
        ev['entries'] = [x['id'] for x in by_event.get(eid, [])]
        ev['sources'] = sorted({x['source'] for x in by_event.get(eid, [])})
        evout.append(ev)
    json.dump(evout, open(os.path.join(HERE, 'export', 'events.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    meta = {'periods': PERIODS, 'period_years': PERIOD_YEARS, 'sources': SOURCES, 'themes': sorted(THEMES),
            'bhava': sorted(BHAVAS), 'teaching': sorted(TEACHINGS), 'persons': sorted(PERSONS), 'places': sorted(PLACES)}
    json.dump(meta, open(os.path.join(HERE, 'export', 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    out = ['# Временная шкала лил Шри Чайтаньи (сводка)', '',
           '*Собрано автоматически из `lilas/*.yaml` и `events.yaml` скриптом `build.py`; не править вручную.*', '',
           f'Всего записей: {len(full)}; событий: {len(events)}.', '']
    cur = None
    for e in full:
        if e['period'] != cur:
            cur = e['period']; out += ['', f"## {cur}. {PERIODS.get(cur, '')}", '']
        when = []
        if e.get('date'): when.append(e['date'])
        if e.get('years') and e.get('years_from') != 'period':
            y = e['years']; when.append(f"{y[0]}" if y[0] == y[1] else f"{y[0]}–{y[1]}")
            if e.get('age'): a = e['age']; when.append(f"возраст {a[0]}" if a[0] == a[1] else f"возраст {a[0]}–{a[1]}")
        date = f" ({'; '.join(when)})" if when else ''
        out.append(f"- **{e['title']}**{date} — {e['summary']}  ")
        meta = f"  `{e['id']}` · {e['source']}, {e['ref']} · ур. {e['authority']}"
        for k in ('themes', 'bhava', 'teaching'):
            if e.get(k): meta += f" · {k}: {', '.join(e[k])}"
        meta += f" · {' '.join(e.get('persons') or [])} · {' '.join(e.get('places') or [])}"
        if e.get('event'): meta += f" · событие `{e['event']}` ({e['attestation']} ист.)"
        if e.get('parallels'): meta += f" · ср.: {e['parallels']}"
        if e.get('divergence'): meta += f" · расхождение: {e['divergence']}"
        if e.get('notes'): meta += f" · *{e['notes']}*"
        out.append(meta)
    open(os.path.join(HERE, 'TIMELINE.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(len(full), 'записей;', len(events), 'событий;', len(errors), 'ошибок')
    return not errors


if __name__ == '__main__':
    sys.exit(0 if build() else 1)
