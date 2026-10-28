#!/bin/bash
# Перед этапом А: взять общие справочники базы лил (лица, места, источники) из основной ветки, чтобы не заводить
# дубли тегов (так было: @vaishnavananda-acharya при уже существующем @vaishnavananda). Записи cc.yaml и events-cc.yaml
# ведёт только чат ЧЧ; основной чат забирает их сам (`git checkout origin/<ветка ЧЧ> -- lila-db/lilas/cc.yaml …`).
# Запуск: bash tools/coord/sync_lila.sh   (в локальном режиме без удалённого репозитория — ничего не делает)
. "$(dirname "$0")/env.sh"
MAIN=${LILA_MAIN:-claude/book-translation-tesseract-bengali-yaygag}
cd "$REPO"
git remote | grep -q . || { echo "нет удалённого репозитория — пропуск"; exit 0; }
git fetch -q origin "$MAIN" || { echo "!! нет ветки $MAIN"; exit 1; }
git checkout "origin/$MAIN" -- lila-db/PERSONS.md lila-db/PLACES.md lila-db/SOURCES.md
python3 lila-db/build.py -w 2>&1 | tail -1
git checkout -- lila-db/TIMELINE.md lila-db/EVENTS.md lila-db/export 2>/dev/null
echo "Если build.py показал «нет тега @…» — тег в cc.yaml заменить на принятый в основной ветке (PERSONS.md)."
