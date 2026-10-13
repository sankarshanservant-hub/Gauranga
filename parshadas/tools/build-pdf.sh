#!/bin/sh
# Сборка статьи в PDF: build-pdf.sh <ru|en>/<тег>.md <выход без расширения> "<Заглавие>"
# md без служебных меток → docx (pandoc, стили tools/reference.docx: Liberation Serif, A4) → pdf (LibreOffice).
set -e
D=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d)
sed 's/<!--[^>]*-->//g' "$1" | cat -s > "$T/in.md"
pandoc "$T/in.md" -o "$T/out.docx" --reference-doc="$D/reference.docx" --toc --toc-depth=2 \
  --metadata title="$3" --metadata toc-title="Содержание" --metadata lang=ru
soffice --headless --convert-to pdf --outdir "$T" "$T/out.docx" >/dev/null 2>&1
cp "$T/out.pdf" "$2.pdf"; cp "$T/in.md" "$2.md"; rm -rf "$T"
