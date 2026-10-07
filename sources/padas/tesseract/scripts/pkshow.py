import json, sys, re
d = json.load(open(sys.argv[1]))
G = re.compile('গৌর|গোরা|গোৌর|শচী|নদীয়া|নদিয়া|চৈতন্|চৈতন্ত|নিতাই|নিত্যানন্দ|বিশ্বম্ভর|নিমাই|গদাধর|অদ্বৈত|সন্ন্যাস|সন্্যাস|নীলাচল|শ্রীবাস|গোরাচাঁদ|গোরাচান্দ')
for n in sys.argv[2:]:
    ents = d.get(n, [])
    print('#' * 10, n, len(ents), 'variants')
    for e in sorted(ents, key=lambda e: (e['interp'], 0 if e['file'].startswith('pk_v') else 1))[:2]:
        t = e['text']
        lines = [l for l in t.split('\n') if l.strip()]
        print('--', e['file'], e['line'], 'interp' if e['interp'] else 'anchor', 'GAURA' if G.search(t) else '')
        print('\n'.join(lines[-int(sys.argv[0] and 18):]))
