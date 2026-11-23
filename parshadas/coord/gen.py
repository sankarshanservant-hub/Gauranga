import json,sys
N="Также: если в parshadas/review/namamrita-samudra.md есть стих о нём (ней) с ясным тождеством — внеси в реестр (F +пров.)."
P={
'bhakti-vilasa-tirtha':dict(NAME='Шрила Бхакти Виласа Тиртха Госвами Махарадж',TAG='@bhakti-vilasa-tirtha',PDF='Bhakti-Vilasa-Tirtha',PLANKEY='120',CH='120',FILE='120-bhaktivilasa-tirtha.md',PAGES='B 1130–1145, pdf 1154–1169 (сводный файл; есть -part1…-part4)',SEE='Для согласованности: как он подан в parshadas/ru/bhaktisiddhanta.md (гуру; храм над самадхи, Шьяма-кунда — B 1135), ru/bhakti-pramoda-puri.md, ru/bhakti-dayita-madhava.md, ru/shridhara-maharaja.md (готовы).',HINT='Шрила Бхакти Виласа Тиртха Госвами Махарадж (Кунджабихари Видьябхушана) — ближайший помощник Шрилы Бхактисиддханты в управлении Гаудия Матхом, затем ачарья Шри Чайтанья Матха; храм над самадхи Прабхупады, Шьяма-кунда; заложил храм Рамананда-Гаудия-матха (Коввур?) — по реестру/PERSONS. Источники: B (глава 16 страниц — главный), T, M; «Хармонист», «Гаудия»; Саньял; наследие Шридхара Махараджа и «Наши учителя» (наши — цитировать можно; там могут быть суждения о расколе после 1937 — подавать сдержанно, без мирских оценок и полемики); современные книги (gauranga-private/sources/) — только факты. Даты — по календарю ШЧСМ (если есть). Статья большая — порциями. '+N,THEO=': события после ухода Бхактисиддханты (раздел Гаудия Матха, суды) — фактически и бережно, без осуждения лиц; «ушёл из этого мира»'),
'bhakti-prajnana-yati':dict(NAME='Шрила Бхакти Праджняна Яти Госвами Махарадж',TAG='@bhakti-prajnana-yati',PDF='Bhakti-Prajnana-Yati',PLANKEY='121',CH='121',FILE='121-bhaktiprajnana-yati.md',PAGES='B 1146–1167, pdf 1170–1191 (сводный файл; есть -part1…-part5)',SEE='Для согласованности: как он подан в parshadas/ru/bhaktisiddhanta.md, ru/bhakti-vilasa-tirtha.md (пишется параллельно — не ссылаться как на готовую), ru/shridhara-maharaja.md.',HINT='Шрила Бхакти Праджняна Яти Госвами Махарадж — ученик Шрилы Бхактисиддханты, ачарья Шри Чайтанья Матха после Бхакти Виласы Тиртхи (проверь по B). Тег: в lila-db/PERSONS.md его, вероятно, нет — заведи @bhakti-prajnana-yati (проверь дубли). Источники: B (глава 22 страницы — главный), T, M, «Наши учителя», scsm-web-biographies, современные — только факты. Даты — по календарю ШЧСМ (если есть). Статья большая — порциями. '+N,THEO=': без мирских оценок внутриматхских событий; «ушёл из этого мира»'),
}








stage,slug=sys.argv[1],sys.argv[2]
t=open({'A':'stageA.txt','B':'stageB.txt','V':'stageV.txt'}[stage]).read()
d=dict(P[slug],SLUG=slug)
for k,v in d.items(): t=t.replace('{'+k+'}',v)
open(f'{stage}_{slug}.txt','w').write(t); print(f'{stage}_{slug}.txt')
