#!/bin/sh
# Архив для перевода «Сарвабхаума-шатаки» в отдельном чате:
#   sh sarvabhauma-shataka/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/sarvabhauma-kit
mkdir -p $K/sample $K/ref
cp sarvabhauma-shataka/KIT-README.md sources/sarvabhauma-shataka/mula-iast.txt $K/
cp sources/sarvabhauma-shataka/README.md $K/SOURCE.md
cp stotras/ru/01.md $K/sample/ru.md; cp stotras/en/01.md $K/sample/en.md
sed -n '/^### 1$/,/^### 6$/p' chaitanya-chandramrita/skt/s01.md | sed '$d' > $K/sample/full.md
cp stotras/GLOSSARY.md $K/ref/GLOSSARY.md
rm -f "$OUT"; (cd $T && zip -qr "$OUT" sarvabhauma-kit); rm -rf $T; echo "$OUT"
