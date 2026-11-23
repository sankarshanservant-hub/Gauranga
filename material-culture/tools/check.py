"""Проверка карточек material-culture/items/*.yaml: обязательные поля, уникальность id, перечни, изображения.
  python3 material-culture/tools/check.py        # проверка + сводка по рубрикам
  python3 material-culture/tools/check.py --json # + выгрузка export/items.json (для игры/сайта)
"""
import glob, json, os, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ROOT = os.path.dirname(BASE)
RUBRICS = {'home', 'kitchen', 'dress', 'rites', 'town', 'music', 'nature', 'puri', 'travel'}
EVID = {'epoch', 'later-reconstruction', 'hagiography'}
FREE = ('PD', 'CC0', 'CC-BY', 'CC-BY-SA', 'Open Access')
errs, items = [], []
for f in sorted(glob.glob(os.path.join(BASE, 'items', '*.yaml'))):
    data = yaml.safe_load(open(f, encoding='utf-8')) or []
    for it in data:
        it['_file'] = os.path.basename(f)
        items.append(it)
seen = {}
for it in items:
    i = it.get('id', '?')
    w = lambda m: errs.append(f"{it['_file']}: {i}: {m}")
    if not str(i).startswith('mc-'): w('id должен начинаться с mc-')
    if i in seen: w(f'повтор id (также в {seen[i]})')
    seen[i] = it['_file']
    for k in ('title', 'text'):
        v = it.get(k) or {}
        if not (v.get('ru') and v.get('en')): w(f'{k}: нужны ru и en')
    if it.get('rubric') not in RUBRICS: w(f"rubric {it.get('rubric')!r} не из {sorted(RUBRICS)}")
    if it.get('era_evidence') not in EVID: w(f"era_evidence {it.get('era_evidence')!r} не из {sorted(EVID)}")
    if not isinstance(it.get('hagiography', []), list): w('hagiography — список')
    if not isinstance(it.get('sources', []), list): w('sources — список')
    for im in it.get('images') or []:
        fp = os.path.join(ROOT, im.get('file', ''))
        if not im.get('file') or not os.path.exists(fp): w(f"нет файла изображения {im.get('file')}")
        elif os.path.getsize(fp) > 2 * 1024 * 1024: w(f"изображение > 2 МБ: {im['file']}")
        if not str(im.get('license', '')).startswith(FREE): w(f"лицензия {im.get('license')!r} не свободная?")
        for k in ('author', 'url'):
            if not im.get(k): w(f"изображение {im.get('file')}: нет {k}")
nosrc = [it.get('id') for it in items if not (it.get('hagiography') or it.get('sources'))]
for e in errs: print('ОШИБКА', e)
if nosrc: print(f'ВНИМАНИЕ: без единой ссылки (hagiography и sources пусты): {len(nosrc)} — {", ".join(nosrc)}')
by = {}
for it in items: by.setdefault(it.get('rubric'), []).append(it)
print(f'карточек: {len(items)}; изображений: {sum(len(it.get("images") or []) for it in items)}')
for r, l in sorted(by.items(), key=lambda x: str(x[0])):
    ev = {}
    for it in l: ev[it.get('era_evidence')] = ev.get(it.get('era_evidence'), 0) + 1
    print(f'  {r}: {len(l)}  ({", ".join(f"{k} {v}" for k, v in sorted(ev.items(), key=lambda x: str(x[0])))})')
if '--json' in sys.argv:
    os.makedirs(os.path.join(BASE, 'export'), exist_ok=True)
    out = [{k: v for k, v in it.items() if not k.startswith('_')} for it in items]
    json.dump(out, open(os.path.join(BASE, 'export', 'items.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('→ export/items.json')
sys.exit(1 if errs else 0)
