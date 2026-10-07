#!/bin/bash
# usage: ocrpage.sh pdf outdir page
pdf=$1; od=$2; p=$3
f=$(printf "%s/p%04d" "$od" "$p")
[ -s "$f.txt" ] && exit 0
pdftoppm -f $p -l $p -r 300 -gray -singlefile "$pdf" "$f" && OMP_THREAD_LIMIT=1 tesseract "$f.pgm" "$f" -l ben --psm 3 >/dev/null 2>&1; rm -f "$f.pgm"
