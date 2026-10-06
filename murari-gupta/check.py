"""Проверка сарги: python3 check.py 1.01 [1.02 ...] (без аргументов — все готовые)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def nums_skt(t):
    return [h.strip() for h in re.findall(r'^### (.+)$', t, re.M) if h.strip() != 'colophon']

def nums_tr(t):
    return re.findall(r'^\*\*([\d–-]+)\.\*\*', t, re.M)

def notes(t):
    refs = set(re.findall(r'(?<!^)\[\^([^\]]+)\]', re.sub(r'(?m)^\[\^[^\]]+\]:', '', t))); defs = set(re.findall(r'^\[\^([^\]]+)\]:', t, re.M))
    return refs, defs

def check(s):
    p = {k: os.path.join(HERE, k, s + '.md') for k in ('skt', 'ru', 'en')}
    miss = [k for k, f in p.items() if not os.path.exists(f)]
    if miss:
        print(s, 'НЕТ ФАЙЛОВ:', miss); return False
    t = {k: open(f, encoding='utf-8').read() for k, f in p.items()}
    ok = True
    ns, nr, ne = nums_skt(t['skt']), nums_tr(t['ru']), nums_tr(t['en'])
    if not (ns == nr == ne):
        ok = False
        print(s, 'номера расходятся: skt', len(ns), 'ru', len(nr), 'en', len(ne))
        for a, b, c in zip(ns, nr, ne):
            if not (a == b == c): print('   первое расхождение:', a, b, c); break
    for part in re.split(r'^### ', t['skt'], flags=re.M)[1:]:
        h = part.split('\n', 1)[0].strip()
        if h == 'colophon': continue
        for tag in ('SKT:', 'WFW-RU:', 'WFW-EN:'):
            if tag not in part: ok = False; print(s, h, 'нет', tag)
        if re.search(r'[a-zA-Zঀ-৿]', part.split('SKT:', 1)[-1].split('VAR:')[0].split('WFW-RU:')[0]):
            ok = False; print(s, h, 'в SKT не деванагари')
    for k in ('ru', 'en'):
        r, d = notes(t[k])
        if r - d: ok = False; print(s, k, 'сноски без определения:', sorted(r - d))
        if d - r: ok = False; print(s, k, 'определения без ссылки:', sorted(d - r))
    if notes(t['ru'])[0] != notes(t['en'])[0]: ok = False; print(s, 'метки сносок RU/EN различаются')
    print(s, 'OK' if ok else 'ОШИБКИ', f'({len(ns)} шлок)')
    return ok

if __name__ == '__main__':
    args = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(os.path.join(HERE, 'ru')) if f.endswith('.md'))
    sys.exit(0 if all([check(a) for a in args]) else 1)
