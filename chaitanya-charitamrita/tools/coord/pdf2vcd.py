#!/usr/bin/env python3
# Прозаический перевод ВЧД, извлечённый из .pdf (Антья 12: vcd/txt/CC_<Гл>.pdf.txt — с Диска пользователя),
# привести к виду выгрузки .doc для tools/prep_vcd.py:
#  * бенгальский текст из pdf испорчен (шрифтовая кодировка) — заменить текстом стиха из vedabase (ed/work/vb-<Гл>.json),
#    а затем, как всегда, сверить со сканом издания Гаудия Матха (сверка листов) — vedabase служит лишь заготовкой;
#  * транслитерация набрана ПРОПИСНЫМИ — в строчные;
#  * оторванные «॥», «॥ N» — присоединить к бенгальской строке.
# Перевод и пословный ВЧД не трогаются. Запуск: python3 tools/coord/pdf2vcd.py Antya12
import json, os, re, sys
CC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ch = sys.argv[1]
src = os.path.join(CC, 'vcd', 'txt', 'CC_%s.pdf.txt' % ch)
dst = os.path.join(CC, 'vcd', 'txt', 'CC_%s.txt' % ch)
vb = json.load(open(os.path.join(CC, 'ed', 'work', 'vb-%s.json' % ch), encoding='utf-8'))
BD = '০১২৩৪৫৬৭৮৯'
def bn2i(s): return int(''.join(str(BD.index(c)) for c in s))
def bnum(n): return ''.join(BD[int(c)] for c in str(n))
def has_bn(s): return any('ঀ' <= c <= '৿' for c in s)
def has_cyr(s): return any('Ѐ' <= c <= 'ӿ' for c in s)
VB = {}
for k, v in vb.items():
    a, _, b = k.partition('-')
    for i_, n in enumerate(range(int(a), int(b or a) + 1)):
        VB.setdefault(n, ('%d' % n, v['bn'][min(i_, len(v['bn']) - 1)]))   # у сдвоенных записей bn — список по стихам
def vb_lines(n):
    k, t = VB[n]
    t = re.sub(r'[\s।॥]*[০-৯]+[\s।॥]*$', '', re.sub(r'॥\s*[০-৯]+\s*॥\s*$', '', t.strip())).strip()
    t = re.sub(r'[\s।॥]*[০-৯]+[\s।॥]*$', '', t).strip()
    if '\n' in t: ls = [x.strip(' ।') for x in t.split('\n') if x.strip()]
    else:            # нет перевода строки: делим по знаку препинания ближе к середине
        cands = [m.end() for m in re.finditer(r'[।!?,—]\s', t)]
        if cands:
            mid = len(t) / 2; p = min(cands, key=lambda x: abs(x - mid)); ls = [t[:p].strip(' ।'), t[p:].strip(' ।')]
        else: ls = [t]
    return ls, k
L = [l.rstrip() for l in open(src, encoding='utf-8')]
# оторванные «॥» / «॥ N» / «N ॥» — к предыдущей бенгальской строке
out = []
for l in L:
    s = l.strip()
    if s and re.fullmatch(r'[॥।৷\s০-৯]+', s) and out:
        j = len(out) - 1
        while j >= 0 and not out[j].strip(): j -= 1
        if j >= 0 and has_bn(out[j]) and not has_cyr(out[j]): out[j] = out[j].rstrip() + ' ' + s; continue
    out.append(l)
L = out
# группы бенгальских строк, оканчивающиеся ॥ N ॥
res, i, used, log = [], 0, set(), []
while i < len(L):
    if has_bn(L[i]) and not has_cyr(L[i]):
        j = i; grp = []
        while j < len(L) and ((has_bn(L[j]) and not has_cyr(L[j])) or (not L[j].strip() and j + 1 < len(L) and has_bn(L[j + 1]) and not has_cyr(L[j + 1]))):
            if L[j].strip(): grp.append(L[j])
            j += 1
        nums = [bn2i(m) for g_ in grp for m in re.findall(r'[॥?!]\s*([০-৯]+)\s*(?:॥|$)', g_.strip())]
        if nums and all(n in VB for n in nums):
            for n in nums:
                ls, k = vb_lines(n)
                if k in used and '-' in k: continue
                used.add(k)
                for q, x in enumerate(ls):
                    res.append(x + (' ॥ %s ॥' % bnum(n) if q == len(ls) - 1 else ' ৷'))
                log.append('%s→vb %s' % (n, k))
        else:
            res.extend(grp); log.append('!! без замены: %s' % (grp[-1][-40:] if grp else ''))
        i = j; continue
    l = L[i]
    letters = [c for c in l if c.isalpha()]
    if letters and has_cyr(l) and all(not c.islower() for c in letters) and len(letters) >= 3:
        l = l.lower()            # транслитерация прописными (комбинирующие знаки не затрагиваются)
    res.append(l); i += 1
open(dst, 'w', encoding='utf-8').write('\n'.join(res) + '\n')
print('%s: стихов заменено по vedabase: %d; без замены: %d -> %s' % (ch, sum(1 for x in log if '→' in x),
      sum(1 for x in log if x.startswith('!!')), os.path.relpath(dst, CC)))
for x in log:
    if x.startswith('!!'): print('  ' + x)
