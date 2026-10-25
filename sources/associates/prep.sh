#!/bin/sh
# Скачивает три книги (archive.org) в files/ и раскладывает текст по страницам: files/pages/<T|M|B>/pNNNN.txt
# (NNNN — номер страницы PDF). files/ в .gitignore: книги под авторским правом, в репозиторий не кладутся.
set -e
cd "$(dirname "$0")"; mkdir -p files; cd files
B=https://archive.org/download
get() { [ -s "$1" ] || curl -sSL -o "$1" "$2"; }
get T.pdf "$B/tirtha-swami-bhakti-ballabh-2001-1999.-sri-chaitanya-his-life-and-associates/Tirtha%2C%20Swami%20Bhakti%20Ballabh%20%282001%2C%201999%29.%20%27Sri%20Chaitanya%20-%20His%20Life%20and%20Associates%27_text.pdf"
get M.pdf "$B/OxRq_lives-of-the-vaishnava-saints-translated-from-bengali-source-by-bhakti-vidhan-ma/Lives%20of%20the%20Vaishnava%20Saints%20Translated%20from%20Bengali%20Source%20by%20Bhakti%20Vidhan%20Mahayogi%20Swami%20-%20Anonymous%20_text.pdf"
get B.pdf "$B/EHso_shri-gaura-parshad-o-gaudiya-acharyaganera-charitavali-bengali-mayapura-shri-chaitanya-matha/Shri%20Gaura%20Parshad%20O%20Gaudiya%20Acharyaganera%20Charitavali%20Bengali%20-%20%20Mayapura%20Shri%20Chaitanya%20Matha_text.pdf"
for k in T M B; do
  mkdir -p pages/$k
  n=$(pdfinfo $k.pdf | awk '/^Pages:/{print $2}')
  i=1; while [ $i -le $n ]; do
    f=$(printf 'pages/%s/p%04d.txt' $k $i)
    [ -s "$f" ] || pdftotext -f $i -l $i $( [ $k = B ] && echo "" || echo -layout ) $k.pdf "$f"
    i=$((i+1))
  done
done
echo done
