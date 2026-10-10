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
# версия в адресах файлов: браузер не смешает закэшированную старую страницу с новыми стилями/скриптами/данными
V=$(git -C "$ROOT" rev-parse --short HEAD)-$(date +%s)
sed -i "s#href=\"style.css\"#href=\"style.css?v=$V\"#; s#src=\"app.js\"#src=\"app.js?v=$V\"#" index.html
sed -i "s#data/timeline.json'#data/timeline.json?v=$V'#; s#data/verses/\${name}.json\`#data/verses/\${name}.json?v=$V\`#" app.js
grep -q "style.css?v=" index.html && grep -q "timeline.json?v=" app.js && grep -q "json?v=$V" app.js || { echo "не удалось проставить версию"; exit 1; }
# страница: просим браузер всегда сверяться с сервером
sed -i 's#<meta charset="utf-8">#<meta charset="utf-8">\n<meta http-equiv="Cache-Control" content="no-cache">#' index.html
touch .nojekyll
git add -A
git -c user.name="$(git -C "$ROOT" config user.name)" -c user.email="$(git -C "$ROOT" config user.email)" \
  commit -q -m "Сайт «Гаура-лила» из $(git -C "$ROOT" rev-parse --short HEAD)"
git remote add origin "$(git -C "$ROOT" remote get-url origin)"
git push -q -f origin gh-pages
cd "$ROOT" && rm -rf "$TMP"
echo "опубликовано в gh-pages"
