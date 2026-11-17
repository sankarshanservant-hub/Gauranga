"""Вносит порцию «Гаура-чарита-чинтамани» из отдельного чата:
python3 -I tools/intake.py <папка книги> <папка с порцией> GCC-KK-FROM-TO
Дописывает ru/KK.md и en/KK.md; REPORT выносит в review/reports-KK.md; проверяет парность и уникальность сносок
и уникальность номеров строф (нумерация издания: допускаются пропуски и буквенные повторы K.Na)."""
import re, sys, os
root, inp, portion = sys.argv[1], sys.argv[2], sys.argv[3]
kk = portion.split('-')[1]
for kind in ('ru', 'en'):
    raw = open(f'{inp}/{portion}-{kind}.md', encoding='utf-8').read()
    rep = re.search(r'<!--\s*REPORT(.*?)-->', raw, re.S)
    new = re.sub(r'<!--\s*REPORT.*?-->', '', raw, flags=re.S).strip('\n') + '\n'
    path = f'{root}/{kind}/{kk}.md'
    exists = os.path.exists(path)
    cur = open(path, encoding='utf-8').read().rstrip('\n') + '\n' if exists else ''
    def split(t):
        m = re.search(r'(?m)^\[\^[^\]]+\]:', t)
        return (t[:m.start()], t[m.start():]) if m else (t, '')
    body, notes = split(cur)
    nb, nn = split(new)
    out = (body.rstrip('\n') + '\n\n' if body else '') + nb.strip('\n') + '\n\n' + (notes.rstrip('\n') + '\n' if notes else '') + nn.strip('\n') + '\n'
    labels = re.findall(r'(?m)^\[\^([^\]]+)\]:', out)
    refs = set(re.findall(r'\[\^([^\]]+)\](?!:)', out))
    dup = {l for l in labels if labels.count(l) > 1}
    assert not dup, (kind, dup)
    assert refs == set(labels), (kind, refs ^ set(labels))
    nums = [(int(a), b) for a, b in re.findall(r'(?m)^\*\*\d+\.(\d+)([a-z]?)\.\*\*', out)]
    assert len(set(nums)) == len(nums), (kind, 'duplicate numbers')   # издание местами нумерует заново — буквенные номера (2.14a)
    print(kind, kk, 'units', len(nums), 'notes', len(labels))
    if rep and kind == 'ru':
        rp = f'{root}/review/reports-{kk}.md'
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        head = '' if os.path.exists(rp) else f'# Кирана {int(kk)} — отчёты переводчика и приёмка\n'
        open(rp, 'a', encoding='utf-8').write(f'{head}\n## Порция {portion}\n\n{rep.group(1).strip()}\n')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(out)
