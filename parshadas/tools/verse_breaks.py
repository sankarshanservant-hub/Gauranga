#!/usr/bin/env python3
"""Для PDF: в абзаце из коротких строк (стихи, пады) сохранить переносы строк — pandoc иначе сливает их в одну.
Проза в статьях перенесена по ~120 знаков, поэтому абзац, где все строки (кроме, может быть, последней) короче 80
знаков и строк не меньше двух, считается стихами. Таблицы, списки, сноски, заголовки не трогаются.
Запуск: verse_breaks.py < in.md > out.md"""
import re, sys

def block(lines):
    if len(lines) < 2 or any(re.match(r'\s*([#|]|[-*+] |\d+\. |\[\^|    )', l) for l in lines):
        return lines
    if all(len(l) < 80 for l in lines[:-1]) and len(lines[-1]) < 120:
        return [l.rstrip() + '\\' for l in lines[:-1]] + [lines[-1]]
    return lines

out, cur = [], []
for l in sys.stdin.read().split('\n'):
    if l.strip():
        cur.append(l)
    else:
        out += block(cur) + [l]; cur = []
out += block(cur)
sys.stdout.write('\n'.join(out))
