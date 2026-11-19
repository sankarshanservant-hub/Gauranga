#!/bin/sh
# Комплекты для перевода статей Бхактивиноды Тхакура (бенгали → RU+EN) в отдельном чате.
#   sh bhaktivinoda-articles/tools/make_kit.sh <выходная-папка> [часть]
# Части (каждая ≤ ~25 МБ): 1 — группы A+B (BVA-01…20), 2 — C, BVA-21…46, 3 — C, BVA-47…72, 4 — D (BVA-73…87).
# Без второго аргумента собираются все четыре: bhaktivinoda-articles-kit-partN.zip
# Список статей и страниц — bhaktivinoda-articles/articles.tsv (src/pdf_from/pdf_to — основа; alt — сверка).
set -e
cd "$(dirname "$0")/../.."
OUTDIR=${1:?outdir}; ONLY=${2:-}
mkdir -p "$OUTDIR"; OUTDIR=$(cd "$OUTDIR" && pwd)
S=sources/bhaktivinoda-articles/src
SCM_PDF=$S/prabandhabali_MayapurSCM_text.pdf;            SCM_OCR=$S/prabandhabali_MayapurSCM_ocr-pages.txt
ST5_PDF=$S/sajjana-toshani-thakur/ST5_1893_dli315943.pdf; ST5_OCR=$S/sajjana-toshani-thakur/ST5_1893_ocr-pages.txt
GVS_PDF=$S/prabandhavali_v1_GVS1950.pdf;                  GVS_OCR=$S/prabandhavali_v1_GVS1950_ocr-pages.txt
TSV=bhaktivinoda-articles/articles.tsv

pdf_of() { case $1 in SCM04) echo $SCM_PDF;; ST5) echo $ST5_PDF;; GVS) echo $GVS_PDF;; esac; }
ocr_of() { case $1 in SCM04) echo $SCM_OCR;; ST5) echo $ST5_OCR;; GVS) echo $GVS_OCR;; esac; }

# страницы источника: изображения (150 dpi, серые JPEG) + OCR с метками
put_pages() { # src from to dir
  P=$(pdf_of $1); O=$(ocr_of $1); mkdir -p "$4/img"
  pdftoppm -r 150 -gray -jpeg -jpegopt quality=55 -f $2 -l $3 "$P" "$4/img/$1-p"
  awk -v a=$2 -v b=$3 -v s=$1 '
    { gsub(/\f/, "") }
    /^=== pdf [0-9]+ ===$/ { n=$3+0; on=(n>=a && n<=b); if (on) print "=== " s " pdf " n " ==="; next }
    on { print }' "$O" >> "$4/ocr.txt"
}

part_of() { # id -> part
  n=$(echo $1 | sed 's/BVA-0*//'); if [ $n -le 20 ]; then echo 1; elif [ $n -le 46 ]; then echo 2; elif [ $n -le 72 ]; then echo 3; else echo 4; fi
}

build_part() {
  PART=$1; T=$(mktemp -d); K=$T/bhaktivinoda-articles-kit
  mkdir -p $K/articles $K/ref
  cp bhaktivinoda-articles/KIT-README.md bhaktivinoda-articles/ARTICLES.md $K/
  cp parshadas/GLOSSARY.md $K/ref/parshadas-GLOSSARY.md
  cp sanyal/TASK-translation-ru.md $K/ref/sanyal-TASK-terms.md
  tail -n +2 $TSV | tr '\t' '|' | while IFS='|' read id grp title translit src a b alt note; do
    [ "$(part_of $id)" = "$PART" ] || continue
    D=$K/articles/$id; mkdir -p $D
    printf '%s\n%s (%s)\nГруппа: %s\nОснова: %s, pdf %s–%s\nСверка: %s\n%s\n' "$id" "$title" "$translit" "$grp" "$src" "$a" "$b" "${alt:-—}" "$note" > $D/INFO.txt
    echo "##### ОСНОВА: $src pdf $a–$b" > $D/ocr.txt
    put_pages $src $a $b $D
    if [ -n "$alt" ]; then
      echo "$alt" | tr ',' '\n' | while IFS=: read s r; do
        echo "##### СВЕРКА: $s pdf $r" >> $D/ocr.txt
        put_pages $s ${r%-*} ${r#*-} $D
      done
    fi
  done
  Z=$OUTDIR/bhaktivinoda-articles-kit-part$PART.zip
  rm -f "$Z"; (cd $T && zip -qr "$Z" bhaktivinoda-articles-kit); rm -rf $T
  SZ=$(du -m "$Z" | cut -f1); echo "$Z  ${SZ} МБ"
  [ $SZ -le 26 ] || echo "ВНИМАНИЕ: часть $PART больше 25 МБ — понизить quality или разделить" >&2
}

if [ -n "$ONLY" ]; then build_part $ONLY; else for p in 1 2 3 4; do build_part $p; done; fi
