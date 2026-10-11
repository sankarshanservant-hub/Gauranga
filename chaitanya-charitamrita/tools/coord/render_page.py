#!/usr/bin/env python3
# Запасной рендер страницы PDF в 300 dpi gray PGM без poppler: pip install pymupdf
# Запуск: python3 render_page.py CC_SS.pdf 290 p290.pgm
import sys, fitz
pdf, p, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
pix = fitz.open(pdf)[p - 1].get_pixmap(dpi=300, colorspace=fitz.csGRAY)
pix.save(out if not out.endswith('.pgm') else out[:-4] + '.png')
if out.endswith('.pgm'):
    from PIL import Image
    Image.open(out[:-4] + '.png').save(out); __import__('os').remove(out[:-4] + '.png')
