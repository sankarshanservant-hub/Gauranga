# Карточки паршад и база данных — предложение (черновик для обсуждения, 2026-10-14)

Основание — замысел «The Golden Avatar / Chaitanya Master Story Bible» (документ учителя пользователя) и то, что
уже есть в репозитории (`lila-db/`, `parshadas/`).

## 1. Что из замысла у нас уже есть
| Замысел | У нас |
|---|---|
| SOURCE REGISTRY, уровни A–D | `lila-db/SOURCES.md` (A–D) |
| LILA DATABASE, EVENT_ID, сверка версий | `lila-db/lilas/*.yaml` (описания по источникам) + `events*.yaml` (одно событие — одна карточка) |
| MASTER TIMELINE | `lila-db/PERIODS.md`, `TIMELINE.md`, годы/возраст в `export/lilas.json` |
| Реестр имён и мест | `lila-db/PERSONS.md` (`@тег`), `PLACES.md` (`#тег`) |
| Темы, бхава, темы учения | `lila-db/THEMES.md` |
| Claim Ledger (каждое утверждение → источник) | `parshadas/facts/<тег>.md` (F/Q/I-пункты со ссылками) |
| Character Encyclopedia (досье) | статьи `parshadas/ru|en/<тег>.md` |

Не хватает: **структурированной карточки лица** (досье в машиночитаемом виде), **сети отношений**,
**каталога духовных отождествлений** с вариантами, **реестра наставлений** (TEACHING_ID) и — отдельно —
**сценарного слоя** (оценки, арки, «через какое событие зритель знакомится»).

**Комментарии Шрилы Шридхара Махараджа** — наследие миссии пользователя: использовать свободно, цитировать и
переводить (см. CLAUDE.md).

## 2. Принцип: три слоя, которые никогда не смешиваются
1. **Факты** (источник → утверждение): `facts/` и `lila-db/`. Уровни A–D как в `SOURCES.md`.
2. **Карточка лица** — сжатая структура над фактами: каждое поле ссылается на F-пункты реестра и/или события
   `ev-…`. Ничего нового не утверждает.
3. **Сценарный слой** — отдельный файл `screen/<тег>.yaml`: драматургия, оценки 1–5, арки, допустимые и
   недопустимые сценарные выводы. Уровни замысла E (историческая реконструкция) и F (драматургическое
   связующее) живут **только здесь** и никогда не попадают в слои 1–2.

## 3. Формат карточки `parshadas/cards/<тег>.yaml` (проект)
```yaml
id: "@madhavendra-puri"          # тег из lila-db/PERSONS.md
names:
  ru: "Мадхавендра Пури"
  en: "Madhavendra Puri"
  variants: ["Мадхава Пури", "Шри Пурипада", "Пури Госвами"]   # как называют источники
kind: associate                  # associate | family | guru | acharya | opponent | ruler | deity | other
circle: [elders]                 # круги: elders | navadvipa | panca-tattva | puri | vrindavana | goswamis | later
period: [P00, P01]               # периоды lila-db, когда лицо присутствует
life:
  appearance: {date: "", tithi: "", place: "", conf: "", facts: []}
  disappearance: {date: "", tithi: "", place: "#remuna?", conf: "спорно", facts: [F152, F154]}
  samadhi: [{place: "#remuna", facts: [F153]}]
origin: {places: ["#..."], family: [], varna: "", facts: []}
relations:                       # типизированные связи → сеть отношений (export/relations.json)
  - {type: disciple, who: "@ishvara-puri", facts: [F111]}
  - {type: disciple, who: "@advaita", facts: [F40], note: "время посвящения расходится (ЧБ / ЧЧ)"}
  - {type: met, who: "@nityananda", event: ev-nityananda-madhavendra, facts: [F47]}
  - {type: served-deity, who: "@gopala-govardhana", facts: [F60]}
  # типы: father mother spouse son daughter sibling relative | guru disciple siksha-guru siksha-disciple |
  #       friend companion servant served-by | met | opposed | ruler-of | deity-served | lineage-predecessor
identities:                      # духовные отождествления — каждое со своим источником, варианты не сливать
  - {in: krishna-lila, as: "…", source: "ГГД 22", level: B, facts: [F12], variants: []}
events: [ev-…, ev-…]             # ключевые события (lila-db/events*.yaml), по порядку жизни
teachings_given: []              # TEACHING_ID (будущий реестр наставлений)
teachings_received: []
works: [{title: "шлоки в «Падьявали»", facts: [F159]}]
places: ["#govardhana", "#remuna", "#puri"]
character:                       # черты — ТОЛЬКО с опорой на эпизод (не психология от себя)
  - {trait: "безразличие к телу в экстазе разлуки", facts: [F28], events: [ev-…]}
significance: {facts: [I1, I2]}  # смысл (мысли авторов — своими словами)
sources: {T: "36–43", M: "", B: "1–75", other: ["ЧЧ Мадхья 4", "ЧБ Ади 9"]}
article: {ru: "parshadas/ru/madhavendra-puri.md", en: "parshadas/en/madhavendra-puri.md"}
open_questions: ["место и время ухода"]
```
Правила: поля пустые — можно опускать; `facts` — номера пунктов `facts/<тег>.md`; `level` — A–D по
`lila-db/SOURCES.md`; расхождения — поле `note` или `variants`, никогда не «усреднять».

## 4. Сценарный слой `parshadas/screen/<тег>.yaml` (позже, по решению)
```yaml
id: "@pratāparudra"
introduced_by: ev-…              # через какое событие зритель знакомится
seeks: "…"                       # чего ищет — с опорой на facts/events
obstacle: "…"
turning_point: ev-…
reveals_of_mahaprabhu: "…"       # какую грань Махапрабху раскрывает его история
arc: [ev-…, ev-…, ev-…]          # многосерийная арка
ratings: {spiritual: 5, character: 4, dramatic: 5, visual: 4}
allowed_inferences: ["…"]        # допустимые сценарные выводы
forbidden_inferences: ["мирская психология вечных спутников", "…"]
level_E_F: ["…"]                 # реконструкции — явно помечены
```

## 5. Сборка и чтение
- `parshadas/tools/cards.py` (сделать): проверяет теги (`PERSONS.md`, `PLACES.md`), события (`events*.yaml`),
  номера F/Q/I (по `facts/`), собирает `export/persons.json`, `export/relations.json` (рёбра графа),
  `export/identities.json`.
- Поиск — расширить `lila-db/query.py`: `person:@nityananda`, `rel:disciple`, `identity:gopi`, `circle:puri`.
- Почему так легко парсить: один небольшой YAML на лицо с фиксированными ключами; связи — только через теги и
  `ev-` id; всё тяжёлое (тексты, факты) — по ссылкам, читается только при необходимости.

## 6. Порядок
1. Утвердить формат (этот файл).
2. Пилот: карточки трёх готовых лиц (Мадхавендра Пури, Джаганнатха Мишра, Шачи) — из их реестров, без новых
   источников; `cards.py` + export.
3. Дальше — карточка составляется вместе с реестром каждого нового лица (Нитьянанда — первым), в том же проходе.
4. Реестр наставлений (TEACHING_ID) и сценарный слой — после пилота, по решению пользователя.
