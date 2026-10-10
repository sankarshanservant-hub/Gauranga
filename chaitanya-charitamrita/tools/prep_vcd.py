# Этап А: глава ВЧД (vcd/txt/CC_<Лила><NN>.txt) -> ed/vcd/CC_<Лила><NN>.md (формат vcd/new/*.md),
# всё удалённое -> ed/review/removed-<Глава>.md, все правки -> ed/review/fixes-<Глава>.md.
# Использование: python3 tools/prep_vcd.py Adi07 [Madhya05 ...]
# Ручные правки главы: ed/fixes/<Глава>.txt, строки вида
#   @N поле: было => стало  # причина        (поле: bn | tl | ww | tr | title; для bn/tl/ww — подстрока любой строки)
# Сверка с vedabase: ed/work/vb-<Глава>.json ({"N" или "N-M": {"bn":[...], "tr":[...]}}, tools/extract.py).
import re, os, sys, json, unicodedata, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyr import conv

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BD = '০১২৩৪৫৬৭৮৯'
LILA = {'Adi': 'Ади-лила', 'Madhya': 'Мадхья-лила', 'Antya': 'Антья-лила'}
JUNK = '\u3000\uFFA0\u3164\u1160\t\u00a0'

def bn2i(s): return int(''.join(str(BD.index(c)) for c in s))
def has_bn(s): return any('ঀ' <= c <= '৿' for c in s)
def has_cyr(s): return any('Ѐ' <= c <= 'ӿ' for c in s)
def is_sep(s): return s.strip(' ' + JUNK) == ''
VEND = re.compile(r'॥\s*([০-৯]*)\s*॥')
PNUM = re.compile(r'^\((\d+)(?:\s*[–-]\s*(\d+))?\)\s*')

def squash(s):
    """мусор Word -> пробел; в пословном/транслитерации слова через два пробела"""
    s = re.sub('[' + JUNK + ']', ' ', s)
    return re.sub(r' {2,}', '  ', s).strip()

def join_wrapped(lines):
    out = ''
    for l in lines:
        l = re.sub('[' + JUNK + ']', ' ', l).strip()
        l = re.sub(r' {2,}', ' ', l)
        if not out: out = l
        elif re.search(r'\w-$', out) and not re.search(r'\s-$', out): out += l
        else: out += ' ' + l
    return out

def norm_tl(s):
    s = unicodedata.normalize('NFC', s.lower())
    return re.sub(r'[^\ẁ-ͯ]', '', s)

def sim(a, b): return difflib.SequenceMatcher(None, norm_tl(a), norm_tl(b)).ratio()

autofix = []
def parse(path):
    L = [l.rstrip('\n') for l in open(path, encoding='utf-8')]
    pend = [l.endswith('\xa0') for l in L]           # конец абзаца в выгрузке antiword
    vend = [i for i, l in enumerate(L) if VEND.search(l) and has_bn(l) and not has_cyr(l)]
    # группы стихов: подряд идущие ॥N॥, между которыми только бенгальские строки
    groups = []
    for i in vend:
        if groups and all(has_bn(L[k]) and not has_cyr(L[k]) for k in range(groups[-1][-1] + 1, i)):
            groups[-1].append(i)
        else: groups.append([i])
    blocks = []
    for g in groups:
        s = g[0]
        while s - 1 >= 0 and has_bn(L[s - 1]) and not has_cyr(L[s - 1]) and not VEND.search(L[s - 1]): s -= 1
        blocks.append({'start': s, 'ends': g})
    # шапка
    head = [l.strip(' ' + JUNK) for l in L[:blocks[0]['start']]]
    title_lines = []
    for l in head:
        if l: title_lines.append(l)
        elif title_lines and is_sep(l) and len(title_lines) >= 4: break
    hdr = [x for x in title_lines[:4]]
    pre = L[len([1 for _ in head]) and 0: blocks[0]['start']]
    verses, removed = [], []
    # всё, что в шапке после 4 строк заголовка, — удалить
    hb = []
    cnt = 0
    for i in range(blocks[0]['start']):
        if L[i].strip(' ' + JUNK):
            cnt += 1
            if cnt > 4: hb.append(i)
    if hb: removed.append({'where': 'до стиха 1', 'lines': [L[i] for i in range(hb[0], blocks[0]['start'])]})
    for bi, b in enumerate(blocks):
        nxt = blocks[bi + 1]['start'] if bi + 1 < len(blocks) else len(L)
        nums = []
        bn = []
        cur = []
        for i in range(b['start'], b['ends'][-1] + 1):
            cur.append(L[i])
            m = VEND.search(L[i])
            if m and i in b['ends']:
                if m.group(1): nums.append(bn2i(m.group(1)))
                else:     # «॥ ॥» без номера — номер по порядку
                    n0 = (nums[-1] if nums else (verses[-1]['nums'][-1] if verses else 0)) + 1
                    nums.append(n0); cur[-1] = cur[-1].replace(m.group(0), '॥ %s ॥' % bnum(n0))
                    autofix.append((n0, 'bn', 'пропущен номер «॥ ॥»', '॥ %s ॥' % bnum(n0)))
                bn.append(cur); cur = []
        i = b['ends'][-1] + 1
        # до абзаца (N): транслитерация, пословный, пояснения к словам
        body = []
        while i < nxt and not PNUM.match(L[i].lstrip(JUNK + ' ')):
            body.append(L[i]); i += 1
        tr_lines = []
        if i < nxt:
            tr_lines.append(L[i]); j = i + 1
            while j < nxt and not pend[j - 1] and not is_sep(L[j]) and not (has_bn(L[j]) and not has_cyr(L[j])):
                tr_lines.append(L[j]); j += 1
            i = j
        rest = list(range(i, nxt))
        verses.append({'nums': nums, 'bn_raw': bn, 'body': body, 'tr_raw': tr_lines, 'rest': [L[k] for k in rest]})
    return hdr, verses, removed

def vb_lines(vb, n):
    """строки транслитерации vedabase (кириллицей) для стиха n; сдвоенные «a-b» делятся поровну"""
    for key, e in vb.items():
        a, b = (list(map(int, key.split('-'))) + [None])[:2]
        b = b or a
        if a <= n <= b:
            ls = [conv(x)[0] for t in e['tr'] for x in t.split('\n')]
            k = len(ls) // (b - a + 1)
            return ls[(n - a) * k:(n - a + 1) * k]
    return []

def split_body(v, vb):
    """body -> пары (транслит, пословный) + пояснения к словам (удаляются)"""
    exp = []
    for n in v['nums']: exp += vb_lines(vb, n)
    lines = [l for l in v['body'] if not is_sep(l)]
    pairs, gloss, k = [], [], 0
    tlwords = set()
    for x in exp: tlwords |= {norm_tl(w) for w in re.split(r'[\s\-—,]+', x) if w}
    for idx, l in enumerate(lines):
        if gloss or (k >= len(exp) and pairs and pairs[-1][1] is not None):
            gloss.append(l); continue
        if k < len(exp) and sim(l, exp[k]) > 0.6:
            pairs.append([squash(l), None]); k += 1; continue
        left = l.split(' — ')[0] if ' — ' in l else None
        if left is not None and pairs and all(norm_tl(w) in tlwords or norm_tl(w) == '' for w in re.split(r'[\s\-,]+', left) if w) \
                and any(unicodedata.combining(c) or c == 'й' for c in left):
            gloss.append(l); continue
        if pairs and pairs[-1][1] is None:
            pairs[-1][1] = squash(l); continue
        # строка без пары: возможно, транслитерация, сильно отличающаяся от vedabase
        pairs.append([squash(l), None]); k += 1
    return pairs, gloss, exp

def load_fixes(path):
    fx = []
    if not os.path.exists(path): return fx
    for l in open(path, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l.strip() or l.startswith('#'): continue
        m = re.match(r'^@(\S+)\s+(\w+):\s*(.*?)\s*=>\s*(.*?)\s*(?:#\s*(.*))?$', l)
        if not m: print('  ! bad fix line:', l); continue
        fx.append({'n': m.group(1), 'f': m.group(2), 'old': m.group(3), 'new': m.group(4), 'why': m.group(5) or '', 'used': 0})
    return fx

def bnum(n): return ''.join(BD[int(c)] for c in str(n))

def run(chap):
    lila, nn = re.match(r'([A-Za-z]+)(\d+)', chap).groups()
    src = os.path.join(ROOT, 'vcd', 'txt', 'CC_%s.txt' % chap)
    vbp = os.path.join(ROOT, 'ed', 'work', 'vb-%s.json' % chap)
    vb = json.load(open(vbp, encoding='utf-8')) if os.path.exists(vbp) else {}
    hdr, verses, removed = parse(src)
    fixes = load_fixes(os.path.join(ROOT, 'ed', 'fixes', '%s.txt' % chap))
    log_auto = {'junk': 0}
    warn = []
    out = []
    title = hdr[3] if len(hdr) > 3 else ''
    for f in fixes:
        if f['f'] == 'title' and f['old'] in title:
            title = title.replace(f['old'], f['new']); f['used'] += 1
    out += ['“Шри Чайтанья-чаритамрита”  ', LILA[lila] + '  ', 'Глава %d  ' % int(nn), '**%s**  ' % title,
            '(перевод Вриндавана Чандры даса)', '']
    expect = 1
    rows = []
    for v in verses:
        nums = v['nums']
        lab = '%d' % nums[0] if len(nums) == 1 else '%d–%d' % (nums[0], nums[-1])
        if nums[0] != expect: warn.append('нумерация: перед ॥%d॥ ожидался %d' % (nums[0], expect))
        expect = nums[-1] + 1
        for x in v['bn_raw'] + [v['body'], v['tr_raw']]:
            log_auto['junk'] += sum(1 for l in x for c in l if c in '\u3000\uFFA0\u3164\u1160\t')
        bn = [[squash(l) for l in g] for g in v['bn_raw']]
        pairs, gloss, exp = split_body(v, vb)
        tr = join_wrapped(v['tr_raw'])
        m = PNUM.match(tr)
        tlab = (m.group(1) + ('–' + m.group(2) if m.group(2) else '')) if m else '?'
        if tlab != lab: autofix.append((lab, 'tr', 'номер перевода (%s)' % tlab, '(%s)' % lab))
        tr = tr[m.end():] if m else tr
        # ручные правки
        key = lab.replace('–', '-')
        for f in fixes:
            if f['n'] != key and f['n'] != str(nums[0]): continue
            fld = f['f']
            def rep(s):
                if f['old'] in s:
                    f['used'] += 1; return s.replace(f['old'], f['new'])
                return s
            if fld == 'tr': tr = rep(tr)
            elif fld == 'bn': bn = [[rep(l) for l in g] for g in bn]
            elif fld == 'tl': pairs = [[rep(a), b] for a, b in pairs]
            elif fld == 'ww': pairs = [[a, rep(b) if b else b] for a, b in pairs]
            elif fld == 'addww':     # @N addww: <строка транслит. (начало)> => <пословный>
                for p in pairs:
                    if p[1] is None and p[0].startswith(f['old']): p[1] = f['new']; f['used'] += 1
        # «_» в пословном у ВЧД — сцепка слов одной глоссы (в .doc); в md — обычный пробел
        for p in pairs:
            if p[1] and '_' in p[1]: log_auto['us'] = log_auto.get('us', 0) + p[1].count('_'); p[1] = p[1].replace('_', ' ')
        if gloss: removed.append({'where': 'стих %s, пояснение к словам после пословного' % lab, 'lines': gloss})
        rest = v['rest']
        # разбить «хвост» на куски по разделителям
        chunks, curc = [], []
        for l in rest:
            if is_sep(l):
                if curc: chunks.append(curc); curc = []
            else: curc.append(l)
        if curc: chunks.append(curc)
        for c in chunks:
            txt = ' '.join(c)
            if re.search(r'Махарадж|Прабхупад|Шридхар', txt): kind = 'современный комментарий'
            elif c is chunks[-1] and (has_bn(txt) or (len(c) <= 3 and any(unicodedata.combining(ch) for ch in txt))) and v is not verses[-1]:
                kind = 'подзаголовок «Анубхашьи» перед стихом %d' % expect
            else: kind = 'прочее'
            removed.append({'where': 'после стиха %s — %s' % (lab, kind), 'lines': c})
        # md
        for g in bn: out.append('  \n'.join(g)); out.append('')
        il = []
        for a, b in pairs:
            il.append(a)
            if b: il.append(b)
        out.append('  \n'.join(il)); out.append('')
        out.append('(%s) %s' % (lab, tr)); out.append('')
        rows.append({'lab': lab, 'nums': nums, 'bn': bn, 'pairs': pairs, 'exp': exp, 'tr': tr})
        # проверка транслитерации и бенгальского против vedabase
    md = '\n'.join(out).rstrip() + '\n'
    od = os.path.join(ROOT, 'ed')
    for d in ('vcd', 'review'): os.makedirs(os.path.join(od, d), exist_ok=True)
    open(os.path.join(od, 'vcd', 'CC_%s.md' % chap), 'w', encoding='utf-8').write(md)
    # журнал удалённого
    R = ['# Удалено при подготовке главы %s (этап А)' % chap, '',
         'Дословно, в порядке следования. Строки выгрузки сохранены как есть (переносы — как в .doc).', '']
    for r in removed:
        R.append('## ' + r['where']); R.append('')
        R += ['    ' + re.sub('[' + JUNK + ']', ' ', l).rstrip() for l in r['lines']]; R.append('')
    open(os.path.join(od, 'review', 'removed-%s.md' % chap), 'w', encoding='utf-8').write('\n'.join(R))
    # журнал правок
    F = ['# Правки главы %s (этап А)' % chap, '',
         '## Автоматически', '',
         '- Мусорные символы Word (U+1160, U+3000, U+FFA0, U+3164, табуляции) убраны, слова пословного разделены двумя пробелами: %d символов.' % log_auto['junk'],
         '- «_» внутри глоссы пословного (сцепка слов в .doc) заменён пробелом: %d.' % log_auto.get('us', 0),
         '- Переносы строк выгрузки внутри перевода склеены; переносы после дефиса — без пробела.', '',
         '## Вручную (ed/fixes/%s.txt)' % chap, '', '| Стих | Поле | Было | Стало | Причина |', '|---|---|---|---|---|']
    for n, fld, a, b in autofix:
        F.insert(F.index('## Вручную (ed/fixes/%s.txt)' % chap) - 1, '- Стих %s, %s: %s → %s.' % (n, fld, a, b))
    for f in fixes:
        F.append('| %s | %s | %s | %s | %s |' % (f['n'], f['f'], f['old'], f['new'], f['why']))
        if not f['used']: warn.append('правка не применена: @%s %s: %s' % (f['n'], f['f'], f['old']))
    open(os.path.join(od, 'review', 'fixes-%s.md' % chap), 'w', encoding='utf-8').write('\n'.join(F) + '\n')
    json.dump(rows, open(os.path.join(od, 'work', 'rows-%s.json' % chap), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%s: %d блоков, стихи 1–%d; удалено фрагментов: %d; правок: %d' % (chap, len(verses), expect - 1, len(removed), len(fixes)))
    for w in warn: print('  !', w)

if __name__ == '__main__':
    for c in sys.argv[1:]: run(c)
