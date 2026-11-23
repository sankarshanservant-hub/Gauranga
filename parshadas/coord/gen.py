import json,sys
N="Также: если в parshadas/review/namamrita-samudra.md есть стих о нём (ней) с ясным тождеством — внеси в реестр (F +пров.)."
P={
'bhaktisiddhanta':dict(NAME='Шрила Бхактисиддханта Сарасвати Госвами Тхакур Прабхупада',TAG='@bhaktisiddhanta',PDF='Bhaktisiddhanta-Sarasvati',PLANKEY='119',CH='119',FILE='119-bhaktisiddhanta-sarasvati.md',PAGES='B 1122–1129, pdf 1146–1153 (сводный файл; есть -part1/-part2)',SEE='Для согласованности: как он подан в parshadas/ru/bhaktivinoda.md (отец), ru/gaurakishora-dasa-babaji.md (гуру), ru/jagannatha-dasa-babaji.md, ru/krishnadasa-babaji.md, ru/shridhara-maharaja.md, ru/bhaktivedanta-svami.md, ru/govinda-maharaja.md (готовы).',HINT='Шрила Бхактисиддханта Сарасвати (Бималапрасад, 1874–1937) — сын Бхактивиноды, ученик Гауракишоры Даса Бабаджи; основатель Гаудия Матха (64 матха), «Гаудия», «Хармонист», «Анубхашья», «Гаудия-бхашья»; санньяса 1918; уход 1 янв. 1937 (Кришна-чатуртхи Нараяна-масы? — по календарю ШЧСМ). Это ачарья-авторитет всего проекта. Источники (кроме T, M, B): его собственные сочинения в репозитории (Анубхашья — chaitanya-charitamrita/ed/ru/*-anu.md; Гаудия-бхашья — chaitanya-bhagavata/src/txt; «Чайтанья-даршане» — sources/chaitanya-darshane; «Хармонист» — sources/harmonist-1928-29; Саньял 1933 — sources/sanyal); приватная библиотека /home/user/gauranga-private/sources/ (README и SEARCH-LOG.md): «Наши учителя» (nashi-uchitelya — книга нашей миссии, цитировать можно со ссылкой), «Sri Guru and His Grace» и иное наследие Шрилы Шридхара Махараджа (наше — цитировать можно, со ссылкой), scsm-web-biographies; «Сарасвати-джаяшри» (бенг. 1934 — сырой OCR; англ. 2026 — современный, только для фактов), «Шрила Прабхупадера Харикатхамрита» (бенг. сканы), «Саджджана-тошани» 1915/1917, «Амара Прабхура Катха», «Гаура-паршада-чаритавали» (бенг., не PD — только факты), «Prabhupada Saraswati Thakura» (gosai), фотобиография WVA, «Жизнь и идеалы…» (рус. фрагмент), «Луч Вишну» (рус.) — современные: только для фактов и сверки, не цитировать и не пересказывать формулировки. Реестр большой — пиши порциями, коммить часто. '+N,THEO=': ачарья — нитья-сиддха, «Варшабхануви-дайита дас»; полемика с сахаджиями, смартами, майявадой — защита чистой бхакти, без мирских оценок; санньяса и даива-варнашрама — по его собственным словам; уход — «вошёл в вечные игры», не «умер»; последние наставления — дословно по первоисточнику'),
}







stage,slug=sys.argv[1],sys.argv[2]
t=open({'A':'stageA.txt','B':'stageB.txt','V':'stageV.txt'}[stage]).read()
d=dict(P[slug],SLUG=slug)
for k,v in d.items(): t=t.replace('{'+k+'}',v)
open(f'{stage}_{slug}.txt','w').write(t); print(f'{stage}_{slug}.txt')
