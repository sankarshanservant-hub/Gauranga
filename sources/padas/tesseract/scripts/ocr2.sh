#!/bin/bash
S=/tmp/claude-0/-home-user-Gauranga/7b2c56d5-8710-5f94-af24-6c5c741d0e9d/scratchpad
for spec in "ps ps 512" "kgc kgc 284" "gpt1 gpt1 840"; do
 set -- $spec
 mkdir -p $S/out/tess/$1
 seq 1 $3 | xargs -P4 -I{} $S/scripts/ocrpage.sh $S/dl/anth/$2.pdf $S/out/tess/$1 {}
done
echo done
