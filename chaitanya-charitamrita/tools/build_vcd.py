# Сборка vcd/new/CC_AntyaNN.md из скелета (бенгальский + транслитерация) и файла перевода (пословный + перевод).
# Использование: python3 build_vcd.py 16 [17 ...]
# Скелет: vcd/new/work/antyaNN.json (tools/mkskel.py). Перевод: vcd/new/work/fillNN.txt:
#   @title Название главы
#   @N            (или @N-M для сдвоенных стихов)
#   пословный к 1-й строке транслитерации (слова через два пробела)
#   ...
#   = перевод (может продолжаться на следующих строках)
#   @notes
#   [^1]: текст сноски
import json,re,sys,os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','vcd','new')
def parse_fill(path):
    title='';items=[];notes=[];cur=None;mode=None
    for raw in open(path,encoding='utf-8').read().split('\n'):
        l=raw.rstrip()
        if l.startswith('@title'): title=l[6:].strip(); continue
        if l.startswith('@notes'): mode='notes'; cur=None; continue
        m=re.match(r'^@(\d+)(?:-(\d+))?\s*$',l)
        if m:
            a=int(m.group(1)); b=int(m.group(2) or a)
            cur={'a':a,'b':b,'ww':[],'tr':''}; items.append(cur); mode='ww'; continue
        if mode=='notes':
            if l.strip(): notes.append(l)
            continue
        if cur is None: continue
        if l.startswith('='):
            mode='tr'; cur['tr']=l[1:].strip(); continue
        if mode=='tr':
            if l.strip(): cur['tr']+=' '+l.strip()
            continue
        if l.strip(): cur['ww'].append(l.strip())
    return title,items,notes
def br(lines): return '  \n'.join(lines)
def build(c):
    sk={v['n']:v for v in json.load(open(os.path.join(D,'work','antya%d.json'%c),encoding='utf-8'))}
    title,items,notes=parse_fill(os.path.join(D,'work','fill%d.txt'%c))
    out=['“Шри Чайтанья-чаритамрита”  ','Антья-лила  ','Глава %d  '%c,'**%s**  '%title,
         '(перевод выполнен в стиле Вриндавана Чандры даса, 2026)','']
    errs=[]; expect=1
    for it in items:
        ns=list(range(it['a'],it['b']+1))
        if ns[0]!=expect: errs.append('gap/order before %d (expected %d)'%(ns[0],expect))
        expect=ns[-1]+1
        trl=[];bn=[]
        for n in ns:
            v=sk[n]; bn.append(v['bn']); trl+=v['tr']
        if len(trl)!=len(it['ww']): errs.append('%s: translit %d lines, ww %d'%(ns,len(trl),len(it['ww'])))
        for b in bn: out.append(br(b)); out.append('')
        il=[]
        for i,t in enumerate(trl):
            il.append(t); il.append(it['ww'][i] if i<len(it['ww']) else '???')
        out.append(br(il)); out.append('')
        lab='%d'%ns[0] if len(ns)==1 else '%d–%d'%(ns[0],ns[-1])
        out.append('(%s) %s'%(lab,it['tr'])); out.append('')
    if notes:
        out.append('---'); out.append('')
        for n in notes: out.append(n); out.append('')
    open(os.path.join(D,'CC_Antya%d.md'%c),'w',encoding='utf-8').write('\n'.join(out).rstrip()+'\n')
    print('Antya %d: %d verses up to %d of %d'%(c,sum(i['b']-i['a']+1 for i in items),expect-1,max(sk)))
    for e in errs: print('  !',e)
for a in sys.argv[1:]: build(int(a))
