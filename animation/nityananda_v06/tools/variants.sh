#!/usr/bin/env bash
# Три варианта длины шага рядом (A — как v0.4, B — +25 %, C — +40 %), обычная скорость.
# Использование: tools/variants.sh <godot> <папка вывода>
set -euo pipefail
GODOT="$1"; OUT="$(mkdir -p "$2" && cd "$2" && pwd)"; cd "$(dirname "$0")/.."
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
TMP="$(mktemp -d)"
"$GODOT" --headless --path . --import >/dev/null 2>&1 || true
declare -A LBL=([A]="A  как v0.4 — шаг 117 px, 100 шагов/мин" [B]="B  шаг ×1,25 — 146 px, 89 шагов/мин" [C]="C  шаг ×1,4 — 163 px, 83 шага/мин")
row() {  # имя, кадров, разрешение, аргументы сцены
  local name="$1" frames="$2" res="$3"; shift 3
  local inputs=() filt="" i=0
  for v in A B C; do
    xvfb-run -a -s "-screen 0 1400x1600x24" "$GODOT" --path . --rendering-driver opengl3 --resolution "$res" \
      --write-movie "$TMP/${name}_$v.png" --fixed-fps 30 --quit-after "$frames" res://main.tscn -- \
      --variant=$v --nohud "$@" >/dev/null 2>&1
    inputs+=(-framerate 30 -i "$TMP/${name}_$v%08d.png")
    filt+="[$i]drawtext=fontfile=$FONT:text='${LBL[$v]}':x=12:y=10:fontsize=17:fontcolor=0x333333,pad=iw+4:ih:0:0:color=0x999999[v$i];"
    i=$((i+1))
  done
  ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "${filt}[v0][v1][v2]hstack=3" \
    -c:v libx264 -pix_fmt yuv420p -crf 22 "$OUT/$name.mp4"
}
# продвижение, линия земли и следы опоры (4 с, без возврата к началу экрана)
row 10_variants_forward_ground 120 620x660 --mode=forward --ground --cycles=99 --scale=0.42 --ox=0 --oy=26 --fx=-100
# то же с разметкой: ткань (жёлтый — близко к порогу, красный/синий — сверх порога) и дорисовки (пурпурный)
row 11_variants_forward_problems 120 620x660 --mode=forward --ground --stretch --synth --cycles=99 --scale=0.42 --ox=0 --oy=26 --fx=-100
# на месте, крупнее
row 12_variants_in_place 90 520x900 --mode=in_place --ground --scale=0.56 --ox=60 --oy=68
rm -rf "$TMP"
