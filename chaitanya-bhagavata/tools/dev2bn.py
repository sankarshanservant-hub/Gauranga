#!/usr/bin/env python3
"""Издание Хари Даса Шастри (бенгальский текст деванагари, распознанный слой archive.org) → бенгальское письмо.
Строки с хинди (комментарий) и короткий мусор отбрасываются. Запуск: python3 dev2bn.py <hds-devanagari.txt> > hds-bn.txt"""
import re, sys
HINDI = re.compile(r'(^|\s)(है|हैं|की|का|में|के|करते|हो|हुए|था|थे|किया|अर्थात्?|इत्यर्थः|उन|यह|वह|एवं|को|से|पर|कर|गये|होकर|अपने|तो|भी|लिए|हूँ)(\s|$|।)')
for l in open(sys.argv[1], encoding='utf-8'):
    l = l.strip()
    if not l or len(l) < 8 or HINDI.search(l): continue
    o = ''.join(chr(ord(c) + 0x80) if 0x0901 <= ord(c) <= 0x094D or 0x0950 <= ord(c) <= 0x0963 or 0x0966 <= ord(c) <= 0x096F else c for c in l)
    print(o.replace('঵', 'ব').replace('঱', 'র'))
