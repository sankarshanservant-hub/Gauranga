"""Dump all text lines of the EN 2015 PDF with font info to JSONL (page, x0, y0, size, fonts, text-with-italics)."""
import sys, json, collections
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine, LAParams
src, out = sys.argv[1], sys.argv[2]
def styl(fn):
    fn = fn.split('+')[-1]
    return 'i' if 'Italic' in fn else ('b' if 'Bold' in fn or 'Semibold' in fn else 'r')
with open(out, 'w') as o:
    for pno, pg in enumerate(extract_pages(src, laparams=LAParams(line_margin=0.3))):
        lines = []
        for el in pg:
            if not isinstance(el, LTTextContainer): continue
            for line in el:
                if not isinstance(line, LTTextLine): continue
                chars = [c for c in line if isinstance(c, LTChar)]
                if not chars: continue
                fonts = collections.Counter((c.fontname.split('+')[-1], round(c.size, 1)) for c in chars)
                (fn, sz), _ = fonts.most_common(1)[0]
                # text with italic markup
                txt, cur = '', 'r'
                for c in line:
                    t = c.get_text()
                    s = styl(c.fontname) if isinstance(c, LTChar) else cur
                    if t.strip() == '': s = cur
                    if s != cur:
                        if cur == 'i': txt += '*'
                        if s == 'i': txt += '*'
                        cur = s
                    txt += t
                if cur == 'i': txt = txt.rstrip('\n') + '*'
                lines.append(dict(p=pno + 1, x=round(line.x0), y=round(line.y0), f=fn, s=sz, t=txt.rstrip('\n')))
        lines.sort(key=lambda d: -d['y'])
        for d in lines: o.write(json.dumps(d, ensure_ascii=False) + '\n')
