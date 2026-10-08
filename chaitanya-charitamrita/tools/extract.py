import re,json,glob,os,sys,html
d=sys.argv[1]; out={}
def sect(s,name):
    i=s.find('class="av-%s"'%name)
    if i<0: return []
    j=s.find('class="av-',i+10)
    seg=s[i:j]
    return [html.unescape(re.sub(r'<br ?/?>','\n',x)).replace('<em>','').replace('</em>','').strip() for x in re.findall(r'<div class="em-mb-4 em-leading-[78][^"]*">(.*?)</div>',seg,re.S)]
for f in glob.glob(d+'/*.html'):
    s=open(f,encoding='utf-8').read()
    k=os.path.basename(f)[:-5]
    out[k]={'bn':sect(s,'bengali') or sect(s,'devanagari'),'tr':sect(s,'verse_text')}
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print(len(out),[k for k,v in out.items() if not v['bn']],[k for k,v in out.items() if len(v['bn'])!=len(v['tr'])])
