#!/usr/bin/env python3
"""Сборка художественного издания: ЧЧ, Ади-лила, гл. 1 (перевод Вриндавана Чандры даса).

  python3 -I build.py            # собрать _book.html, отрендерить PDF (Chromium/Node-Playwright) и отчёт
  python3 -I build.py --html     # только _book.html

Источник текста: ../ed/vcd/CC_Adi01.md. План иллюстраций — словарь PLAN ниже (ключ — номер стиха, перед которым
срабатывает директива). Иллюстрации — art/ (готовит prepare_art.py из исходников Диска).
"""
import json, os, re, subprocess, sys
import pyphen

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parse_chapter import parse

SRC_MD = os.path.join(HERE, '..', 'ed', 'vcd', 'CC_Adi01.md')
OUT_PDF = os.path.join(HERE, 'Adi-01-illustrated.pdf')

# ---------------------------------------------------------------------------------------------
# ПЛАН ИЛЛЮСТРАЦИЙ.  Ключ — номер стиха (первый, если сдвоенный); значение — список директив,
# выполняемых перед этим стихом.
#   spread  — панорама по нижним частям двух страниц разворота (начинается с ближайшей левой страницы);
#   float   — вырезная фигура на прозрачном фоне, текст обтекает силуэт;
#   page    — страница-«сцена» (goswamis, finale);
#   break   — принудительный конец страницы.
# ---------------------------------------------------------------------------------------------
PLAN = {
    '4':   [('spread', dict(pan='pan_dhameshvar'))],
    '15':  [('spread', dict(pan='pan_kk'))],
    '30':  [('float', dict(fig='vb_1', side='left', w=40, hang=8, mt=1))],
    '36':  [('page', dict(profile='goswamis', maxV=1))],
    '42':  [('float', dict(fig='arch_deity', arch=True, side='right', w=44, mt=1, mb=3))],
    '64':  [('float', dict(fig='murari_svarupa', side='right', w=62, hang=10))],
    '84':  [('float', dict(fig='va_1', side='left', w=36))],
    '95':  [('spread', dict(pan='pan_kazi', band=74))],
    '105': [('float', dict(fig='krishnadas_write', side='right', w=58, hang=8))],
    '110': [('page', dict(profile='finale', maxV=1))],
}

HY = pyphen.Pyphen(lang='ru_RU', left=3, right=3)
CYR = re.compile(r'[А-Яа-яЁё]{7,}')


def hyph(s):
    return CYR.sub(lambda m: HY.inserted(m.group(0), hyphen='­'), s)


def main():
    meta, verses = parse(SRC_MD)
    for v in verses:
        v['tr'] = hyph(v['tr'].replace('&', '&amp;').replace('<', '&lt;'))
        v['tr'] = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', v['tr'])
        v['tr'] = re.sub(r'\*(.+?)\*', r'<i>\1</i>', v['tr'])
    profiles = json.load(open(os.path.join(HERE, 'art', 'profiles.json'), encoding='utf-8'))
    plan = []
    for v in verses:
        for kind, cfg in PLAN.get(str(v['n1']), []):
            if kind == 'spread': plan.append({'t': 'spread', 'cfg': cfg, 'force': cfg.get('force', False)})
            elif kind == 'float': plan.append({'t': 'float', 'cfg': cfg})
            elif kind == 'page': plan.append({'t': 'page', 'profile': cfg['profile'], 'maxV': cfg.get('maxV')})
            elif kind == 'break': plan.append({'t': 'break'})
        plan.append({'t': 'verse', 'v': v})
    data = {'meta': meta, 'plan': plan, 'profiles': profiles}
    html = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{meta['book']}. {meta['lila']}, {meta['chapter']}</title>
<link rel="stylesheet" href="book.css"></head><body><div id="book"></div>
<script>const DATA = {json.dumps(data, ensure_ascii=False)};</script>
<script src="paginate.js"></script></body></html>'''
    open(os.path.join(HERE, '_book.html'), 'w', encoding='utf-8').write(html)
    print('html ok:', len(verses), 'стихов')
    if '--html' in sys.argv: return
    subprocess.run(['node', os.path.join(HERE, 'render.js'), os.path.join(HERE, '_book.html'), OUT_PDF], check=True)


if __name__ == '__main__':
    main()
