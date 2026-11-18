"""Выверка «Расика-мангалы»: python3 -I tools/check.py <папка книги>
RU/EN — одни номера и метки сносок; ссылки = определения; стоп-слова; служебные ссылки в тексте."""
import re, sys, os, glob, collections
root = sys.argv[1]
STOP_RU = r'статуя|статуи|изваян|идол|вожделен|похот|страст'
STOP_EN = r'\bstatue|\bidol\b|\blust\b|\bpassion'
problems = collections.Counter()
for ru in sorted(glob.glob(f'{root}/ru/*.md')):
    k = os.path.basename(ru)[:-3]; en = f'{root}/en/{k}.md'
    R, E = open(ru).read(), open(en).read()
    for name, T in (('ru', R), ('en', E)):
        lab = re.findall(r'(?m)^\[\^([^\]]+)\]:', T); refs = set(re.findall(r'\[\^([^\]]+)\](?!:)', T))
        if len(lab) != len(set(lab)): print(k, name, 'дубли меток'); problems['dup'] += 1
        if refs != set(lab): print(k, name, 'ссылки≠определения', sorted(refs ^ set(lab))[:5]); problems['refs'] += 1
        body = T[:m.start()] if (m := re.search(r'(?m)^\[\^', T)) else T
        for l in body.splitlines():
            if re.search(r'\bRM-\d|pdf \d|OCR|\.md\b', l): print(k, name, 'служебное в тексте:', l[:120]); problems['svc'] += 1
    nr = re.findall(r'(?m)^\*\*(S?\d+)\.\*\*', R); ne = re.findall(r'(?m)^\*\*(S?\d+)\.\*\*', E)
    if nr != ne: print(k, 'номера RU≠EN', len(nr), len(ne)); problems['num'] += 1
    lr = re.findall(r'(?m)^\[\^([^\]]+)\]:', R); le = re.findall(r'(?m)^\[\^([^\]]+)\]:', E)
    if lr != le: print(k, 'сноски RU≠EN', len(lr), len(le)); problems['notes'] += 1
    # ссылки на сноски в одних и тех же двустишиях
    def where(T): return {lab: n for n, blk in re.findall(r'(?ms)^\*\*(S?\d+)\.\*\*(.*?)(?=^\*\*S?\d+\.\*\*|^\[\^|\Z)', T) for lab in re.findall(r'\[\^([^\]]+)\]', blk)}
    wr, we = where(R), where(E)
    diff = [l for l in wr if l in we and wr[l] != we[l]]
    if diff: print(k, 'сноски в разных двустишиях RU/EN:', [(l, wr[l], we[l]) for l in diff][:4]); problems['place'] += 1
    for name, T, pat in (('ru', R, STOP_RU), ('en', E, STOP_EN)):
        for l in T.splitlines():
            if re.search(pat, l, re.I): print(k, name, 'стоп-слово:', re.search(f'.{{0,60}}({pat}).{{0,40}}', l, re.I).group(0)); problems['stop'] += 1
print('ИТОГО', dict(problems))
