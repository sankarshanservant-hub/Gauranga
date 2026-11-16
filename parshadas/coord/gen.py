import json,sys
P={
'prakashananda-sarasvati':dict(NAME='Пракашананда Сарасвати',TAG='@prakashananda-sarasvati',PDF='Prakashananda-Sarasvati',PLANKEY='061',CH='061',FILE='061-prakashananda-sarasvati.md',PAGES='B 886–888, pdf 910–912',SEE='Для согласованности: как он подан в parshadas/ru/prabodhananda-sarasvati.md (там подробно разобран спор о тождестве — ссылайся, не дублируй), ru/chandrashekhara-acharya.md (Чандрашекхара-вайдья в Каши, если есть), ru/tapana-mishra (если есть), ru/sanatana-gosvami.md, ru/rupa-gosvami.md.',HINT='Пракашананда Сарасвати — глава санньяси-майявади в Каши: хула на Господа (ЧЧ Ади 7.40–42, Мадхья 17.103–149 — «Пракашананда» в Каши, Мадхья 17.110 и далее), встреча в доме маратхского брахмана и беседа о Веданте (ЧЧ Ади 7.41–149, «Анубхашья»), обращение (Мадхья 25.1–170, Ади 7.149–151), прочие свидетельства (ЧЧН, Мурари, Карнапура, Лочан). Отождествление с @prabodhananda-sarasvati — по Бхактисиддханте неверно (реестр Прабодхананды уже разбирает спор — ссылайся). Тёзки — развести.',THEO=': майявада — оскорбление Господа, но обращение Пракашананды — милость Господа и его подлинная перемена; не изображать карикатурно; Веданта-сутра — по толкованию Махапрабху (ЧЧ Ади 7), без уступок майяваде; «Бог-нирвишеша» — мнение оппонента, ясно обозначенное'),
}
stage,slug=sys.argv[1],sys.argv[2]
t=open({'A':'stageA.txt','B':'stageB.txt','V':'stageV.txt'}[stage]).read()
d=dict(P[slug],SLUG=slug)
for k,v in d.items(): t=t.replace('{'+k+'}',v)
open(f'{stage}_{slug}.txt','w').write(t); print(f'{stage}_{slug}.txt')
