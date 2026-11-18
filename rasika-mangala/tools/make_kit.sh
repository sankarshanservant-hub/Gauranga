#!/bin/sh
# Архив для перевода «Расика-мангалы» в отдельном чате: sh rasika-mangala/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/rasika-mangala-kit
mkdir -p $K/img $K/ocr $K/ref $K/sample
cp rasika-mangala/KIT-README.md $K/
cp bhakti-ratnakara/GLOSSARY.md $K/GLOSSARY.md
cp prema-vilasa/GLOSSARY.md $K/ref/prema-vilasa-GLOSSARY.md
cp bhakti-ratnakara/ru/15.md $K/sample/ru.md; cp bhakti-ratnakara/en/15.md $K/sample/en.md
S=rasika-mangala/src
cp $S/rasika-mangala_full_Gopiballavpur_455-Chaitanyabda_ocr-pages.txt $K/ocr/RM-full_ocr-pages.txt
cp $S/rasika-mangala_v1_Kishori-Das-Babaji_1997_ocr-pages.txt $K/ocr/RM-1997-v1_ocr-pages.txt
P=$S/rasika-mangala_full_Gopiballavpur_455-Chaitanyabda_2nd-ed.pdf
for n in $(seq 37 215); do pdfimages -png -f $n -l $n $P $T/x; mv $T/x-000.png $K/img/$(printf 'rm-%03d.png' $n); rm -f $T/x-*.png; done
rm -f "$OUT"; (cd $T && zip -qr "$OUT" rasika-mangala-kit); rm -rf $T; echo "$OUT"
