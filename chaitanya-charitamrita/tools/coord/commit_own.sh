#!/bin/bash
# Для исполнителей: закоммитить только свои файлы (+ пуш, если есть удалённый репозиторий).
# Запуск: bash tools/coord/commit_own.sh "сообщение" файл1 файл2 …   (пути — от chaitanya-charitamrita/)
. "$(dirname "$0")/env.sh"
msg=$1; shift
cd "$CC"
for i in 1 2 3 4 5; do [ -e "$REPO/.git/index.lock" ] || break; sleep 2; done
git add -- "$@" && git commit -q -m "$msg

${COMMIT_TRAILER:-}" -- "$@" || { echo "(нечего коммитить)"; exit 0; }
if git remote | grep -q .; then
  git pull -q --rebase origin "$BRANCH" 2>/dev/null || true
  for d in 0 2 4 8; do sleep $d; git push -q origin "$BRANCH" 2>/dev/null && break; done
fi
git log --oneline -1
