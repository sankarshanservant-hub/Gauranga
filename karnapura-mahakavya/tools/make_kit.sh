#!/bin/sh
# Архив для перевода «Махакавьи» на английский в отдельном чате: sh karnapura-mahakavya/tools/make_kit.sh <выход.zip>
set -e
cd "$(dirname "$0")/../.."
OUT=${1:?zip}; T=$(mktemp -d); K=$T/mahakavya-en-kit
mkdir -p $K/ru $K/ref $K/sample
cp karnapura-mahakavya/KIT-README.md $K/
cp karnapura-mahakavya/ru/*.md $K/ru/
cp murari-gupta/GLOSSARY.md $K/GLOSSARY.md
cp lila-db/PERSONS.md lila-db/PLACES.md $K/ref/
cat murari-gupta/en/1.01.md murari-gupta/en/1.02.md > $K/sample/murari-en.md
rm -f "$OUT"; (cd $T && zip -qr "$OUT" mahakavya-en-kit); rm -rf $T; echo "$OUT"
