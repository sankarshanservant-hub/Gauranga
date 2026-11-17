#!/bin/sh
# Собирает архив для перевода «Бхакти-ратнакары» в отдельном чате: sh tools/make_kit.sh <выходной.zip> [первая таранга]
# Нужны рабочие файлы src/ (python3 -I tools/prep.py).
set -e
cd "$(dirname "$0")/.."
OUT=${1:?zip}; FIRST=${2:-4}
T=$(mktemp -d); K=$T/bhakti-ratnakara-kit; mkdir -p $K/ref $K/done/ru $K/done/en $K/src
cp KIT-README.md TASK.md GLOSSARY.md $K/
cp ../prema-vilasa/GLOSSARY.md $K/ref/prema-vilasa-GLOSSARY.md
cp ../padas/GLOSSARY.md $K/ref/padas-GLOSSARY.md
cp ru/*.md $K/done/ru/; cp en/*.md $K/done/en/
for n in $(seq $FIRST 15); do t=$(printf %02d $n); cp src/t$t-W.txt src/t$t-B.txt $K/src/; done
rm -f "$OUT"; (cd $T && zip -qr "$OUT" bhakti-ratnakara-kit); rm -rf $T
echo "$OUT"
