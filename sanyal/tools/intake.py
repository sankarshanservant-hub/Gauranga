"""Вносит фрагмент перевода Саньяла: python3 -I sanyal/tools/intake.py <папка с порцией> SN-<раздел>-NN
Сверяет номера абзацев [N] с фрагментом (sanyal/tools/split.py), снимает номера, дописывает sanyal/ru/<раздел>.md;
REPORT — в sanyal/review/reports-<раздел>.md."""
import os, re, sys, subprocess, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
inp, portion = sys.argv[1], sys.argv[2]
sec = re.match(r'SN-(.+)-\d\d$', portion).group(1)
with tempfile.TemporaryDirectory() as t:
    subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'sanyal/tools/split.py'), t], check=True, stdout=subprocess.DEVNULL)
    frag = open(os.path.join(t, portion + '.txt'), encoding='utf-8').read()
want = [int(x) for x in re.findall(r'(?m)^\[(\d+)\]', frag)]
raw = open(os.path.join(inp, portion + '-ru.md'), encoding='utf-8').read()
rep = re.search(r'<!--\s*REPORT(.*?)-->', raw, re.S)
body = re.sub(r'<!--.*?-->', '', raw, flags=re.S).strip()
got = []
for a, b in re.findall(r'(?m)^\[(\d+)(?:[–-](\d+))?\]', body):
    got += list(range(int(a), int(b or a) + 1))
assert got == want, (portion, 'абзацы', sorted(set(want) ^ set(got)), len(want), len(got))
for pat in (r'статуя|статуи|изваян|идол|вожделен|похот|страст',):
    for l in body.splitlines():
        if re.search(pat, l, re.I): print('СТОП-СЛОВО:', l[:150])
body = re.sub(r'(?m)^\[\d+(?:[–-]\d+)?\]\s*', '', body)
path = os.path.join(ROOT, 'sanyal/ru', sec + '.md')
os.makedirs(os.path.dirname(path), exist_ok=True)
cur = open(path, encoding='utf-8').read().rstrip('\n') + '\n\n' if os.path.exists(path) else ''
open(path, 'w', encoding='utf-8').write(cur + body + '\n')
if rep:
    rp = os.path.join(ROOT, 'sanyal/review', f'reports-{sec}.md')
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    head = '' if os.path.exists(rp) else f'# Саньял, «Sree Krishna Chaitanya», {sec} — отчёты переводчика\n'
    open(rp, 'a', encoding='utf-8').write(f'{head}\n## {portion}\n\n{rep.group(1).strip()}\n')
print(portion, 'абзацев', len(want), '→', path)
