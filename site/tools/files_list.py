#!/usr/bin/env python3
"""Опись файлов сайта для работы без интернета (sw.js, offline.js) → stdout (JSON).

    python3 site/tools/files_list.py <папка сайта> <версия> > <папка сайта>/data/files.json

core — основа, которую помощник sw.js сохраняет сразу (страница, стили, код, лента лил, спутники, места, картинки,
MapLibre): пути без ?v=. data — главы писаний, стихи к лилам, жизнеописания: [путь, байты, отпечаток] — их сохраняют
при открытии или кнопкой «Скачать все писания»; по отпечатку offline.js узнаёт изменившиеся после новой публикации.
Музыка (assets/audio) в опись не входит. Вызывается из site/tools/publish_pages.sh; локально — для проверки.
"""
import hashlib
import json
import os
import sys

root, version = sys.argv[1], sys.argv[2]
DATA_DIRS = ('data/library/', 'data/verses/', 'data/parshadas/')
core, data = [], []
for d, _, names in os.walk(root):
    for n in sorted(names):
        full = os.path.join(d, n)
        p = os.path.relpath(full, root).replace(os.sep, '/')
        if p.startswith(('.git/', 'assets/audio/', 'assets/src/', 'tools/', 'content/')) or p in ('data/files.json', 'sw.js', '.nojekyll'):
            continue
        if p.endswith(('.md', '.py', '.sh', '.txt')):
            continue
        if p.startswith(DATA_DIRS) and p != 'data/library/index.json':
            b = open(full, 'rb').read()
            data.append([p, len(b), hashlib.sha1(b).hexdigest()[:12]])
        elif p != 'index.html':
            core.append(p)
json.dump({'v': version, 'core': sorted(core), 'data': sorted(data)}, sys.stdout, ensure_ascii=False, separators=(',', ':'))
