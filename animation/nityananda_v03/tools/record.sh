#!/usr/bin/env bash
# Запись проверочных роликов v0.3 через Movie Maker Godot (нужны godot 4.3+, xvfb-run, ffmpeg).
# Использование: tools/record.sh <путь к godot> <папка вывода>
set -euo pipefail
GODOT="$1"; OUT="$2"; cd "$(dirname "$0")/.."
mkdir -p "$OUT"
"$GODOT" --headless --path . --import >/dev/null 2>&1 || true
rec() {  # имя, кадров, аргументы сцены...
  local name="$1" frames="$2"; shift 2
  local tmp; tmp="$(mktemp -d)"
  xvfb-run -a -s "-screen 0 1400x1600x24" "$GODOT" --path . --rendering-driver opengl3 \
    --write-movie "$tmp/f.png" --fixed-fps 30 --quit-after "$frames" res://main.tscn -- "$@" 2>&1 | grep -E "ERROR|SCRIPT|Done" || true
  ffmpeg -y -loglevel error -framerate 30 -i "$tmp/f%08d.png" -c:v libx264 -pix_fmt yuv420p -crf 23 "$OUT/$name.mp4"
  rm -rf "$tmp"
}
rec 01_walk_in_place_2cycles 72 --mode=in_place
rec 02_walk_forward_2cycles 72 --mode=forward
# один цикл (1,2 с) замедленно ×0.25 = 144 кадра: с костями и тот же цикл без них
rec 03_slow_cycle_bones 144 --mode=in_place --debug --slow=0.25
rec 04_slow_cycle_no_bones 144 --mode=in_place --slow=0.25
rec 05_walk_forward_bones 144 --mode=forward --debug
rec 06_walk_in_place_synth_marked 72 --mode=in_place --synth
