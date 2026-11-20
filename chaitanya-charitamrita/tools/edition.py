#!/usr/bin/env python3
# Пробное издание всей книги одним PDF: титул, место под предисловие, содержание, шмуцтитулы лил, 62 главы.
#   full — полное издание (бенгальский, транслитерация, пословный, перевод, оба комментария);
#   text — лёгкое издание (только перевод стихов).
# Главы — как в tools/md2pdf.py (выверенная редакция ed/vcd-rev, ed/en-rev). В PDF — закладки (оглавление) по заголовкам.
# Использование: python3 tools/edition.py full|text [a5|a4] [ru|en] [out.pdf]
import html, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md2pdf
from md2pdf import build, CSS, FONT_BN, CHROME, ROOT

ed = sys.argv[1] if len(sys.argv) > 1 else 'text'
size = sys.argv[2] if len(sys.argv) > 2 else 'a5'
lang = sys.argv[3] if len(sys.argv) > 3 else 'ru'
LILAS = [('Adi', 17), ('Madhya', 25), ('Antya', 20)]
T = {'ru': {'book': 'Шри Чайтанья-чаритамрита', 'author': 'Шрила Кришнадас Кавирадж Госвами',
            'full': 'Полное издание: бенгальский текст, транслитерация, пословный и литературный перевод, «Амрита-праваха-бхашья» Шрилы Бхактивиноды Тхакура и «Анубхашья» Шрилы Бхактисиддханты Сарасвати Тхакура',
            'text': 'Лёгкое издание: перевод стихов',
            'trans': 'Перевод стихов — Вриндаван Чандра дас (Антья-лила, главы 16–19, — перевод в его стиле, 2026); выверка по изданию Гаудия Матха и «Анубхашье»; перевод комментариев — впервые для этого издания',
            'trial': '2026', 'pref': 'Предисловие', 'pref_t': 'Предисловие будет добавлено.',
            'toc': 'Содержание', 'ch': 'Глава', 'lila': {'Adi': 'Ади-лила', 'Madhya': 'Мадхья-лила', 'Antya': 'Антья-лила'}},
     'en': {'book': 'Śrī Caitanya-caritāmṛta', 'author': 'Śrīla Kṛṣṇadāsa Kavirāja Gosvāmī',
            'full': 'Complete edition: Bengali text, transliteration, word-for-word and verse translation, Śrīla Bhaktivinoda Ṭhākura’s «Amṛta-pravāha-bhāṣya» and Śrīla Bhaktisiddhānta Sarasvatī Ṭhākura’s «Anubhāṣya»',
            'text': 'Concise edition: translation of the verses',
            'trans': 'English translation from the Bengali, following the Gauḍīya Maṭha edition and the «Anubhāṣya»; the commentaries are translated for the first time for this edition',
            'trial': '2026', 'pref': 'Preface', 'pref_t': 'The preface will be added.',
            'toc': 'Contents', 'ch': 'Chapter', 'lila': {'Adi': 'Ādi-līlā', 'Madhya': 'Madhya-līlā', 'Antya': 'Antya-līlā'}}}[lang]

def title(chap):
    f = os.path.join(ROOT, 'ed', 'vcd-rev' if lang == 'ru' else 'en-rev', 'CC_%s.md' % chap)
    m = re.search(r'^\*\*(.+?)\*\*', open(f, encoding='utf-8').read(), re.M)
    return m.group(1) if m else ''

EXTRA = """
.tp { break-after: page; text-align: center; padding-top: 30mm; }
.tp .t1 { font-size: 24pt; font-weight: bold; margin-bottom: 6mm; } .tp .t2 { font-size: 13pt; margin-bottom: 18mm; }
.tp .t3 { font-size: 10.5pt; margin: 0 6mm 6mm; } .tp .t4 { font-size: 9.5pt; font-style: italic; margin: 0 6mm; }
.tp .t5 { font-size: 9pt; color: #777; margin-top: 30mm; }
.pref { break-after: page; } .pref h1, .toc h1 { font-size: 16pt; text-align: center; margin: 6mm 0 8mm; }
.pref p.ph { font-style: italic; text-align: center; color: #555; }
.pref p { text-align: justify; hyphens: auto; text-indent: 6mm; margin: 0 0 1.5mm; } .pref h2 { font-size: 12pt; text-align: center; margin: 6mm 0 3mm; }
.toc { break-after: page; font-size: 10pt; } .toc h2 { font-size: 11.5pt; margin: 5mm 0 2mm; }
.toc ol { margin: 0; padding-left: 7mm; } .toc li { margin: 0 0 0.8mm; } .toc a { color: #111; text-decoration: none; }
.lp { break-before: page; break-after: page; text-align: center; padding-top: 55mm; }
.lp h1 { font-size: 22pt; } .lp div { font-size: 12pt; }
header.ch:first-of-type { break-before: page; }
"""

H = ['<section class="tp"><div class="t1">%s</div><div class="t2">%s</div><div class="t3">%s</div><div class="t4">%s</div><div class="t5">%s</div></section>'
     % tuple(html.escape(x) for x in (T['book'], T['author'], T.get(ed, ''), T['trans'] if ed == 'full' else re.split(r'; (?:перевод комментариев|the commentaries)', T['trans'])[0], T['trial']))]
def preface():
    f = os.path.join(ROOT, 'ed', 'preface-%s.md' % lang)
    if not os.path.exists(f): return '<section class="pref"><h1>%s</h1><p class="ph">%s</p></section>' % (T['pref'], T['pref_t'])
    out = []
    for para in re.split(r'\n\s*\n', open(f, encoding='utf-8').read().strip()):
        t = html.escape(para.strip())
        t = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t); t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
        if t.startswith('# '): out.append('<h1>%s</h1>' % t[2:])
        elif t.startswith('## '): out.append('<h2>%s</h2>' % t[3:])
        else: out.append('<p>%s</p>' % t)
    return '<section class="pref">%s</section>' % ''.join(out)
H.append(preface())
if ed == 'preface': H = [preface()]
toc = ['<section class="toc"><h1>%s</h1>' % T['toc']]
for L, n in LILAS:
    toc.append('<h2>%s</h2><ol>' % T['lila'][L])
    for i in range(1, n + 1):
        c = '%s%02d' % (L, i)
        toc.append('<li><a href="#ch-%s">%s</a></li>' % (c, html.escape(title(c))))
    toc.append('</ol>')
if ed != 'preface': H.append(''.join(toc) + '</section>')
for L, n in ([] if ed == 'preface' else LILAS):
    H.append('<section class="lp"><h1>%s</h1><div>%s</div></section>' % (T['lila'][L], html.escape(T['book'])))
    for i in range(1, n + 1):
        c = '%s%02d' % (L, i)
        h = '\n'.join(build(c, ed, size, lang, ret=True))
        for x in ('href="#fn-', 'id="fn-', 'href="#ref-', 'id="ref-'):
            h = h.replace(x, x + c + '-')
        h = h.replace('<header class="ch">', '<header class="ch" id="ch-%s">' % c, 1)
        H.append(h)
        print(c, end=' ', flush=True)
print()
page = {'a5': 'A5', 'a4': 'A4'}[size]
doc = '<!doctype html><html lang="%s"><head><meta charset="utf-8"><title>%s</title><style>%s%s</style></head><body>%s</body></html>' \
      % (lang, html.escape(T['book']), CSS % (FONT_BN, page), EXTRA, '\n'.join(H))
od = os.path.join(ROOT, 'ed', 'pdf'); os.makedirs(od, exist_ok=True)
pp = sys.argv[4] if len(sys.argv) > 4 else os.path.join(od, 'CC_book-%s-%s%s.pdf' % (ed, size, '' if lang == 'ru' else '-en'))
hp = os.path.splitext(pp)[0] + '.html'
open(hp, 'w', encoding='utf-8').write(doc)
subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--generate-pdf-document-outline',
                '--print-to-pdf=' + pp, 'file://' + os.path.abspath(hp)], check=True, capture_output=True, timeout=3600)
os.remove(hp)
# закладки: Chrome берёт заголовки по строкам вёрстки и склеивает перенесённые слова («Гуру идругим») —
# верхний уровень (предисловие, содержание, лилы, главы) переписываем точными названиями
if ed != 'preface':
    import pypdf
    from pypdf.generic import TextStringObject, NameObject
    want = [T['pref'], T['toc']]
    for L, n in LILAS: want += [T['lila'][L]] + [title('%s%02d' % (L, i)) for i in range(1, n + 1)]
    w = pypdf.PdfWriter(clone_from=pp)
    it = w._root_object['/Outlines'].get_object().get('/First'); k = 0
    while it is not None and k < len(want):
        o = it.get_object(); o[NameObject('/Title')] = TextStringObject(want[k]); k += 1
        it = o.get('/Next')
    if k != len(want): print('!! закладок верхнего уровня: %d, ожидалось %d' % (k, len(want)))
    w.write(pp)
print(pp)
