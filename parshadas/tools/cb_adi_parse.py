#!/usr/bin/env python3
"""Разбор ЧБ Ади (chaitanya-bhagavata/src/txt/CB_Adi_all.txt — двухколоночная выгрузка PDF) в перевод по стихам:
chaitanya-bhagavata/src/txt/CB_Adi_verses.json {"глава.стих": "перевод"}. Колонки разводятся по позиции, глава — по
колонтитулу «глава N», перевод — первый абзац после транслитерации. Покрытие ~94 % стихов; при сомнении — файл-источник."""
import re, json
from pathlib import Path
SRC = Path(__file__).resolve().parents[2] / 'chaitanya-bhagavata/src/txt'
t=(SRC/'CB_Adi_all.txt').read_text(errors='replace')
pages=t.split('\f')
TR=re.compile(r'[№ЎЇ+={}\\%*’Ё]')
def segs(l):
    if not l.strip(): return None,None
    lead=len(l)-len(l.lstrip())
    if lead>=28: return None,(lead,l.strip())
    for mm in re.finditer(r'\S(\s{3,})(\S)',l):
        if 30<=mm.start(2)<=62 or (mm.start(2)<=80 and l[mm.start(2):].startswith('Стих')): return (lead,l[:mm.start(1)+1].strip()),(mm.start(2),l[mm.start(2):].strip())
    return (lead,l.strip()),None
stream=[]  # (chapter, indent_rel, text)
chap=0
for pg in pages:
    m=re.search(r'глава (\d+)\s*$',pg,re.M)
    if m: chap=int(m.group(1))
    L,R=[],[]
    for l in pg.splitlines():
        a,b=segs(l)
        L.append(a); R.append(b)
    for col in (L,R):
        xs=[s[0] for s in col if s]
        base=min(xs) if xs else 0
        for s in col:
            stream.append((chap,None) if s is None else (chap,(s[0]-base,s[1])))
        stream.append((chap,None))
verses={}; cur=None; buf=[]
def clean(s): return re.sub(r'(\w)- (\w)',r'\1\2',s)
def flush():
    if cur is None: return
    out=[]; started=False
    for it in buf:
        if it is None:
            if started and out[-1].rstrip().endswith(('.','!','?','»','”',']')): break
            continue
        ind,s=it
        if re.search(r'глава \d+$|^\d+$|^Стихи? \d+',s): continue
        if not started:
            if TR.search(s) or not re.match(r'^[«“"(\[]?[А-ЯЁ]',s): continue
            out.append(s); started=True
        else:
            if ind>=1 and out and out[-1].rstrip().endswith(('.','!','?','»','”',']')): break
            out.append(s)
    verses.setdefault(cur, clean(' '.join(out)))
for ch,it in stream:
    if it and re.match(r'^Стихи? (\d+)(?:\s*[–-]\s*\d+)?$',it[1]):
        flush(); cur=(ch,int(re.match(r'^Стихи? (\d+)',it[1]).group(1))); buf=[]
    elif cur: buf.append(it)
flush()
json.dump({f'{c}.{n}':v for (c,n),v in sorted(verses.items())},open(SRC/'CB_Adi_verses.json','w'),ensure_ascii=False,indent=0)
print(len(verses), 'стихов')
