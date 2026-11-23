"""Поиск бытовых реалий в наших переводах житий (ЧЧ — пер. Вриндавана Чандры даса, ЧБ — изд. Шри Чайтанья
Сарасват Матха). Печатает ссылку на стих и отрывок перевода.
  python3 material-culture/tools/hgrep.py 'кухн|очаг' [--cc --cb --lo --mu --ka] [--only 'Adi1[34]'] [-w 300]
(--lo — Лочан Дас, --mu — Мурари Гупта, --ka — Карнапура «Махакавья»; --only — регэксп по главе/разделу)
"""
import re, sys, glob, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
KH = {'Adi': 'Ади', 'Madhya': 'Мадхья', 'Antya': 'Антья'}


def cc():
    for f in sorted(glob.glob(f'{ROOT}/chaitanya-charitamrita/ed/vcd/CC_*.md')):
        m = re.search(r'CC_(Adi|Madhya|Antya)(\d+)', f)
        if not m: continue
        for line in open(f, encoding='utf-8'):
            v = re.match(r'\((\d+(?:[–-]\d+)?)\)\s+(.*)', line)
            if v: yield f'ЧЧ {KH[m[1]]} {int(m[2])}.{v[1]}', m[1] + m[2], v[2], f


def cb():
    for f in sorted(glob.glob(f'{ROOT}/chaitanya-bhagavata/ed/CB_*.md')):
        m = re.search(r'CB_(Adi|Madhya|Antya)(\d+)', f)
        if not m: continue
        for line in open(f, encoding='utf-8'):
            v = re.match(r'\*\*(\d+(?:[–-]\d+)?)\.\*\*\s+(.*)', line)
            if v: yield f'ЧБ {KH[m[1]]} {int(m[2])}.{v[1]}', m[1] + m[2], v[2], f


def md(path, tag, head_re):
    """Переводы в md-книгах: строки '**N.** текст' (+ продолжение до пустой строки); раздел — по заголовкам."""
    f = f'{ROOT}/{path}'
    sec, buf, num = '', [], None
    def flush():
        if num: return (f'{tag} {sec} {num}', sec, ' '.join(buf), f)
    for line in open(f, encoding='utf-8'):
        h = re.match(head_re, line)
        if h:
            r = flush(); num = None
            if r: yield r
            sec = h[1]; continue
        v = re.match(r'\*\*(\d+(?:[–-]\d+)?)\.\*\*\s+(.*)', line)
        if v:
            r = flush()
            if r: yield r
            num, buf = v[1], [v[2].strip()]
        elif num and line.strip() and not line.startswith(('*', '[^', '#', '>')):
            buf.append(line.strip())
        elif num and not line.strip():
            r = flush(); num = None
            if r: yield r
    r = flush()
    if r: yield r


def lochana():
    yield from md('lochana/Lochana-Chaitanya-Mangala-ru-full.md', 'Лочан', r'^# (.+?)(?:\s*\(порция.*)?$')


def murari():
    yield from md('murari-gupta/Murari-Gupta-Kadacha-ru-full.md', 'Мурари', r'^## Пракрама (\d+, сарга \d+)')


def karna():
    yield from md('karnapura-mahakavya/Mahakavya-ru-full.md', 'Карнапура', r'^## (Сарга \S+)')


def main():
    a = sys.argv[1:]
    pat = re.compile(a[0], re.I)
    w = int(a[a.index('-w') + 1]) if '-w' in a else 220
    only = a[a.index('--only') + 1] if '--only' in a else None
    al = {'--cc': cc, '--cb': cb, '--lo': lochana, '--mu': murari, '--ka': karna}
    srcs = [fn for k, fn in al.items() if k in a] or list(al.values())
    n = 0
    for s in srcs:
        for ref, ch, t, f in s():
            if only and not re.search(only, ch): continue
            mm = pat.search(t)
            if not mm: continue
            i = max(0, mm.start() - w // 2)
            print(f'{ref}: …{t[i:i + w]}…')
            n += 1
    print(f'— {n}', file=sys.stderr)


main()
