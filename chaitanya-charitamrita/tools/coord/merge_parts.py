#!/usr/bin/env python3
# Слить часть 2 комментариев (ed/{ru,en}/<Гл>-{apb,anu}.p2.md) с основным файлом части 1 и проверить:
# дубли разделов, неопределённые/дважды определённые сноски, совпадение списков разделов RU и EN.
# Запуск: python3 tools/coord/merge_parts.py Adi10      (после — git rm файлов *.p2.md)
import re, sys, os
CC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
c = sys.argv[1]; ok = True
for lang in ('ru', 'en'):
    for k in ('apb', 'anu'):
        p1 = os.path.join(CC, 'ed', lang, '%s-%s.md' % (c, k)); p2 = p1.replace('.md', '.p2.md')
        if not os.path.exists(p2): print('нет', p2); continue
        a = open(p1, encoding='utf-8').read().rstrip('\n'); b = open(p2, encoding='utf-8').read().rstrip('\n')
        a1, a2 = (a.split('\n---\n', 1) + [''])[:2]; b1, b2 = (b.split('\n---\n', 1) + [''])[:2]
        body = a1.rstrip('\n') + '\n\n' + b1.strip('\n')
        notes = '\n\n'.join(x for x in (a2.strip('\n'), b2.strip('\n')) if x)
        out = body + ('\n\n---\n\n' + notes if notes else '') + '\n'
        secs = re.findall(r'^## (.+)$', out, re.M)
        dup = {s for s in secs if secs.count(s) > 1}
        refs = set(re.findall(r'\[\^([^\]]+)\](?!:)', out)); defs = re.findall(r'^\[\^([^\]]+)\]:', out, re.M)
        bad = (dup, refs - set(defs), {d for d in defs if defs.count(d) > 1})
        print(lang, k, 'разделов', len(secs), '| дубли', bad[0] or '-', '| без определения', bad[1] or '-', '| дважды', bad[2] or '-')
        if any(bad): ok = False
        open(p1, 'w', encoding='utf-8').write(out)
for k in ('apb', 'anu'):
    r = re.findall(r'^## .+$', open(os.path.join(CC, 'ed/ru/%s-%s.md' % (c, k)), encoding='utf-8').read(), re.M)
    e = re.findall(r'^## .+$', open(os.path.join(CC, 'ed/en/%s-%s.md' % (c, k)), encoding='utf-8').read(), re.M)
    if r != e: ok = False; print('!! RU/EN разделы не совпадают:', k)
print('OK' if ok else '!! есть замечания — исправить до коммита')
