#!/bin/sh
# Архив для перевода «Шакха-нирнаямриты» в отдельном чате: sh shakha-nirnayamrita/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=$(realpath -m "${1:?zip}"); T=$(mktemp -d); K=$T/shakha-nirnayamrita-kit
mkdir -p $K/img $K/ocr $K/ref $K/sample
S=shakha-nirnayamrita/src
cp shakha-nirnayamrita/KIT-README.md $K/
cp parshadas/GLOSSARY.md $K/GLOSSARY.md
cp lila-db/PERSONS.md lila-db/PLACES.md $K/ref/
cp gaura-ganoddesha/ru/01.md $K/sample/ru.md; cp gaura-ganoddesha/en/01.md $K/sample/en.md
cp $S/SNA_Lahari-pdf301-303_tesseract-pages.txt $K/ocr/SNA_tesseract-pages.txt
cp $S/SNA_Lahari-pdf301-303_IA-ocr-pages.txt $K/ocr/SNA_IA-ocr-pages.txt
cp $S/img/sna-301.jpg $S/img/sna-302.jpg $S/img/sna-303.jpg $K/img/
rm -f "$OUT"; (cd $T && zip -qr "$OUT" shakha-nirnayamrita-kit); rm -rf $T; echo "$OUT $(du -h "$OUT" | cut -f1)"
