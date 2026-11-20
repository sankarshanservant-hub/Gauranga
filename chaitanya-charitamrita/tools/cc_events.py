# Кандидаты событий базы лил для главы ЧЧ: события и записи, у которых поле cc указывает на эту главу.
# Использование: python3 tools/cc_events.py Ади 1   (лила по-русски: Ади | Мадхья | Антья)
import yaml, glob, os, re, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lila-db')
lila, ch = sys.argv[1], sys.argv[2]
pat = re.compile(r'%s\s*%s(?![\d])' % (lila, ch))
ev = {}
for f in ['events.yaml'] + sorted(os.path.basename(x) for x in glob.glob(os.path.join(D, 'events-*.yaml'))):
    for e in yaml.safe_load(open(os.path.join(D, f), encoding='utf-8')) or []:
        ev[e['id']] = (e.get('title', ''), str(e.get('cc', '')), f)
hits = {k for k, (t, cc, f) in ev.items() if pat.search(cc)}
for f in glob.glob(os.path.join(D, 'lilas', '*.yaml')):
    for r in yaml.safe_load(open(f, encoding='utf-8')) or []:
        if pat.search(str(r.get('cc', ''))) and r.get('event') in ev: hits.add(r['event'])
for k in sorted(hits): print('%s | %s | cc: %s | %s' % (k, ev[k][0], ev[k][1], ev[k][2]))
print('— событий: %d' % len(hits))
