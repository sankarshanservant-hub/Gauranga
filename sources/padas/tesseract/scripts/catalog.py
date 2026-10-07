import re, json, sys
rows = []
sec = None
for l in open('/home/user/Gauranga/padas/CATALOG.md', encoding='utf-8'):
    if l.startswith('## ') or l.startswith('### '):
        sec = l.strip('# \n')
    m = re.match(r'^\| ([А-ЯЁ]{2}-\d{3}) \|', l)
    if not m:
        continue
    c = [x.strip() for x in l.strip().strip('|').split('|')]
    pk = re.findall(r'(?<![\d.])≈?(\d{1,4})(?= \(т\.|\s*\(т|$|;|,)', c[3]) if len(c) > 3 else []
    rows.append({'id': c[0], 'first': c[1], 'gpt': c[2], 'pk': c[3], 'pknums': [int(x) for x in re.findall(r'(\d{1,4}) \(т\. ?\d', c[3])] + [int(x) for x in re.findall(r'^≈?(\d{1,4})\b', c[3])], 'other': c[4], 'sec': sec})
json.dump(rows, open(sys.argv[1], 'w'), ensure_ascii=False, indent=0)
print(len(rows))
allpk = sorted({n for r in rows for n in r['pknums']})
print(len(allpk))
