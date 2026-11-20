#!/bin/bash
# Итоговая сборка глав: md из ВЧД + правки, проверки, EN-стихи, размещение комментариев, PDF (RU/EN, полное и
# только перевод, A5). Запуск: bash tools/coord/finish.sh Adi16 [Adi17 …]
. "$(dirname "$0")/env.sh"
cd "$CC"
for c in "$@"; do
  python3 tools/prep_vcd.py $c 2>&1 | grep -i 'не примен\|^  ! '
  python3 tools/check_ed.py $c | head -3
  python3 tools/build_en.py $c | tail -1
  for l in ru en; do for e in full text; do python3 tools/md2pdf.py $c $e a5 $l >/dev/null || echo "!! PDF $c $l $e"; done; done
done
python3 tools/coord/placement.py "$@"
python3 ../lila-db/build.py -w 2>&1 | tail -1; git -C "$REPO" checkout -- lila-db/TIMELINE.md lila-db/EVENTS.md lila-db/export
ls -la ed/pdf/ | grep -E "$(echo "$@" | tr ' ' '|')" | awk '{print $5, $9}'
