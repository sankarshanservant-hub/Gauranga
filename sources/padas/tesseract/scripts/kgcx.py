"""Cross-reference KGC gaura/nitai padas of contemporaries with the catalog."""
import re, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bnorm import skel, grams
ORD = [('ঊনত্রিংশ', 29), ('উনত্রিংশ', 29), ('অষ্টাবিংশ', 28), ('সপ্তবিংশ', 27), ('ষড়্বিংশ', 26), ('ষড়বিংশ', 26), ('পঞ্চবিংশ', 25),
       ('চতুর্বিংশ', 24), ('ত্রয়োবিংশ', 23), ('দ্বাবিংশ', 22), ('একবিংশ', 21), ('ঊনবিংশ', 19), ('উনবিংশ', 19), ('অষ্টাদশ', 18),
       ('সপ্তদশ', 17), ('ষোড়শ', 16), ('পঞ্চদশ', 15), ('চতুর্দশ', 14), ('ত্রয়োদশ', 13), ('দ্বাদশ', 12), ('একাদশ', 11),
       ('ত্রিংশ', 30), ('বিংশ', 20), ('দশম', 10), ('নবম', 9), ('অষ্টম', 8), ('সপ্তম', 7), ('ষষ্ঠ', 6), ('পঞ্চম', 5), ('চতুর্থ', 4),
       ('তৃতীয়', 3), ('দ্বিতীয়', 2), ('প্রথম', 1)]
ORDK = [(skel(w), n) for w, n in ORD]
path = sys.argv[1]
lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
cat = json.load(open(sys.argv[2]))
catg = [(r['id'], grams(r['first'])) for r in cat]
KEEP = set(sys.argv[3].split(','))
kshan = [0] * len(lines)
cur = 0
for i, l in enumerate(lines):
    if 'ক্ষণদ' in l or 'ক্ষণ দ' in l or 'ক্ষণদা' in l:
        k = skel(l.split('ক্ষণ')[0])
        for w, n in ORDK:
            if k.endswith(w):
                cur = n; break
    kshan[i] = cur
for rec in open(sys.argv[4], encoding='utf-8'):
    m = re.match(r'\S+:(\d+)-(\d+) \[(.)\] ([^|]+)\|\|', rec)
    a, b, g, poets = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4).strip()
    if g != 'G' or not (set(poets.split(',')) & KEEP):
        continue
    seg = [l.strip() for l in lines[a - 1:b] if l.strip()]
    num = re.sub(r'[^০-৯]', '', seg[0])
    body = [l for l in seg[1:] if len(l) > 12][:2]
    fl = ' / '.join(body)
    gq = grams(' '.join(body))
    best = max(((len(gq & cg) / max(1, min(len(gq), len(cg))), cid) for cid, cg in catg if cg), default=(0, ''))
    hdr = ' '.join(seg[1:3])
    print(f'{kshan[a-1]}.{num}\t{a}\t{poets}\t{hdr[:40]}\t{fl[:110]}\t{best[1] if best[0]>=0.55 else "-"}\t{best[0]:.2f}')
