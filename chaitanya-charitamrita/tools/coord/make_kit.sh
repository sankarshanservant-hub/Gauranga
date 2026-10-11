#!/bin/bash
# Собрать автономный комплект (для VS Code / Claude Code без GitHub): проект + заранее подготовленные данные.
# Запуск: bash tools/coord/make_kit.sh <страница_от> <страница_до> [выходная папка]
#   страницы — диапазон скана, для которого класть готовый OCR (напр. 268 860 — Ади 16–17 и вся Мадхья).
# Результат: <выход>/cc-kit-YYYYMMDD.zip (проект без скана и PDF; cc-work: OCR tsv/txt, CCBSST).
set -e
. "$(dirname "$0")/env.sh"
P1=$1; P2=$2; OUT=${3:-$W/kit}
D=$(date +%Y%m%d); K="$OUT/cc-kit"; rm -rf "$K"; mkdir -p "$K/gauranga" "$K/cc-work/scan1" "$K/cc-work/bsst"
cd "$REPO"
cp CLAUDE.md "$K/gauranga/"
cp -r fonts "$K/gauranga/" 2>/dev/null || true
tar --exclude='chaitanya-charitamrita/src/*.pdf' --exclude='chaitanya-charitamrita/ed/pdf' --exclude='__pycache__' \
    -cf - chaitanya-charitamrita lila-db | tar -xf - -C "$K/gauranga"
mkdir -p "$K/gauranga/chaitanya-charitamrita/ed/pdf"
# тексты других житий, на которые ссылается база лил (проверка lila-db/build.py и поле divergence), + «Чайтанья-бхагавата» (txt)
DIRS=$(grep -rhoP '^\s*file:\s*"?\K[^"\s]+' lila-db/lilas/*.yaml | sed 's#/[^/]*$##' | sort -u | grep -v '^chaitanya-charitamrita')
tar --exclude='*.pdf' --exclude='*.doc' --exclude='*.epub' -cf - $DIRS chaitanya-bhagavata/src/txt 2>/dev/null | tar -xf - -C "$K/gauranga"
cp chaitanya-charitamrita/KIT-README.md "$K/"
for p in $(seq $P1 $P2); do for f in t$p.tsv o$p.txt; do [ -s "$SCAN/$f" ] && cp "$SCAN/$f" "$K/cc-work/scan1/"; done; done
cp "$W"/bsst/*.txt "$K/cc-work/bsst/" 2>/dev/null || true
echo "Готовый OCR страниц $P1–$P2 скана CC_SS.pdf (tesseract ben: tNNN.tsv — psm 3, oNNN.txt — psm 4) и второй OCR CCBSST (bsst/<Гл>.txt). Картинки страниц (pNNN.pgm) отрисуются при подготовке главы." > "$K/cc-work/README.txt"
cd "$OUT" && rm -f cc-kit-$D.zip && zip -qr cc-kit-$D.zip cc-kit && ls -la "$OUT/cc-kit-$D.zip"
du -sh "$K/gauranga" "$K/cc-work"
