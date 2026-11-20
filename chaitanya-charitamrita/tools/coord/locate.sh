#!/bin/bash
# Найти страницы главы в CC_SS.pdf: OCR диапазона и по каждой странице — номера стихов ॥N॥ и колофоны.
# Запуск: bash tools/coord/locate.sh P1 P2   (начало главы = страница, где кончилась предыдущая)
. "$(dirname "$0")/env.sh"
seq $1 $2 | xargs -P 4 -I{} sh "$CC/tools/coord/ocr_page.sh" {}
for p in $(seq $1 $2); do
  echo "$p: $(grep -o '॥ *[০-৯]\+ *॥' $SCAN/o$p.txt | tr -d ' ' | tr '\n' ' ' | cut -c1-150) $(grep -o 'ইতি অ[^ ]*ভাষ্যে *[^ ]*\|ইতি অনুভা[^ ]* *[^ ]*\|কথাসার' $SCAN/o$p.txt | tr '\n' ' ')"
done
echo "Конец главы — страница с «ইতি অনুভাষ্যে <N-й> পরিচ্ছেদ»; там же «কথাসার» следующей."
