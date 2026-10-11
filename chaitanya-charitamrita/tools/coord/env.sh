# Общие переменные координатора. Подключать: . chaitanya-charitamrita/tools/coord/env.sh
export REPO="${REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
export CC="$REPO/chaitanya-charitamrita"
export BRANCH="${BRANCH:-$(git -C "$REPO" rev-parse --abbrev-ref HEAD)}"
# Рабочая папка вне репозитория (страницы скана, OCR, вырезки, страницы vedabase). Не коммитится.
export W="${CC_WORK:-/tmp/cc-work}"
export SCAN="$W/scan1"
mkdir -p "$W" "$SCAN"
