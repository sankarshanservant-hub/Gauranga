# Раздел «Путешествие» — архив кода и данных

Снимок из репозитория `sankarshanservant-hub/avadhut-archive` (ветка main, 14dba52 2026-10-25).

Сайт: Astro 7 (статический), карта — MapLibre GL 6.11.2 без ключей, подложка OpenFreeMap (positron/dark), спутник — Esri World Imagery. Живые страницы: https://avadhutmaharaj.com/travel/ и https://avadhutmaharaj.com/travel/india/

## Из HANDOFF.md

- **Путешествие `/travel/` (2026-10-16, отдельный раздел в шапке):** карта мира — в каких городах
  читались лекции (`/travel/`, клик по городу → лекции по годам и площадкам) и «Святая Индия»
  (`/travel/india/`: Индия → город → святые места — храмы, кунды, гхаты — с описанием, цитатой
  Махараджа оттуда, лекциями; паломничества `#trip:<id>`; ссылка делится: `#vrindavan/radha-damodar`).
  Карта — MapLibre GL (копируется из node_modules в `public/vendor/` скриптом
  `scripts/copy-maplibre.mjs`, свой адрес нужен для CSP), подложка OpenFreeMap без ключа, спутник Esri.
  Код — `public/travel/map.js` + `travel.css`, данные собирает `src/lib/travel.ts` из `src/data/travel/`:
  `world-places.json` + `lecture-places.json` (пересчёт: `python3 -I scripts/travel/derive-places.py --report`,
  ручные решения — `lecture-places-manual.json`, ручное главнее), `india-places.json` (27 городов,
  118 мест; `approx: true` — точка не сверена, таких большинство — **проверить по карте**),
  `india-lectures.json` (174 лекции, 15 паломничеств; уверенность high/medium/low, low — по соседним
  датам). На странице лекции место показывается ссылкой на карту (кроме low). Не на карте: 5 лекций
  «Южная Индия»/«Гималаи» без города. Идея: правка точек админом прямо на карте.
  **Holy Spots (2026-10-18):** база старого приложения (holyspots.vedareader.ru, Supabase
  `rxvckkqqunyqtxjyabub`, читается публичным anon-ключом из бандла приложения) импортирована:
  снимок — `data/holyspots/`, импорт — `python3 -I scripts/travel/import-holyspots.py` (сопоставляет
  места по названию+расстоянию, точные координаты, фото, описания `details`, новые места
  `source: holyspots`; парикрамы-треки → `src/data/travel/india-routes.json`). Фото на сайте грузятся
  прямо из хранилища Supabase — если проект закроют, их надо перенести к себе. Полная выгрузка базы
  для разработчика приложения лежит на Google Диске (папка «Holy Spots — выгрузка базы (2026-10-18)»,
  Apps Script `holyspots-to-drive.gs` в ней докачивает таблицы и все фото).


## Что где
| Путь | Что это |
|---|---|
| `src/pages/travel/index.astro` | Карта мира: города, где читались лекции |
| `src/pages/travel/india/index.astro` | «Святая Индия»: Индия → город → святое место; адреса `#город`, `#город/место`, `#trip:<id>`, `#route:<id>` |
| `src/pages/travel/india-spots.json.ts` | Подробности мест (описание, все фото) — грузятся при открытии места |
| `src/lib/travel.ts` | Сборка данных для страниц из `src/data/travel/*.json` |
| `public/travel/map.js` | Вся логика карты: загрузка MapLibre, маркеры (HTML), парикрамы (трек — сплошной, схема — пунктир), панель, спутник, тема |
| `public/travel/travel.css` | Стили раздела |
| `scripts/copy-maplibre.mjs` | Копирует MapLibre из node_modules в `public/vendor/` как `.js` (nginx отдаёт `.mjs` неверным типом) |
| `src/data/travel/india-places.json` | Регионы, 30 городов, 360 мест (355 на карте, 5 скрыты) (`coords` = [lng, lat]; `approx` — приблизительно; `hidden` — скрыто; `hs` — id в Holy Spots; `details` — подробный текст) |
| `src/data/travel/india-lectures.json` | Лекции, прочитанные в Индии → город/место, паломничества (trips) |
| `src/data/travel/india-routes.json` | GPS-треки парикрам (из Holy Spots) |
| `src/data/travel/india-routes-manual.json` | Схемы обходов без трека (Говардхан по книге «Враджа-лила», ч.3) |
| `src/data/travel/world-places.json`, `lecture-places*.json` | Карта мира: города и привязка лекций |
| `scripts/travel/import-holyspots.py` | Импорт базы Holy Spots: сопоставление мест, фото, тексты, исправления ошибок (`HS_FIX`), треки |
| `scripts/travel/parse-holyspots-pdf.py` | Редакторские тексты из PDF-таблицы Holy Spots |
| `scripts/travel/derive-places.py` | Места лекций по миру из названий/YouTube/расшифровок |
| `data/holyspots/` | Снимок базы Holy Spots (без хинди) и исходный PDF |
| `site-integration/` | Где раздел подключён к сайту: шапка, мягкая навигация, ссылка «место» на странице лекции |

Не входят: остальной сайт, `data/registry.csv` (реестр 2223 лекций; заголовки/даты лекций нужны `travel.ts` через коллекцию `lectures`), расшифровки.
