# Проверка подготовленной главы ed/vcd/CC_<Глава>.md (этап А).
# Использование: python3 tools/check_ed.py Adi07 [...]
# Проверяет: у каждого стиха есть бенгальский текст, транслитерация, пословный (под каждой строкой) и перевод;
# номера идут подряд; нет мусорных символов; число стихов = числу стихов vedabase (ed/work/vb-<Глава>.json).
import re, os, sys, json, unicodedata
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BD = '০১২৩৪৫৬৭৮৯'
JUNK = '　ﾠㅤᅠ\t _'
def bn2i(s): return int(''.join(str(BD.index(c)) for c in s))
def has_bn(s): return any('ঀ' <= c <= '৿' for c in s)
def is_tl(s): return any(unicodedata.combining(c) for c in s) or bool(re.search(r'[а-я]', s)) and not re.search(r'[А-Я]', s[:1])

def check(chap):
    md = open(os.path.join(ROOT, 'ed', 'vcd', 'CC_%s.md' % chap), encoding='utf-8').read()
    errs, warn = [], []
    for i, l in enumerate(md.split('\n'), 1):
        if any(c in l for c in JUNK): errs.append('строка %d: мусорный символ %r' % (i, [c for c in l if c in JUNK][0]))
    paras = [p for p in md.split('\n\n') if p.strip()]
    expect, cur, verses = 1, None, []
    for p in paras[1:]:
        lines = [x.rstrip() for x in p.split('\n')]
        if has_bn(p) and re.search(r'॥\s*[০-৯]+\s*॥', p):
            n = bn2i(re.search(r'॥\s*([০-৯]+)\s*॥\s*$', lines[-1].strip()).group(1))
            if cur is None or cur.get('tr'): cur = {'nums': [], 'tl': None, 'tr': None}; verses.append(cur)
            cur['nums'].append(n)
            if n != expect: errs.append('нумерация: ॥%d॥, ожидался %d' % (n, expect))
            expect = n + 1
        elif re.match(r'^\(\d+(–\d+)?\) ', p):
            m = re.match(r'^\((\d+)(?:–(\d+))?\) (.*)', p, re.S)
            lab = list(range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1))
            if cur is None or lab != cur['nums']: errs.append('перевод (%s) не совпадает со стихом %s' % (m.group(1), cur and cur['nums']))
            if not m.group(3).strip(): errs.append('%s: пустой перевод' % lab)
            if cur: cur['tr'] = m.group(3)
        elif cur is not None and not cur.get('tr'):
            # транслитерация + пословный: строки чередуются; пословный — с двумя пробелами между словами
            cur['tl'] = lines
    for v in verses:
        lab = '–'.join(map(str, v['nums'][::max(1, len(v['nums']) - 1)]))
        if not v['tl']: errs.append('%s: нет транслитерации' % lab); continue
        # строка транслитерации — с диакритикой (макрон, точка снизу и т. п.), пословный — без
        L = [x.strip() for x in v['tl']]
        T = [any(c in '\u0301\u0303\u0304\u0307\u0310\u0323' for c in x) for x in L]
        ww_missing = sum(1 for i, t in enumerate(T) if t and (i + 1 == len(T) or T[i + 1]))
        if not any(T): errs.append('%s: нет транслитерации' % lab)
        if ww_missing: warn.append('%s: нет пословного к %d строке(ам) транслитерации' % (lab, ww_missing))
        if not v['tr']: errs.append('%s: нет перевода' % lab)
    vbp = os.path.join(ROOT, 'ed', 'work', 'vb-%s.json' % chap)
    if os.path.exists(vbp):
        from cmp_bn import vb_skips
        nvb = max(int(k.split('-')[-1]) for k in json.load(open(vbp))) - len(vb_skips(chap))
        if nvb != expect - 1: warn.append('стихов %d, у vedabase %d' % (expect - 1, nvb))
    print('%s: стихов %d (блоков %d); ошибок %d, замечаний %d' % (chap, expect - 1, len(verses), len(errs), len(warn)))
    for e in errs: print('  ! ' + e)
    for w in warn: print('  ~ ' + w)
    return expect - 1, len(errs), warn

if __name__ == '__main__':
    for c in sys.argv[1:]: check(c)
