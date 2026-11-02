#!/usr/bin/env python3
"""Сборка художественного издания: ЧЧ, Ади-лила, гл. 1 — две колонки A4, стихи ВЧД + комментарии.

  python3 -I build.py            # _book.html → PDF (Chromium/Node-Playwright) + отчёт по страницам
  python3 -I build.py --html     # только _book.html

Источники:
  ../ed/vcd/CC_Adi01.md                 — стихи (перевод Вриндавана Чандры даса);
  ../ed/ru/Adi01-apb.md, Adi01-anu.md   — «Амрита-праваха-бхашья» и «Анубхашья» (разделы «## N»; «## 0» — резюме
                                          главы; «### …» в anu — заголовок раздела Бхактисиддханты перед стихом);
  ../vcd/txt/CC_Adi01.txt               — подзаголовки ВЧД (ст. 1–2) и комментарий Шрилы Б. Р. Шридхара Махараджа.
Иллюстрации — art/ (prepare_art.py). План — ANCHORS / FLOATS / FIGS ниже.
"""
import json, os, re, subprocess, sys
import pyphen

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from parse_chapter import parse

SRC_MD = os.path.join(CC, 'ed', 'vcd', 'CC_Adi01.md')
OUT_PDF = os.path.join(HERE, 'Adi-01-illustrated.pdf')

# Иллюстрации, привязанные к стиху: движок добивается, чтобы стих и иллюстрация были на одном развороте/странице.
ANCHORS = [
    dict(id='dhameshvar', verse='4', type='spread', pan='pan_dhameshvar'),   # «сын Шачи» — Гаура в Навадвипе
    dict(id='kk', verse='15', type='spread', pan='pan_kk'),                   # Радха-Мадана-мохан, Кришнадас во Вриндаване
    dict(id='goswamis', verse='36', type='goswamis'),                          # шесть Госвами
    dict(id='banner', verse='82', type='banner'),                              # почтение всем вайшнавам
    dict(id='kazi', verse='95', type='spread', pan='pan_kazi', band=64),      # тьма рассеяна милостью Гауры-Нитая
]
# Вырезные фигуры в колонке, текст обтекает силуэт (перед стихом N, внутри его блока).
FLOATS = {
    '20': dict(fig='krishnadas_pray', side='left', w=30, mt=8),
    '30': dict(fig='vb_1', side='left', w=31, mt=8),
    '42': dict(fig='arch_deity', arch=True, side='right', w=33, mt=8, mb=2),
    '105': dict(fig='krishnadas_write', side='right', w=36, mt=8),
}
# Рисунки во всю ширину колонки — после комментария к стиху N.
FIGS = {
    '64': dict(fig='murari_svarupa', cap='Мурари Гупта и Сварупа Дамодара'),
}

HY = pyphen.Pyphen(lang='ru_RU', left=3, right=3)
CYR = re.compile(r'[А-Яа-яЁё]{7,}')


def hyph(s):
    return CYR.sub(lambda m: HY.inserted(m.group(0), hyphen='­'), s)


def md_inline(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\{\?(.*?)\}', r'<span title="неразборчиво">[\1?]</span>', s)
    return hyph(s)


def read_comm(path):
    """Разделы «## N» → список элементов {t: p|gloss|poem, h: html}; «### …» → подзаголовок (строки через <br>)."""
    if not os.path.exists(path):
        return {}, {}
    secs, subs, key = {}, {}, None
    text = open(path, encoding='utf-8').read()
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    for block in re.split(r'\n\s*\n', text):
        if not block.strip():
            continue
        lines = [l for l in block.split('\n') if l.strip()]
        rest = []
        for ln in lines:
            st = ln.strip()
            m = re.match(r'^##\s+(\S+)\s*$', st)
            if m:
                key = m.group(1).replace('-', '–'); secs.setdefault(key, []); continue
            m = re.match(r'^###\s+(.+)$', st)
            if m and key is not None:
                subs[key] = (subs[key] + '<br>' if key in subs else '') + md_inline(m.group(1).strip()); continue
            if st.startswith('# ') or key is None:
                continue
            rest.append(ln)
        if key is None or not rest:
            continue
        if re.fullmatch(r'\(“[^”]+”\)', ' '.join(x.strip() for x in rest)):
            continue                                              # служебная строка-заголовок издания
        hard = len(rest) > 1 and any(l.endswith('  ') for l in rest[:-1])
        if hard and re.sub(r'^\d+(?:[–-]\d+)?\.\s+', '', rest[0].strip()).startswith('**'):
            for k, l in enumerate(rest):
                l = l.strip()
                if k == 0 and not secs[key]:
                    l = re.sub(r'^\d+(?:[–-]\d+)?\.\s+', '', l)
                secs[key].append({'t': 'gloss', 'h': md_inline(l)})
        elif hard:
            out = []
            for l in rest:
                h = md_inline(l.strip())
                out.append(f'<span class="pl ind">{h}</span>' if re.match(r'^\s{2,}', l) else f'<span class="pl">{h}</span>')
            for i in range(0, len(out), 4):                        # строфы по 4 строки — неразрывные блоки
                secs[key].append({'t': 'poem', 'h': ''.join(out[i:i + 4])})
        else:
            p = ' '.join(x.strip() for x in rest)
            if not secs[key]:
                p = re.sub(r'^\d+(?:[–-]\d+)?\.\s+', '', p)              # «15. …» — номер заменяет метка
            secs[key].append({'t': 'p', 'h': md_inline(p)})
    return secs, subs


def target_verse(key, verses):
    """Раздел «N» или «N–M» → индекс стиха, после которого ставить комментарий (по последнему номеру)."""
    last = int(re.split(r'[–-]', key)[-1])
    for i, v in enumerate(verses):
        lo = v['n1']; hi = int(v['n'].split('–')[-1])
        if lo <= last <= hi:
            return i
    return None


def sridhar_comments():
    """Комментарии Шрилы Б. Р. Шридхара Махараджа из исходника ВЧД: {номер стиха: [абзацы]}."""
    t = open(os.path.join(CC, 'vcd', 'txt', 'CC_Adi01.txt'), encoding='utf-8').read().split('\n')
    out, cur_n, buf, on = {}, None, [], False
    BEN = re.compile(r'[ঀ-৿]')
    for ln in t:
        m = re.match(r'^\((\d+)', ln.strip())
        if m:
            cur_n = m.group(1); on = False; continue
        s = ln.replace('　', ' ').strip()
        if BEN.search(ln):
            if on and buf: out[cur_n] = buf
            on, buf = False, []; continue
        if ln.startswith('　') and s:
            if s.startswith('Шрила Б.Р. Шридхар Махарадж:'):
                on = True; buf = [s.split(':', 1)[1].strip()]; continue
            if on:
                buf.append(s); continue
        elif on and s:
            buf[-1] += ' ' + s
    if on and buf: out[cur_n] = buf
    fix = {'обыкночение': 'обыкновение', 'илюзорен': 'иллюзорен'}
    return {k: [re.sub('|'.join(fix), lambda m: fix[m.group(0)], p) for p in v] for k, v in out.items()}


VCD_SUBS = {  # подзаголовки «Анубхашьи» в переводе ВЧД (есть только к ст. 1–2)
    '1': 'Начало всеблагоприятного вступления, предложение поклонов Высшей Истине — Шри Кришне Чайтанье',
    '2': 'Предложение поклонов Аватарам эпохи; Нитай и Гаура появились одновременно, подобно солнцу и луне, и даровали всем душам Свою милость',
}


def main():
    meta, verses = parse(SRC_MD)
    for v in verses:
        v['tr'] = md_inline(v['tr'])
        v['comm'] = []
    apb, _ = read_comm(os.path.join(CC, 'ed', 'ru', 'Adi01-apb.md'))
    anu, anu_subs = read_comm(os.path.join(CC, 'ed', 'ru', 'Adi01-anu.md'))
    a0, n0 = apb.pop('0', []), anu.pop('0', [])
    intro = {'summary': [x for x in a0 if x['t'] == 'p'], 'apbPoem': [x for x in a0 if x['t'] == 'poem'],
             'anuPoem': [x for x in n0 if x['t'] == 'poem']}
    for label, secs in (('Амрита-праваха-бхашья', apb), ('Анубхашья', anu)):
        for key, items in secs.items():
            if not items:
                continue
            i = target_verse(key, verses)
            if i is None:
                print('!! раздел без стиха:', label, key); continue
            verses[i]['comm'].append({'label': label, 'items': items})
    for key, sub in anu_subs.items():
        i = target_verse(key.split('–')[0], verses)
        if i is not None:
            verses[i]['sub'] = sub
    for n, sub in VCD_SUBS.items():
        for v in verses:
            if v['n'] == n and not v.get('sub'):
                v['sub'] = hyph(sub)
    for n, paras in sridhar_comments().items():
        for v in verses:
            if v['n'] == n:
                v['comm'].append({'label': 'Шрила Б. Р. Шридхар Махарадж', 'items': [{'t': 'p', 'h': hyph(p)} for p in paras]})
    for v in verses:
        if v['n'] in FLOATS: v['floats'] = [FLOATS[v['n']]]
        if v['n'] in FIGS: v['figs'] = [FIGS[v['n']]]
    ncomm = sum(1 for v in verses if any(c['label'] != 'Шрила Б. Р. Шридхар Махарадж' for c in v['comm']))
    print(f'стихов: {len(verses)}; с комментарием АПБ/Анубхашьи: {ncomm}; резюме главы: {"есть" if intro["summary"] else "нет"}')
    profiles = json.load(open(os.path.join(HERE, 'art', 'profiles.json'), encoding='utf-8'))
    data = {'meta': meta, 'verses': verses, 'intro': intro, 'anchors': ANCHORS, 'profiles': profiles, 'final': True}
    html = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{meta['book']}. {meta['lila']}, {meta['chapter']}</title>
<link rel="stylesheet" href="book.css"></head><body><div id="book"></div>
<script>const DATA = {json.dumps(data, ensure_ascii=False)};</script>
<script src="paginate.js"></script></body></html>'''
    open(os.path.join(HERE, '_book.html'), 'w', encoding='utf-8').write(html)
    if '--html' in sys.argv:
        return
    subprocess.run(['node', os.path.join(HERE, 'render.js'), os.path.join(HERE, '_book.html'), OUT_PDF], check=True)


if __name__ == '__main__':
    main()
