# Задание: лилы ЧЧ (Мадхья 2–25, Антья 1–20) и ЧБ (Мадхья 1–28, Антья 1–10) в базу — без комментариев

Решение пользователя (2026-10-15): внести лилы оставшихся глав сейчас, по переводу, **без комментариев**
(комментарии Бхактивиноды и Бхактисиддханты — отдельная работа чата полного издания ЧЧ; он лилы больше не заводит).

## Формат — как у готовых записей
- Читать: `lila-db/README.md` (формат записи и событий), `lila-db/PARALLEL.md` (параллельная работа — обязательно),
  образцы: `lila-db/lilas/cc.yaml` (ЧЧ Ади) и `lila-db/lilas/cb.yaml` (ЧБ Ади), `THEMES.md`, `PERIODS.md`.
- Одна запись — одна лила (эпизод) по порядку изложения; главы-учения (беседы, сиддханта) — `kind: teaching`, по
  одной теме на запись; вступления и колофоны — `kind: author` (кратко, можно одной записью на главу).
- `summary` — 1–3 фразы своими словами по тексту главы; богословие — CLAUDE.md.
- `event` — сначала искать существующее событие (`grep -n -i … lila-db/events*.yaml`, `python3 lila-db/query.py text:…`);
  описания того же эпизода в других источниках (Мурари, Лочан, Карнапура, ЧЧ ↔ ЧБ) — одно событие. Новые события —
  только в свой файл `lila-db/events-<код>.yaml`.
- Теги лиц и мест — из `PERSONS.md` / `PLACES.md`; новые — в конец своего раздела (перед этим `git pull`, проверить
  дубли: `grep -o '^| @[a-z0-9-]*' lila-db/PERSONS.md | sort | uniq -d` — пусто).
- Поля `cc` / `cb` — глава; `verses` — обязательно.

## Файлы стихов
| Что | Файл | Метки стихов |
|---|---|---|
| ЧЧ Мадхья 2–25 | `chaitanya-charitamrita/ed/vcd/CC_MadhyaNN.md` | «(N) …» |
| ЧЧ Антья 1–11, 13–15, 20 | `chaitanya-charitamrita/vcd/txt/CC_AntyaNN.txt` | «(N) …» |
| ЧЧ Антья 12 | `chaitanya-charitamrita/vcd/txt/ШБ.txt` (проза Антья 12, файл так назван) | «(N) …» |
| ЧЧ Антья 16–19 | `chaitanya-charitamrita/vcd/new/CC_AntyaNN.md` | «(N) …» |
| ЧБ Мадхья 1–28, Антья 1–10 | `chaitanya-bhagavata/ed/CB_<Кханда>NN.md` (собрано `tools/prep_cb_txt.py` из `src/txt`) | `**N.**` |

## Распределение (номера id не пересекаются; файлы — только свои)
| Код | Главы | Файл записей | id | События |
|---|---|---|---|---|
| cc-m1 | ЧЧ Мадхья 2–9 | `lilas/cc-madhya-a.yaml` | cc-1001… | `events-cc-m1.yaml` |
| cc-m2 | ЧЧ Мадхья 10–17 | `lilas/cc-madhya-b.yaml` | cc-2001… | `events-cc-m2.yaml` |
| cc-m3 | ЧЧ Мадхья 18–25 | `lilas/cc-madhya-c.yaml` | cc-3001… | `events-cc-m3.yaml` |
| cc-a | ЧЧ Антья 1–20 | `lilas/cc-antya.yaml` | cc-4001… | `events-cc-a.yaml` |
| cb-m1 | ЧБ Мадхья 1–14 | `lilas/cb-madhya-a.yaml` | cb-1001… | `events-cb-m1.yaml` |
| cb-m2 | ЧБ Мадхья 15–28 | `lilas/cb-madhya-b.yaml` | cb-2001… | `events-cb-m2.yaml` |
| cb-a | ЧБ Антья 1–10 | `lilas/cb-antya.yaml` | cb-3001… | `events-cb-a.yaml` |
`source` везде — `cc` или `cb`. Дубли событий между параллельными исполнителями (одно и то же событие заведено
дважды) выверяет координатор после всех.

## Порядок и сохранность
По главам; после каждой главы — `python3 lila-db/build.py -w` (0 ошибок в своих записях), коммит и пуш по
`PARALLEL.md` (только свои файлы; сгенерированное — `git checkout -- lila-db/TIMELINE.md lila-db/EVENTS.md lila-db/export`).
Ветка — `claude/gracious-shannon-knppn0`.
