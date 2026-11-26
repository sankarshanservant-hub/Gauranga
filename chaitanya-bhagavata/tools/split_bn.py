#!/usr/bin/env python3
"""Бенгальский текст ЧБ из распознанного издания Шри Чайтанья Сарасват Матха (1995, archive.org,
gRvk_sri-chaitanya-bhagavat-bengali-sri-chaitanya-saraswat-math, *_djvu.txt) → черновые поглавные файлы
chaitanya-bhagavata/bn-raw/CB_<Кханда><NN>.md: стихи по меткам ॥N॥ издания, как есть (без правки распознавания).
Запуск: python3 chaitanya-bhagavata/tools/split_bn.py <scsm_djvu.txt>"""
import os, re, sys

BN = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
KEYS = [f'Adi{i:02d}' for i in range(1, 18)] + [f'Madhya{i:02d}' for i in range(1, 29)] + [f'Antya{i:02d}' for i in range(1, 11)]
MARK = re.compile(r'[॥।|]\s*([০-৯]{1,3})\s*(?=[॥।|])')


def main(src):
    s = open(src, encoding='utf-8').read()
    ones = [m for m in MARK.finditer(s) if m.group(1) == '১']
    assert len(ones) == len(KEYS), f'начал глав (॥১॥) найдено {len(ones)}, ожидалось {len(KEYS)}'
    # начало главы — за две строки до метки ॥১॥ (стих — двустишие)
    starts = []
    for m in ones:
        p = s.rfind('\n', 0, m.start())
        p = s.rfind('\n', 0, max(p - 1, 0))
        starts.append(p + 1)
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, '..', 'bn-raw'); os.makedirs(out, exist_ok=True)
    report = []
    for k, (a, b) in zip(KEYS, zip(starts, starts[1:] + [len(s)])):
        ch = s[a:b]
        verses, last, prev = [], 0, 0
        for m in MARK.finditer(ch):
            n = int(m.group(1).translate(BN))
            body = ch[last:m.start()].strip()
            last = m.end()
            if n <= prev or n > prev + 15: body = f'<!-- ⚠ метка {n} после {prev} -->\n' + body
            verses.append((n, body)); prev = max(prev, n) if n < prev + 15 else prev
        tail = ch[last:].strip()
        with open(os.path.join(out, f'CB_{k}.md'), 'w', encoding='utf-8') as f:
            f.write(f'<!-- ЧБ {k}: бенгальский текст по изд. Шри Чайтанья Сарасват Матха (1995), распознавание archive.org без правки -->\n\n')
            for n, body in verses:
                f.write(f'**{n}.**\n{body}\n\n')
            if tail: f.write(f'<!-- хвост главы (заголовки, колофон, мусор распознавания) -->\n{tail}\n')
        nums = [n for n, _ in verses]
        report.append((k, len(nums), max(nums) if nums else 0))
    for r in report: print(*r)


if __name__ == '__main__':
    main(sys.argv[1])
