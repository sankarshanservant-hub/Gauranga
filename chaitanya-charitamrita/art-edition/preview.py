#!/usr/bin/env python3
"""Превью разворотов из PDF: python3 -I preview.py [dpi] -> _prev/spread-XX.png (+ листы по 3 разворота)."""
import subprocess, sys, os, glob
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); dpi=int(sys.argv[1]) if len(sys.argv)>1 else 55
P=os.path.join(HERE,'_prev'); os.makedirs(P,exist_ok=True)
for f in glob.glob(P+'/*'): os.remove(f)
subprocess.run(['pdftoppm','-r',str(dpi),'-png',os.path.join(HERE,'Adi-01-illustrated.pdf'),P+'/p'],check=True)
pg=sorted(glob.glob(P+'/p-*.png')); ims=[Image.open(f).convert('RGB') for f in pg]
w,h=ims[0].size; spreads=[]
# стр.1 — правая; далее (2,3),(4,5)...
spreads.append((None,ims[0]))
for i in range(1,len(ims),2): spreads.append((ims[i], ims[i+1] if i+1<len(ims) else None))
out=[]
for k,(l,r) in enumerate(spreads):
    S=Image.new('RGB',(2*w+6,h),(90,90,90))
    if l: S.paste(l,(0,0))
    if r: S.paste(r,(w+6,0))
    S.save(f'{P}/spread-{k:02d}.png'); out.append(S)
for j in range(0,len(out),3):
    grp=out[j:j+3]; W=max(s.width for s in grp)
    sheet=Image.new('RGB',(W,sum(s.height+6 for s in grp)),(40,40,40)); y=0
    for s in grp: sheet.paste(s,(0,y)); y+=s.height+6
    sheet.save(f'{P}/sheet-{j//3:02d}.png')
print(len(ims),'pages',len(out),'spreads', w,h)
