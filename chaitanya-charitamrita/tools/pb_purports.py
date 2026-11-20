# Комментарии Бхактиведанты Свами по ПЕРВОМУ изданию (BBT 1974; prabhupadabooks.com) — для сравнительного анализа.
# Текст в репозиторий не коммитится. Использование: python3 tools/pb_purports.py <Глава: Adi01> <выход.txt>
import sys, os, re, json, html, subprocess, time
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
chap, out = sys.argv[1], sys.argv[2]
lila, nn = re.match(r'([A-Za-z]+)(\d+)', chap).groups()
rows = json.load(open(os.path.join(ROOT, 'ed', 'work', 'rows-%s.json' % chap), encoding='utf-8'))
res, nop = [], []
for r in rows:
    lab = r['lab'].replace('–', '-')
    url = 'https://prabhupadabooks.com/cc/%s/%d/%s' % (lila.lower(), int(nn), lab)
    s = ''
    for k in range(3):
        s = subprocess.run(['curl', '-sS', '-f', url], capture_output=True, text=True).stdout
        if s: break
        time.sleep(2)
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)); t = re.sub(r'[ \t\r\f\v]+', ' ', t)
    i = t.find('PURPORT')
    if i < 0: nop.append(lab); continue
    body = t[i + 7:]
    for end in ('Link to this page', 'Previous Next', '<< Previous', 'Text copyright'):
        j = body.find(end)
        if j > 0: body = body[:j]
    body = re.sub(r'\s*\n\s*', ' ', body).strip()
    res.append('## %s\n\n%s\n' % (lab, body))
open(out, 'w', encoding='utf-8').write('\n'.join(res))
print('%s: с комментарием %d, без %d' % (chap, len(res), len(nop)))
