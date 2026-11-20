"""Вносит порцию «Расика-мангалы»: python3 -I tools/intake.py <папка книги> <папка с порцией> JCV-VV-FROM-TO
Дописывает ru/VV.md и en/VV.md; REPORT (из ru) — в review/reports-VV.md; проверяет сноски и нумерацию **N.**."""
import re, sys, os
root, inp, portion = sys.argv[1], sys.argv[2], sys.argv[3]
_, ll, a, b = portion.split("-"); v = None
def split(t):
    m = re.search(r'(?m)^\[\^[^\]]+\]:', t)
    return (t[:m.start()], t[m.start():]) if m else (t, '')
for kind in ('ru', 'en'):
    raw = open(f'{inp}/{portion}-{kind}.md', encoding='utf-8').read()
    rep = re.search(r'<!--\s*REPORT(.*?)-->', raw, re.S)
    new = re.sub(r'<!--\s*REPORT.*?-->', '', raw, flags=re.S).strip('\n') + '\n'
    path = f'{root}/{kind}/{ll}.md'
    exists = os.path.exists(path)
    cur = open(path, encoding='utf-8').read().rstrip('\n') + '\n' if exists else ''
    body, notes = split(cur); nb, nn = split(new)
    out = (body.rstrip('\n') + '\n\n' if body else '') + nb.strip('\n') + '\n\n' + (notes.rstrip('\n') + '\n' if notes else '') + nn.strip('\n') + '\n'
    labels = re.findall(r'(?m)^\[\^([^\]]+)\]:', out)
    refs = set(re.findall(r'(?<!^)\[\^([^\]]+)\]', out, re.M))
    dup = {l for l in labels if labels.count(l) > 1}
    assert not dup, (kind, dup)
    assert refs == set(labels), (kind, refs ^ set(labels))
    nums = [int(x) for x in re.findall(r'(?m)^\*\*(\d+)\.\*\*', out)]
    assert nums == list(range(1, len(nums) + 1)) and nums[-1] == int(b), (kind, 'numbering')
    print(kind, ll, 'units', len(nums))
    if rep and kind == 'ru':
        rp = f'{root}/review/reports-{ll}.md'
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        head = '' if os.path.exists(rp) else f'# «Джагадиша-чаритра-виджая», варна {ll} — отчёты переводчика\n'
        open(rp, 'a', encoding='utf-8').write(f'{head}\n## Порция {portion}\n\n{rep.group(1).strip()}\n')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(out)
