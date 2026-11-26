#!/usr/bin/env python3
"""Сверка bn/CB_X.md с транслитерацией ed/CB_X.md по «скелету» согласных (ловит выпавшие строки и перепутанные стихи).
Запуск: python3 chaitanya-bhagavata/tools/ed_sim.py CB_Adi01 [порог=0.93]  — печатает стихи ниже порога.
Расхождения от условностей (ক্ষ/кш, ঁ/н̇) — не ошибки; смотреть глазами."""
import difflib, os, re, sys, unicodedata
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BN = {'ক':'k','খ':'k','গ':'g','ঘ':'g','ঙ':'n','চ':'c','ছ':'c','জ':'j','ঝ':'j','ঞ':'n','ট':'t','ঠ':'t','ড':'d','ড়':'d','ঢ':'d','ঢ়':'d',
      'ণ':'n','ত':'t','ৎ':'t','থ':'t','দ':'d','ধ':'d','ন':'n','প':'p','ফ':'p','ব':'b','ভ':'b','ম':'m','য':'y','য়':'y','র':'r','ল':'l',
      'শ':'s','ষ':'s','স':'s','হ':'h','ং':'m','ৃ':'r','ঋ':'r'}
CY = {'к':'k','г':'g','ч':'c','т':'t','д':'d','н':'n','п':'p','б':'b','в':'b','м':'m','й':'y','р':'r','л':'l','ш':'s','с':'s','х':'h'}
sq = lambda s: re.sub(r'(.)\1+', r'\1', s.replace('h', '').replace('y', ''))
def bsk(s): return sq(''.join(BN.get(c, '') for c in unicodedata.normalize('NFC', s)))
def csk(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').replace('дж', 'j')
    return sq(''.join('j' if c == 'j' else CY.get(c, '') for c in s))
def bn_verses(p):
    t = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
    return {m.group(1).replace('-', '–'): m.group(2) for m in re.finditer(r'^\*\*(\d+(?:[–-]\d+)?)\.\*\*\n(.*?)(?=\n\*\*\d|\Z)', t, re.M | re.S)}
def ed_translit(p):
    d, buf = {}, []
    for l in open(p, encoding='utf-8').read().split('\n'):
        if (m := re.match(r'^\*(.+)\*\s*$', l.strip())) and not l.startswith('**'): buf.append(m.group(1)); continue
        if (m := re.match(r'^\*\*(\d+(?:[–-]\d+)?)\.\*\*', l)): d[m.group(1).replace('-', '–')] = ' '.join(buf); buf = []
    return d
name = sys.argv[1]; thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.93
B = bn_verses(os.path.join(HERE, 'bn', name + '.md')); E = ed_translit(os.path.join(HERE, 'ed', name + '.md'))
low = 0
for k, v in B.items():
    r = difflib.SequenceMatcher(None, bsk(v), csk(E.get(k, ''))).ratio()
    if r < thr: low += 1; print(k, round(r, 2))
print(f'{name}: стихов {len(B)}, ниже {thr}: {low}')
