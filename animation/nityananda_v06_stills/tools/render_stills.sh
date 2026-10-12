#!/usr/bin/env bash
# Неподвижные кадры цикла из проекта v0.6 (проект не меняется: только аргументы запуска).
# Использование: tools/render_stills.sh <godot> <папка для сырых кадров>
set -euo pipefail
GODOT="$1"; RAW="$(mkdir -p "$2" && cd "$2" && pwd)"; PROJ="$(cd "$(dirname "$0")/../../nityananda_v06" && pwd)"
cd "$PROJ"; "$GODOT" --headless --path . --import >/dev/null 2>&1 || true
# фазы: перенос ближней ноги 0.50 / 0.77 / 0.80 / 0.98; тот же набор для дальней 0.00 / 0.27 / 0.30 / 0.48
for ph in 0.50 0.77 0.80 0.98 0.00 0.27 0.30 0.48; do
  for m in n d t s; do
    a=""; case $m in d) a="--debug";; t) a="--stretch";; s) a="--synth";; esac
    xvfb-run -a -s "-screen 0 1400x1600x24" "$GODOT" --path . --rendering-driver opengl3 --resolution 380x1060 \
      --write-movie "$RAW/f_${ph}_$m.png" --fixed-fps 30 --quit-after 2 res://main.tscn -- --mode=in_place --nohud \
      --start=$ph --slow=0.00001 --scale=0.75 --ox=-210 --oy=-30 --logknees $a 2>&1 | grep KNEES | tail -1 > "$RAW/k_${ph}_$m.txt"
  done
done
