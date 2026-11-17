#!/bin/sh
# Архив для перевода «Джаганнатха-чаритамриты» Дивакара Даса (гл. 1–7, 23) в отдельном чате:
#   sh divakara-jagannatha-charitamrita/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/divakara-kit
mkdir -p $K/sample $K/img $K/ocr $K/dict $K/ref
cp divakara-jagannatha-charitamrita/KIT-README.md oriya-pilot/METHOD.md $K/
for k in src full ru en; do cp vaishnava-lilamrita/$k/01.md $K/sample/$k.md; done
S=sources/oriya/divakara-jagannatha-charitamrita
P=$S/Divakara-Das_Jagannatha-Charitamrita_ed-Janardan-Kar_Cuttack-1927_IA-jagannathamruta-gita-1927.pdf
for n in $(seq 2 47) $(seq 140 144); do pdfimages -png -f $n -l $n $P $T/x; mv $T/x-000.png $K/img/$(printf 'd-%03d.png' $n); done
cp $S/Divakara-Das_Jagannatha-Charitamrita_ed-Janardan-Kar_Cuttack-1927_IA-OCR.txt $K/ocr/DD_IA-OCR.txt
cp sources/oriya/dictionaries/Brooks_*.pdf $K/dict/Brooks_1874.pdf
cp sources/oriya/dictionaries/Maltby_*.pdf $K/dict/Maltby_1874.pdf
cp divakara-jagannatha-charitamrita/ref-names.md $K/ref/VL-names.md
rm -f "$OUT"; (cd $T && zip -qr "$OUT" divakara-kit); rm -rf $T; echo "$OUT"
