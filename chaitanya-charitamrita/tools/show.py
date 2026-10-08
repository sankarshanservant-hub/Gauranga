import json,sys,os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','vcd','new','work')
c,a,b=map(int,sys.argv[1:4])
for v in json.load(open(os.path.join(D,'antya%d.json'%c))):
    if a<=v['n']<=b:
        print('#%d%s %s'%(v['n'],' G'+str(v['group']) if v['group'] else '',v['warn']))
        print('\n'.join(v['bn'])); print('\n'.join('  '+t for t in v['tr']))
