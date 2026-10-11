#!/bin/sh
# Страница p скана: 300 dpi gray (для OCR и вырезок) -> tsv (psm 3, для bn_flags/comm_pages) + txt (psm 4, для поиска).
# Запуск: seq 186 216 | xargs -P 4 -I{} sh chaitanya-charitamrita/tools/coord/ocr_page.sh {}
p=$1; S="${CC_WORK:-/tmp/cc-work}/scan1"; mkdir -p "$S"; cd "$S"
PDF="$(cd "$(dirname "$0")/../.." && pwd)/src/CC_SS.pdf"
[ -s p$p.pgm ] || pdftoppm -f $p -l $p -r 300 -gray -singlefile "$PDF" p$p
[ -s t$p.tsv ] || OMP_THREAD_LIMIT=1 tesseract p$p.pgm t$p -l ben --psm 3 tsv >/dev/null 2>&1
[ -s o$p.txt ] || OMP_THREAD_LIMIT=1 tesseract p$p.pgm o$p -l ben --psm 4 >/dev/null 2>&1
