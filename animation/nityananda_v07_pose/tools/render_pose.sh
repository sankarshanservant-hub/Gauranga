#!/usr/bin/env bash
# Одна неподвижная поза прохода ближней ноги мимо опорной (q по умолчанию 0.77), крупно, 1:1 к холсту.
# Исходник — проект v0.7 (не меняется), вариант A — project/ этой папки.
# Использование: tools/render_pose.sh <godot> <папка сырых кадров> [фаза] [доп. аргументы для A]
set -euo pipefail
GODOT="$1"; RAW="$(mkdir -p "$2" && cd "$2" && pwd)"; PH="${3:-0.77}"; EXTRA="${4:-}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
render() {  # $1 проект, $2 метка
  cd "$1"; "$GODOT" --headless --path . --import >/dev/null 2>&1 || true
  for m in n d t s; do
    a=""; case $m in d) a="--debug";; t) a="--stretch";; s) a="--synth";; esac
    xvfb-run -a -s "-screen 0 1400x1600x24" "$GODOT" --path . --rendering-driver opengl3 --resolution 1054x1500 \
      --write-movie "$RAW/$2_$m.png" --fixed-fps 30 --quit-after 2 res://main.tscn -- --mode=in_place --nohud \
      --start=$PH --slow=0.00001 --scale=1 --ox=0 --oy=0 --logknees $a \
      $( [ "$2" = A ] && echo $EXTRA ) 2>&1 | grep KNEES | tail -1 > "$RAW/k_$2_$m.txt"
  done
}
render "$HERE/../nityananda_v07" v07
render "$HERE/project" A
