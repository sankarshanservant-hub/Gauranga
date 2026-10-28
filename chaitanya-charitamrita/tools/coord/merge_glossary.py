#!/usr/bin/env python3
# Внести рабочие глоссарии исполнителей (ed/work/glossary-*.md) в ed/GLOSSARY-commentary.md
# отдельным разделом «## Термины (добавлено по <...>; RU и EN)». Затем: git rm рабочих файлов.
# Запуск: python3 tools/coord/merge_glossary.py "Ади 16–17" ed/work/glossary-Adi16.md ed/work/glossary-Adi17.md
import sys, os, re
CC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
title, files = sys.argv[1], sys.argv[2:]
out = ['', '## Термины (добавлено по %s; RU и EN)' % title]
for f in files:
    t = open(os.path.join(CC, f) if not os.path.isabs(f) else f, encoding='utf-8').read()
    i = t.find('\n## '); body = t[i + 1:] if i >= 0 else t
    out += ['', '### ' + os.path.basename(f)[9:-3], ''] + [re.sub(r'^## ', '#### ', l) for l in body.rstrip('\n').split('\n')]
open(os.path.join(CC, 'ed', 'GLOSSARY-commentary.md'), 'a', encoding='utf-8').write('\n'.join(out) + '\n')
print('добавлено строк:', len(out))
