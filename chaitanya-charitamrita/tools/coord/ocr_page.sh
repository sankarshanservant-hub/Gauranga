#!/bin/sh
# Страница p скана: 300 dpi gray (для OCR и вырезок) -> tsv (psm 3, для bn_flags/comm_pages) + txt (psm 4, для поиска).
# Запуск: seq 186 216 | xargs -P 4 -I{} sh tools/coord/ocr_page.sh {}
# Если tsv/txt уже есть (предрасчёт в комплекте), tesseract не нужен; картинка страницы — pdftoppm или PyMuPDF.
p=$1
CCDIR=$(cd "$(dirname "$0")/../.." && pwd)
PDF="$CCDIR/src/CC_SS.pdf"
[ -z "$CC_WORK" ] && [ -d "$CCDIR/../../cc-work" ] && CC_WORK="$(cd "$CCDIR/../../cc-work" && pwd)"
S="${CC_WORK:-/tmp/cc-work}/scan1"; mkdir -p "$S"; cd "$S" || exit 1
[ -s "$PDF" ] || { echo "нет $PDF" >&2; exit 1; }
if [ ! -s p$p.pgm ]; then
  rm -f p$p.pgm
  if command -v pdftoppm >/dev/null 2>&1; then pdftoppm -f $p -l $p -r 300 -gray -singlefile "$PDF" p$p
  else python3 "$CCDIR/tools/coord/render_page.py" "$PDF" $p p$p.pgm; fi
fi
[ -s p$p.pgm ] || { echo "страница $p не отрисована" >&2; exit 1; }
[ -s t$p.tsv ] || { rm -f t$p.tsv; OMP_THREAD_LIMIT=1 tesseract p$p.pgm t$p -l ben --psm 3 tsv >/dev/null 2>&1; }
[ -s o$p.txt ] || { rm -f o$p.txt; OMP_THREAD_LIMIT=1 tesseract p$p.pgm o$p -l ben --psm 4 >/dev/null 2>&1; }
