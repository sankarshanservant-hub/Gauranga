# Сверка бенгальского текста главы (ed/work/rows-<Гл>.json) с vedabase (ed/work/vb-<Гл>.json).
# Печатает расхождения слов (без учёта тире/дефисов/апострофов/пробелов вокруг тире).
import json, sys, re, os, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import normbn
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ed', 'work')
def nb(s):
    s = normbn(s); s = re.sub(r'[‌‍]', '', s); s = re.sub(r'॥[^॥]*॥', '', s)
    s = s.replace('৷', ' ').replace('।', ' ').replace('–', '-').replace("'", '’')
    s = re.sub(r'\s*—\s*', ' — ', s); s = re.sub(r'\s*-\s*', '-', s)
    s = re.sub(r'\s+([,!?])', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()
def key(w): return re.sub(r'[-—,!?;‘’“”\s]', '', w)
def diffs(chap):
    vb = json.load(open(os.path.join(R, 'vb-%s.json' % chap))); rows = json.load(open(os.path.join(R, 'rows-%s.json' % chap)))
    def vbt(n):
        for k, e in vb.items():
            a, b = (list(map(int, k.split('-'))) + [None])[:2]; b = b or a
            if a <= n <= b: return k, e['bn']
    out = []
    for r in rows:
        for i, n in enumerate(r['nums']):
            k, bl = vbt(n)
            mine = ' '.join(r['bn'][i])
            if '-' in k:   # сдвоенный у vedabase: взять нужное двустишие
                parts = re.findall(r'.*?॥\s*[০-৯]+\s*॥', ' '.join(bl), re.S)
                a = int(k.split('-')[0]); B = nb(parts[n - a]) if n - a < len(parts) else nb(' '.join(bl))
            else: B = nb(' '.join(bl))
            A = nb(mine)
            aw, bw = A.split(), B.split()
            # склейка/разбивка слов не считается, если без пробелов совпадает
            sm = difflib.SequenceMatcher(None, aw, bw)
            d = [(' '.join(aw[i1:i2]), ' '.join(bw[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']
            d = [x for x in d if key(x[0]) != key(x[1])]
            if d: out.append((n, d))
    return out
def ortho(a, b):
    """расхождение только в орфографии/написании (удвоения, слитно-раздельно, апострофы)"""
    def f(x):
        x = re.sub(r'[\s\-’‘,]', '', x)
        for k, v in (('র্দ্ধ', 'র্ধ'), ('র্ধ্ব', 'র্ধ'), ('র্দ্ধ্ব', 'র্ধ'), ('ত্ত্য', 'ত্য'), ('র্ত্ত', 'র্ত'), ('ণ', 'ন'), ('ৎর', 'দ্র'), ('মতে', 'মত'), ('্য্য', '্য')):
            x = x.replace(k, v)
        return re.sub(r'(.)্\1', r'\1', x)
    return f(a) == f(b)

def write_md(chap):
    """ed/review/vedabase-diff-<Глава>.md — все расхождения нашего текста (изд. Гаудия Матха) с vedabase"""
    fx = os.path.join(R, '..', 'fixes', '%s.txt' % chap)
    fixed = []      # (стихи, было, стало) — правки бенгальского по скану
    if os.path.exists(fx):
        for l in open(fx, encoding='utf-8'):
            m = re.match(r'^@([\d-]+) bn:\s*(.*?)\s*=>\s*(.*?)\s*(?:#|$)', l)
            if m: fixed.append((set(range(int(m.group(1).split('-')[0]), int(m.group(1).split('-')[-1]) + 1)), nb(m.group(2)), nb(m.group(3))))
    def was_vb(n, a, b):
        a, b = re.sub(r'[,!?]', '', a), re.sub(r'[,!?]', '', b)
        for ns, old, new in fixed:
            if n not in ns: continue
            if a and all(w in new.split() for w in a.split()) and not all(w in old.split() for w in a.split()): return True
            if not a and b and all(w in old.split() for w in b.split()): return True
        return False
    D = diffs(chap)
    out = ['# Расхождения бенгальского текста %s с vedabase' % chap, '',
           'Текст книги — по изданию Гаудия Матха с комментариями Бхактисиддханты Сарасвати (скан `src/CC_SS.pdf`);',
           'оно авторитетнее vedabase, и все чтения ниже оставлены по нему. Список ведётся для сведения.',
           'Тип: **чтение** — другое слово или форма; орфография — только написание (удвоения, слитно/раздельно, апострофы).',
           'ВЧД — перевод Вриндавана Чандры даса. «Исправлено» — у ВЧД здесь было иначе (обычно как на vedabase),',
           'текст исправлен по скану; было/стало — в `fixes-%s.md`.' % chap, '',
           '| Стих | Гаудия Матх (в книге) | vedabase | Тип | У ВЧД |', '|---|---|---|---|---|']
    nr = no = 0
    for n, d in D:
        for a, b in d:
            o = ortho(a, b); nr += not o; no += o
            out.append('| %s | %s | %s | %s | %s |' % (n, a or '—', b or '—', 'орфография' if o else '**чтение**', 'исправлено' if was_vb(n, a, b) else 'как в ГМ'))
    out += ['', 'Итого: чтений — %d, орфографических — %d.' % (nr, no)]
    open(os.path.join(R, '..', 'review', 'vedabase-diff-%s.md' % chap), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    return nr, no

if __name__ == '__main__':
    for n, d in diffs(sys.argv[1]): print(n, ' | '.join('%s ≠ %s' % x for x in d))
