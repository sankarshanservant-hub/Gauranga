"""Собирает данные сайта: крупные эпизоды → лилы → писания → стихи.

Источник — lila-db/export (сначала `python3 lila-db/build.py`) и файлы переводов. Для каждого отрывка
стихи разбираются на слои: оригинал, транслитерация, пословный, перевод, примечания (наши сноски / «Прим.»),
RU и EN. Оригинал и пословный берутся из самого файла (Карнапура) или из полного издания (*-full.md: Мурари,
Лочан, пады). Запуск: python3 site/tools/build_data.py  →  site/data/timeline.json (эпизоды, лилы, перечни
писаний — грузится сразу) и site/data/verses/<эпизод>.json (стихи — подгружаются при чтении).
"""
import json
import os
import re
import html

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = os.path.join(ROOT, 'site', 'data')

# Крупные эпизоды (временно — по периодам lila-db/PERIODS.md; «Явление Господа» выделено из P01–P02).
# Эпизод забирает события своих периодов; границы внутри P01/P02 — в episode_of (по order события).
EPISODES = [  # (id, RU, EN, периоды, —)
    ('ep-before', 'До явления', 'Before the Advent', ['P00'], None),
    ('ep-ancestors', 'Предки и спутники', 'Ancestors and Associates', ['P01'], None),
    ('ep-advent', 'Явление Господа', 'The Advent of the Lord', ['P01', 'P02'], None),
    ('ep-infancy', 'Младенчество', 'Infancy', ['P02'], None),
    ('ep-childhood', 'Детство', 'Childhood', ['P03'], None),
    ('ep-boyhood', 'Отрочество и учёба', 'Boyhood and Studies', ['P04'], None),
    ('ep-youth', 'Юность: учитель и семья', 'Youth: Teacher and Householder', ['P05'], None),
    ('ep-gaya', 'Гая: посвящение', 'Gaya: Initiation', ['P06'], None),
    ('ep-navadvipa', 'Санкиртана в Навадвипе', 'Sankirtana in Navadvipa', ['P07'], None),
    ('ep-sannyasa', 'Санньяса', 'Sannyasa', ['P08'], None),
    ('ep-to-puri', 'Путь в Пури', 'The Road to Puri', ['P09'], None),
    ('ep-sarvabhauma', 'Пури: Сарвабхаума', 'Puri: Sarvabhauma', ['P10'], None),
    ('ep-south', 'Паломничество по Югу', 'Pilgrimage to the South', ['P11'], None),
    ('ep-ratha', 'Пури: Ратха-ятра', 'Puri: Ratha-yatra', ['P12'], None),
    ('ep-vrindavana', 'Путь во Вриндаван', 'Journey to Vrindavana', ['P13'], None),
    ('ep-final', 'Последние годы в Пури', 'Final Years in Puri', ['P14'], None),
    ('ep-departure', 'Уход и после', 'Departure and After', ['P15'], None),
]
ADVENT_P02_MAX = 5  # события P02 с order ≤ 5 (Ниламбара, грудь, Сита, богини, имя Нимай) — в «Явлении»


def episode_of(ev):
    per, o = ev['period'], ev.get('order') or 0
    if per == 'P01': return 'ep-ancestors' if o < 50 else 'ep-advent'
    if per == 'P02': return 'ep-advent' if o <= ADVENT_P02_MAX else 'ep-infancy'
    for eid, _, _, periods, _ in EPISODES:
        if per in periods: return eid
    return None


# Краткие названия писаний для сайта (RU, EN, автор RU, автор EN)
SOURCES = {
    'murari-kcc': ('Шри Кришна-Чайтанья-чаритамрита', 'Sri Krishna-Chaitanya-charitamrita', 'Мурари Гупта', 'Murari Gupta'),
    'karnapura-ckm': ('Чайтанья-чарита-махакавья', 'Chaitanya-charita-mahakavya', 'Кави Карнапура', 'Kavi Karnapura'),
    'chaitanya-chandrodaya': ('Чайтанья-чандродая', 'Chaitanya-chandrodaya', 'Кави Карнапура', 'Kavi Karnapura'),
    'gaura-krishnodaya': ('Гаура-кришнодая', 'Gaura-krishnodaya', 'Говинда-дева', 'Govinda-deva'),
    'lochana-cm': ('Чайтанья-мангала', 'Chaitanya-mangala', 'Лочан Дас', 'Lochana Dasa'),
    'jayananda-cm': ('Чайтанья-мангала', 'Chaitanya-mangala', 'Джаянанда', 'Jayananda'),
    'prema-vilasa': ('Према-виласа', 'Prema-vilasa', 'Нитьянанда Дас', 'Nityananda Dasa'),
    'advaita-prakasha': ('Адвайта-пракаша', 'Advaita-prakasha', 'Ишана Нагара', 'Ishana Nagara'),
    'padas': ('Пады современников', 'Padas of the contemporaries', 'разные авторы', 'various poets'),
    'vaishnava-vandana': ('Вайшнава-вандана', 'Vaishnava-vandana', 'Джива Госвами, Девакинандана', 'Jiva Gosvami, Devakinandana'),
    'gaura-ganoddesha': ('Гаура-ганоддеша-дипика', 'Gaura-ganoddesha-dipika', 'Кави Карнапура', 'Kavi Karnapura'),
    'bhakti-ratnakara': ('Бхакти-ратнакара', 'Bhakti-ratnakara', 'Нарахари Чакраварти', 'Narahari Chakravarti'),
    'nityananda-vamsha': ('Нитьянанда-вамша-вистара', 'Nityananda-vamsha-vistara', '', ''),
    'gaura-stotras': ('Гимны о Гауре', 'Hymns to Gaura', 'спутники Махапрабху', "Mahaprabhu's associates"),
}
# Полные издания со слоями оригинала (каталог → базовое имя)
FULL = {
    'lochana': 'Lochana-Chaitanya-Mangala-{}-full.md',
    'murari-gupta': 'Murari-Gupta-Kadacha-{}-full.md',
    'padas': 'Padas-{}-full.md',
}

NUM_RE = re.compile(r'^(?:>\s*)?\*\*([0-9][0-9.:a-z+]*?)\.\*\*\s*(.*)$')
PLAIN_NUM_RE = re.compile(r'^(\d+[a-z]?)\.\s+(.*)$')
FN_REF = re.compile(r'\[\^([^\]]+)\]')
FN_DEF = re.compile(r'^\[\^([^\]]+)\]:\s?(.*)$')
TRANSLIT_CH = re.compile('[āīūṛṝḷṣśṇṅñṭḍḥṁṃẏ]')
INDIC = re.compile('[ऀ-෿]')

_cache = {}


def lines_of(rel):
    if rel not in _cache:
        p = os.path.join(ROOT, rel)
        _cache[rel] = open(p, encoding='utf-8').read().split('\n') if os.path.exists(p) else None
    return _cache[rel]


def footnotes(rel):
    key = ('fn', rel)
    if key not in _cache:
        defs, cur = {}, None
        for ln in lines_of(rel) or []:
            m = FN_DEF.match(ln)
            if m:
                cur = m.group(1)
                defs[cur] = m.group(2)
            elif cur and ln.startswith('    '):
                defs[cur] += ' ' + ln.strip()
            else:
                cur = None
        _cache[key] = defs
    return _cache[key]


def md_inline(s):
    s = re.sub(r'(^|\n)>\s?', r'\1', s)
    s = html.escape(s, quote=False)
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    return s


def strip_fn(s):
    return FN_REF.sub('', s).strip()


def paragraphs(lines):
    """Разбивает строки на абзацы; ```-блоки — отдельный абзац с пометкой."""
    out, cur, fence = [], [], False
    for ln in lines:
        if ln.strip().startswith('```'):
            if fence:
                out.append(('fence', cur)); cur = []; fence = False
            else:
                if cur: out.append(('p', cur)); cur = []
                fence = True
            continue
        if fence:
            cur.append(ln); continue
        if not ln.strip():
            if cur: out.append(('p', cur)); cur = []
        else:
            cur.append(ln)
    if cur: out.append(('fence' if fence else 'p', cur))
    return out


def classify(kind, lines):
    t = '\n'.join(lines).strip()
    if kind == 'fence': return 'orig', t
    if t.startswith('>>') or t == '---' or t.startswith('#'): return 'skip', t
    for lab in ('**Пословно:**', '*Пословно:*', '**Word-for-word:**', '*Word for word:*', '*Word-for-word:*', '**Word for word:**'):
        if t.startswith(lab): return 'wbw', t[len(lab):].strip()
    for lab in ('**Перевод.**', '**Translation.**'):
        if t.startswith(lab): return 'text', t[len(lab):].strip()
    for lab in ('**Прим.**', '**Note.**'):
        if t.startswith(lab): return 'note', t[len(lab):].strip()
    if INDIC.search(t) and not re.search('[А-Яа-яA-Za-z]{3}', INDIC.sub('', t)): return 'orig', t
    if t.startswith('*') and t.rstrip().endswith('*') and TRANSLIT_CH.search(t): return 'translit', t.replace('*', '')
    return 'text', t


def full_layers(full_rel, first_line):
    """Слои (orig/translit/wbw), стоящие перед строкой перевода в полном издании."""
    L = lines_of(full_rel)
    if not L: return {}
    key = ('idx', full_rel)
    if key not in _cache:
        d = {}
        for i, ln in enumerate(L):
            d.setdefault(strip_fn(ln), i)
        _cache[key] = d
    j = _cache[key].get(strip_fn(first_line))
    if j is None: return {}
    i = j - 1
    block = []
    while i >= 0:
        ln = L[i]
        if ln.startswith('#') or NUM_RE.match(ln): break
        block.insert(0, ln); i -= 1
    res = {}
    paras = paragraphs(block)
    # берём только хвост из слоёв orig/translit/wbw/skip, идущий подряд перед стихом
    for kind, ls in reversed(paras):
        c, t = classify(kind, ls)
        if c in ('orig', 'translit', 'wbw'):
            res.setdefault(c, t)
        elif c == 'skip':
            continue
        else:
            break
    return res


def parse_units(rel, a, b):
    """Стихи в строках a..b (1-based) файла rel → список единиц."""
    L = lines_of(rel)
    if not L: return []
    seg = L[a - 1:b]
    units, cur = [], None

    def new(n, first):
        u = {'n': n, 'raw': [], 'first': first, 'layers': {}}
        units.append(u); return u

    for kind, ls in paragraphs(seg):
        head = ls[0]
        m = NUM_RE.match(head) if kind == 'p' else None
        pm = PLAIN_NUM_RE.match(head) if kind == 'p' and not m else None
        if kind == 'p' and pm and all(PLAIN_NUM_RE.match(x) for x in ls):
            for x in ls:  # «Адвайта-пракаша»: стих на строку
                mm = PLAIN_NUM_RE.match(x)
                u = new(mm.group(1), x); u['raw'].append(('text', mm.group(2)))
            cur = None; continue
        if m:
            cur = new(m.group(1), head)
            rest = [m.group(2)] + ls[1:] if m.group(2) else ls[1:]
            if rest: cur['raw'].append(('text', '\n'.join(rest)))
            continue
        c, t = classify(kind, ls)
        if c == 'skip': continue
        if cur is None or (c == 'text' and not NUM_RE.match(head) and cur.get('closed')):
            cur = new('', head)
        cur['raw'].append((c, t))
    return units


def lines_from_url(url):
    m = re.search(r'#L(\d+)(?:-L(\d+))?$', url or '')
    return (int(m.group(1)), int(m.group(2) or m.group(1))) if m else None


def build_side(rel, a, b, full_rel):
    units = parse_units(rel, a, b)
    fns = footnotes(rel)
    out = []
    for u in units:
        layers, notes = {}, []
        for c, t in u['raw']:
            if c == 'note': notes.append(t)
            else: layers[c] = (layers.get(c, '') + '\n' + t).strip()
        if full_rel and u['n'] and 'orig' not in layers:
            for k, v in full_layers(full_rel, u['first']).items():
                layers.setdefault(k, v)
        text = layers.get('text', '')
        refs = FN_REF.findall(text)
        for r in refs:
            if r in fns: notes.append(fns[r])
        text = FN_REF.sub(lambda m: '<sup>*</sup>' if m.group(1) in fns else '', md_inline(text))
        v = {'n': u['n'], 'text': text.replace('\n', '<br>')}
        if 'orig' in layers: v['orig'] = html.escape(layers['orig']).replace('\n', '<br>')
        if 'translit' in layers: v['translit'] = html.escape(layers['translit']).replace('\n', '<br>')
        if 'wbw' in layers: v['wbw'] = md_inline(strip_fn(layers['wbw']))
        if notes: v['notes'] = [md_inline(strip_fn(x)) for x in notes]
        out.append(v)
    return out


def full_for(rel, lang):
    top = rel.split('/')[0]
    if top in FULL:
        return f"{top}/{FULL[top].format(lang)}"
    return None


def passage(e):
    ru, en = [], []
    for vr in e.get('verses_resolved') or []:
        ru += build_side(vr['file'], vr['line'], vr['line_to'], full_for(vr['file'], 'ru'))
        if vr.get('file_en') and lines_of(vr['file_en']):
            rng = lines_from_url(vr.get('url_en')) or (vr['line'], vr['line_to'])
            en += build_side(vr['file_en'], rng[0], rng[1], full_for(vr['file_en'], 'en'))
    p = {'id': e['id'], 'ref': e['ref'], 'title': e['title'], 'summary': e.get('summary', ''),
         'authority': e.get('authority'), 'verses': ru}
    if en: p['verses_en'] = en
    if e['source'] == 'padas':
        p['poet'] = e['ref'].split(',')[0]
    return p


def main():
    L = json.load(open(os.path.join(ROOT, 'lila-db/export/lilas.json'), encoding='utf-8'))
    events = json.load(open(os.path.join(ROOT, 'lila-db/export/events.json'), encoding='utf-8'))
    meta = json.load(open(os.path.join(ROOT, 'lila-db/export/meta.json'), encoding='utf-8'))
    pord = list(meta['periods'])
    events.sort(key=lambda e: (pord.index(e['period']) if e['period'] in pord else 99, e.get('order') or 0))
    by_ev = {}
    for e in L:
        if e.get('event'): by_ev.setdefault(e['event'], []).append(e)
    order = list(SOURCES)
    eps = {eid: {'id': eid, 'title': t, 'title_en': te, 'events': []} for eid, t, te, _, _ in EPISODES}
    verses = {eid: {} for eid in eps}
    nverses = 0
    for ev in events:
        ep = episode_of(ev)
        if ep is None or not by_ev.get(ev['id']): continue
        srcs = {}
        for e in by_ev[ev['id']]:
            s = srcs.setdefault(e['source'], {'id': e['source'], 'passages': []})
            s['passages'].append(passage(e))
        slist = sorted(srcs.values(), key=lambda s: (min(p['authority'] or 'D' for p in s['passages']),
                                                    order.index(s['id']) if s['id'] in order else 99))
        cards = []
        for s in slist:
            t = SOURCES.get(s['id'], (s['id'], s['id'], '', ''))
            cards.append({'id': s['id'], 'title': t[0], 'title_en': t[1], 'author': t[2], 'author_en': t[3],
                          'authority': min((p['authority'] or 'D') for p in s['passages'])})
            nverses += sum(len(p['verses']) for p in s['passages'])
        verses[ep][ev['id']] = {s['id']: s['passages'] for s in slist}
        before = ev['period'] == 'P00' or (ev['period'] == 'P01' and (ev.get('order') or 0) < 70)
        eps[ep]['events'].append({
            'id': ev['id'], 'title': ev['title'], 'title_en': ev.get('title_en', ''),
            'years': ev.get('years'), 'date_conf': ev.get('date_conf'),
            'age': None if before else ev.get('age'), 'before': before,
            'calendar': ev.get('calendar', ''), 'cc': ev.get('cc', ''), 'cb': ev.get('cb', ''),
            'sources': cards,
        })
    out = []
    for e in eps.values():
        if not e['events']: continue
        ys = [y for ev in e['events'] for y in (ev['years'] or [])]
        e['years'] = [min(ys), max(ys)] if ys else None
        e['before'] = all(ev['before'] for ev in e['events'])
        out.append(e)
    os.makedirs(os.path.join(DATA, 'verses'), exist_ok=True)
    for f in os.listdir(os.path.join(DATA, 'verses')):
        os.remove(os.path.join(DATA, 'verses', f))
    tl = os.path.join(DATA, 'timeline.json')
    json.dump({'episodes': out}, open(tl, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    # стихи — порциями ≤ CHUNK байт (лилы эпизода подряд), номер порции записан у лилы в timeline.json
    CHUNK = 800_000
    total, nchunks = 0, 0
    evmap = {ev['id']: ev for e in out for ev in e['events']}
    for ep, d in verses.items():
        part, size, k = {}, 0, 1
        def flush():
            nonlocal part, size, k, total, nchunks
            if not part: return
            name = f'{ep}-{k}'
            p = os.path.join(DATA, 'verses', name + '.json')
            json.dump(part, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
            for eid in part: evmap[eid]['chunk'] = name
            total += os.path.getsize(p); nchunks += 1
            part, size, k = {}, 0, k + 1
        for eid, v in d.items():
            n = len(json.dumps(v, ensure_ascii=False).encode())
            if part and size + n > CHUNK: flush()
            part[eid] = v; size += n
        flush()
    json.dump({'episodes': out}, open(tl, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    old = os.path.join(DATA, 'lilas.json')
    if os.path.exists(old): os.remove(old)
    print(f"{len(out)} эпизодов, {sum(len(e['events']) for e in out)} лил, {nverses} стихов; "
          f"timeline.json {os.path.getsize(tl) // 1024} КБ, стихи {total // 1024} КБ в {nchunks} файлах")


if __name__ == '__main__':
    main()
