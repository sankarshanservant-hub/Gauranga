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
  if command -v brew >/dev/null; then brew install tesseract tesseract-lang poppler      # macOS
  elif command -v apt-get >/dev/null; then                                               # Linux / WSL
    (sudo -n true 2>/dev/null && SUDO=sudo) || SUDO="sudo"; [ "$(id -u)" = 0 ] && SUDO=""
    $SUDO apt-get update -q >/dev/null && $SUDO apt-get install -y -q $need >/dev/null
  else echo "!! установите вручную: $need (tesseract с языком ben, poppler)"; fi
fi
python3 -c "import PIL, yaml, docx, gdown, fitz" 2>/dev/null || python3 -m pip install -q pillow pyyaml python-docx gdown pymupdf || python3 -m pip install -q --user --break-system-packages pillow pyyaml python-docx gdown pymupdf
# Скан издания 1928 г. (Гаудия Матх, 1079 с.) — в .gitignore, лежит на Google Диске пользователя (публичная ссылка)
if [ ! -s "$CC/src/CC_SS.pdf" ]; then
  gdown --id 12GBJMUhBfyjsnnOgwlTuz3SHJWX5niAM -O "$CC/src/CC_SS.pdf"
fi
# Chromium для md2pdf.py (headless печать в PDF)
CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1)
[ -z "$CH" ] && CH=$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)
[ -z "$CH" ] && [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
echo "tesseract: $(tesseract --version 2>&1 | head -1) | ben: $(tesseract --list-langs 2>/dev/null | grep -c '^ben$')"
echo "CC_SS.pdf: $(ls -la "$CC/src/CC_SS.pdf" | awk '{print $5}') байт (ожидается 71872685)"
echo "chrome: ${CH:-НЕ НАЙДЕН — md2pdf.py не соберёт PDF; задать CHROME=/путь}"
echo "рабочая папка: $W"
