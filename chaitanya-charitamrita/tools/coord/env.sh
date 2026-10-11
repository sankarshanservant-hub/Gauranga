# Общие переменные координатора. Подключать: . chaitanya-charitamrita/tools/coord/env.sh
export REPO="${REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
export CC="$REPO/chaitanya-charitamrita"
export BRANCH="${BRANCH:-$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)}"
# Рабочая папка вне репозитория (страницы скана, OCR, вырезки, страницы vedabase). Не коммитится.
# по умолчанию: папка cc-work рядом с репозиторием (так устроен автономный комплект), иначе /tmp/cc-work
if [ -z "$CC_WORK" ] && [ -d "$REPO/../cc-work" ]; then CC_WORK="$(cd "$REPO/../cc-work" && pwd)"; fi
export CC_WORK="${CC_WORK:-/tmp/cc-work}"
export W="$CC_WORK"
export SCAN="$W/scan1"
mkdir -p "$W" "$SCAN"
# строки атрибуции коммитов: $COMMIT_TRAILER или файл $W/trailer.txt (координатор пишет его один раз за сессию)
if [ -z "$COMMIT_TRAILER" ] && [ -s "$W/trailer.txt" ]; then export COMMIT_TRAILER="$(cat "$W/trailer.txt")"; fi
