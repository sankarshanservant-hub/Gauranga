#!/bin/sh
# Архив для перевода «Гаура-чарита-чинтамани» в отдельном чате: sh gaura-charita-chintamani/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/gaura-charita-chintamani-kit
mkdir -p $K/img $K/ocr $K/ref $K/sample
cp gaura-charita-chintamani/KIT-README.md $K/
cp bhakti-ratnakara/GLOSSARY.md $K/GLOSSARY.md
cp padas/GLOSSARY.md $K/ref/padas-GLOSSARY.md
cp bhakti-ratnakara/ru/01.md $K/sample/ru.md; cp bhakti-ratnakara/en/01.md $K/sample/en.md
S=sources/narahari-chakravarti/gaura-carita-cintamani
cp $S/gaura-carita-cintamani_bengali_Haridas-Das_Navadvip_1947_ocr.txt $K/ocr/GCC_IA-OCR.txt
pdftoppm -r 200 -gray -jpeg -jpegopt quality=80 -f 6 -l 200 $S/gaura-carita-cintamani_bengali_Haridas-Das_Navadvip_1947.pdf $K/img/g
rm -f "$OUT"; (cd $T && zip -qr "$OUT" gaura-charita-chintamani-kit); rm -rf $T; echo "$OUT"
