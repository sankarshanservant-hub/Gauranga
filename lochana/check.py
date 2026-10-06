"""Проверка порции: python3 check.py 01 [02 ...] (без аргументов — все)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def check(n):
    p = {k: os.path.join(HERE, k, n + '.md') for k in ('ru', 'en')}
    if not all(os.path.exists(f) for f in p.values()):
        print(n, 'НЕТ ФАЙЛА'); return False
    t = {k: open(f, encoding='utf-8').read() for k, f in p.items()}
    ok = True
    nums = {k: re.findall(r'^\*\*(\d+[a-zа-я]?)\.\*\*', v, re.M) for k, v in t.items()}
    if nums['ru'] != nums['en']:
        ok = False; print(n, 'номера RU/EN расходятся:', len(nums['ru']), len(nums['en']))
        for a, b in zip(nums['ru'], nums['en']):
            if a != b: print('   первое расхождение:', a, b); break
    heads = {k: len(re.findall(r'^##? ', v, re.M)) for k, v in t.items()}
    if heads['ru'] != heads['en']: ok = False; print(n, 'число заголовков RU/EN расходится', heads)
    for k, v in t.items():
        refs = set(re.findall(r'\[\^([^\]]+)\]', re.sub(r'(?m)^\[\^[^\]]+\]:', '', v)))
        defs = set(re.findall(r'^\[\^([^\]]+)\]:', v, re.M))
        if refs - defs: ok = False; print(n, k, 'сноски без определения:', sorted(refs - defs))
        if defs - refs: ok = False; print(n, k, 'определения без ссылки:', sorted(defs - refs))
    if set(re.findall(r'\[\^([^\]]+)\]', t['ru'])) != set(re.findall(r'\[\^([^\]]+)\]', t['en'])):
        ok = False; print(n, 'метки сносок RU/EN различаются')
    print(n, 'OK' if ok else 'ОШИБКИ', f"({len(nums['ru'])} двустиший/строф)")
    return ok

if __name__ == '__main__':
    args = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(os.path.join(HERE, 'ru')) if re.match(r'\d\d\.md$', f))
    sys.exit(0 if all([check(a) for a in args]) else 1)
