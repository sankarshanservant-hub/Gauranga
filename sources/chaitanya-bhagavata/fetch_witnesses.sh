#!/bin/sh
# Свидетели текста (распознанный слой archive.org) — в рабочую папку, не в репозиторий: sh fetch_witnesses.sh <папка>
D=${1:-/tmp/cb-witness}; mkdir -p "$D"; cd "$D"
get() { curl -s -m 300 -L -o "$2" "https://archive.org/download/$1"; echo "$2 $(wc -c < "$2")"; }
get "chaitanya-bhagavata-madhya-khanda/Sri_Caitanya_Bhagavata_Madhya_khanda_Puridas_Ananta_Vasudev_das_djvu.txt" puridas-madhya.txt
get "Chaitanya-bhagavata-antya-khanda/Sri_Caitanya_Bhagavata_Antya_khanda_Puridas_Ananta_Vasudev_das_djvu.txt" puridas-antya.txt
get "vKjc_shri-chaitanya-bhagavat-of-vrindavan-das-thakur-edited-by-shri-hari-das-shastri-/Shri%20Chaitanya%20Bhagavat%20Of%20Vrindavan%20Das%20Thakur%20Edited%20By%20Shri%20Hari%20Das%20Shastri%20-%20Shri%20Hari%20Das%20Shastri%2C%20Gada%20Dhar%20Gaur%20Hari%20Press%2C%20Vrindavan_djvu.txt" hds-devanagari.txt
get "bokx_chaitanya-bhagavata-adi-khanda-mula-gaudiya-bhashya-bhakti-siddhanta-sarasw/$(curl -s https://archive.org/metadata/bokx_chaitanya-bhagavata-adi-khanda-mula-gaudiya-bhashya-bhakti-siddhanta-sarasw | python3 -c "import json,sys,urllib.parse;print(urllib.parse.quote([f['name'] for f in json.load(sys.stdin)['files'] if f['name'].endswith('_djvu.txt')][0]))")" gm-adi-bhashya.txt
