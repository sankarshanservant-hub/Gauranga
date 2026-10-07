"""scanbh.py mode file  -- list padas whose bhanita names a contemporary poet.
mode: ps (split at ॥ N ॥) | kgc (split at (N) headings)"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bnorm import skel
POETS = {
    'Васу Гхош': ['বাসুঘোষ', 'বাসুদেবঘোষ', 'বাসুদেবঘোষে', 'বাসুঘোষে', 'বাসুকহে', 'বাসুভনে'],
    'Нарахари': ['নরহরি'],
    'Мурари': ['মুরারিগুপ্ত', 'মুরারিগুপতে', 'দাসমুরারি', 'মুরারিকহে', 'কহেমুরারি'],
    'Шивананда': ['শিবানন্দ', 'শিবাই'],
    'Вамши': ['বংশীবদন', 'বংশীদাস', 'বংশীকহে', 'বংশীবদনে'],
    'Рамананда': ['রামানন্দ'],
    'Парамананда': ['পরমানন্দ'],
    'Гауридас': ['গৌরীদাস'],
    'Говинда Гхош': ['গোবিন্দঘোষ'],
    'Мадхава Гхош': ['মাধবঘোষ'],
    'Кришнадас': ['কৃষ্ণদাস'],
    'Чандрашекхара': ['চন্দ্রশেখর'],
    'Рамачандра': ['রামচন্দ্র'],
    'Баларама': ['বলরাম'],
    'Наянананда': ['নয়নানন্দ'],
    'Йадунандана/Йадунатх': ['যদুনন্দন', 'যদুনাথ'],
    'Вриндаван Дас': ['বৃন্দাবনদাস'],
    'Лочан': ['লোচন'],

    'Ананта': ['অনন্তদাস', 'অনন্তআচার্য', 'দাসঅনন্ত', 'রায়অনন্ত', 'অনন্তকহে'],
    'Кану': ['কানুদাস', 'কানুরাম'],
    'Чайтаньядас': ['চৈতন্যদাস'],
    'Парамешвара': ['পরমেশ্বর'],
    'Шанкара Гхош': ['শঙ্করঘোষ'],
    'Васудева Датта': ['বাসুদেবদত্ত'],
    'Пурушоттама': ['পুরুষোত্তম'],
    'Гададхар': ['গদাধরদাস'],
    'Девакинандана': ['দেবকীনন্দন'],
}
PSK = {p: [skel(n) for n in ns] for p, ns in POETS.items()}
G = re.compile('গৌর|গোরা|গোর|শচী|নদীয়া|নদিয়া|নদীয|চৈতন্|চৈতন্ত|নিতাই|নিত্যানন্দ|বিশ্বম্ভর|নিমাই|গদাধর|অদ্বৈত|সন্ন্যাস|নীলাচল|শ্রীবাস|সুরধুনী|স্থরধুনী')
mode, path = sys.argv[1], sys.argv[2]
text = open(path, encoding='utf-8', errors='replace').read()
lines = text.split('\n')
if mode == 'kgc':
    starts = [i for i, l in enumerate(lines) if re.match(r'^\s*\(\s*[০-৯]{1,2}\s*\)\s*$', l)]
    chunks = [(a, starts[k + 1] if k + 1 < len(starts) else len(lines)) for k, a in enumerate(starts)]
else:
    ends = [i for i, l in enumerate(lines) if re.search(r'[॥|]\s*[০-৯]{1,3}\s*[॥|]', l)]
    chunks = [(a + 1, b + 1) for a, b in zip([-1] + ends, ends)]
for a, b in chunks:
    seg = [l for l in lines[a:b] if l.strip() and not l.startswith('===')]
    if not seg:
        continue
    tail = seg[-6:] if mode == 'kgc' else seg[-3:]
    tk = skel(' '.join(tail))
    hits = [p for p, ks in PSK.items() if any(k in tk for k in ks)]
    if not hits:
        continue
    joined = '\n'.join(seg)
    g = 'G' if G.search(joined) else '-'
    # bhanita line: last line containing a name
    bl = ''
    for l in reversed(seg):
        if any(k in skel(l) for p in hits for k in PSK[p]):
            bl = l.strip(); break
    first = ' / '.join(x.strip() for x in seg[:3])[:160]
    print(f'{os.path.basename(path)}:{a+1}-{b} [{g}] {",".join(hits)} || {first} || BH: {bl[:120]}')
