# Английские комментарии (purports) Бхактиведанты Свами со страниц vedabase -> один текстовый файл (только для
# сравнительного анализа; в репозиторий не коммитится). Использование: python3 tools/vb_purports.py <папка html> <выход.txt>
import sys, os, re, html, glob
d, out = sys.argv[1], sys.argv[2]
def key(f): return [int(x) for x in re.findall(r'\d+', os.path.basename(f))[1:]] or [0]
res, miss = [], []
for f in sorted(glob.glob(os.path.join(d, '*.html')), key=key):
    s = open(f, encoding='utf-8').read()
    i = s.find('class="av-purport"')
    v = '-'.join(map(str, key(f)))
    if i < 0: miss.append(v); continue
    j = s.find('class="av-', i + 10); seg = s[i:j if j > 0 else len(s)]
    paras = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<div class="em-mb-4[^"]*">(.*?)</div>', seg, re.S)]
    res.append('## %s\n\n%s\n' % (v, '\n\n'.join(p for p in paras if p)))
open(out, 'w', encoding='utf-8').write('\n'.join(res))
print('с комментарием: %d; без: %s' % (len(res), ' '.join(miss)))
