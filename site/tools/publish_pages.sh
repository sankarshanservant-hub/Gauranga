#!/bin/sh
# Публикует сайт на GitHub Pages: содержимое site/ (без исходников и инструментов) → корень ветки gh-pages.
# Запуск из корня репозитория: sh site/tools/publish_pages.sh
set -e
ROOT=$(git rev-parse --show-toplevel)
TMP=$(mktemp -d)
cd "$TMP"
git init -q -b gh-pages
cp "$ROOT/site/index.html" "$ROOT/site/style.css" "$ROOT/site/app.js" .
mkdir -p assets data
cp -r "$ROOT/site/assets/img" "$ROOT/site/assets/audio" assets/
cp -r "$ROOT/site/data/." data/
touch .nojekyll
git add -A
git -c user.name="$(git -C "$ROOT" config user.name)" -c user.email="$(git -C "$ROOT" config user.email)" \
  commit -q -m "Сайт «Гаура-лила» из $(git -C "$ROOT" rev-parse --short HEAD)"
git remote add origin "$(git -C "$ROOT" remote get-url origin)"
git push -q -f origin gh-pages
cd "$ROOT" && rm -rf "$TMP"
echo "опубликовано в gh-pages"
