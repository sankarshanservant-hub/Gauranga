# Параллельная работа нескольких исполнителей (с 2026-10-08)

Пользователь разрешил запускать несколько исполнителей одновременно. Чтобы не было конфликтов в `lila-db/` и git:

1. **Свои файлы.** Каждый исполнитель пишет только:
   - свою папку перевода (`<папка>/…`);
   - `lila-db/lilas/<код>.yaml` — свои записи;
   - `lila-db/events-<код>.yaml` — свои **новые** события (формат как `events.yaml`; `build.py` читает все
     `events-*.yaml`). `events.yaml` и чужие файлы не править (нашлась ошибка — написать в отчёте).
   - Дописывать **только в конец**: `lila-db/SOURCES.md` (одна строка источника), `PERSONS.md`, `PLACES.md` (новые
     теги; перед добавлением — `git pull` и проверить, не завёл ли тот же тег другой исполнитель).
2. **Сгенерированное не коммитить:** перед коммитом `git checkout -- lila-db/TIMELINE.md lila-db/EVENTS.md lila-db/export`
   (их пересобирает координатор).
3. **Коммит:** `git add <только свои файлы>`; `git commit`; затем
   `git pull -q --rebase --autostash origin claude/book-translation-tesseract-bengali-yaygag && git push -q -u origin claude/book-translation-tesseract-bengali-yaygag`.
   При конфликте в `PERSONS.md`/`PLACES.md`/`SOURCES.md` — оставить обе части (свои строки и чужие), без потерь.
   Push упал — повторить pull+push (до 4 раз с паузами 2, 4, 8, 16 с).
   Подпись коммита:
   `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
   `Claude-Session: https://claude.ai/code/session_01KGC2T1PiSRGJe48WTtGST9`
4. **Проверка:** `python3 lila-db/build.py -w` — 0 ошибок в своих записях (чужие незаконченные ошибки — не трогать,
   упомянуть в отчёте).
5. **Категории (A–D) — по `SOURCES.md`;** уровень источника предложить в строке SOURCES с пояснением; отдельные записи
   понижать с пояснением в `notes`.
6. Временное — только в `/tmp/claude-0/-home-user-Gauranga/7b2c56d5-8710-5f94-af24-6c5c741d0e9d/scratchpad/<код>/`.
