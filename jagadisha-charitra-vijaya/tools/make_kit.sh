#!/bin/sh
# Архив для перевода «Джагадиша-чаритра-виджаи» в отдельном чате: sh jagadisha-charitra-vijaya/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=$(realpath -m "${1:?zip}"); T=$(mktemp -d); K=$T/jagadisha-charitra-vijaya-kit
mkdir -p $K/img $K/ocr $K/ref $K/sample
S=jagadisha-charitra-vijaya/src
cp jagadisha-charitra-vijaya/KIT-README.md $K/
cp parshadas/GLOSSARY.md $K/GLOSSARY.md
cp lila-db/PERSONS.md lila-db/PLACES.md $K/ref/
cp bhakti-ratnakara/ru/15.md $K/sample/ru.md; cp bhakti-ratnakara/en/15.md $K/sample/en.md
awk '/^=== pdf/{p=substr($3,1,3)+0} p<=79' $S/JCV_pdf013-080_tesseract-pages.txt > $K/ocr/JCV_tesseract-pages.txt
awk '/^=== pdf/{p=substr($3,1,3)+0} p<=79' $S/JCV_pdf013-080_IA-ocr-pages.txt > $K/ocr/JCV_IA-ocr-pages.txt
for n in $(seq 13 79); do cp $S/img/$(printf "jcv-%03d.jpg" $n) $K/img/; done
rm -f "$OUT"; (cd $T && zip -qr "$OUT" jagadisha-charitra-vijaya-kit); rm -rf $T; echo "$OUT $(du -h "$OUT" | cut -f1)"
