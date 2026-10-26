"""Собирает данные сайта: крупные эпизоды → лилы → писания → стихи.

Источник — lila-db/export (сначала `python3 lila-db/build.py`) и файлы переводов. Для каждого отрывка
стихи разбираются на слои: оригинал, транслитерация, пословный, перевод, примечания (наши сноски / «Прим.»),
RU и EN. Оригинал и пословный берутся из самого файла (Карнапура) или из полного издания (*-full.md: Мурари,
Лочан, пады). Запуск: python3 site/tools/build_data.py  →  site/data/timeline.json (эпизоды, лилы, перечни
писаний — грузится сразу) и site/data/verses/<эпизод>.json (стихи — подгружаются при чтении).
"""
import glob
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


# Источники, которые не идут на сайт (пока нет). Издания Шри Чайтанья Сарасват Матха — наши (CLAUDE.md).
EXCLUDE_SOURCES = set()

# Краткие названия писаний для сайта (RU, EN, автор RU, автор EN)
SOURCES = {
    'cc': ('Шри Чайтанья-чаритамрита', 'Sri Chaitanya-charitamrita', 'Кришнадас Кавирадж Госвами', 'Krishnadasa Kaviraja Gosvami'),
    'cb': ('Шри Чайтанья-бхагавата', 'Sri Chaitanya-bhagavata', 'Вриндаван Дас Тхакур', 'Vrindavana Dasa Thakura'),
    'anuragavalli': ('Анурага-валли', 'Anuraga-valli', 'Манохара Дас', 'Manohara Dasa'),
    'prema-vivarta': ('Шри Према-виварта', 'Sri Prema-vivarta', 'приписывается Джагадананде Пандиту', 'attributed to Jagadananda Pandita'),
    'chaitanya-upanishad': ('Шри Чайтанья-упанишад', 'Sri Chaitanya Upanishad', 'Атхарваведа', 'Atharva Veda'),
    'jagannatha-vallabha': ('Шри Джаганнатха-валлабха-натака', 'Sri Jagannatha-vallabha-nataka', 'Рамананда Рай', 'Ramananda Raya'),
    'govinda-karcha': ('Кадача Говинды Даса', 'The Kadacha of Govinda Dasa', 'приписывается Говинде Дасу', 'attributed to Govinda Dasa'),
    'narottama-vilasa': ('Нароттама-виласа', 'Narottama-vilasa', 'Нарахари Чакраварти', 'Narahari Chakravarti'),
    'karnananda': ('Карнананда', 'Karnananda', 'Ядунандана Дас', 'Yadunandana Dasa'),
    'bhaktamal': ('Бхактамалы', 'Bhaktamalas', 'Набхадас и др.', 'Nabhadasa and others'),
    'vallabha-varta': ('Варты Валлабхи', 'Vallabha vartas', 'традиция Валлабхи', 'Vallabha tradition'),
    'vaishnava-lilamrita': ('Вайшнава-лиламрита', 'Vaishnava-lilamrita', 'Мадхава Паттанаяк', 'Madhava Pattanayak'),
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

NUM_RE = re.compile(r'^(?:>\s*)?\*\*([0-9][0-9.:a-zа-я+]*?)\.\*\*\s*(.*)$')   # «51а» — и кириллицей
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


def para_starts(rel):
    """Номера строк (1-based), с которых начинаются абзацы основного текста (до сносок), и для каждого абзаца —
    номер стиха **N.**, если абзац им начинается."""
    key = ('paras', rel)
    if key not in _cache:
        L = lines_of(rel) or []
        out, prev = [], ''
        for i, ln in enumerate(L):
            if FN_DEF.match(ln):
                break
            if ln.strip() and not prev.strip():
                m = NUM_RE.match(ln)
                out.append((i + 1, m.group(1).replace('а', 'a') if m else None))   # 51а (кир.) = 51a (лат.)
            prev = ln
        _cache[key] = out
    return _cache[key]


def align_en(ru_rel, a, b):
    """Отрезок строк a..b русского файла без нумерации (драма, проза) → отрезок английского файла.
    Опора — номера стихов: от ближайшего предшествующего стиха считается столько же абзацев в английском.
    Если строение файлов между опорами расходится — None."""
    en_rel = ru_rel.replace('/ru/', '/en/')
    if en_rel == ru_rel or not lines_of(en_rel):
        return None
    R, E = para_starts(ru_rel), para_starts(en_rel)
    en_lab = {}
    for k, (ln, n) in enumerate(E):
        if n and n not in en_lab: en_lab[n] = k

    def idx(line, end=False):
        k = max((i for i, (ln, _) in enumerate(R) if ln <= line), default=0)
        base = max((i for i in range(k + 1) if R[i][1] and R[i][1] in en_lab), default=None)
        if base is None:
            ke = k                                   # до первого стиха — по счёту абзацев от начала
        else:
            ke = en_lab[R[base][1]] + (k - base)
            nxt = next((i for i in range(base + 1, len(R)) if R[i][1] and R[i][1] in en_lab), None)
            if nxt is not None and en_lab[R[nxt][1]] - en_lab[R[base][1]] != nxt - base:
                return None                          # между опорами разное число абзацев
        if ke >= len(E): return None
        if not end: return E[ke][0]
        return (E[ke + 1][0] - 1) if ke + 1 < len(E) else len(lines_of(en_rel))
    ea, eb = idx(a), idx(b, True)
    return (en_rel, ea, eb) if ea and eb and eb >= ea else None


def passage(e):
    ru, en = [], []
    for vr in e.get('verses_resolved') or []:
        ru += build_side(vr['file'], vr['line'], vr['line_to'], full_for(vr['file'], 'ru'))
        if vr.get('file_en') and lines_of(vr['file_en']):
            rng = lines_from_url(vr.get('url_en')) or (vr['line'], vr['line_to'])
            en += build_side(vr['file_en'], rng[0], rng[1], full_for(vr['file_en'], 'en'))
        elif vr.get('count') is None and '/ru/' in vr['file']:     # отрезок по фрагментам строк
            al = align_en(vr['file'], vr['line'], vr['line_to'])
            if al:
                en += build_side(al[0], al[1], al[2], full_for(al[0], 'en'))
    vr0 = (e.get('verses_resolved') or [{}])[0]
    p = {'id': e['id'], 'ref': e['ref'], 'title': e['title'], 'summary': e.get('summary', ''),
         'authority': e.get('authority'), 'verses': ru, 'file': vr0.get('file'), 'from': vr0.get('from')}
    if en: p['verses_en'] = en
    if e['source'] == 'padas':
        p['poet'] = e['ref'].split(',')[0]
    return p


# ——— участники лил ———
# Не участники: Сам Господь (Он — в каждой лиле), аллегорические лица, авторы писаний в своих текстах
# и поэты пад (их тег стоит у записи, но они не участвуют в описываемой лиле).
NOT_PARTICIPANTS = {'@mahaprabhu', '@krishna', '@radha'}  # Кришна и Радха — Сам Гауранга и Его бхава, не отдельные участники
SOURCE_AUTHORS = {
    'lochana-cm': {'@lochana-dasa', '@narahari-sarakara'},   # Лочан и его гуру, упоминаемый в колофонах
    'jayananda-cm': {'@jayananda'},
    'prema-vilasa': {'@nityananda-dasa-author'},
    'gaura-krishnodaya': {'@govinda-deva-kavi'},
    'bhakti-ratnakara': {'@narahari-chakravarti'},
    'narottama-vilasa': {'@narahari-chakravarti'},
    'karnananda': {'@yadunandana-dasa-author'},
}


def persons_registry():
    """PERSONS.md → {тег: {name, name_en, note, section}}"""
    reg, section = {}, ''
    for ln in open(os.path.join(ROOT, 'lila-db/PERSONS.md'), encoding='utf-8'):
        m = re.match(r'^\| \*\*(.+?)\*\* \|', ln)
        if m:
            section = m.group(1); continue
        m = re.match(r'^\|\s*(@[a-z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$', ln)
        if m:
            reg[m.group(1)] = {'name': m.group(2), 'name_en': m.group(3), 'note': m.group(4), 'section': section}
    return reg


def participants(entries, reg):
    from collections import Counter
    c = Counter()
    for e in entries:
        if e.get('kind') == 'author':
            continue
        skip = set(NOT_PARTICIPANTS) | SOURCE_AUTHORS.get(e['source'], set())
        if e['source'] == 'padas':   # поэт пады — первый отрезок ссылки («Васу Гхош, ПК …»)
            poet = e['ref'].split(',')[0].lower()
            skip |= {t for t in e.get('persons', []) if t in reg and reg[t]['name'].split()[0].lower() in poet}
        for t in e.get('persons') or []:
            if t in skip or t not in reg or reg[t]['section'] == 'Аллегорические лица':
                continue
            c[t] += 1
    return [t for t, _ in c.most_common()]


def places_of(entries):
    seen = []
    for e in entries:
        for p in e.get('places') or []:
            if p not in seen: seen.append(p)
    return seen


def places_registry():
    reg = {}
    for ln in open(os.path.join(ROOT, 'lila-db/PLACES.md'), encoding='utf-8'):
        m = re.match(r'^\|\s*(#[a-z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$', ln)
        if m: reg[m.group(1)] = {'name': m.group(2), 'name_en': m.group(3), 'note': m.group(4)}
    return reg


def holy_spots():
    """Таблица святых мест раздела «Путешествие» сайта Шрилы Авадхута Махараджа (maps/src/holy-spots-avadhut.csv)
    → {id: {...}}; центры городов — из maps/ref/avadhut-travel/india-places.json."""
    import csv
    spots = {}
    for x in csv.DictReader(open(os.path.join(ROOT, 'maps/src/holy-spots-avadhut.csv'), encoding='utf-8-sig')):
        spots[x['id']] = {'name': x['Название'], 'name_en': x['Name (EN)'], 'kind': x['Тип'], 'city': x['Город'],
                          'lat': float(x['Широта']), 'lon': float(x['Долгота']),
                          'exact': x['Точность'] == 'точно', 'src': x['Источник координат'], 'url': x['На карте сайта']}
    cities = {c['id']: c for c in json.load(open(os.path.join(ROOT, 'maps/ref/avadhut-travel/india-places.json'), encoding='utf-8'))['cities']}
    return spots, cities


KIND = {'Храм': 'temple', 'Кунда': 'kund', 'Самадхи': 'samadhi', 'Гхат': 'ghat', 'Лес, роща': 'forest', 'Холм': 'hill',
        'Место явления': 'birthplace', 'Матх': 'math', 'Река': 'river'}


def build_places(events_out):
    """site/data/places.json: имена (PLACES.md) + координаты + лилы места. Координаты по приоритету:
    maps/places-overrides.yaml > maps/places-holyspots.yaml (святые места по таблице миссии) >
    maps/places-candidates.json (OSM, предварительно). Все святые места таблицы — site/data/holyspots.json."""
    import yaml
    reg = places_registry()
    cand = json.load(open(os.path.join(ROOT, 'maps/places-candidates.json'), encoding='utf-8'))
    over = yaml.safe_load(open(os.path.join(ROOT, 'maps/places-overrides.yaml'), encoding='utf-8')) or {}
    hsmap = yaml.safe_load(open(os.path.join(ROOT, 'maps/places-holyspots.yaml'), encoding='utf-8')) or {}
    spots, cities = holy_spots()
    lilas = {}
    for ev in events_out:
        for p in ev['places']:
            lilas.setdefault(p, []).append(ev['id'])
    out, used = {}, {}
    for tag, r in reg.items():
        c = cand.get(tag, {}); o = over.get(tag[1:]) or {}
        h = hsmap.get(tag[1:]); h = {'spot': h} if isinstance(h, str) else (h or {})
        d = {'name': r['name'], 'name_en': r['name_en'], 'note': r['note'], 'type': c.get('type', 'point')}
        if c.get('parent') or o.get('parent'): d['parent'] = '#' + (o.get('parent') or c['parent'].lstrip('#'))
        geo = None
        if 'lat' in o:
            geo = {'lat': o['lat'], 'lon': o['lon'], 'status': o.get('status', 'approx')}
        elif o.get('status') == 'hidden':
            geo = None
        elif h.get('spot'):
            s = spots[h['spot']]
            geo = {'lat': s['lat'], 'lon': s['lon'], 'status': h.get('status') or ('exact' if s['exact'] else 'approx'),
                   'spot': h['spot'], 'url': s['url'], 'kind': KIND.get(s['kind'], 'other')}
            used[h['spot']] = tag
        elif h.get('city'):
            cc = cities[h['city']]
            geo = {'lat': cc['center'][1], 'lon': cc['center'][0], 'status': h.get('status', 'approx'),
                   'url': 'https://avadhutmaharaj.com/travel/india/#' + h['city']}
        elif 'lat' in c:
            geo = {'lat': c['lat'], 'lon': c['lon'], 'status': 'unverified'}
        if geo:
            d.update(geo)
        note = o.get('note') or h.get('note')
        if note: d['geo_note'] = note
        d['lilas'] = lilas.get(tag, [])
        out[tag] = d
    json.dump(out, open(os.path.join(DATA, 'places.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    # святые места сегодня (слой «Святые места») — кроме тех, что уже стоят как места лил
    hs = [{'id': k, 'n': s['name'], 'ne': s['name_en'], 'k': KIND.get(s['kind'], 'other'), 'c': [s['lon'], s['lat']],
           'x': int(s['exact']), 'u': s['url'], **({'t': used[k]} if k in used else {})} for k, s in spots.items()]
    json.dump(hs, open(os.path.join(DATA, 'holyspots.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return out


def add_articles(people_out, reg):
    """Статьи о спутниках (parshadas/ru|en/*.md — сводные жизнеописания) → site/data/parshadas/<тег>-<lang>.json.
    У спутника со статьёй временный текст-заглушка убирается; ачарьи-преемники, не участвующие в лилах, добавляются
    в реестр сайта (группа «Ачарьи-преемники»). Даты и места явления и ухода — из parshadas/export/persons.json."""
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    import mdhtml
    exp = {p['id']: p for p in json.load(open(os.path.join(ROOT, 'parshadas/export/persons.json'), encoding='utf-8'))}
    out_dir = os.path.join(DATA, 'parshadas')
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))
    def used(tag):
        return bool(people_out.get(tag, {}).get('_used'))
    n = 0
    for lang in ('ru', 'en'):
        for f in sorted(glob.glob(os.path.join(ROOT, 'parshadas', lang, '*.md'))):
            md = open(f, encoding='utf-8').read()
            m = re.search(r'(@[a-z0-9-]+)', md.split('\n', 2)[1] if md.count('\n') > 1 else '')
            if not m:
                continue
            tag = m.group(1)
            body = re.sub(r'^\*[^\n]*@[a-z0-9-]+\*\s*$', '', md, count=1, flags=re.M)   # строка «имя · @тег»
            title, h = mdhtml.render(body, lang=lang)
            json.dump({'title': title, 'html': h}, open(os.path.join(out_dir, f'{tag[1:]}-{lang}.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, separators=(',', ':'))
            n += 1
            p = people_out.get(tag)
            if p is None:
                r = reg.get(tag) or {}
                e = exp.get(tag, {}).get('names', {})
                p = people_out[tag] = {'name': r.get('name') or e.get('ru') or title, 'name_en': r.get('name_en') or e.get('en') or title,
                                       'section': r.get('section', 'Спутники'), 'note': re.sub(r'\s*\{[^}]*\}', '', r.get('note', '')).strip(' ;,·')}
            p.setdefault('article', [])
            p['article'].append(lang)
            p.pop('bio', None); p.pop('bio_en', None)
            x = exp.get(tag)
            if x:
                if x.get('kind') == 'acharya':
                    p['section'] = 'Ачарьи-преемники' if 'later' in (x.get('circle') or []) else \
                        ('Ачарьи-предшественники' if p['section'] in ('Аллегорические лица', 'Спутники') and not used(tag) else p['section'])
                elif p['section'] == 'Аллегорические лица':   # строка дописана в конец PERSONS.md, после этого раздела
                    p['section'] = 'Спутники'
                life = {}
                for k in ('appearance', 'disappearance'):
                    v = (x.get('life') or {}).get(k) or {}
                    if v.get('date') or v.get('place'):
                        life[k] = {'date': v.get('date', ''), 'place': v.get('place', '')}
                if life:
                    p['life'] = life
    print('статей о спутниках:', n)


def ggd_verses():
    t = open(os.path.join(ROOT, 'gaura-ganoddesha/Gaura-Ganoddesha-Dipika-ru.md'), encoding='utf-8').read()
    return {m.group(1): md_inline(strip_fn(m.group(2))) for m in re.finditer(r'^\*\*(\d+)\.\*\* (.+)$', t, re.M)}


def main():
    L = json.load(open(os.path.join(ROOT, 'lila-db/export/lilas.json'), encoding='utf-8'))
    events = json.load(open(os.path.join(ROOT, 'lila-db/export/events.json'), encoding='utf-8'))
    meta = json.load(open(os.path.join(ROOT, 'lila-db/export/meta.json'), encoding='utf-8'))
    pord = list(meta['periods'])
    events.sort(key=lambda e: (pord.index(e['period']) if e['period'] in pord else 99, e.get('order') or 0))
    by_ev = {}
    for e in L:
        if e.get('event') and e['source'] not in EXCLUDE_SOURCES: by_ev.setdefault(e['event'], []).append(e)
    order = list(SOURCES)
    eps = {eid: {'id': eid, 'title': t, 'title_en': te, 'events': []} for eid, t, te, _, _ in EPISODES}
    verses = {eid: {} for eid in eps}
    reg = persons_registry()
    used_people = set()
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
        people = participants(by_ev[ev['id']], reg)
        used_people.update(people)
        before = ev['period'] == 'P00' or (ev['period'] == 'P01' and (ev.get('order') or 0) < 70)
        eps[ep]['events'].append({
            'id': ev['id'], 'title': ev['title'], 'title_en': ev.get('title_en', ''),
            'years': ev.get('years'), 'date_conf': ev.get('date_conf'),
            'age': None if before else ev.get('age'), 'before': before,
            'calendar': ev.get('calendar', ''), 'cc': ev.get('cc', ''), 'cb': ev.get('cb', ''),
            'sources': cards, 'persons': people,
            'places': places_of(by_ev[ev['id']]),
        })
    out = []
    for e in eps.values():
        if not e['events']: continue
        ys = [y for ev in e['events'] for y in (ev['years'] or [])]
        e['years'] = [min(ys), max(ys)] if ys else None
        e['before'] = all(ev['before'] for ev in e['events'])
        seen = []   # участники эпизода — по порядку первого появления в его лилах
        for ev in e['events']:
            seen += [t for t in ev['persons'] if t not in seen]
        e['persons'] = seen
        out.append(e)
    os.makedirs(os.path.join(DATA, 'verses'), exist_ok=True)
    for f in os.listdir(os.path.join(DATA, 'verses')):
        os.remove(os.path.join(DATA, 'verses', f))
    # реестр участников: имена — из PERSONS.md, описания (пока заглушки) — из site/content/persons.yaml
    import yaml
    bios = yaml.safe_load(open(os.path.join(ROOT, 'site/content/persons.yaml'), encoding='utf-8')) or {}
    ggd = ggd_verses()
    people_out = {}
    for t in sorted(used_people):
        r = reg[t]
        b = bios.get(t[1:]) or {}
        d = {'name': r['name'], 'name_en': r['name_en'], 'section': r['section'],
             'note': re.sub(r'\s*\{[^}]*\}', '', r['note']).strip(' ;,·')}   # служебные пометки {карточка: …} — не для сайта
        if b.get('bio_ru'): d['bio'] = [md_inline(x.strip()) for x in b['bio_ru'].split('\n\n') if x.strip()]
        if b.get('bio_en'): d['bio_en'] = [md_inline(x.strip()) for x in b['bio_en'].split('\n\n') if x.strip()]
        if b.get('ggd'): d['ggd'] = [{'n': str(n), 'text': ggd[str(n)]} for n in b['ggd'] if str(n) in ggd]
        d['_used'] = True
        people_out[t] = d
    add_articles(people_out, reg)
    for d in people_out.values():
        d.pop('_used', None)
    json.dump(people_out, open(os.path.join(DATA, 'persons.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    pl = build_places([ev for e in out for ev in e['events']])
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
