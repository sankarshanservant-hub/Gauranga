#!/bin/bash
# ocrcol.sh pdf page side(L|R|F) outprefix  -> prints text of column
pdf=$1; p=$2; side=$3; o=$4
pdftoppm -f $p -l $p -r 300 -gray -singlefile "$pdf" $o
python3 -I - "$o.pgm" "$side" <<'PY'
import sys
from PIL import Image
im=Image.open(sys.argv[1]); w,h=im.size; s=sys.argv[2]
if s=='L': im=im.crop((0,0,w//2+20,h))
elif s=='R': im=im.crop((w//2-20,0,w,h))
im.save(sys.argv[1])
PY
OMP_THREAD_LIMIT=1 timeout 120 tesseract $o.pgm - -l ben --psm 6 2>/dev/null
