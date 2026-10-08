import json,re,sys,unicodedata
sys.path.insert(0,sys.path[0]); from cyr import conv
BD='০১২৩৪৫৬৭৮৯'
def bnum(n): return ''.join(BD[int(c)] for c in str(n))
def normbn(s):
    s=unicodedata.normalize('NFC',s)
    s=s.replace('য়','য়').replace('ড়','ড়').replace('ঢ়','ঢ়')
    s=re.sub('র্([বতযমজদ])(?!্)',r'র্\1্\1',s)
    s=s.replace('“','').replace('”','')
    s=s.replace('।','৷')
    return s
def clean_tr(t):
    t=t.replace('“','').replace('”','')
    return t
def load(path,overrides=None):
    d=json.load(open(path)); ch={}
    for k,v in d.items():
        c=int(k.split('-')[0]); nums=[int(x) for x in k.split('-')[1:]]
        bns=v['bn']; trs=v['tr']
        if overrides and k in overrides: bns=overrides[k]
        group=nums if len(nums)>1 else None
        for i,n in enumerate(range(nums[0],nums[-1]+1)):
            ch.setdefault(c,[]).append({'n':n,'bn':bns[i] if i<len(bns) else '','tr':trs[i] if i<len(trs) else '','group':group})
    for c in ch: ch[c].sort(key=lambda e:e['n'])
    return ch
def tr_lines(e):
    out=[]
    e['_trparts']=[]
    c,_=conv(clean_tr(e['tr']),e['bn'])
    for line in c.split('\n'):
        for part in line.split(' '):
            p=part.strip()
            if p: out.append(p); e['_trparts'].append(p)
    return out

def blen(x): return sum(1 for c in x if not unicodedata.combining(c))
E='  '
ISW=re.compile('[অ-হড়-য়]')
def strip_d(x):
    x=x.strip()
    x=re.sub(r'\s*[৷।॥]+(’?)\s*$',r'\1',x)
    x=re.sub(r'\s*ধ্রু\s*[৷।॥]*\s*$','',x)
    return x.strip()
def bn_lines(e,ntr,override=None):
    if override is not None:
        lines=list(override)
    else:
        b=normbn(e['bn']).strip()
        for _ in range(3): b=re.sub(r'\s*[॥৷।]*\s*[০-৯]+\s*[॥৷।]+\s*(ধ্রু\s*[॥৷।]*\s*)?$','',b)
        b=re.sub(r'\s*[০-৯]+\s*[॥৷।]+\s*(ধ্রু\s*[॥৷।]*)?\s*',' ',b)  # inner stray numbers
        b=re.sub(r'\s*[০-৯]+\s*$','',b)
        flat=' '.join(x.strip() for x in b.split('\n') if x.strip())
        btok=flat.split()
        parts=e.get('_trparts',[])
        tcounts=[len([w for w in p.split() if re.search('[a-zа-яё]',w)]) for p in parts]
        bw=[i for i,w in enumerate(btok) if ISW.search(w)]
        if not parts or sum(tcounts)!=len(bw):
            e['warn']='tokens %d vs %d'%(sum(tcounts),len(bw))
            lines=[x.strip() for x in b.split('\n') if x.strip()] or ['[?]']
            lines=[re.sub(r'\s*[৷।]\s*$','',x) for x in lines]
            if ntr==6 and len(lines)<=2:
                flat=' '.join(lines)
                chs=[x.strip() for x in re.findall(r'.+?(?:[,?!]’?(?=\s)|$)',flat) if x.strip()]
                chs=[strip_d(x) for x in chs]
                if len(chs)==6:
                    lines=[chs[0]+' '+chs[1], E+chs[2]+' ৷', chs[3]+' '+chs[4], E+chs[5]]; e['warn']+=' (comma split)'
            elif ntr==4 and len(lines)==2 and sum(blen(x) for x in parts)/4>26:
                # long sanskrit meter: split each line at pada boundary
                out=[]
                for li,x in enumerate(lines):
                    pa,pb=parts[2*li],parts[2*li+1]
                    m=re.search(r'-\s',x)
                    if m: k=m.end()
                    else:
                        target=len(x)*len(pa)/(len(pa)+len(pb))
                        sp=[i for i,c in enumerate(x) if c==' ']
                        k=min(sp,key=lambda i:abs(i-target))+1 if sp else len(x)
                    out+= [x[:k].strip(), E+E+x[k:].strip()]
                lines=out
                lines[1]=lines[1]+' ৷'
            elif len(lines)==2:
                lines[0]=lines[0]+' ৷'
        else:
            cuts=[];acc=0
            for k in tcounts[:-1]:
                acc+=k; cuts.append(bw[acc])
            ch=[];prev=0
            for ci in cuts: ch.append(strip_d(' '.join(btok[prev:ci]))); prev=ci
            ch.append(strip_d(' '.join(btok[prev:])))
            tri=lambda p: p.rstrip().endswith((',','!','?'))
            if ntr==6:
                lines=[ch[0]+' '+ch[1], E+ch[2]+' ৷', ch[3]+' '+ch[4], E+ch[5]]
            elif ntr==4 and tri(parts[1]) and tri(parts[2]) and not tri(parts[0]) is None:
                lines=[E+ch[0]+' ৷', ch[1]+' '+ch[2], E+ch[3]]
            elif ntr==4:
                lines=[ch[0]+' '+ch[1]+' ৷', ch[2]+' '+ch[3]]
            elif ntr==2:
                lines=[ch[0]+' ৷', ch[1]]
            elif ntr==1:
                lines=[ch[0]]
            else:
                lines=[' '.join(ch)]; e['warn']='ntr %d'%ntr
    lines=[re.sub(r'([?!]’?)\s*৷$',r'\1',x) for x in lines]
    lines[-1]=lines[-1]+' ॥ %s ॥'%bnum(e['n'])
    return lines
