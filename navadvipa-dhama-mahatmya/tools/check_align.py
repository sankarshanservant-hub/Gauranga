"""Проверка: последовательность меток **N.** в ru/NN.md совпадает с en/NN.md. Запуск: python3 tools/check_align.py [NN ...]"""
import os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def labels(path):
    return [m.group(1) for l in open(path, encoding='utf-8') if (m := re.match(r'^\*\*([^*]+?)\.\*\*', l))]


ok = True
chs = sys.argv[1:] or [f'{i:02d}' for i in range(1, 20)]
for ch in chs:
    ru, en = os.path.join(HERE, 'ru', f'{ch}.md'), os.path.join(HERE, 'en', f'{ch}.md')
    if not os.path.exists(ru): print(f'{ch}: ru нет'); continue
    a, b = labels(ru), labels(en)
    if a == b: print(f'{ch}: OK ({len(a)} меток)'); continue
    ok = False
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    print(f'{ch}: РАСХОЖДЕНИЕ — ru {len(a)}, en {len(b)} меток; первое на позиции {i + 1}: '
          f'ru {a[i] if i < len(a) else "—"} / en {b[i] if i < len(b) else "—"}')
    empty = [l for l in open(ru, encoding='utf-8') if re.match(r'^\*\*[^*]+?\.\*\*\s*$', l)]
    if empty: print(f'   пустые метки в ru: {len(empty)}')
sys.exit(0 if ok else 1)
