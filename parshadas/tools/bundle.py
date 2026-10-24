#!/usr/bin/env python3
"""Подборка источников по лицу (без ИИ): главы целиком + упоминания (абзац с именем и соседние) из OCR трёх книг.
OCR — gauranga-private/ocr/{T,M,B}/pNNNN.txt. Результат — один md-файл (вне репозитория!).
  bundle.py OUT --ocr DIR --T-chapter 36-43 --B-chapter 21-95 --T 'regex' --M 'regex' --B 'regex' [--B-skip-chapter]"""
import argparse, re
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--ocr', required=True)
for k in 'TMB':
    ap.add_argument(f'--{k}', default=None, help='regex имени')
    ap.add_argument(f'--{k}-chapter', default='', help='страницы PDF главы: a-b[,c-d]')
a = ap.parse_args()

def rng(s):
    out = set()
    for part in filter(None, s.split(',')):
        x, _, y = part.partition('-'); out |= set(range(int(x), int(y or x) + 1))
    return out

res = []
for k in 'TMB':
    d = Path(a.ocr) / k; chap = rng(getattr(a, f'{k}_chapter'))
    pat = getattr(a, k); rx = re.compile(pat, re.I) if pat else None
    if chap:
        res.append(f'\n# {k}: глава (PDF {min(chap)}–{max(chap)})\n')
        for p in sorted(chap):
            res.append(f'\n[{k} pdf {p}]\n' + (d / f'p{p:04d}.txt').read_text())
    if rx:
        res.append(f'\n# {k}: упоминания вне главы\n')
        for f in sorted(d.glob('p*.txt')):
            p = int(f.stem[1:])
            if p in chap: continue
            paras = [x.strip() for x in re.split(r'\n\s*\n', f.read_text()) if x.strip()]
            hit = [i for i, x in enumerate(paras) if rx.search(x)]
            if not hit: continue
            keep = sorted({j for i in hit for j in (i - 1, i, i + 1) if 0 <= j < len(paras)})
            res.append(f'\n[{k} pdf {p}]\n' + '\n\n'.join(paras[j] for j in keep) + '\n')
Path(a.out).write_text(''.join(res))
print(a.out, len(''.join(res)), 'chars')
