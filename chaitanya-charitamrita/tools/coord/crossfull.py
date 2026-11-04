#!/usr/bin/env python3
# Найти сквозные стихи главы: полные (FULL) и частичные (part) совпадения строк бенгальского текста ed/vcd/CC_<Гл>.md
# с уже выверенными главами ed/vcd-rev/. Запуск из chaitanya-charitamrita/: python3 tools/coord/crossfull.py Madhya23
import re,sys,glob,os
D='০১২৩৪৫৬৭৮৯'
def norm(l): return re.sub(r'[\s\-’‘,—;:!?“”"\'ঃ]','',re.sub(r'॥.*','',l)).strip('৷।')
def blocks(f):
    s=open(f).read().partition('\n---\n')[0]; out={}
    for p in s.split('\n\n'):
        ms=re.findall(r'॥\s*([০-৯]+)\s*॥',p)
        if ms and any('ঀ'<=c<='৿' for c in p):
            lines=[norm(l) for l in p.split('\n') if any('ঀ'<=c<='৿' for c in l)]
            n='-'.join(str(int(''.join(str(D.index(c)) for c in m))) for m in ms)
            out[n]=lines
    return out
ch=sys.argv[1]; me=blocks('ed/vcd/CC_%s.md'%ch)
idx={}
for f in sorted(x for x in glob.glob('ed/vcd-rev/CC_*.md') if os.path.basename(x)[3:-3]!=ch):
    c=os.path.basename(f)[3:-3]
    for n,ls in blocks(f).items():
        for l in ls: idx.setdefault(l,[]).append((c,n))
for n,ls in me.items():
    common=None
    for l in ls:
        s=set(idx.get(l,[]))
        common=s if common is None else common&s
    part=[x for l in ls for x in idx.get(l,[])]
    if common: print(n,'FULL',sorted(common)[:4])
    elif part: print(n,'part',sorted(set(part))[:3], '%d/%d'%(sum(1 for l in ls if l in idx),len(ls)))
