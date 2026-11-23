"""Добавить источники в карточки, не трогая форматирование YAML.
  python3 material-culture/tools/patch_sources.py patch.json
patch.json: {"mc-id": {"sources": [...], "todo": "новый текст" | null (удалить), "evidence_add_ru": "...", "evidence_add_en": "..."}}
"""
import glob, json, os, re, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def wrap(t, w=112):
    out, cur = [], ''
    for word in t.split():
        if len(cur) + len(word) + 1 > w: out.append(cur); cur = word
        else: cur = (cur + ' ' + word).strip()
    if cur: out.append(cur)
    return out


patch = json.load(open(sys.argv[1], encoding='utf-8'))
done = set()
for f in glob.glob(os.path.join(BASE, 'items', '*.yaml')):
    s = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^(?=- id: )', s)
    ch = False
    for k, p in enumerate(parts):
        m = re.match(r'- id: (\S+)', p)
        if not m or m[1] not in patch: continue
        d = patch[m[1]]; done.add(m[1])
        if d.get('sources'):
            src = json.dumps(d['sources'], ensure_ascii=False)
            m2 = re.search(r'(?ms)^  sources: (\[.*?\])\n(?=  [a-z_]+:)', p)
            old = json.loads(m2[1]) if m2 and m2[1].strip() != '[]' else []
            new = old + [x for x in d['sources'] if x not in old]
            body = ',\n            '.join(json.dumps(x, ensure_ascii=False) for x in new)
            p = p[:m2.start()] + f'  sources: [{body}]\n' + p[m2.end():]
        if 'todo' in d:
            p = re.sub(r'(?m)^  todo: .*\n?', '', p)
            if d['todo']:
                p = p.rstrip('\n') + '\n  todo: ' + json.dumps(d['todo'], ensure_ascii=False) + '\n'
                if not p.endswith('\n\n'): p += '\n'
        for lang in ('ru', 'en'):
            add = d.get(f'evidence_add_{lang}')
            if add:
                mm = re.search(rf'(?m)^  evidence_note:\n(?:    .*\n)*?    {lang}: (>-\n(?:      .*\n)+|".*"\n)', p)
                blk = mm[1]
                if blk.startswith('"'):
                    txt = json.loads(blk.strip())
                    nb = '>-\n' + '\n'.join('      ' + l for l in wrap(txt + ' ' + add)) + '\n'
                else:
                    lines = [l.strip() for l in blk.split('\n')[1:] if l.strip()]
                    nb = '>-\n' + '\n'.join('      ' + l for l in wrap(' '.join(lines) + ' ' + add)) + '\n'
                p = p[:mm.start(1)] + nb + p[mm.end(1):]
        parts[k] = p; ch = True
    if ch: open(f, 'w', encoding='utf-8').write(''.join(parts))
miss = set(patch) - done
if miss: print('не найдены:', sorted(miss))
print('обновлено:', len(done))

