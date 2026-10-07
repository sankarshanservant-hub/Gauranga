#!/bin/bash
# half.sh vol pdf page
S=/tmp/claude-0/-home-user-Gauranga/7b2c56d5-8710-5f94-af24-6c5c741d0e9d/scratchpad
v=$1; pdf=$2; p=$3
for side in L R; do
  o=$S/out/half/${v}_${p}_$side
  [ -s $o.txt ] && continue
  pdftoppm -f $p -l $p -r 300 -gray -singlefile $S/dl/pk/$pdf.pdf $o
  python3 -I -c "
import sys
from PIL import Image
im=Image.open(sys.argv[1]); w,h=im.size
im=(im.crop((0,0,w//2+15,h)) if sys.argv[2]=='L' else im.crop((w//2-15,0,w,h)))
im.save(sys.argv[1])" $o.pgm $side
  OMP_THREAD_LIMIT=1 timeout 200 tesseract $o.pgm $o -l ben --psm 6 >/dev/null 2>&1; rm -f $o.pgm
done
