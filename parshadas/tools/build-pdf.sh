#!/bin/sh
# Сборка статьи в PDF: build-pdf.sh <ru|en>/<тег>.md <выход без расширения> "<Заглавие>"
# md без служебных меток → docx (pandoc, стили tools/reference.docx: Liberation Serif, A4) → pdf (LibreOffice).
set -e
D=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d)
# Заглавие — только в свойствах документа (title-meta, через YAML-блок, а не --metadata: в аргументах командной
# строки pandoc без UTF-8-локали портит кириллицу); на странице его даёт заголовок «# …» статьи. Оглавления нет:
# LibreOffice при конвертации не заполняет поле TOC (выходил пустой заголовок).
sed 's/<!--[^>]*-->//g' "$1" | cat -s > "$T/body.md"
{ printf -- '---\ntitle-meta: "%s"\nlang: ru\n---\n\n' "$3"; cat "$T/body.md"; } > "$T/in.md"
pandoc "$T/in.md" -o "$T/out.docx" --reference-doc="$D/reference.docx"
soffice --headless --convert-to pdf --outdir "$T" "$T/out.docx" >/dev/null 2>&1
cp "$T/out.pdf" "$2.pdf"; cp "$T/body.md" "$2.md"; rm -rf "$T"
