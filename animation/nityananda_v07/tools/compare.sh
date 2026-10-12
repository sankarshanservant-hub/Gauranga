#!/usr/bin/env bash
# Сравнительные ролики v0.3 и v0.4 (без костей и подписей). Использование: tools/compare.sh <godot> <папка вывода>
set -euo pipefail
GODOT="$1"; OUT="$(cd "$2" && pwd)"; HERE="$(cd "$(dirname "$0")/.." && pwd)"; PREV="$HERE/../nityananda_v03"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
TMP="$(mktemp -d)"
render() {  # проект, имя, кадров, аргументы
  local proj="$1" name="$2" frames="$3"; shift 3
  (cd "$proj" && "$GODOT" --headless --path . --import >/dev/null 2>&1 || true
   xvfb-run -a -s "-screen 0 1400x1600x24" "$GODOT" --path . --rendering-driver opengl3 --resolution 1280x900 \
     --write-movie "$TMP/$name.png" --fixed-fps 30 --quit-after "$frames" res://main.tscn -- --nohud "$@" >/dev/null 2>&1)
}
pair() {  # имя, кадров, crop, аргументы
  local name="$1" frames="$2" crop="$3"; shift 3
  render "$PREV" "a_$name" "$frames" "$@"
  render "$HERE" "b_$name" "$frames" "$@"
  ffmpeg -y -loglevel error -framerate 30 -i "$TMP/a_$name%08d.png" -framerate 30 -i "$TMP/b_$name%08d.png" -filter_complex \
    "[0]crop=$crop,drawtext=fontfile=$FONT:text='v0.3':x=20:y=20:fontsize=28:fontcolor=0x333333[a];[1]crop=$crop,drawtext=fontfile=$FONT:text='v0.4':x=20:y=20:fontsize=28:fontcolor=0x333333[b];[a][b]hstack=2" \
    -c:v libx264 -pix_fmt yuv420p -crf 23 "$OUT/$name.mp4"
}
pair 07_compare_v03_v04_in_place_normal 72 520:900:380:0 --mode=in_place
pair 08_compare_v03_v04_in_place_slow 144 520:900:380:0 --mode=in_place --slow=0.25
pair 09_compare_v03_v04_forward_normal 144 760:900:0:0 --mode=forward
rm -rf "$TMP"
