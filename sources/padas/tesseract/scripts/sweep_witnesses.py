# Порция 19: поиск пад ГПТ1 (диапазон строк gpt1.txt) по свидетелям — БР (1912, 1913, 1960), «Гаура-чарита-чинтамани», «Гита-чандродая», ПК, КГЧ, ПС,
# «Нароттама-виласа», «Навадвипа-парикрама»; для каждой пады — сколько строк совпало (3-граммы скелета, порог 0.62) и номера строк в свидетеле.
# python3 -I sweep_witnesses.py 12403 13104   (медленно: ~2–3 мин на раздел)
import re,sys
sys.path.insert(0,'/home/user/Gauranga/sources/padas/tesseract/scripts')
from bnorm import grams
S='/home/user/Gauranga/sources/'
W={'BR12':S+'narahari-chakravarti/bhakti-ratnakara/bhakti-ratnakara_bengali_DLI-356273_ed2_1912_ocr.txt',
'BR60':S+'narahari-chakravarti/bhakti-ratnakara/bhakti-ratnakara_bengali_Gaudiya-Mission_ed2_1960_ocr.txt',
'BR13':S+'narahari-chakravarti/bhakti-ratnakara/bhakti-ratnakara_bengali_Rasabihari-Sankhyatirtha_Murshidabad_ed2_1913_ocr.txt',
'GCC':S+'narahari-chakravarti/gaura-carita-cintamani/gaura-carita-cintamani_bengali_Haridas-Das_Navadvip_1947_ocr.txt',
'GCd':S+'narahari-chakravarti/gita-candrodaya/gita-candrodaya+namamrita-samudra_bengali_Haridas-Das_Navadvip_1948_ocr.txt',
'PK1':S+'padas/tesseract/pk_v1.txt','PK2':S+'padas/tesseract/pk_v2.txt','PK3':S+'padas/tesseract/pk_v3.txt','PK4':S+'padas/tesseract/pk_v4.txt',
'KGC':S+'padas/tesseract/kgc.txt','PS':S+'padas/tesseract/ps.txt',
'NV':S+'narahari-chakravarti/narottama-vilasa/narottama-vilasa_bengali_DLI-289137_1924_ocr.txt',
'NP':S+'narahari-chakravarti/navadvipa-parikrama/navadvipa-parikrama_bengali_Nagendranath-Vasu_Sahitya-Parishad_1909_ocr.txt',
}
WL={}
for k,f in W.items():
    L=open(f,encoding='utf-8',errors='replace').read().split('\n')
    WL[k]=[(i+1,grams(L[i]+' '+(L[i+1] if i+1<len(L) else ''))) for i in range(len(L))]
G=open(S+'padas/tesseract/gpt1.txt',encoding='utf-8').read().split('\n')
a,b=int(sys.argv[1]),int(sys.argv[2])
hdr=re.compile(r'^\s*\S{1,6}\s*পদ')
pad=None;P=[]
for i in range(a-1,b):
    l=G[i]
    if hdr.match(l): pad=[l.strip(),[]];P.append(pad);continue
    if pad and len(l.strip())>18: pad[1].append(l.strip())
for h,ls in P:
    res={}
    for l in ls:
        q=grams(l)
        if len(q)<8: continue
        for k,arr in WL.items():
            best=max(arr,key=lambda x:len(q&x[1])/len(q))
            s=len(q&best[1])/len(q)
            if s>=0.62: res.setdefault(k,[]).append(best[0])
    print(h[:20],'| lines',len(ls),'|',' '.join(f"{k}:{len(v)}/{min(v)}-{max(v)}" for k,v in res.items() if len(v)>=2), '|', ls[0][:40] if ls else '')
