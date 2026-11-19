#!/bin/sh
# Архив для перевода «Пата-нирнаи», «Пата-парьятаны» и «Шакха-нирнаи Абхирамы»: sh pata-nirnaya/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=$(realpath -m "${1:?zip}"); T=$(mktemp -d); K=$T/pata-nirnaya-kit
mkdir -p $K/img $K/ocr $K/ref $K/sample
S=pata-nirnaya/src
cp pata-nirnaya/KIT-README.md $K/
cp parshadas/GLOSSARY.md $K/GLOSSARY.md
cp lila-db/PERSONS.md lila-db/PLACES.md $K/ref/
cp vaishnava-vandana/ru/01.md $K/sample/ru.md; cp vaishnava-vandana/en/01.md $K/sample/en.md
cp $S/PN-PP_KDB-print_tesseract-pages.txt $K/ocr/PN-PP_KDB_tesseract-pages.txt
cp $S/PP-ASN_SPP1318_pdf116-121_tesseract-pages.txt $K/ocr/PP-ASN_SPP1318_tesseract-pages.txt
cp $S/img/*.jpg $K/img/
rm -f "$OUT"; (cd $T && zip -qr "$OUT" pata-nirnaya-kit); rm -rf $T; echo "$OUT $(du -h "$OUT" | cut -f1)"
