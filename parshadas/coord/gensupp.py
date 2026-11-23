import sys
S={
'srinivasa-acharya':dict(NAME='Шриниваса Ачарья',TAG='@srinivasa-acharya',PDF='Srinivasa-Acharya',SOURCES='«Бхакти-ратнакара» тараньги 5–15 (≈450 записей brt-; цитаты по bhakti-ratnakara/ru|en), а также пересмотреть ПВ/НВ/«Анурагавалли»/«Карнананда» по записям lila-db',EXTRA='Статья уже исправлялась по БР 10–11 (2026-11-22; см. review). Материала очень много — включай существенное, сжимай перечни. Согласуй со статьями @narottama-dasa, @shyamananda, @ramachandra-kaviraja, @jahnava (уже дополнены по БР 5–15) — противоречия перечисли.'),
'jahnava':dict(NAME='Джахнава-деви',TAG='@jahnava',PDF='Jahnava',SOURCES='«Бхакти-ратнакара» 5–15 (≈64 записи), ДЧВ/ГЧЧ при наличии, «Пата-нирная»',EXTRA='Статья частично правилась по БР 11 (2026-11-22/23). Согласуй со статьями @virabhadra, @narottama-dasa, @srinivasa-acharya (последняя дополняется параллельно — не правь её).'),
'jagadisha-pandita':dict(NAME='Джагадиша Пандит',TAG='@jagadisha-pandita',PDF='Jagadisha-Pandita',SOURCES='«Джагадиша-чаритра-виджая» (jagadisha-charitra-vijaya/, RU+EN; целое житие, уровень C) и БР (4 записи)',EXTRA='ДЧВ — целое житие: дай ему в статье отдельный раздел «По “Джагадиша-чаритра-виджае” (поздний источник)», сопоставляя с ЧЧ/ЧБ; семья Джагадиши и Махеша Пандит — коротко (у @mahesha-pandita своя статья — правку там перечисли, не делай).'),
}
slug=sys.argv[1]; d=dict(S[slug],SLUG=slug)
t=open('supp.txt').read()
for k,v in d.items(): t=t.replace('{'+k+'}',v)
open(f'S_{slug}.txt','w').write(t); print(f'S_{slug}.txt')
