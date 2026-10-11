#!/bin/bash
# Подготовка главы координатором (проход 0): vedabase → md из ВЧД → OCR страниц → второй OCR (CCBSST) → флаги
# бенгальского → материалы комментариев (вырезки колонок + OCR) → ed/bn/<Гл>-ocr.md.
# Запуск: bash tools/coord/prep_chapter.sh Adi16 268 290      (страницы — из locate.sh, включая стыковые)
# Несколько коротких глав: запускать по очереди для каждой; материалы комментариев у каждой — в $W/comm/<Гл>.
set -e
. "$(dirname "$0")/env.sh"
C=$1; P1=$2; P2=$3
L=$(echo $C | sed 's/[0-9]*$//'); N=$(echo $C | sed 's/^[A-Za-z]*//'); n=$((10#$N))
l=$(echo $L | tr A-Z a-z)
cd "$CC"
echo "== $C ($l $n), скан с. $P1–$P2"
# 1. vedabase (только текст стихов и перевод — для сверки чтений; авторитет — издание ГМ)
VB="$W/vb/$C"; mkdir -p "$VB"
curl -sS --retry 3 -o "$W/vb/$C.idx.html" "https://vedabase.io/en/library/cc/$l/$n/"
grep -o "href=\"/en/library/cc/$l/$n/[0-9-]*/\"" "$W/vb/$C.idx.html" | sed "s/.*\/$n\/\([0-9-]*\)\/\"/\1/" | sort -u > "$W/vb/$C.list"
(cd "$VB"; cat "$W/vb/$C.list" | xargs -P 6 -I{} sh -c "[ -s {}.html ] || curl -sS --retry 3 -o {}.html https://vedabase.io/en/library/cc/$l/$n/{}/")
echo "vedabase: $(ls $VB | wc -l) страниц; группы и пропуски:"; python3 tools/extract.py "$VB" ed/work/vb-$C.json | cut -c1-120
# 2. md из ВЧД (vcd/txt/CC_<Гл>.txt) + автоправки + сверка с vedabase
python3 tools/prep_vcd.py $C 2>&1 | grep -v '^  ~' | tail -4
python3 tools/check_ed.py $C | head -1; echo "  «нет пословного»: $(python3 tools/check_ed.py $C | grep -c 'нет пословного')"
python3 - "$C" <<'PY'
import re,sys
d='০১২৩৪৫৬৭৮৯'; t=open('vcd/txt/CC_%s.txt'%sys.argv[1],encoding='utf-8').read()
nums=[int(''.join(str(d.index(c)) for c in m)) for m in re.findall(r'॥ *([০-৯]+) *॥',t)]
prev=0; j=[]
for x in nums:
    if x!=prev+1: j.append('%d→%d'%(prev,x))
    prev=x
print('  нумерация ВЧД (vcd/txt): последний ॥%d॥; скачки: %s'%(nums[-1] if nums else 0, ', '.join(j) or 'нет'))
PY
# 3. OCR страниц (если locate.sh ещё не сделал)
seq $P1 $P2 | xargs -P 4 -I{} sh tools/coord/ocr_page.sh {}
# 4. второй OCR: CCBSST на archive.org (поглавно; иногда отдаёт 500 — повтор)
case $L in Adi) IT=CCBSSTAdi01;; Madhya) IT=CCBSSTMadhya;; Antya) IT=CCBSSTAntya;; esac
mkdir -p "$W/bsst"; DJ="$W/bsst/$C.txt"
for i in 1 2 3 4 5; do [ -s "$DJ" ] && [ $(wc -c < "$DJ") -gt 10000 ] && break
  curl -sSL -o "$DJ" "https://archive.org/download/$IT/CC-BSST-$L-$(printf %02d $n)_djvu.txt" || true; sleep $((2**i)); done
echo "CCBSST djvu: $(wc -c < "$DJ") байт"
# 5. флаги бенгальского (листы вырезок — $SCAN/sheets/<Гл>-K.png) и порядок стихов
python3 tools/bn_flags.py $C "$SCAN" $P1 $P2 "$DJ" 2>&1 | tail -2
# 6. материалы комментариев и черновой OCR по колонкам
python3 tools/comm_pages.py $C "$SCAN" $P1 $P2 "$W/comm/$C" | tail -1
{ echo "# ${L} $n: черновой OCR скана CC_SS.pdf (изд. 1928), с. $P1–$P2, по колонкам (первая и последняя страницы — также соседние главы). Не выверен."; echo
  for p in $(seq $P1 $P2); do cat "$W/comm/$C/p$p.txt"; echo; done; } > ed/bn/$C-ocr.md
echo "последние номера стихов на последних страницах скана:"
for p in $((P2-1)) $P2; do echo "  $p: $(grep -o '॥ *[০-৯]\+ *॥' $SCAN/o$p.txt | tr -d ' ' | tr '\n' ' ')"; done
echo "готово. Материалы: листы $SCAN/sheets/$C-*.png, комментарии $W/comm/$C/, ed/work/bnflags-$C.txt, ed/work/order-$C.txt"
