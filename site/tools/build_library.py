"""Читалка сайта: все наши переводы целиком (RU и EN), по главам.

Для книг с «полным изданием» (*-full.md: оригинал, транслитерация, пословный) берётся оно и делится по заголовкам;
иначе — поглавные файлы ru/*.md, en/*.md. Разбор разметки — mdhtml.py (слои: оригинал / транслитерация /
пословный / перевод / примечания).
Выход: site/data/library/index.json (книги, главы, связь «файл перевода → глава» для ссылок из ленты лил)
и site/data/library/<книга>/<lang>-<NN>.json ({title, html}).
Запуск: python3 site/tools/build_library.py

Издания Шри Чайтанья Сарасват Матха — наши (CLAUDE.md): «Чайтанья-бхагавата» (рус. пер.) и ЧЧ публикуются.
"""
import glob
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import mdhtml  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'site', 'data', 'library')

# group: 'skt' санскритские сочинения · 'bng' бенгальские жития · 'late' поздние сочинения о спутниках ·
# 'pada' пады, гимны, ванданы · 'other' иные традиции и прочее
BOOKS = [
    dict(id='cc', group='bng', title='Шри Чайтанья-чаритамрита', title_en='Sri Chaitanya-charitamrita',
         author='Кришнадас Кавирадж Госвами', author_en='Krishnadasa Kaviraja Gosvami',
         note='Перевод Вриндавана Чандры даса (Ади, Мадхья); Антья 16–19 — в его стиле.',
         note_en='Russian translation by Vrindavana Chandra Dasa (Adi, Madhya); Antya 16–19 in his style.',
         ru=['chaitanya-charitamrita/ed/vcd/CC_Adi*.md', 'chaitanya-charitamrita/ed/vcd/CC_Madhya*.md',
             'chaitanya-charitamrita/vcd/new/CC_Antya1[6-9].md'], en=[], cc=True),
    dict(id='cb', group='bng', title='Шри Чайтанья-бхагавата', title_en='Sri Chaitanya-bhagavata',
         author='Вриндаван Дас Тхакур', author_en='Vrindavana Dasa Thakura',
         note='Русский перевод — изд. Шри Чайтанья Сарасват Матха (Ади-кханда, 2006); Мадхья и Антья — до окончательной редактуры.',
         note_en='Russian translation published by Sri Chaitanya Saraswat Math (Adi-khanda, 2006); Madhya and Antya before final editing.',
         ru=['chaitanya-bhagavata/ed/CB_Adi*.md', 'chaitanya-bhagavata/ed/CB_Madhya*.md', 'chaitanya-bhagavata/ed/CB_Antya*.md'],
         en=[], cc=True),
    dict(id='murari', group='skt', title='Шри Кришна-Чайтанья-чаритамрита (Кадача)', title_en='Sri Krishna-Chaitanya-charitamrita (Kadacha)',
         author='Мурари Гупта', author_en='Murari Gupta',
         ru_full='murari-gupta/Murari-Gupta-Kadacha-ru-full.md', en_full='murari-gupta/Murari-Gupta-Kadacha-en-full.md', level=2,
         chapters='murari-gupta/{lang}/*.md'),
    dict(id='karnapura-ckm', group='skt', title='Шри Чайтанья-чарита-махакавья', title_en='Sri Chaitanya-charita-mahakavya',
         author='Кави Карнапура', author_en='Kavi Karnapura', ru=['karnapura-mahakavya/ru/*.md'], en=[]),
    dict(id='chaitanya-chandrodaya', group='skt', title='Чайтанья-чандродая', title_en='Chaitanya-chandrodaya',
         author='Кави Карнапура', author_en='Kavi Karnapura', ru=['chaitanya-chandrodaya/ru/*.md'], en=['chaitanya-chandrodaya/en/*.md']),
    dict(id='gaura-ganoddesha', group='skt', title='Гаура-ганоддеша-дипика', title_en='Gaura-ganoddesha-dipika',
         author='Кави Карнапура', author_en='Kavi Karnapura', ru=['gaura-ganoddesha/ru/*.md'], en=[]),
    dict(id='chaitanya-chandramrita', group='skt', title='Шри Чайтанья-чандрамрита', title_en='Sri Chaitanya-chandramrita',
         author='Прабодхананда Сарасвати', author_en='Prabodhananda Sarasvati', ru=['chaitanya-chandramrita/ru/*.md'], en=[]),
    dict(id='gaura-krishnodaya', group='skt', title='Шри Гаура-кришнодая', title_en='Sri Gaura-krishnodaya',
         author='Говинда-дева', author_en='Govinda-deva', ru=['gaura-krishnodaya/ru/*.md'], en=['gaura-krishnodaya/en/*.md']),
    dict(id='jagannatha-vallabha', group='skt', title='Шри Джаганнатха-валлабха-натака', title_en='Sri Jagannatha-vallabha-nataka',
         author='Рамананда Рай', author_en='Ramananda Raya',
         ru_full='jagannatha-vallabha/Jagannatha-Vallabha-ru-full.md', en_full='jagannatha-vallabha/Jagannatha-Vallabha-en-full.md', level=1,
         chapters='jagannatha-vallabha/{lang}/*.md'),
    dict(id='chaitanya-upanishad', group='skt', title='Шри Чайтанья-упанишад', title_en='Sri Chaitanya Upanishad',
         author='Атхарваведа (изд. Бхактивиноды Тхакура)', author_en='Atharva Veda (ed. Bhaktivinoda Thakura)',
         ru=['chaitanya-upanishad/ru/*.md'], en=['chaitanya-upanishad/en/*.md']),
    dict(id='lochana', group='bng', title='Шри Чайтанья-мангала', title_en='Sri Chaitanya-mangala',
         author='Лочан Дас', author_en='Lochana Dasa',
         ru_full='lochana/Lochana-Chaitanya-Mangala-ru-full.md', en_full='lochana/Lochana-Chaitanya-Mangala-en-full.md', level=1,
         chapters='lochana/{lang}/*.md'),
    dict(id='jayananda', group='bng', title='Чайтанья-мангала (фрагменты)', title_en='Chaitanya-mangala (fragments)',
         author='Джаянанда', author_en='Jayananda', ru=['jayananda/ru/*.md'], en=['jayananda/en/*.md']),
    dict(id='advaita-prakash', group='bng', title='Адвайта-пракаша', title_en='Advaita-prakasha',
         author='Ишана Нагара', author_en='Ishana Nagara', ru=['advaita-prakash/[0-9]*.md'], en=[]),
    dict(id='govinda-kadacha', group='bng', title='Кадача Говинды Даса', title_en='The Kadacha of Govinda Dasa',
         author='приписывается Говинде Дасу', author_en='attributed to Govinda Dasa',
         ru=['govinda-kadacha/ru/*.md'], en=['govinda-kadacha/en/*.md']),
    dict(id='prema-vivarta', group='bng', title='Шри Према-виварта', title_en='Sri Prema-vivarta',
         author='приписывается Джагадананде Пандиту', author_en='attributed to Jagadananda Pandita',
         ru=['prema-vivarta/ru/*.md'], en=['prema-vivarta/en/*.md']),
    dict(id='prema-vilasa', group='late', title='Према-виласа', title_en='Prema-vilasa',
         author='Нитьянанда Дас', author_en='Nityananda Dasa', ru=['prema-vilasa/ru/*.md'], en=['prema-vilasa/en/*.md']),
    dict(id='nityananda-vamsha', group='late', title='Нитьянанда-вамша-вистара', title_en='Nityananda-vamsha-vistara',
         author='', author_en='', ru=['nityananda-vamsha/ru/*.md'], en=['nityananda-vamsha/en/*.md']),
    dict(id='bhakti-ratnakara', group='late', title='Бхакти-ратнакара (таранги 1–4)', title_en='Bhakti-ratnakara (tarangas 1–4)',
         author='Нарахари Чакраварти', author_en='Narahari Chakravarti', ru=['bhakti-ratnakara/ru/*.md'], en=['bhakti-ratnakara/en/*.md']),
    dict(id='narottama-vilasa', group='late', title='Нароттама-виласа', title_en='Narottama-vilasa',
         author='Нарахари Чакраварти', author_en='Narahari Chakravarti', ru=['narottama-vilasa/ru/*.md'], en=['narottama-vilasa/en/*.md']),
    dict(id='karnananda', group='late', title='Карнананда', title_en='Karnananda',
         author='Ядунандана Дас', author_en='Yadunandana Dasa', ru=['karnananda/ru/*.md'], en=['karnananda/en/*.md']),
    dict(id='anuragavalli', group='late', title='Анурага-валли', title_en='Anuraga-valli',
         author='Манохара Дас', author_en='Manohara Dasa', ru=['anuragavalli/ru/*.md'], en=['anuragavalli/en/*.md']),
    dict(id='padas', group='pada', title='Пады современников Шри Чайтаньи', title_en='Padas of Sri Chaitanya’s contemporaries',
         author='разные поэты', author_en='various poets',
         ru_full='padas/Padas-ru-full.md', en_full='padas/Padas-en-full.md', level=1, chapters='padas/{lang}/*.md'),
    dict(id='stotras', group='pada', title='Гимны спутников о Гауре', title_en='Hymns of the associates to Gaura',
         author='Рагхунатха Дас Госвами, Рупа Госвами и др.', author_en='Raghunatha Dasa Gosvami, Rupa Gosvami and others',
         ru=['stotras/ru/*.md'], en=['stotras/en/*.md']),
    dict(id='vaishnava-vandana', group='pada', title='Вайшнава-ванданы', title_en='Vaishnava-vandanas',
         author='Джива Госвами (приписывается), Девакинандана', author_en='Jiva Gosvami (attributed), Devakinandana',
         ru=['vaishnava-vandana/ru/*.md'], en=['vaishnava-vandana/en/*.md']),
    dict(id='vallabha', group='other', title='Шри Чайтанья в текстах других традиций', title_en='Sri Chaitanya in the texts of other traditions',
         author='варты Валлабхи, «Бхактамалы»', author_en='Vallabha vartas, Bhaktamalas', ru=['vallabha/ru/*.md'], en=['vallabha/en/*.md']),
    dict(id='vaishnava-lilamrita', group='other', title='Вайшнава-лиламрита (гл. 4, 28–81)', title_en='Vaishnava-lilamrita (ch. 4, 28–81)',
         author='Мадхава Паттанаяк (ория)', author_en='Madhava Pattanayak (Oriya)',
         ru=['oriya-pilot/vaishnava-lilamrita/ru.md'], en=['oriya-pilot/vaishnava-lilamrita/en.md']),
]
GROUPS = [
    ('skt', 'Санскритские сочинения', 'Sanskrit works'),
    ('bng', 'Бенгальские жизнеописания', 'Bengali biographies'),
    ('late', 'Сочинения о спутниках и преемниках', 'Works on the associates and successors'),
    ('pada', 'Пады, гимны, ванданы', 'Padas, hymns, vandanas'),
    ('other', 'Иные традиции', 'Other traditions'),
]
CC_LILA = {'Adi': ('Ади-лила', 'Adi-lila'), 'Madhya': ('Мадхья-лила', 'Madhya-lila'), 'Antya': ('Антья-лила', 'Antya-lila')}
CB_KHANDA = {'Adi': ('Ади-кханда', 'Adi-khanda'), 'Madhya': ('Мадхья-кханда', 'Madhya-khanda'), 'Antya': ('Антья-кханда', 'Antya-khanda')}
SKIP_TITLES = re.compile(r'оглавлени|^contents$|^table of contents', re.I)


def files_of(patterns):
    out = []
    for p in patterns:
        out += sorted(glob.glob(os.path.join(ROOT, p)))
    return [f for f in out if not re.search(r'poetry\.md$', f)]


def cc_title(path, lang):
    m = re.search(r'(CC|CB)_(Adi|Madhya|Antya)(\d+)', path)
    lila, n = m.group(2), int(m.group(3))
    md = open(path, encoding='utf-8').read(800)
    sub = re.search(r'\*\*(.+?)\*\*', md)
    name = (CC_LILA if m.group(1) == 'CC' else CB_KHANDA)[lila][0 if lang == 'ru' else 1]
    return f"{name}, {'глава' if lang == 'ru' else 'chapter'} {n}" + (f". {sub.group(1)}" if sub else '')


def first_heading(md):
    m = re.search(r'^#\s+(.+)$', md, re.M)
    return m.group(1).strip().strip('*') if m else None


def chapters_of(book, lang):
    """→ [(title, md, source_file or None)]"""
    full = book.get(f'{lang}_full')
    if full and os.path.exists(os.path.join(ROOT, full)):
        md = open(os.path.join(ROOT, full), encoding='utf-8').read()
        out = []
        secs = mdhtml.split_sections(md, book['level'])
        for i, (t, body) in enumerate(secs):
            if t is None or SKIP_TITLES.search(t):
                continue
            text = re.sub(r'^#.*$|\[\^[^\]]+\]:.*$', '', body, flags=re.M).strip()
            if len(text) < 200:          # заголовок части без текста («Пракрама первая»)
                continue
            if i == 0 or t == first_heading(md):   # титул книги — пропускаем (главы RU и EN должны совпадать)
                continue
            out.append((t, body, None))
        return out
    pats = book.get(lang) or []
    out = []
    for f in files_of(pats):
        md = open(f, encoding='utf-8').read()
        t = cc_title(f, lang) if book.get('cc') else (first_heading(md) or os.path.basename(f)[:-3])
        out.append((t, md, os.path.relpath(f, ROOT)))
    # заголовок повторяет название книги в каждой главе (Карнапура) — берём первый подзаголовок
    ts = [t for t, _, _ in out]
    if len(ts) > 1 and len(set(ts)) == 1:
        out = [((re.search(r'^##\s+(.+)$', md, re.M) or re.search(r'^#\s+(.+)$', md, re.M)).group(1).strip(), md, src)
               for t, md, src in out]
    return out


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    index = {'groups': [{'id': g, 'title': r, 'title_en': e} for g, r, e in GROUPS], 'books': [], 'files': {}}
    total = 0
    import yaml
    info = yaml.safe_load(open(os.path.join(ROOT, 'site/content/books.yaml'), encoding='utf-8')) or {}
    for b in BOOKS:
        entry = {k: b.get(k, '') for k in ('id', 'group', 'title', 'title_en', 'author', 'author_en', 'note', 'note_en')}
        inf = info.get(b['id'])
        if inf:
            entry['info'] = {k: [mdhtml.inline(x) for x in inf.get(k, [])] for k in ('facts_ru', 'facts_en', 'about_ru', 'about_en')}
        else:
            print('нет справки:', b['id'])
        os.makedirs(os.path.join(OUT, b['id']))
        for lang in ('ru', 'en'):
            chs = chapters_of(b, lang)
            entry[lang] = []
            for i, (t, md, src) in enumerate(chs):
                title, h = mdhtml.render(md, lang=lang)
                # первый заголовок, повторяющий название главы (оно показывается отдельно), — убрать
                m = re.match(r'\s*(?:<p class="l-text"><i>[^<]*</i></p>\s*)?<h(\d)>(.*?)</h\1>\s*', h, re.S)
                if m and re.sub('<[^>]+>', '', m.group(2)).strip() == re.sub(r'\*', '', t).strip():
                    h = h[:m.start(1) - 2] + h[m.end():] if h.lstrip().startswith('<p') else h[m.end():]
                layers = sorted(set(re.findall(r'class="[^"]*\bl-(orig|translit|wbw|notes)', h)))
                name = f'{lang}-{i + 1:03d}.json'
                json.dump({'title': re.sub(r'\[\^[^\]]+\]', '', t).strip(), 'html': h}, open(os.path.join(OUT, b['id'], name), 'w', encoding='utf-8'),
                          ensure_ascii=False, separators=(',', ':'))
                total += os.path.getsize(os.path.join(OUT, b['id'], name))
                t = re.sub(r'\[\^[^\]]+\]', '', t).strip()          # знаки сносок в названии главы — не нужны
                entry[lang].append({'t': t, 'layers': layers})
                if src:
                    index['files'][src] = [b['id'], lang, i]
        # для «полных изданий» — связь поглавных файлов (на них ссылается база лил) с разделами полного текста
        if b.get('chapters'):
            for lang in ('ru', 'en'):
                titles = [c['t'] for c in entry[lang]]
                for f in sorted(glob.glob(os.path.join(ROOT, b['chapters'].format(lang=lang)))):
                    h = re.sub(r'\[\^[^\]]+\]', '', first_heading(open(f, encoding='utf-8').read()) or '').strip()
                    if h in titles:
                        index['files'][os.path.relpath(f, ROOT)] = [b['id'], lang, titles.index(h)]
        index['books'].append(entry)
        print(f"{b['id']}: RU {len(entry['ru'])} гл., EN {len(entry['en'])} гл.")
    json.dump(index, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f"книг {len(index['books'])}; объём глав {total // 1024 // 1024} МБ; связей файл→глава {len(index['files'])}")


if __name__ == '__main__':
    main()
