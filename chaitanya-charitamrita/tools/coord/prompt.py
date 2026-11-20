#!/usr/bin/env python3
# Собрать задание исполнителю из шаблона prompts/*.md: python3 tools/coord/prompt.py prompts/X.md KEY=VAL …
# Общие подстановки: CC, W, BRANCH, TRAILER (из $COMMIT_TRAILER), COMMON (prompts/_common.md); CH_LIST по умолчанию = CH.
import os, re, sys, subprocess
CC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
tpl = open(sys.argv[1] if os.path.isabs(sys.argv[1]) else os.path.join(CC, sys.argv[1]), encoding='utf-8').read()
v = dict(a.split('=', 1) for a in sys.argv[2:])
v.setdefault('CC', CC)
_kit = os.path.join(CC, '..', '..', 'cc-work')
v.setdefault('W', os.environ.get('CC_WORK') or (os.path.abspath(_kit) if os.path.isdir(_kit) else '/tmp/cc-work'))
v.setdefault('BRANCH', subprocess.run(['git', '-C', CC, 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True).stdout.strip())
tf = os.path.join(v['W'], 'trailer.txt')
v.setdefault('TRAILER', os.environ.get('COMMIT_TRAILER', '').strip() or (open(tf, encoding='utf-8').read().strip() if os.path.exists(tf) else '') or '(строки атрибуции сессии)')
if 'CH' in v: v.setdefault('CH_LIST', v['CH']); v.setdefault('COMM', v['CH']); v.setdefault('GLOSS', v['CH'])
v.setdefault('EXTRA', '')
v['COMMON'] = open(os.path.join(CC, 'prompts', '_common.md'), encoding='utf-8').read().strip()
for _ in range(2):
    tpl = re.sub(r'\{\{(\w+)\}\}', lambda m: v[m.group(1)] if m.group(1) in v else m.group(0), tpl)
left = sorted(set(re.findall(r'\{\{(\w+)\}\}', tpl)))
if left: sys.exit('не заполнено: ' + ', '.join(left))
print(re.sub(r'\n{3,}', '\n\n', tpl).strip())
