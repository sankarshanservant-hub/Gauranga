#!/bin/bash
# Всё сетевое для главы — заранее (vedabase → ed/work/vb-<Гл>.json; CCBSST djvu → $W/bsst/<Гл>.txt).
# Запуск: bash tools/coord/fetch_net.sh Madhya01 [Madhya02 …]
. "$(dirname "$0")/env.sh"
cd "$CC"
for C in "$@"; do
  L=$(echo $C | sed 's/[0-9]*$//'); N=$(echo $C | sed 's/^[A-Za-z]*//'); n=$((10#$N)); l=$(echo $L | tr A-Z a-z)
  VB="$W/vb/$C"; mkdir -p "$VB" "$W/bsst"
  if [ ! -s ed/work/vb-$C.json ]; then
    curl -sS --retry 3 -o "$W/vb/$C.idx.html" "https://vedabase.io/en/library/cc/$l/$n/"
    grep -o "href=\"/en/library/cc/$l/$n/[0-9-]*/\"" "$W/vb/$C.idx.html" | sed "s/.*\/$n\/\([0-9-]*\)\/\"/\1/" | sort -u > "$W/vb/$C.list"
    (cd "$VB"; cat "$W/vb/$C.list" | xargs -P 6 -I{} sh -c "[ -s {}.html ] || curl -sS --retry 3 -o {}.html https://vedabase.io/en/library/cc/$l/$n/{}/")
    python3 tools/extract.py "$VB" ed/work/vb-$C.json | cut -c1-100 | sed "s/^/$C vedabase: /"
  fi
  case $L in Adi) IT=CCBSSTAdi01;; Madhya) IT=CCBSSTMadhya;; Antya) IT=CCBSSTAntya;; esac
  DJ="$W/bsst/$C.txt"
  for i in 1 2 3 4 5; do [ -s "$DJ" ] && [ $(wc -c < "$DJ") -gt 10000 ] && break
    curl -sSL -o "$DJ" "https://archive.org/download/$IT/CC-BSST-$L-$(printf %02d $n)_djvu.txt" || true; sleep $((2**i)); done
  echo "$C djvu: $(wc -c < "$DJ")"
done
