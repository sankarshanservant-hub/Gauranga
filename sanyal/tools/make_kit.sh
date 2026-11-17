#!/bin/sh
# Архив для перевода Саньяла (EN→RU) в отдельном чате: sh sanyal/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/sanyal-kit
mkdir -p $K/frag $K/ref
cp sanyal/KIT-README.md sanyal/TASK-translation-ru.md $K/
python3 -I sanyal/tools/split.py $K/frag
cp sources/sanyal/Sanyal_1933_scan_ocr.txt $K/ref/scan-1933-ocr.txt
rm -f "$OUT"; (cd $T && zip -qr "$OUT" sanyal-kit); rm -rf $T; echo "$OUT"
