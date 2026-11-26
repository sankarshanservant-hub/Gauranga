#!/usr/bin/env python3
"""Бенгальский текст ЧБ из распознанного издания Шри Чайтанья Сарасват Матха (1995, archive.org,
gRvk_sri-chaitanya-bhagavat-bengali-sri-chaitanya-saraswat-math, *_djvu.txt) → черновые поглавные файлы
chaitanya-bhagavata/bn-raw/CB_<Кханда><NN>.md: стихи по меткам ॥N॥ издания, как есть (без правки распознавания).
Запуск: python3 chaitanya-bhagavata/tools/split_bn.py <scsm_djvu.txt>"""
import os, re, sys

BN = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
KEYS = [f'Adi{i:02d}' for i in range(1, 18)] + [f'Madhya{i:02d}' for i in range(1, 29)] + [f'Antya{i:02d}' for i in range(1, 11)]
MARK = re.compile(r'[॥।|]\s*([০-৯]{1,3})\s*(?=[॥।|])')


def marks(s):
    """Метки стихов по порядку: (позиция, конец, номер); номер чинится (лишняя «৮» впереди), начало главы — сброс к 1–3."""
    out, prev = [], 0
    for m in MARK.finditer(s):
        t = m.group(1).translate(BN); n = int(t)
        cand = [n] + ([int(t[1:])] if t.startswith('8') and len(t) > 1 else [])
        ok = [c for c in cand if prev < c <= prev + 12]
        if ok: n = min(ok, key=lambda c: c - prev); new = False
        elif n in (1, 2, 3) and prev > 15: new = True
        else: continue
        out.append((m.start(), m.end(), n, new)); prev = n
    return out


def main(src):
    s = open(src, encoding='utf-8').read()
    ms = marks(s)
    chapters, cur = [], []
    for x in ms:
        if x[3] and cur: chapters.append(cur); cur = []
        cur.append(x)
    chapters.append(cur)
    assert len(chapters) == len(KEYS), f'глав {len(chapters)}, ожидалось {len(KEYS)}'
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, '..', 'bn-raw'); os.makedirs(out, exist_ok=True)
    for k, ch in zip(KEYS, chapters):
        # начало текста главы — две строки до первой метки
        p = s.rfind('\n', 0, ch[0][0]); p = s.rfind('\n', 0, max(p - 1, 0)) + 1
        with open(os.path.join(out, f'CB_{k}.md'), 'w', encoding='utf-8') as f:
            f.write(f'<!-- ЧБ {k}: бенгальский текст по изд. Шри Чайтанья Сарасват Матха (1995), распознавание archive.org без правки -->\n\n')
            last, prev = p, 0
            for a, b, n, _ in ch:
                body = s[last:a].strip(); last = b
                if n != prev + 1: f.write(f'<!-- ⚠ пропуск: {prev + 1}–{n - 1} не размечены (текст — в стихе {n} или потерян) -->\n')
                f.write(f'**{n}.**\n{body}\n\n'); prev = n
        print(k, len(ch), ch[-1][2])


if __name__ == '__main__':
    main(sys.argv[1])
