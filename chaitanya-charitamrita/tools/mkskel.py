# vedabase json -> skeleton json per chapter (bn lines, translit lines)
import json,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from gen import load,tr_lines,bn_lines
src,outdir=sys.argv[1],sys.argv[2]
ch=load(src)
ov={}
if len(sys.argv)>3 and os.path.exists(sys.argv[3]): ov=json.load(open(sys.argv[3]))
for c in sorted(ch):
    res=[]
    for e in ch[c]:
        t=tr_lines(e)
        k='%d-%d'%(c,e['n'])
        if k in ov and 'tr' in ov[k]: t=ov[k]['tr']
        b=bn_lines(e,len(t),ov[k]['bn'] if k in ov and 'bn' in ov[k] else None)
        if k in ov: e['warn']=''
        res.append({'n':e['n'],'group':e['group'],'bn':b,'tr':t,'warn':e.get('warn','')})
    json.dump(res,open(os.path.join(outdir,'antya%d.json'%c),'w'),ensure_ascii=False,indent=1)
    print(c,len(res),sum(1 for r in res if r['warn']))
