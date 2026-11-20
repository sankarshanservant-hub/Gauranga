#!/usr/bin/env python3
# Цитаты стихов ЧЧ в комментариях, которые остались в прежнем переводе после выверки.
# Использование: python3 tools/rev_quotes.py Madhya01 [Madhya02 …]  — ищет во всех ed/ru|en/*-a*.md
# начало прежнего перевода каждого изменённого стиха (ed/vcd → ed/vcd-rev; ed/en → ed/en-rev) и печатает находки;
# заменять вручную (цитата бывает частичной или во вложенных кавычках).
import os, re, sys, glob
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def verses(f):
    if not os.path.exists(f): return {}
    body = open(f, encoding='utf-8').read().partition('\n---\n')[0]
    return {m.group(1): re.sub(r'\s+', ' ', re.sub(r'\[\^[\w-]+\]', '', m.group(2))).strip()
            for m in re.finditer(r'^\((\d+(?:–\d+)?)\) (.*?)(?=\n\n|\Z)', body, re.M | re.S)}

for lang, old_d, new_d in (('ru', 'vcd', 'vcd-rev'), ('en', 'en', 'en-rev')):
    comm = {f: re.sub(r'\s+', ' ', open(f, encoding='utf-8').read())
            for f in glob.glob(os.path.join(ROOT, 'ed', lang, '*-a*.md'))}
    for ch in sys.argv[1:]:
        o = verses(os.path.join(ROOT, 'ed', old_d, 'CC_%s.md' % ch))
        n = verses(os.path.join(ROOT, 'ed', new_d, 'CC_%s.md' % ch))
        for k, ot in o.items():
            if k not in n or n[k] == ot: continue
            core = ot.strip('“”"«»').rstrip('.')
            for frag in {core[:60], core[-50:]}:
                if len(frag) < 25: continue
                for f, t in comm.items():
                    if frag in t:
                        print('%s %s %s.%s | %s\n   NEW: %s' % (lang, os.path.basename(f), ch, k, frag, n[k][:200]))
