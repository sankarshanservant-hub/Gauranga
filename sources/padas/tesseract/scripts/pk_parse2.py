"""Assign PK numbers to pada-end lines, using anchors + interpolation.
Usage: pk_parse2.py out.json file1 start1 file2 start2 ...
"""
import re, json, sys
BD = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
endlike = re.compile(r'॥[^॥]{0,3}[০-৯][০-৯ ।॥1)|]{0,12}\s*$|[০-৯]{1,3}\s*[।॥1]\s*[০-৯]{2,4}\s*[॥।]?\s*$')
anchor = re.compile(r'[॥|]\s*([০-৯]{1,3}\s*[॥।1\)|]+\s*[০-৯]{1,4}|[০-৯]{2,7})\s*[॥।|]?')
out = {}
args = sys.argv[2:]
for fi in range(0, len(args), 3):
    path, vol, start = args[fi], int(args[fi + 1]), int(args[fi + 2])
    lines = open(path, encoding='utf-8').read().split('\n')
    ends = []  # (line_index, assigned_number or None)
    prev = start
    for i, l in enumerate(lines):
        if 'সংখ্যক' in l or 'সংখাক' in l:
            continue
        if not endlike.search(l.rstrip()):
            continue
        cand = None
        ms = list(anchor.finditer(l))
        if ms:
            parts = re.split(r'[\s॥।1\)|]+', ms[-1].group(1))
            s = parts[-1].translate(BD)
            for k in (4, 3, 2, 1):
                if len(s) >= k:
                    v = int(s[-k:])
                    if prev < v <= prev + 25:
                        cand = v
                        break
        if cand:
            prev = cand
        ends.append([i, cand])
    # interpolate
    idx = [j for j, e in enumerate(ends) if e[1]]
    for a, b in zip(idx, idx[1:]):
        na, nb = ends[a][1], ends[b][1]
        between = ends[a + 1:b]
        if len(between) == nb - na - 1:
            for k, e in enumerate(between):
                e[1] = -(na + k + 1)  # negative = interpolated
    last = 0
    for i, n in ends:
        if n:
            num = abs(n)
            blk = lines[last + 1:i + 1][-45:]
            out.setdefault(str(num), []).append({'vol': vol, 'file': path.split('/')[-1], 'line': i + 1,
                                                  'interp': n < 0, 'text': '\n'.join(blk)})
        last = i
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False)
found = {int(k) for k in out}
miss = [n for n in range(1, 3102) if n not in found]
print(len(found), 'found; missing', len(miss))
