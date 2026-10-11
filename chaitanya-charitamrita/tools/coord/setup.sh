#!/bin/bash
# Подготовка нового контейнера: системные пакеты, Python-пакеты, скан издания Гаудия Матха.
# Запуск: bash chaitanya-charitamrita/tools/coord/setup.sh
set -e
. "$(dirname "$0")/env.sh"
need=""
command -v tesseract >/dev/null || need="$need tesseract-ocr"
tesseract --list-langs 2>/dev/null | grep -qx ben || need="$need tesseract-ocr-ben"
command -v pdftoppm >/dev/null || need="$need poppler-utils"
if [ -n "$need" ]; then
  (sudo -n true 2>/dev/null && SUDO=sudo) || SUDO=""
  $SUDO apt-get update -q >/dev/null && $SUDO apt-get install -y -q $need >/dev/null
fi
python3 -c "import PIL, yaml, docx, gdown" 2>/dev/null || pip install -q pillow pyyaml python-docx gdown
# Скан издания 1928 г. (Гаудия Матх, 1079 с.) — в .gitignore, лежит на Google Диске пользователя (публичная ссылка)
if [ ! -s "$CC/src/CC_SS.pdf" ]; then
  gdown --id 12GBJMUhBfyjsnnOgwlTuz3SHJWX5niAM -O "$CC/src/CC_SS.pdf"
fi
# Chromium для md2pdf.py (headless печать в PDF)
CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1)
[ -z "$CH" ] && CH=$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)
echo "tesseract: $(tesseract --version 2>&1 | head -1) | ben: $(tesseract --list-langs 2>/dev/null | grep -c '^ben$')"
echo "CC_SS.pdf: $(ls -la "$CC/src/CC_SS.pdf" | awk '{print $5}') байт (ожидается 71872685)"
echo "chrome: ${CH:-НЕ НАЙДЕН — md2pdf.py не соберёт PDF; задать CHROME=/путь}"
echo "рабочая папка: $W"
