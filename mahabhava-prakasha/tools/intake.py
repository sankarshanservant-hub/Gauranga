"""Вносит порцию из отдельного чата: python3 -I tools/intake.py <папка книги> <папка с порцией> MP-CC-FROM-TO
Дописывает src/full/ru/en главы CC; проверяет нумерацию, уникальность и парность сносок."""
import re, sys, os
root, inp, portion = sys.argv[1], sys.argv[2], sys.argv[3]   # порция, напр. MP-01-1-40
kinds = sys.argv[4].split(',') if len(sys.argv) > 4 else ['src', 'full', 'ru', 'en']   # напр. en — только перевод
cc = portion.split('-')[1]
for kind in kinds:
    new = open(f'{inp}/{portion}-{kind}.md', encoding='utf-8').read()
    new = re.sub(r'<!--\s*REPORT.*?-->', '', new, flags=re.S).strip('\n') + '\n'
    path = f'{root}/{kind}/{cc}.md'
    exists = os.path.exists(path)
    cur = open(path, encoding='utf-8').read().rstrip('\n') + '\n' if exists else ''
    if kind in ('src', 'full'):
        if exists:
            new = new[new.index('## Лист'):]
        out = cur + ('\n' if exists else '') + new
    else:
        new = re.sub(r'`MP-\d\d-\d+-\d+-full\.md`', f'`full/{cc}.md`', new)
        def split(t):
            m = re.search(r'(?m)^\[\^[^\]]+\]:', t)
            return (t[:m.start()], t[m.start():]) if m else (t, '')
        body, notes = split(cur)
        nb, nn = split(new)
        if exists:
            nb = '\n'.join(l for l in nb.split('\n') if not l.startswith('# ') and not re.match(r'^\*(Перевод с ория|Translat)', l))
        else:
            nb = re.sub(r'(?m)^(# .*?), гл(ава|\.) (\d+) \(ст\. [^)]*\)', r'\1, глава \3', nb)
            nb = re.sub(r'(?m)^(# .*?), Chapter (\d+) \(vv\. [^)]*\)', r'\1, Chapter \2', nb)
        out = (body.rstrip('\n') + '\n\n' if body else '') + nb.strip('\n') + '\n\n' + (notes.rstrip('\n') + '\n' if notes else '') + nn.strip('\n') + '\n'
        labels = re.findall(r'(?m)^\[\^([^\]]+)\]:', out)
        refs = set(re.findall(r'\[\^([^\]]+)\](?!:)', out))
        dup = {l for l in labels if labels.count(l) > 1}
        assert not dup, (kind, dup)
        assert refs == set(labels), (kind, refs ^ set(labels))
        nums = re.findall(r'(?m)^\*\*\d+\.(\d+)\.\*\*', out)
        assert [int(x) for x in nums] == list(range(1, len(nums) + 1)), (kind, 'numbering')
        print(kind, cc, 'units', len(nums), 'notes', len(labels))
    open(path, 'w', encoding='utf-8').write(out)
