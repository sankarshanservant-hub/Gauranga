"""Вносит порцию из отдельного чата в файл таранги: python3 -I tools/intake.py <ru|en> <TT> <порция.md>
Порция — блоки **N.** … и определения сносок [^N]: … (блок <!-- REPORT … --> отбрасывается).
Единицы порции дописываются после последней единицы файла (перед определениями сносок), определения сносок —
в конец файла. Проверяет: номера порции продолжают файл, сноски продолжают нумерацию, ссылки и определения совпадают.
"""
import os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lang, tt, part = sys.argv[1], sys.argv[2], sys.argv[3]
path = os.path.join(HERE, lang, f'{int(tt):02d}.md')
cur = open(path, encoding='utf-8').read().rstrip('\n') + '\n'
new = open(part, encoding='utf-8').read()
new = re.sub(r'<!--\s*REPORT.*?-->', '', new, flags=re.S).strip('\n') + '\n'

def split(t):
    m = re.search(r'(?m)^\[\^[^\]]+\]:', t)
    return (t[:m.start()], t[m.start():]) if m else (t, '')

body, notes = split(cur)
nbody, nnotes = split(new)
last = re.findall(r'(?m)^\*\*(\d+)[a-z]?\.\*\*', body)
first = re.findall(r'(?m)^\*\*(\d+)[a-z]?\.\*\*', nbody)
assert first, 'в порции нет единиц'
if last and int(first[0]) != int(last[-1]) + 1:
    sys.exit(f'номер порции {first[0]} не продолжает файл (последний {last[-1]})')
lastn = max([int(x) for x in re.findall(r'(?m)^\[\^(\d+)\]:', notes)] or [0])
refs = sorted({int(x) for x in re.findall(r'\[\^(\d+)\](?!:)', nbody)})
defs = sorted(int(x) for x in re.findall(r'(?m)^\[\^(\d+)\]:', nnotes))
if refs != defs:
    sys.exit(f'ссылки {refs} и определения {defs} сносок не совпадают')
if refs and refs[0] != lastn + 1:
    sys.exit(f'сноски порции начинаются с {refs[0]}, а в файле последняя {lastn}')
out = body.rstrip('\n') + '\n\n' + nbody.strip('\n') + '\n\n' + (notes.rstrip('\n') + '\n' if notes else '') + nnotes.strip('\n') + '\n'
open(path, 'w', encoding='utf-8').write(out)
print(f'{path}: +{len(first)} единиц ({first[0]}–{first[-1]}), +{len(defs)} сносок')
