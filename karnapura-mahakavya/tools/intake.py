"""Вносит порцию английского перевода «Махакавьи»: python3 -I tools/intake.py <папка книги> <папка с порцией> MK-SS-FROM-TO
Дописывает en/SS.md; REPORT — в review/reports-en-SS.md. Проверяет: стихи FROM..TO подряд, деванагари и IAST — как в ru/SS.md,
у каждого стиха есть Word for word и Translation."""
import re, sys, os
root, inp, portion = sys.argv[1], sys.argv[2], sys.argv[3]
_, ss, a, b = portion.split('-'); a, b = int(a), int(b)
raw = open(f'{inp}/{portion}-en.md', encoding='utf-8').read()
rep = re.search(r'<!--\s*REPORT(.*?)-->', raw, re.S)
new = re.sub(r'<!--\s*REPORT.*?-->', '', raw, flags=re.S).strip('\n') + '\n'
def verses(t):
    parts = re.split(r'(?m)^### (\d+(?:[–-]\d+)?)\s*$', t)
    return parts[0], {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}, [parts[i] for i in range(1, len(parts), 2)]
first = lambda lab: int(re.match(r'\d+', lab).group(0))
last = lambda lab: int(re.findall(r'\d+', lab)[-1])
def skt(blk):
    dev = re.search(r'```\n(.*?)\n```', blk, re.S)
    iast = re.search(r'```\n\*(.*?)\*\n', blk + '\n', re.S)
    return (dev.group(1).strip() if dev else None, iast.group(1).strip() if iast else None)
head, ev, order = verses(new)
_, rv, rorder = verses(open(f'{root}/ru/{ss}.md', encoding='utf-8').read())
want = [l for l in rorder if a <= first(l) <= b]
assert order == want and last(want[-1]) == b, ('номера', order[:3], order[-3:], want[:3], want[-3:])
bad = []
for n in order:
    e, r = skt(ev[n]), skt(rv[n])
    if e != r: bad.append(n)
    for lab in ('**Word for word', '**Translation'):
        if lab not in ev[n]: bad.append((n, lab))
assert not bad, ('санскрит/разделы не совпадают', bad[:10])
for m in re.finditer(r'(?i).{0,50}\b(idol|statue|lust|death)\b.{0,40}', new):
    print('стоп-слово:', m.group(0).replace('\n', ' '))
path = f'{root}/en/{ss}.md'
cur = open(path, encoding='utf-8').read().rstrip('\n') + '\n\n' if os.path.exists(path) else ''
if cur:
    _, cv, corder = verses(cur)
    assert corder and last(corder[-1]) == a - 1, ('стык', corder[-1:] , a)
else:
    assert a == 1 and head.strip().startswith('# '), 'первая порция сарги — с шапкой'
open(path, 'w', encoding='utf-8').write(cur + (new if not cur else new.lstrip('\n')))
if rep:
    rp = f'{root}/review/reports-en-{ss}.md'
    h = '' if os.path.exists(rp) else f'# «Махакавья», сарга {int(ss)} — отчёты переводчика EN\n'
    open(rp, 'a', encoding='utf-8').write(f'{h}\n## Порция {portion}\n\n{rep.group(1).strip()}\n')
print(portion, 'ok', len(order), 'стихов; ru в сарге:', len(rorder))
