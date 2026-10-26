"""Build navadvipa-dhama-mahatmya/en/*.md from en_lines.jsonl (dump of the SCSM 2015 English PDF).
Chapters: translation of each verse under **N.**; prose sections: paragraphs (Sanskrit quotes kept, italic)."""
import json, re, sys, collections, os
L = [json.loads(l) for l in open(sys.argv[1])]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

def kind(d):
    f, s = d['f'], d['s']
    if f.startswith('Nadia'): return 'beng'
    if s == 7.5 and 9 < d['p'] < 512: return 'foot'
    if d['y'] >= 558: return 'head'
    if d['y'] <= 45 and re.fullmatch(r'\s*\d+\s*', d['t']): return 'pageno'
    if s == 6.5: return 'gloss'
    if f == 'PalatinoLTStd-Medium' and s in (8.0, 9.0, 8.2, 8.8): return 'translit'
    if s == 10.0 and f == 'PalatinoLTStd-Roman': return 'caption'
    if s in (16.0, 17.0, 18.0, 12.0, 15.1, 20.0) : return 'heading'
    if f.startswith('PalatinoLTStd-Italic') and s in (8.0, 7.5): return 'cite'
    if s in (9.0,) : return 'body'
    return 'other'

# vocabulary for de-hyphenation
vocab = collections.Counter()
for d in L:
    if kind(d) == 'body':
        for w in re.findall(r"[\w’'-]+", d['t'].replace('*', '')[:-1]):
            vocab[w.lower()] += 1

def join_lines(lines):
    out = ''
    for t in lines:
        t = t.strip()
        if not out: out = t; continue
        m = re.search(r"([\w’]+)-$", out.replace('*', ''))
        if out.endswith('-') and m and not out.endswith('--'):
            w1 = m.group(1); w2 = re.match(r"[\w’]*", t.replace('*', '')).group(0)
            hy, jn = f'{w1}-{w2}'.lower(), f'{w1}{w2}'.lower()
            if vocab[hy] and vocab[hy] >= vocab[jn]: out = out + t
            elif vocab[jn]: out = out[:-1] + t
            elif all(ord(c) < 128 for c in w1 + w2): out = out[:-1] + t
            else: out = out + t
        elif out.endswith('—') or t.startswith('—'): out = out + t
        else: out = out + ' ' + t
    out = re.sub(r'\*(\s*)\*', r'\1', out)          # merge adjacent italics
    out = re.sub(r'\*([^*\n]*?\S)\s+\*', r'*\1* ', out)  # "*X *" -> "*X* "
    out = re.sub(r'\*\s+([^*\n]+?)\*', r' *\1*', out)
    out = re.sub(r'(?<=[A-Za-zāīū])X(?=[a-zāīū])', 'ā̐', out).replace('d3hu', 'dũhu')   # glyph ā̐ in the PDF font
    out = re.sub(r'(?<=[a-z])0(?=[a-z])', 'ā̐', out)
    out = re.sub(r'[  ]{2,}', ' ', out).replace(' ', ' ').strip()
    return out

def fix_italics(t):
    if t.startswith('**') and re.match(r'^\*\*[^*]+\.\*\* ', t):
        m = re.match(r'^(\*\*[^*]+\.\*\* )(.*)$', t, re.S); return m.group(1) + fix_italics(m.group(2))
    if t.startswith('> ') or t.count('*') % 2: return t
    parts = t.split('*'); out = ''
    for i, seg in enumerate(parts):
        if i % 2 == 0: out += seg
        elif seg.strip():
            lead = seg[:len(seg) - len(seg.lstrip())]; trail = seg[len(seg.rstrip()):]
            out += lead + '*' + seg.strip() + '*' + trail
        else: out += seg
    return re.sub(r'\*(\w)', lambda m: '*' + m.group(1), re.sub(r'  +', ' ', out))

def margin(p):
    xs = [d['x'] for d in L if d['p'] == p and kind(d) == 'body']
    return collections.Counter(xs).most_common(1)[0][0] if xs else 48
MARG = {}
FOOT = {}
FIX = {(105, 339): 'śrī-jīva vaṁśīra pade praṇati karila [40]'}   # misprint in the edition: [41] for [40]

def section(p0, p1):
    """Return list of blocks: ('h', text) | ('v', label, text) | ('p', text) | ('q', [lines]) | ('c', text)"""
    blocks, cur, tl, label = [], [], [], None
    def flush_body():
        nonlocal cur
        if cur:
            for para in cur:
                t = join_lines(para)
                if t:
                    if label is not None and blocks and blocks[-1][0] == 'v' and blocks[-1][1] == label and not blocks[-1][3]:
                        blocks[-1] = ('v', label, (blocks[-1][2] + '\n\n' + t).strip(), False)
                    elif label is not None and not (blocks and blocks[-1][0] == 'v' and blocks[-1][1] == label):
                        blocks.append(('v', label, t, False))
                    else: blocks.append(('p', t))
        cur = []
    heads = []
    for d in [d for d in L if p0 <= d['p'] <= p1]:
        k = kind(d)
        if k in ('beng', 'head', 'pageno', 'gloss', 'caption', 'other'): continue
        if k == 'foot': FOOT.setdefault((p0, p1), []).append(d['t']); continue
        if (d['p'], d['y']) in FIX: d = dict(d, t=FIX[(d['p'], d['y'])])
        if k == 'heading':
            flush_body(); label = None
            if blocks and blocks[-1][0] == 'h' and d['p'] == blocks[-1][2]:
                blocks[-1] = ('h', blocks[-1][1] + ' ' + d['t'].strip('* '), d['p'])
            else: blocks.append(('h', d['t'].strip('* '), d['p']))
            continue
        if k == 'translit':
            if cur: flush_body(); label = None
            tl.append(d['t'].strip())
            m = re.search(r'\[(\d+(?:[–-]\d+)?)\]\s*$', d['t'])
            if m:
                n = m.group(1).replace('-', '–')
                # previous number without its own translation (gloss+translation shared) -> range
                if label is not None and not cur and not (blocks and blocks[-1][0] == 'v' and blocks[-1][1] == label):
                    label = label.split('–')[0] + '–' + n.split('–')[-1]
                else: label = n
                tl = []
            continue
        if k == 'cite':
            if tl: blocks.append(('q', tl)); tl = []
            flush_body(); blocks.append(('c', d['t'].strip())); continue
        if tl:  # translit without number = quoted shloka
            blocks.append(('q', tl)); tl = []; label = None
        # body line
        if d['p'] not in MARG: MARG[d['p']] = margin(d['p'])
        indent = d['x'] - MARG[d['p']] >= 10
        if not cur or indent and label is None: cur.append([d['t']])
        else: cur[-1].append(d['t'])
    flush_body()
    if tl: blocks.append(('q', tl))
    return blocks

def render(blocks, title=None):
    out = []
    for b in blocks:
        if b[0] == 'h': out.append(f'## {b[1]}')
        elif b[0] == 'v': out.append(f'**{b[1]}.** {b[2]}')
        elif b[0] == 'p': out.append(b[1])
        elif b[0] == 'q': out.append('\n'.join(f'> *{x.strip()}*' + ('  ' if i < len(b[1]) - 1 else '') for i, x in enumerate(b[1])))
        elif b[0] == 'c': out.append(f'> {b[1]}')
    return '\n\n'.join(fix_italics(x) for x in out) + '\n'

MERGE = {'04': [('43', '45'), ('50', '51')], '05': [('7', '8')], '13': [('12', '13'), ('30', '33')], '16': [('72', '73')], '18': [('6', '7')]}
# chapter page ranges
chap = [(int(d['p'])) for d in L if kind(d) == 'heading' and d['s'] == 12.0 and d['t'].strip().startswith('chapter')]
bounds = chap + [385]
names = ['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen']
report = []
for i, p0 in enumerate(chap):
    bl = section(p0, bounds[i + 1] - 1)
    hs = [b for b in bl if b[0] == 'h']
    title = re.sub(r'^chapter \w+ ', '', hs[1][1] if len(hs) > 1 else hs[0][1])
    bl = [b for b in bl if b[0] != 'h']
    for a, b in MERGE.get(f'{i+1:02d}', []):   # merges made when aligning RU (see review/ru-NN.md)
        k = next(j for j, x in enumerate(bl) if x[0] == 'v' and x[1].split('–')[0] == a)
        m = next(j for j, x in enumerate(bl) if x[0] == 'v' and x[1].split('–')[-1] == b)
        bl[k:m + 1] = [('v', f'{a}–{b}', ' '.join(x[2] for x in bl[k:m + 1]), False)]
    labs = [b[1] for b in bl if b[0] == 'v']
    # check continuity
    nums = []
    for l in labs:
        a = l.split('–'); nums += list(range(int(a[0]), int(a[-1]) + 1))
    gaps = [n for n in range(1, max(nums) + 1) if n not in nums]
    dup = [n for n, c in collections.Counter(nums).items() if c > 1]
    stray = [b for b in bl if b[0] in ('p', 'q', 'c')]
    report.append(f'ch{i+1:02d} p{p0}: {len(labs)} labels, max {max(nums)}, gaps {gaps}, dup {dup}, stray {len(stray)}')
    txt = f'# Chapter {i+1}. {title}\n\n' + render(bl)
    fn = FOOT.get((p0, bounds[i + 1] - 1))
    if fn:
        note = join_lines(fn).lstrip('*').strip()
        if note.startswith('*'): note = note[1:]
        txt = txt.replace('seven sons*,', 'seven sons[^1],', 1) + f'\n[^1]: {note}\n'
    open(f'{OUT}/{i+1:02d}.md', 'w').write(txt)
# Bhava-taranga
bl = section(387, 451)
bl = [b for b in bl if b[0] != 'h']
labs = [b[1] for b in bl if b[0] == 'v']
report.append(f'bhava-taranga: {len(labs)} labels, last {labs[-1]}, stray {len([b for b in bl if b[0] != "v"])}')
open(f'{OUT}/19.md', 'w').write('# Śrī Śrī Navadvīpa-bhāva-taraṅga. Waves of the Ecstasy of Nabadwīp\n\n' + render(bl))
# front matter
for name, (a, b) in {'00-translators-note': (11, 14), '00-publishers-notes': (15, 18), '00-ahvana': (19, 22),
                     '00-preface': (23, 24), '00-vandana': (25, 28), '20-gaura-krishna-tattva': (453, 456),
                     '21-land-of-sweetness': (457, 480), '22-ten-offences': (481, 482), '23-glossary': (483, 511)}.items():
    if not os.path.exists(f'{OUT}/{name}.md'):   # front/back matter was fixed by hand afterwards — never overwrite
        open(f'{OUT}/{name}.md', 'w').write(render(section(a, b)))
print('\n'.join(report))
