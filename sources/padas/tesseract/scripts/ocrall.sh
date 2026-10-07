#!/bin/bash
S=/tmp/claude-0/-home-user-Gauranga/7b2c56d5-8710-5f94-af24-6c5c741d0e9d/scratchpad
for spec in "1 pk_337379 422" "2 pk_336618 476" "3 pk_336920 348" "4 pk_354459 280"; do
 set -- $spec
 mkdir -p $S/out/tess/v$1
 seq 1 $3 | xargs -P4 -I{} $S/scripts/ocrpage.sh $S/dl/pk/$2.pdf $S/out/tess/v$1 {}
done
echo done
