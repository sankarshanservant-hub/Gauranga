"""Вносит порцию: python3 -I tools/intake.py <папка книги> <папка с порцией> PFX-FROM-TO
Дописывает ru/PFX.md и en/PFX.md; REPORT (из ru) — в review/reports-PFX.md; проверяет сноски и нумерацию **N.** (подряд с 1)."""
import re, sys, os
root, inp, portion = sys.argv[1], sys.argv[2], sys.argv[3]
pfx, a, b = portion.split('-')
def split(t):
    m = re.search(r'(?m)^\[\^[^\]]+\]:', t)
    return (t[:m.start()], t[m.start():]) if m else (t, '')
for kind in ('ru', 'en'):
    raw = open(f'{inp}/{portion}-{kind}.md', encoding='utf-8').read()
    rep = re.search(r'<!--\s*REPORT(.*?)-->', raw, re.S)
    new = re.sub(r'<!--.*?-->', '', raw, flags=re.S).strip('\n') + '\n'
    path = f'{root}/{kind}/{pfx}.md'
    exists = os.path.exists(path)
    cur = open(path, encoding='utf-8').read().rstrip('\n') + '\n' if exists else ''
    body, notes = split(cur); nb, nn = split(new)
    out = (body.rstrip('\n') + '\n\n' if body else '') + nb.strip('\n') + '\n\n' + (notes.rstrip('\n') + '\n' if notes else '') + nn.strip('\n') + '\n'
    labels = re.findall(r'(?m)^\[\^([^\]]+)\]:', out)
    refs = set(re.findall(r'(?<!^)\[\^([^\]]+)\]', out, re.M))
    dup = {l for l in labels if labels.count(l) > 1}
    assert not dup, (kind, dup)
    assert refs == set(labels), (kind, sorted(refs ^ set(labels))[:5])
    nums = [int(x) for x in re.findall(r'(?m)^\*\*(\d+)\.\*\*', out)]
    assert nums == list(range(1, len(nums) + 1)) and nums[-1] == int(b), (kind, 'numbering')
    for l in out.splitlines():
        if re.search(r'статуя|изваян|идол|вожделен|похот|\bстраст|statue|\bidol|\blust\b|passion', l, re.I): print('СТОП:', kind, l[:120])
    print(kind, pfx, 'units', len(nums))
    if rep and kind == 'ru':
        rp = f'{root}/review/reports-{pfx}.md'; os.makedirs(os.path.dirname(rp), exist_ok=True)
        head = '' if os.path.exists(rp) else f'# {pfx} — отчёты переводчика\n'
        open(rp, 'a', encoding='utf-8').write(f'{head}\n## Порция {portion}\n\n{rep.group(1).strip()}\n')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(out)
