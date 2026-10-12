#!/usr/bin/env bash
# Ролики v0.7: сравнение с v0.6 и замедленный цикл. Один масштаб (0,5) и одна линия земли.
# Использование: tools/compare_c.sh <godot> <папка вывода>
set -euo pipefail
GODOT="$1"; OUT="$(mkdir -p "$2" && cd "$2" && pwd)"; HERE="$(cd "$(dirname "$0")/.." && pwd)"; PREV="$HERE/../nityananda_v06"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
TMP="$(mktemp -d)"
VIEW=(--variant=C --nohud --ground --cycles=99 --scale=0.5 --ox=0 --oy=20 --fx=-125)
render() {  # проект, имя, кадров, аргументы
  local proj="$1" name="$2" frames="$3"; shift 3
  (cd "$proj" && "$GODOT" --headless --path . --import >/dev/null 2>&1 || true
   xvfb-run -a -s "-screen 0 1400x1600x24" "$GODOT" --path . --rendering-driver opengl3 --resolution 820x760 \
     --write-movie "$TMP/$name.png" --fixed-fps 30 --quit-after "$frames" res://main.tscn -- "${VIEW[@]}" "$@" >/dev/null 2>&1)
}
label() { echo "drawtext=fontfile=$FONT:text='$1':x=14:y=10:fontsize=20:fontcolor=0x333333"; }
single() {  # имя, кадров, подпись, аргументы
  local name="$1" frames="$2" text="$3"; shift 3
  render "$HERE" "$name" "$frames" "$@"
  ffmpeg -y -loglevel error -framerate 30 -i "$TMP/$name%08d.png" -vf "$(label "$text")" -c:v libx264 -pix_fmt yuv420p -crf 21 "$OUT/$name.mp4"
}
pair() {  # имя, кадров, аргументы
  local name="$1" frames="$2"; shift 2
  render "$PREV" "a_$name" "$frames" "$@"
  render "$HERE" "b_$name" "$frames" "$@"
  ffmpeg -y -loglevel error -framerate 30 -i "$TMP/a_$name%08d.png" -framerate 30 -i "$TMP/b_$name%08d.png" -filter_complex \
    "[0]$(label 'v0.6'),pad=iw+4:ih:0:0:color=0x999999[a];[1]$(label 'v0.7 (по конспекту)')[b];[a][b]hstack=2" \
    -c:v libx264 -pix_fmt yuv420p -crf 21 "$OUT/$name.mp4"
}
pair 17_compare_v06_v07_forward 150 --mode=forward
pair 18_compare_v06_v07_forward_slow 174 --mode=forward --slow=0.25
single 19_v07_slow_cycle_no_bones 174 'v0.7 — один цикл ×0.25, без костей' --mode=forward --slow=0.25
single 20_v07_slow_cycle_bones 174 'v0.7 — тот же цикл с костями' --mode=forward --slow=0.25 --debug
rm -rf "$TMP"
