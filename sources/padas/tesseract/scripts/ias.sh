#!/bin/bash
q="$1"
curl -sS -G "https://archive.org/advancedsearch.php" --data-urlencode "q=$q" --data-urlencode "fl[]=identifier" --data-urlencode "fl[]=title" --data-urlencode "fl[]=date" --data-urlencode "fl[]=year" --data-urlencode "rows=40" --data-urlencode "output=json" | python3 -c "
import json,sys
d=json.load(sys.stdin)['response']
print('##', sys.argv[1], d['numFound'])
for x in d['docs']: print('  ', x.get('identifier'), '|', x.get('title'), '|', x.get('date') or x.get('year'))" "$q"
