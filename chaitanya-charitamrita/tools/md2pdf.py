# Глава ed/vcd/CC_<Глава>.md -> PDF (через HTML и Chromium). Две редакции:
#   full — бенгальский, транслитерация, пословный, перевод (полное издание);
#   text — только перевод (лёгкое издание).
# Использование: python3 tools/md2pdf.py Adi07 [full|text] [a5|a4] [ru|en]   -> ed/pdf/CC_Adi07-<ред>.pdf
import os, re, sys, html, subprocess, unicodedata
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FONT_BN = os.path.abspath(os.path.join(ROOT, '..', 'fonts', 'NotoSerifBengali-Regular.ttf'))
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'

TXT = {'ru': {'apb': 'Амрита-праваха-бхашья', 'anu': 'Анубхашья', 'notes': 'Примечания'},
       'en': {'apb': 'Amṛta-pravāha-bhāṣya', 'anu': 'Anubhāṣya', 'notes': 'Notes'}}
TLM = '\u0301\u0303\u0304\u0307\u0310\u0323'
def is_tl(line): return any(c in '̣́̃̄̇̐' for c in line)
def has_bn(s): return any('ঀ' <= c <= '৿' for c in s)

def inline(t, notes):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\[\^([\w-]+)\]', lambda m: '<sup class="fn"><a href="#fn-%s" id="ref-%s">%d</a></sup>'
               % (m.group(1), m.group(1), notes.index(m.group(1)) + 1 if m.group(1) in notes else 0), t)
    return t

def load_comm(chap, kind, lang='ru'):
    """ed/ru/<Глава>-<kind>.md -> ({ключ раздела: текст}, сноски) ; ключ '0', '5' или '5–6'"""
    f = os.path.join(ROOT, 'ed', lang, '%s-%s.md' % (chap, kind))
    if not os.path.exists(f): return {}, ''
    t = open(f, encoding='utf-8').read()
    body, _, foot = t.partition('\n---\n')
    sec = {}
    for m in re.finditer(r'^## +([\d–-]+)\s*\n(.*?)(?=^## |\Z)', body, re.M | re.S):
        sec[m.group(1).replace('-', '–')] = m.group(2).strip()
    return sec, foot

SUB = re.compile(r'^> (?:Подзаголовок|Subheading):\s*(.+)$', re.M)

def comm_html(text, notes):
    out = []
    for para in re.split(r'\n\s*\n', text):
        para = para.strip()
        if not para or SUB.match(para): continue
        lines = [l.strip() for l in para.split('\n') if l.strip()]
        if all(l.startswith('- ') for l in lines):          # глоссы списком: каждое слово с новой строки
            out.append('<ul class="gl">%s</ul>' % ''.join('<li>%s</li>' % inline(l[2:], notes) for l in lines))
        else:
            out.append('<p>%s</p>' % inline(' '.join(lines), notes))
    return ''.join(out)

def subheading(text):
    m = SUB.search(text)
    return m.group(1).strip() if m else ''

def build(chap, ed='full', size='a5', lang='ru'):
    T = TXT[lang]
    md = open(os.path.join(ROOT, 'ed', 'vcd' if lang == 'ru' else 'en', 'CC_%s.md' % chap), encoding='utf-8').read()
    body, _, foot = md.partition('\n---\n')
    apb, fa = load_comm(chap, 'apb', lang) if ed == 'full' else ({}, '')
    anu, fn = load_comm(chap, 'anu', lang) if ed == 'full' else ({}, '')
    foot = foot + '\n' + fa + '\n' + fn
    notes = re.findall(r'^\[\^([\w-]+)\]:', foot, re.M)
    paras = [p for p in body.split('\n\n') if p.strip()]
    hdr = [l.strip() for l in paras[0].split('\n')]
    H = ['<header><div class="book">%s</div><div class="lila">%s</div><div class="ch">%s</div><h1>%s</h1><div class="by">%s</div></header>'
         % tuple(inline(x.strip('*'), notes) for x in hdr[:5])]
    if apb.get('0'):
        H.append('<section class="intro"><h2>%s</h2>%s</section>' % (T['apb'], '%s') % comm_html(apb['0'], notes))
    blk = []
    for p in paras[1:]:
        lines = [l.rstrip() for l in p.split('\n')]
        if has_bn(p):
            if ed == 'full': blk.append('<div class="bn">%s</div>' % '<br>'.join(html.escape(l.strip()) for l in lines))
        elif re.match(r'^\(\d+(–\d+)?\) ', p):
            m = re.match(r'^\((\d+(?:–\d+)?)\) (.*)', p, re.S)
            lab = m.group(1); a, b = (lab.split('–') + [lab])[:2]
            blk.append('<p class="tr"><span class="n">%s</span> %s</p>' % (lab, inline(m.group(2), notes)))
            keys = [k for k in list(apb) + list(anu) if k != '0' and (k == lab or k == a or k.split('–')[-1] == b)]
            sh = ''
            for k in dict.fromkeys(keys):
                if k in anu and subheading(anu[k]): sh = subheading(anu[k])
            for name, src in ((T['apb'], apb), (T['anu'], anu)):
                for k in dict.fromkeys(keys):
                    if k in src and comm_html(src[k], notes):
                        blk.append('<div class="comm"><span class="cn">%s.</span> %s</div>' % (name, comm_html(src[k], notes)))
            H.append('<section class="v">%s%s</section>' % (('<h3 class="sub">%s</h3>' % inline(sh, notes)) if sh else '', ''.join(blk))); blk = []
        elif ed == 'full':
            rows = []
            for k, l in enumerate(x.strip() for x in lines):
                if (is_tl(l) if lang == 'ru' else k % 2 == 0): rows.append('<div class="tl">%s</div>' % html.escape(l))
                else: rows.append('<div class="ww">%s</div>' % html.escape(l).replace('  ', '&ensp;&ensp;'))
            blk.append('<div class="tlww">%s</div>' % ''.join(rows))
    if notes:
        H.append('<section class="notes"><h2>%s</h2><ol>' % T['notes'])
        for k in notes:
            t = re.search(r'^\[\^%s\]:\s*(.*)$' % re.escape(k), foot, re.M).group(1)
            H.append('<li id="fn-%s">%s <a href="#ref-%s">↩</a></li>' % (k, inline(t, notes), k))
        H.append('</ol></section>')
    page = {'a5': 'A5', 'a4': 'A4'}[size]
    css = """
@font-face { font-family: 'NSBengali'; src: url('file://%s'); }
@page { size: %s; margin: 14mm 13mm 16mm 13mm;
        @bottom-center { content: counter(page); font: 9pt 'Liberation Serif'; } }
body { font-family: 'Liberation Serif', 'DejaVu Serif', serif; font-size: 11pt; line-height: 1.38; color: #111; }
header { text-align: center; margin: 8mm 0 9mm; }
header .book { font-size: 13pt; } header .lila, header .ch { font-size: 11pt; margin-top: 1mm; }
header h1 { font-size: 17pt; margin: 4mm 0 2mm; } header .by { font-style: italic; font-size: 10pt; }
section.v { margin: 0 0 5.5mm; }
section.v .bn, section.v .tlww { break-inside: avoid; }
.bn { font-family: 'NSBengali', serif; font-size: 12pt; line-height: 1.6; text-align: center; margin-bottom: 2mm; }
.tlww { margin: 0 0 2mm 6mm; }
.tl { font-style: italic; font-family: 'DejaVu Serif', 'Liberation Serif', serif; font-size: 9.6pt; }
.ww { font-size: 9pt; color: #555; margin-bottom: 0.8mm; }
p.tr { margin: 0; text-align: justify; hyphens: auto; }
p.tr .n { font-weight: bold; }
.comm { margin-top: 2.5mm; font-size: 10pt; text-align: justify; hyphens: auto; }
.comm p { margin: 0 0 1.5mm; } .comm ul.gl { list-style: none; margin: 1mm 0 1.5mm; padding-left: 4mm; } .comm ul.gl li { margin: 0 0 0.6mm; text-indent: -4mm; padding-left: 4mm; } .comm .cn { font-weight: bold; font-style: italic; }
.comm p:first-child { display: inline; } .comm p:first-child + p { margin-top: 1.5mm; }
h3.sub { break-after: avoid; page-break-after: avoid; font-size: 10.5pt; font-style: italic; font-weight: normal; text-align: center; margin: 0 0 2mm; }
section.intro { font-size: 10pt; text-align: justify; margin-bottom: 6mm; } section.intro h2 { font-size: 11pt; text-align: center; }
sup.fn a { text-decoration: none; color: #333; font-size: 8pt; }
section.notes { border-top: 0.5pt solid #999; margin-top: 8mm; font-size: 9.5pt; }
section.notes h2 { font-size: 11pt; } section.notes a { text-decoration: none; color: #555; }
""" % (FONT_BN, page)
    doc = '<!doctype html><html lang="%s">' % lang + '<head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s</body></html>' \
          % (html.escape(chap), css, '\n'.join(H))
    od = os.path.join(ROOT, 'ed', 'pdf'); os.makedirs(od, exist_ok=True)
    sfx = '' if lang == 'ru' else '-en'
    hp = os.path.join(od, 'CC_%s-%s%s.html' % (chap, ed, sfx)); pp = os.path.join(od, 'CC_%s-%s%s.pdf' % (chap, ed, sfx))
    open(hp, 'w', encoding='utf-8').write(doc)
    subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--print-to-pdf=' + pp, 'file://' + os.path.abspath(hp)], check=True, capture_output=True)
    os.remove(hp)
    print(pp)

if __name__ == '__main__':
    a = sys.argv[1:]
    build(a[0], a[1] if len(a) > 1 else 'full', a[2] if len(a) > 2 else 'a5', a[3] if len(a) > 3 else 'ru')
