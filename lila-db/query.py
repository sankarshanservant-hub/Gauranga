"""Поиск по базе лил (по export/lilas.json; сначала python3 build.py).
Примеры:
  python3 query.py @jagai-madhai                 # по тегу спутника
  python3 query.py '#puri' theme:jagannatha      # место + тема (условия через И)
  python3 query.py bhava:radha source:murari-kcc
  python3 query.py period:P07 kind:teaching teaching:holy-name
  python3 query.py year:1510 age:24 auth:A       # попадает в диапазон / уровень не ниже A
  python3 query.py event:ev-jagai-madhai
  python3 query.py text:Сарвабхаума              # подстрока в title/summary/notes/ref
  python3 query.py ident:Вишакха                 # лилы с участием тех, кто в Кришна-лиле — Вишакха (по карточкам)
  python3 query.py who:@svarupa-damodara         # справка о лице: карточка, отождествления, связи, статья
  python3 query.py who:Вишакха                   # кто отождествляется с … (поиск по отождествлениям)
  python3 query.py ... -l                        # кратко: только id и название
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_people = None


def people():
    global _people
    if _people is None:
        f = os.path.join(HERE, 'export', 'persons.json')
        _people = {p['id']: p for p in json.load(open(f, encoding='utf-8'))} if os.path.exists(f) else {}
    return _people


def ident_match(v):
    """Теги лиц, у которых в отождествлениях (карточки parshadas/) есть подстрока v."""
    v = v.lower()
    return {t for t, p in people().items()
            if any(v in ' '.join(str(i.get(k, '')) for k in ('as', 'variants')).lower() for i in p.get('identities') or [])}


def who(q):
    ps = [people()[q]] if q in people() else [people()[t] for t in sorted(ident_match(q))]
    for p in ps:
        print(f"{p['id']} · {p['ru']} ({p['en']}){' · ' + p['note'] if p.get('note') else ''}")
        if p.get('summary'): print('   ', p['summary'])
        for i in p.get('identities') or []:
            print(f"    [{i.get('in')}] {i.get('as')} — {i.get('source', '')} ({i.get('level', '')})")
        rel = p.get('relations') or []
        if rel:
            by = {}
            for r in rel: by.setdefault(r['type'], []).append(r['who'])
            print('    связи:', '; '.join(f"{k}: {', '.join(v[:6])}{' …' if len(v) > 6 else ''}" for k, v in by.items()))
        art = p.get('article') or {}
        print(f"    лил: {len(p.get('lilas') or [])}, событий: {len(p.get('events') or [])}"
              f"{', статья: ' + art['ru'] if art.get('ru') else ''}")
    print(f'— найдено: {len(ps)}')


def match(e, c):
    if c.startswith('@'): return c in (e.get('persons') or [])
    if c.startswith('#'): return c in (e.get('places') or [])
    k, _, v = c.partition(':')
    if k in ('theme', 'themes'): return v in (e.get('themes') or [])
    if k in ('bhava', 'teaching'): return v in (e.get(k) or [])
    if k in ('source', 'period', 'kind', 'event'): return e.get(k) == v
    if k == 'auth': return (e.get('authority') or 'D') <= v
    if k in ('year', 'age'):
        r = e.get('years' if k == 'year' else 'age')
        return bool(r) and r[0] <= int(v) <= r[1]
    if k == 'scripture': return any(v.lower() in s.lower() for s in e.get('scriptures') or [])
    if k == 'ident':
        return bool(ident_match(v) & set(e.get('persons') or []))
    if k == 'text':
        hay = ' '.join(str(e.get(x, '')) for x in ('title', 'summary', 'notes', 'ref', 'parallels', 'divergence'))
        return v.lower() in hay.lower()
    raise SystemExit(f'неизвестное условие: {c}')


def main(args):
    short = '-l' in args
    conds = [a for a in args if a != '-l']
    if len(conds) == 1 and conds[0].startswith('who:'):
        return who(conds[0][4:])
    data = json.load(open(os.path.join(HERE, 'export', 'lilas.json'), encoding='utf-8'))
    res = [e for e in data if all(match(e, c) for c in conds)]
    for e in res:
        if short:
            print(e['id'], '·', e['title'])
        else:
            y = e.get('years'); a = e.get('age')
            print(f"{e['id']} [{e['period']}{' ' + str(y[0]) + '–' + str(y[1]) if y else ''}{' возр. ' + str(a[0]) + '–' + str(a[1]) if a else ''}] {e['title']}")
            print('   ', e['summary'])
            print('   ', e['source'], e['ref'], '·', e.get('file', ''), '·', ' '.join((e.get('themes') or []) + (e.get('persons') or []) + (e.get('places') or [])))
    print(f'— найдено: {len(res)}')


if __name__ == '__main__':
    main(sys.argv[1:])
