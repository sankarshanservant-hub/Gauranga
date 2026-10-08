"""Дописывает порцию в ru/NN.md и en/NN.md: python3 -I tools/append.py NN DIR
DIR содержит ru.md, ru-notes.md, en.md, en-notes.md (стихи — перед сносками, сноски — в конец)."""
import os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nn, d = sys.argv[1], sys.argv[2]
for lang in ('ru', 'en'):
    path = os.path.join(HERE, lang, nn + '.md')
    verses = open(os.path.join(d, lang + '.md'), encoding='utf-8').read().strip('\n')
    notes_p = os.path.join(d, lang + '-notes.md')
    notes = open(notes_p, encoding='utf-8').read().strip('\n') if os.path.exists(notes_p) else ''
    s = open(path, encoding='utf-8').read()
    i = s.find('\n[^1]:')
    if i < 0:
        body, fn = s.rstrip('\n'), ''
    else:
        body, fn = s[:i].rstrip('\n'), s[i:].strip('\n')
    out = body + '\n\n' + verses + '\n\n' + fn + ('\n' + notes if notes else '') + '\n'
    open(path, 'w', encoding='utf-8').write(out)
    nums = [l for l in out.splitlines() if l.startswith('**') and l[2:3].isdigit()]
    print(lang, 'стихов:', len(nums), 'последний:', nums[-1].split('**')[1] if nums else '-')
