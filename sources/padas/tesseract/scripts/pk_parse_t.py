import re, json, sys
BD = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
R = '/home/user/Gauranga/sources/'
S = '/tmp/claude-0/-home-user-Gauranga/7b2c56d5-8710-5f94-af24-6c5c741d0e9d/scratchpad/out/'
VOLS = [
    (1, S+'pk_v1.txt', 0),
    (2, S+'pk_v2.txt', 600),
    (3, S+'pk_v3.txt', 1570),
    (4, S+'pk_v4.txt', 2385),
]
mark = re.compile(r'[॥|]\s*([০-৯]{1,3}\s*[॥।1\)|]+\s*[০-৯]{1,4}|[০-৯]{2,7})\s*[॥।|]?')
out = {}
for vol, path, start in VOLS:
    lines = open(path, encoding='utf-8').read().split('\n')
    prev = start
    last_end = 0
    for i, l in enumerate(lines):
        ms = list(mark.finditer(l))
        if not ms:
            continue
        m = ms[-1]
        g = m.group(1)
        parts = re.split(r'[\s॥।1\)|]+', g)
        s = parts[-1].translate(BD)
        cand = None
        for k in (4, 3, 2, 1):
            if len(s) >= k:
                v = int(s[-k:])
                if prev < v <= prev + 25:
                    cand = v
                    break
        if cand is None:
            continue
        # text block: from last_end to i, keep last 40 lines
        blk = lines[max(last_end + 1, i - 40):i + 1]
        out[cand] = {'vol': vol, 'line': i + 1, 'text': '\n'.join(blk)}
        prev = cand
        last_end = i
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False)
nums = sorted(out)
missing = [n for n in range(1, 3102) if n not in out]
print(len(out), 'found; missing', len(missing))
print(missing[:400])
