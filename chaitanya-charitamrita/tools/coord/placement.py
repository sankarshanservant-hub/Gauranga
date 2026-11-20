#!/usr/bin/env python3
# Проверка: каждый раздел комментария (## N или ## N–M) попадает в блок стиха при сборке PDF
# (правило md2pdf: a <= последний номер раздела <= b). Запуск: python3 tools/coord/placement.py Adi16 [Adi17 …]
import re, sys, os
CC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(CC, 'tools')); os.chdir(CC)
import md2pdf
bad = 0
for ch in sys.argv[1:]:
    for lang in ('ru', 'en'):
        md = open('ed/%s/CC_%s.md' % ('vcd' if lang == 'ru' else 'en', ch), encoding='utf-8').read()
        labs = re.findall(r'^\((\d+(?:–\d+)?)\) ', md, re.M)
        for kind in ('apb', 'anu'):
            sec, _ = md2pdf.load_comm(ch, kind, lang); used = set()
            for lab in labs:
                a, b = (lab.split('–') + [lab])[:2]
                used |= {k for k in sec if k != '0' and int(a) <= int(k.split('–')[-1]) <= int(b)}
            um = [k for k in sec if k != '0' and k not in used]
            if um: bad += 1; print('!!', ch, lang, kind, 'не размещены:', um)
print('размещение: OK' if not bad else '!! есть неразмещённые разделы')
