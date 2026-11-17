#!/bin/sh
# Архив для перевода «Махабхава-пракаши» в отдельном чате: sh mahabhava-prakasha/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/mahabhava-prakasha-kit
mkdir -p $K/sample $K/img $K/ocr $K/dict $K/ref
cp mahabhava-prakasha/KIT-README.md oriya-pilot/METHOD.md $K/
for k in src full ru en; do cp vaishnava-lilamrita/$k/01.md $K/sample/$k.md; done
S=sources/oriya/kanai-khuntia-mahabhava-prakasha
pdfimages -png $S/Kanai-Khuntia_Mahabhava-Prakasha_publ-Fakir-Mohan-Das_Baripada-1965_IA-sri-mahabhabaprakash-1965.pdf $T/x
mv $T/x-020.png $K/img/corrigenda.png
i=1; for n in $(seq 3 19); do mv $T/x-$(printf %03d $n).png $K/img/$(printf 'pref-%02d.png' $i); i=$((i+1)); done
i=1; for n in $(seq 21 42); do mv $T/x-$(printf %03d $n).png $K/img/$(printf 's-%02d.png' $i); i=$((i+1)); done
cp $S/Kanai-Khuntia_Mahabhava-Prakasha_1965_IA-OCR.txt $K/ocr/MP_IA-OCR.txt
cp sources/oriya/dictionaries/Brooks_*.pdf $K/dict/Brooks_1874.pdf
cp sources/oriya/dictionaries/Maltby_*.pdf $K/dict/Maltby_1874.pdf
cp mahabhava-prakasha/ref-names.md $K/ref/VL-names.md
rm -f "$OUT"; (cd $T && zip -qr "$OUT" mahabhava-prakasha-kit); rm -rf $T; echo "$OUT"
