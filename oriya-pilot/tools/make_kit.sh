#!/bin/sh
# Архив для перевода «Вайшнава-лиламриты» в отдельном чате: sh oriya-pilot/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/vaishnava-lilamrita-kit
mkdir -p $K/pilot $K/img $K/ocr $K/dict $K/ref
cp oriya-pilot/KIT-README.md oriya-pilot/METHOD.md oriya-pilot/QUESTIONS.md $K/
cp oriya-pilot/vaishnava-lilamrita/*.md $K/pilot/
S=sources/oriya/madhava-chaitanya-vilasa
pdfimages -png -f 46 -l 127 $S/Madhava_Vaishnava-Lilamrita_ed-Acharya_1986_IA-baishnaba-lilamruta-1986.pdf $T/x
i=45; for f in $(ls $T/x-*.png); do mv $f $K/img/$(printf 'l-%03d.png' $i); i=$((i+1)); done
cp $S/Madhava_Vaishnava-Lilamrita_ed-Acharya_1986_IA-OCR.txt $K/ocr/VL_IA-OCR.txt
cp sources/oriya/dictionaries/Brooks_*.pdf $K/dict/Brooks_1874.pdf
cp sources/oriya/dictionaries/Maltby_*.pdf $K/dict/Maltby_1874.pdf
cp padas/GLOSSARY.md $K/ref/padas-GLOSSARY.md; cp prema-vilasa/GLOSSARY.md $K/ref/prema-vilasa-GLOSSARY.md
rm -f "$OUT"; (cd $T && zip -qr "$OUT" vaishnava-lilamrita-kit); rm -rf $T; echo "$OUT"
