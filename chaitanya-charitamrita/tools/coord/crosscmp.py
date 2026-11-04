#!/usr/bin/env python3
# Сверить переводы сквозных стихов в выверенных главах (RU ed/vcd-rev, EN ed/en-rev) дословно.
# Запуск: python3 tools/coord/crosscmp.py Madhya23:16=Adi01:60 Madhya23:29=Madhya02:61 …
import re,sys
def tr(f,n):
    s=open(f,encoding='utf-8').read()
    m=re.search(r'^\(%s\) (.*)$'%re.escape(n),s,re.M)
    return re.sub(r'\[\^[^\]]+\]','',m.group(1)) if m else None
for a,b in [x.split('=') for x in sys.argv[1:]]:
    ca,na=a.split(':'); cb,nb=b.split(':')
    for d in ('vcd-rev','en-rev'):
        x=tr('ed/%s/CC_%s.md'%(d,ca),na); y=tr('ed/%s/CC_%s.md'%(d,cb),nb)
        print(d,a,b,'SAME' if x==y else 'DIFF\n  '+str(x)+'\n  '+str(y))
