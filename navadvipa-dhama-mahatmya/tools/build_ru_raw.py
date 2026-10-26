"""Raw Russian text (SCSM 2001) by chapters: paragraphs, de-hyphenated. Output ru_raw/NN.md (no verse labels yet)."""
import json, re, sys, collections, os
L = [json.loads(l) for l in open(sys.argv[1])]
OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
H = '(cid:7)'
def body(d): return d['f'] == 'JournalC' and d['s'] == 11.5
def foot(d): return d['f'] == 'JournalC' and d['s'] == 10.0 and not re.fullmatch(r'\s*\d+\s*', d['t'])
vocab = collections.Counter()
for d in L:
    if body(d):
        for w in re.findall(r'[\w-]+', d['t'].replace(H, '-').rstrip('-')): vocab[w.lower()] += 1
KEEP2 = {'то', 'нибудь', 'либо', 'ка', 'таки', 'де'}
def join(lines):
    out = ''
    for t in lines:
        t = re.sub(r'\s+', ' ', t).strip()
        if not out: out = t; continue
        if out.endswith(H):
            out = out[:-len(H)]
            w1 = re.search(r'[\w]+$', out); w2 = re.match(r'[\w]+', t)
            w1 = w1.group(0) if w1 else ''; w2 = w2.group(0) if w2 else ''
            hy, jn = f'{w1}-{w2}'.lower(), f'{w1}{w2}'.lower()
            if w2.lower() in KEEP2 or w1.lower() in ('кое', 'полу') or (w2[:1].isupper() and w1[:1].isupper()) \
               or (vocab[hy] > vocab[jn]): out += '-' + t
            else: out += t
        else: out += ' ' + t
    return out.replace(H, '-').replace(' - ', ' — ')
def margin(p):
    xs = [d['x'] for d in L if d['p'] == p and body(d)]
    return collections.Counter(xs).most_common(1)[0][0] if xs else 44
# chapter start pages (RU) and titles
CH = [(17, 'Высочайшее положение'), (25, 'Истинная природа и размеры Навадвипы'), (31, 'Паломничество в святую дхаму'),
      (35, 'Встреча'), (43, 'Антардвипа'), (55, 'Симантадвипа'), (65, 'Годрумадвипа (часть первая)'),
      (73, 'Годрумадвипа (часть вторая)'), (81, 'Мадхьядвипа (часть первая)'), (85, 'Мадхьядвипа (часть вторая)'),
      (91, 'Коладвипа'), (103, 'Ритудвипа'), (107, 'Ритудвипа и Джахнудвипа'), (113, 'Модадрумадвипа (часть первая)'),
      (117, 'Модадрумадвипа и Рудрадвипа'), (127, 'Рудрадвипа'), (133, 'Священные вопросы и ответы'),
      (137, 'Путешествие во Вриндавану'), (147, 'Навадвипа-бхава-таранга. Святая дхама'), (168, None)]
def sect(p0, p1):
    paras, notes, M = [], [], {}
    for d in L:
        if not (p0 <= d['p'] <= p1): continue
        if foot(d):
            if d['t'].startswith('*') or not notes: notes.append([d['t']])
            else: notes[-1].append(d['t'])
            continue
        if not body(d): continue
        if d['p'] not in M: M[d['p']] = margin(d['p'])
        if not paras or d['x'] - M[d['p']] >= 8: paras.append([d['t']])
        else: paras[-1].append(d['t'])
    return [join(p) for p in paras], [join(n) for n in notes]
for i, (p0, title) in enumerate(CH[:-1]):
    paras, notes = sect(p0, CH[i + 1][0] - 1)
    n = i + 1
    txt = f'# Глава {n}. {title}\n\n' if n < 19 else f'# {title}\n\n'
    txt += '\n\n'.join(paras) + '\n'
    if notes: txt += '\n' + '\n\n'.join('[^*]: ' + x for x in notes) + '\n'
    open(f'{OUT}/{n:02d}.md', 'w').write(txt)
    print(n, len(paras), 'paras', len(notes), 'notes', sum(len(p) for p in paras), 'chars')
paras, notes = sect(3, 14)
open(f'{OUT}/00-biography.md', 'w').write('# Шрила Бхактивинода Тхакура (биографический очерк)\n\n' + '\n\n'.join(paras) + '\n\n' + '\n\n'.join('[^*]: ' + x for x in notes) + '\n')
