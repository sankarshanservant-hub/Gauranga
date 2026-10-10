# Материалы для перевода комментариев: для каждой страницы скана — изображения колонок (по 2 части на колонку,
# ~120 dpi, читаемо) и текст OCR по колонкам (tesseract psm 3, порядок строк сверху вниз).
# Использование: python3 tools/comm_pages.py <Глава> <папка скана: pN.pgm, tN.tsv> P1 P2 <выход>
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocr_verses import lines_of
from PIL import Image
chap, d, p1, p2, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
os.makedirs(out, exist_ok=True)
SC = 0.55
for p in range(p1, p2 + 1):
    im = Image.open(os.path.join(d, 'p%d.pgm' % p)); W, H = im.size
    Ls = sorted(lines_of(os.path.join(d, 't%d.tsv' % p)), key=lambda l: l['top'])
    txt = []
    for ci, (x0, x1) in enumerate(((0, W // 2 + 15), (W // 2 - 15, W))):
        col = im.crop((x0, 0, x1, H))
        col = col.resize((int(col.size[0] * SC), int(col.size[1] * SC)))
        h = col.size[1]
        for k, (y0, y1) in enumerate(((0, h // 2 + 30), (h // 2 - 30, h))):
            col.crop((0, y0, col.size[0], y1)).save(os.path.join(out, 'p%02d-%s%d.png' % (p, 'LR'[ci], k + 1)))
        side = [l for l in Ls if (l['left'] + l['right']) / 2 < W / 2] if ci == 0 else [l for l in Ls if (l['left'] + l['right']) / 2 >= W / 2]
        txt.append('## стр. %d, %s колонка (OCR, черновой)\n\n' % (p, 'левая' if ci == 0 else 'правая') + '\n'.join(l['text'] for l in side))
    open(os.path.join(out, 'p%02d.txt' % p), 'w', encoding='utf-8').write('\n\n'.join(txt) + '\n')
print('готово:', out)
