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
def is_bn_gap(L, a, b):
    # два ॥N॥ подряд разделены двумя и более пустыми строками-разделителями «ᅠ» — это разные стихи, не сдвоенный
    return sum(1 for k in range(a + 1, b) if L[k].strip() in ('\uffa0', '\u1160', 'ᅠ')) >= 2

def parse(path):
    L = [l.rstrip('\n') for l in open(path, encoding='utf-8')]
    pend = [l.endswith('\xa0') for l in L]           # конец абзаца в выгрузке antiword
    vend = [i for i, l in enumerate(L) if VEND.search(l) and has_bn(l) and not has_cyr(l)]
    # группы стихов: подряд идущие ॥N॥, между которыми только бенгальские строки
    groups = []
    for i in vend:
        if groups and all((has_bn(L[k]) and not has_cyr(L[k])) or is_sep(L[k]) for k in range(groups[-1][-1] + 1, i)) \
                and any(has_bn(L[k]) for k in range(groups[-1][-1] + 1, i)) and not is_bn_gap(L, groups[-1][-1], i):
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
            if is_sep(L[i]): continue
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
    lines = [re.sub(r' {2,}', '  ', re.sub('[' + JUNK + ']', ' ', l)).strip() for l in v['body'] if not is_sep(l)]
    pairs, gloss = [], []
    tlwords = set()
    for x in exp: tlwords |= {norm_tl(w) for w in re.split(r'[\s\-—,]+', x) if w}
    TLM = '\u0301\u0303\u0304\u0307\u0310\u0323'
    RUS = set('ыьъюяёщцфЫЬЪЮЯЁЩЦФ')
    def tlish(t): return any(c in TLM for c in t) and not any(c in RUS for c in t)
    near = []                         # нумерация сдвоенных стихов у vedabase может быть сдвинута (Ади 1.72–73 / 73–74)
    for n in range(v['nums'][0] - 1, v['nums'][-1] + 2): near += vb_lines(vb, n)
    def is_tl(l):
        # похожесть на строку vedabase — только для строк без русских букв-маркеров и не с заглавной (пословный ВЧД бывает
        # почти дословным: «Брахма, Вишну, Шива — три гуна-Аватары», Ади 1.67)
        return tlish(l) or (bool(near) and not any(c in RUS for c in l) and not l[:1].isupper()
                            and max(sim(l, e) for e in near) > 0.7)
    def is_gloss(l):
        if ' — ' not in l: return False
        left, right = l.split(' — ', 1)
        lw = [w for w in re.split(r'[\s\-,;]+', left) if w]
        return bool(lw) and (any(c in TLM for c in left) or all(norm_tl(w) in tlwords for w in lw)) \
            and any(c in RUS for c in right) and not any(c in RUS for c in left)
    for l in lines:
        if gloss: gloss.append(l); continue
        if pairs and pairs[-1][1] is not None and is_gloss(l): gloss.append(l); continue
        if is_tl(l): pairs.append([squash(l), None]); continue
        if pairs and pairs[-1][1] is None: pairs[-1][1] = squash(l); continue
        if pairs: pairs[-1][1] += '  ' + squash(l); continue    # перенос строки пословного в .doc
        gloss.append(l)
    return pairs, gloss, exp

# Ссылки на шастры: у ВЧД «[ШБ, 11.2.40]» -> как в изданиях писаний «(Шримад-Бхагаватам, 11.2.40)»
REF_MAP = {'ШБ': 'Шримад-Бхагаватам', 'Шримад Бхагаватам': 'Шримад-Бхагаватам', 'Бг': 'Бхагавад-гита',
           'Брс': 'Бхакти-расамрита-синдху', 'БРС': 'Бхакти-расамрита-синдху', 'Б.р.с': 'Бхакти-расамрита-синдху',
           'Хари-бхакти-судходаи': 'Хари-бхакти-судходая', 'Хари-бхакти-судходайа': 'Хари-бхакти-судходая',
           'Лалита-Мадхава': 'Лалита-мадхава', 'Говинда-лӣла̄мр̣та': 'Говинда-лиламрита',
           'Уджжвала-ниламани': 'Уджвала-ниламани', 'Чайтанйа-чандродайа-на̄т̣ака': 'Чайтанья-чандродая-натака'}
SPEECH = re.compile(r'сказал|говорит|обратил|взмолил|плачет|молит|спросил|ответил')
def fix_refs(tr, log):
    def r(m):
        body = m.group(1).strip().rstrip(')')
        if SPEECH.search(body) or body == 'pic': return m.group(0)
        mm = re.match(r'^(.*?)[,\s]*(\d[\d.,\s–-]*)$', body)
        title, num = (mm.group(1), mm.group(2).strip()) if mm else (body, '')
        title = REF_MAP.get(title.strip(), title.strip())
        new = '(%s)' % (title + (', ' + num if num else ''))
        log.append((m.group(0), new)); return new
    tr = re.sub(r'\[([^\]\[]+)\]', r, tr)
    def r2(m):                         # «(ШБ, 10.33.3–4)» — уже в скобках, но сокращение
        new = '(%s,%s)' % (REF_MAP[m.group(1)], m.group(2)); log.append((m.group(0), new)); return new
    tr = re.sub(r'\((%s),?( ?[\d.–-]+)\)' % '|'.join(re.escape(k) for k in REF_MAP), r2, tr)
    def r3(m):                         # «(Видагдха-мадхава 1.2)» -> «(Видагдха-мадхава, 1.2)»
        new = '(%s, %s)' % (m.group(1), m.group(2)); log.append((m.group(0), new)); return new
    tr = re.sub(r'\(([А-ЯЁ][А-Яа-яЁё\- ]+?) (\d+(?:\.\d+)*(?:[–-]\d+)?)\)', r3, tr)
    # «”.(…)», «”(…)» -> «”. (…)» — только ссылка в конце перевода (не пояснение в скобках: «“бхри” (основа слова…)»)
    return re.sub(r'([”»])\.?\s*\(([^()]*)\)$', r'\1. (\2)', tr.rstrip())

def load_fixes(path):
    fx = []
    if not os.path.exists(path): return fx
    for l in open(path, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l.strip() or l.startswith('#') or l.startswith('@vb skip:'): continue   # @vb skip — для cmp_bn
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
    # @N reorder: 74 71 72-73 => 71 72 73-74 — переставить и перенумеровать стихи по изданию Гаудия Матха
    for f in fixes:
        if f['f'] != 'reorder': continue
        olds, news = f['old'].split(), f['new'].split()
        def rng(x): a, b = (x.split('-') + [x])[:2]; return list(range(int(a), int(b) + 1))
        blocks = [next(v for v in verses if v['nums'] == rng(o)) for o in olds]
        idx = sorted(verses.index(b) for b in blocks)
        for i, b, nw in zip(idx, blocks, news):
            nn_ = rng(nw)
            for g, n_ in zip(b['bn_raw'], nn_): g[-1] = VEND.sub('॥ %s ॥' % bnum(n_), g[-1])
            lab_ = '%d' % nn_[0] if len(nn_) == 1 else '%d–%d' % (nn_[0], nn_[-1])
            b['tr_raw'] = [PNUM.sub('(%s) ' % lab_, b['tr_raw'][0], count=1)] + b['tr_raw'][1:]
            b['nums'] = nn_
            verses[i] = b
        f['used'] += 1
        autofix.append((f['new'], 'порядок', 'у ВЧД: ' + f['old'], 'по изд. Гаудия Матха: ' + f['new']))
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
    notes = []
    for v in verses:
        nums = v['nums']
        lab = '%d' % nums[0] if len(nums) == 1 else '%d–%d' % (nums[0], nums[-1])
        if nums[0] != expect and len(nums) == 1:
            mt = PNUM.match(join_wrapped(v['tr_raw']))
            if mt and int(mt.group(1)) == expect:     # у ВЧД номер стиха повторён (напр. Ади 1.34 = шлока 1.1)
                old_n = nums[0]; nums[0] = expect
                v['bn_raw'][0][-1] = VEND.sub('॥ %s ॥' % bnum(expect), v['bn_raw'][0][-1])
                autofix.append((expect, 'bn', 'номер ॥ %s ॥ (повтор шлоки)' % bnum(old_n), '॥ %s ॥' % bnum(expect)))
                lab = str(expect)
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
            elif fld == 'tlsplit':   # @N tlsplit: <строка транслит. без диакритики, принятая за пословный> => (то же)
                for i, p in enumerate(pairs):
                    if p[1] and p[1].startswith(f['old']):
                        pairs.insert(i + 1, [p[1], None]); p[1] = None; f['used'] += 1; break
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
        rl = []; tr = fix_refs(tr, rl)
        for a, b in rl: autofix.append((lab, 'tr', 'ссылка %s' % a, b))
        for f in fixes:     # @N note: => текст редакторской сноски
            if f['f'] == 'note' and f['n'] in (key, str(nums[0])):
                notes.append('[^%s]: %s' % (key, f['new'])); tr += '[^%s]' % key; f['used'] += 1
        out.append('(%s) %s' % (lab, tr)); out.append('')
        rows.append({'lab': lab, 'nums': nums, 'bn': bn, 'pairs': pairs, 'exp': exp, 'tr': tr})
        # проверка транслитерации и бенгальского против vedabase
    if notes: out += ['---', ''] + [x + '\n' for x in notes]
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
    if vb:
        import cmp_bn
        nr, no = cmp_bn.write_md(chap)
        print('  расхождения с vedabase: чтений %d, орфографических %d -> ed/review/vedabase-diff-%s.md' % (nr, no, chap))
    print('%s: %d блоков, стихи 1–%d; удалено фрагментов: %d; правок: %d' % (chap, len(verses), expect - 1, len(removed), len(fixes)))
    for w in warn: print('  !', w)

if __name__ == '__main__':
    for c in sys.argv[1:]: run(c)
