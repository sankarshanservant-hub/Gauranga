# Порция 18: вариант sweep_signatures.py — печатает ВСЕ пады ГПТ1 с подписью по шаблону в диапазоне печатных страниц (без фильтра по каталогу)
# и лучшие совпадения с переводами (T) и каталогом (C): python3 -I sweep_signatures_range.py 255 360 "NH=নরহর|নরহয|নবহরি"
# Сверка подписей ГПТ1 (порции 14–15): python3 -I sweep_signatures.py "VG=বাসু|বাস্থ" "KD=কানু" ...
# Порция 15: окно подписи — 5 последних строк (часть пад кончается сносками), больше вариантов OCR в заголовках «N পদ».
# Печатает пады ГПТ1, у которых подпись (в двух последних строках) совпала с шаблоном, а первой строки нет ни в padas/bn/*.md, ни в CATALOG.md.
# Нужен bnorm.py из этой же папки (sim).
import re,sys,glob
sys.path.insert(0,'/home/user/Gauranga/sources/padas/tesseract/scripts')
from bnorm import sim
L=open('/home/user/Gauranga/sources/padas/tesseract/gpt1.txt',encoding='utf-8').read().split('\n')
hdr=re.compile(r'^\s*[\S]{1,6}\s*(প[দব]্?্?|পন্দ|পঙ্দ|পদ্দ|পদ্র|গদর|গ্দ|প্র)\s*[\s।|.,!]')
tr=[]
for f in sorted(glob.glob("/home/user/Gauranga/padas/bn/*.md")):
    T=open(f,encoding="utf-8").read()
    for m in re.finditer(r"^### (\d+)\.1\nBN:\n(.+)$",T,re.M): tr.append((f.split('/')[-1][:2]+"."+m.group(1),m.group(2)))
cat=open('/home/user/Gauranga/padas/CATALOG.md',encoding='utf-8').read().split('\n')
firsts=[(r.split('|')[1].strip(),r.split('|')[2].strip()) for r in cat if r.startswith('| ') and len(r.split('|'))>3]
padas=[];cur=None;pg=0
for i,l in enumerate(L):
    if i<10350: continue
    if l.startswith('=== gpt1 p'): pg=int(l[10:])-259; continue
    if hdr.match(l):
        cur={'line':i+1,'pg':pg,'h':l.strip(),'t':[]}; padas.append(cur); continue
    if cur is None or not l.strip(): continue
    s=l.strip()
    if re.match(r'^[\(\[]?[০-৯0-9]+[\)।\s]',s) or 'পাঠা' in s or 'পাঠী' in s or 'তরঙ্গিণী' in s or 'তরজ' in s or 'পদ-তর' in s or len(s)<12: continue
    cur['t'].append(s)
PMIN,PMAX=int(sys.argv[1]),int(sys.argv[2]);sys.argv=sys.argv[2:]
pats=dict(a.split('=',1) for a in sys.argv[1:])
for p in padas:
    if not p['t']: continue
    tail=' '.join(p['t'][-5:])
    for k,pat in pats.items():
        if re.search(pat,tail):
            first=p['t'][0]
            bt=max(((sim(first,f),c) for c,f in tr), default=(0,''))
            bc=max(((sim(first,f),c) for c,f in firsts if f), default=(0,''))
            if PMIN<=p["pg"]<=PMAX:
                print(f"{p['h'][:14]:14s} {k} T[{bt[0]:.2f} {bt[1]:6s}] C[{bc[0]:.2f} {bc[1]:7s}] p{p['pg']:4d} L{p['line']:<6d} {first[:45]} || {re.findall('.{0,20}(?:'+pat+').{0,12}',tail)[:1]}")
