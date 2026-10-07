"""For each bhanita line of a contemporary in file, check whether the line occurs in reference corpora."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bnorm import skel, grams
NAMES = ['বাসুঘোষ','বাসুদেবঘোষ','নরহরি','মুরারিগুপ্ত','শিবানন্দ','বংশীবদন','বসুরামানন্দ','পরমানন্দ','গৌরীদাস','গোবিন্দঘোষ','মাধবঘোষ','নয়নানন্দ','যদুনাথ','শঙ্করঘোষ','বাসুদেবদত্ত','পরমেশ্বর','কানুরাম','চৈতন্যদাস','অনন্তদাস','রায়অনন্ত','চন্দ্রশেখর','রামচন্দ্র']
NK = [skel(n) for n in NAMES]
G = re.compile('গৌর|গোরা|শচী|নদীয়া|নদিয়া|চৈতন্|নিতাই|নিত্যানন্দ|বিশ্বম্ভর|নিমাই|গদাধর|অদ্বৈত|সন্ন্যাস|নীলাচল|শ্রীবাস')
src = sys.argv[1]
refs = sys.argv[2:]
idx = []
for r in refs:
    for l in open(r, encoding='utf-8', errors='replace'):
        g = grams(l)
        if len(g) > 6: idx.append(g)
L = open(src, encoding='utf-8', errors='replace').read().split('\n')
for i, l in enumerate(L):
    k = skel(l)
    if not any(n in k for n in NK):
        continue
    ctx = '\n'.join(L[max(0, i - 14):i + 1])
    if not G.search(ctx):
        continue
    q = grams(l)
    if len(q) < 6: continue
    best = max((len(q & g) / len(q) for g in idx), default=0)
    if best < 0.6:
        print(f'{os.path.basename(src)}:{i+1} [{best:.2f}] {l.strip()[:100]}')
