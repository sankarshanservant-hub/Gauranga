"""Проверяет базу лил (теги, периоды, источники) и собирает TIMELINE.md. Запуск: python3 build.py"""
import glob, os, re, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))


def table_col(path, pat):
    return set(re.findall(pat, open(os.path.join(HERE, path), encoding='utf-8').read(), re.M))


PERSONS = table_col('PERSONS.md', r'^\| (@[a-z0-9-]+) \|')
PLACES = table_col('PLACES.md', r'^\| (#[a-z0-9-]+) \|')
SOURCES = table_col('SOURCES.md', r'^\| ([a-z0-9-]+) \|')
PERIODS = dict(re.findall(r'^\| (P\d\d|PX) \| ([^|]+) \|', open(os.path.join(HERE, 'PERIODS.md'), encoding='utf-8').read(), re.M))
KINDS = {'lila', 'pre-advent', 'prophecy', 'vision', 'teaching', 'miracle', 'post-advent', 'author'}


def load():
    entries, errors, ids = [], [], set()
    for f in sorted(glob.glob(os.path.join(HERE, 'lilas', '*.yaml'))):
        data = yaml.safe_load(open(f, encoding='utf-8')) or []
        for e in data:
            where = f"{os.path.basename(f)}:{e.get('id')}"
            for k in ('id', 'source', 'ref', 'period', 'title', 'summary', 'persons', 'places', 'kind', 'authority'):
                if k not in e: errors.append(f'{where}: нет поля {k}')
            if e.get('id') in ids: errors.append(f'{where}: повтор id')
            ids.add(e.get('id'))
            if e.get('source') not in SOURCES: errors.append(f"{where}: неизвестный источник {e.get('source')}")
            if e.get('period') not in PERIODS: errors.append(f"{where}: неизвестный период {e.get('period')}")
            if e.get('kind') not in KINDS: errors.append(f"{where}: неизвестный kind {e.get('kind')}")
            if e.get('authority') not in ('A', 'B', 'C', 'D'): errors.append(f'{where}: authority A/B/C/D')
            for t in e.get('persons') or []:
                if t not in PERSONS: errors.append(f'{where}: тег {t} не в PERSONS.md')
            for t in e.get('places') or []:
                if t not in PLACES: errors.append(f'{where}: тег {t} не в PLACES.md')
            entries.append(e)
    return entries, errors


def build():
    entries, errors = load()
    for x in errors: print('ОШИБКА', x)
    order = list(PERIODS)
    entries.sort(key=lambda e: (order.index(e['period']) if e['period'] in order else 99, e.get('order') or 0, e['source'], e['id']))
    out = ['# Временная шкала лил Шри Чайтаньи (сводка)', '',
           '*Собрано автоматически из `lilas/*.yaml` скриптом `build.py`; не править вручную.*', '',
           f'Всего записей: {len(entries)}.', '']
    cur = None
    for e in entries:
        if e['period'] != cur:
            cur = e['period']; out += ['', f"## {cur}. {PERIODS.get(cur, '').strip()}", '']
        date = f" ({e['date']})" if e.get('date') else ''
        out.append(f"- **{e['title']}**{date} — {e['summary']}  ")
        meta = f"  `{e['id']}` · {e['source']}, {e['ref']} · ур. {e['authority']} · {' '.join(e.get('persons') or [])} · {' '.join(e.get('places') or [])}"
        if e.get('parallels'): meta += f" · ср.: {e['parallels']}"
        if e.get('notes'): meta += f" · *{e['notes']}*"
        out.append(meta)
    open(os.path.join(HERE, 'TIMELINE.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(len(entries), 'записей;', len(errors), 'ошибок')
    return not errors


if __name__ == '__main__':
    sys.exit(0 if build() else 1)
