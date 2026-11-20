#!/bin/bash
# Коммит + пуш (всё в chaitanya-charitamrita и lila-db, без сгенерированных файлов lila-db).
# Запуск: bash tools/coord/save.sh "сообщение"
. "$(dirname "$0")/env.sh"
cd "$REPO"
git checkout -- lila-db/TIMELINE.md lila-db/EVENTS.md lila-db/export 2>/dev/null
git add -A chaitanya-charitamrita lila-db
git commit -q -m "$1

${COMMIT_TRAILER:-}" 2>/dev/null || echo "(нечего коммитить)"
if git remote | grep -q .; then        # есть удалённый репозиторий — пуш с повтором; локальный режим — только коммит
  for d in 0 2 4 8 16; do sleep $d
    git push -q -u origin "$BRANCH" 2>/dev/null && break
    git pull -q --rebase origin "$BRANCH" 2>/dev/null || true
  done
fi
git status -sb | head -1
