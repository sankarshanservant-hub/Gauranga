# Конвейер на одно лицо (отработан на Мадхавендре, Вишнуприи, Нитьянанде, Гададхаре)

Общие правила — `CLAUDE.md`, `parshadas/TASK.md` (реестр, статьи, стиль, богословие, даты по календарю, verse.py),
`parshadas/CARDS.md` (карточка). Здесь — порядок работы. Тексты книг, бандлы и переводы B в публичный репозиторий
**не класть**.

## Источники
- **B** — рабочий английский перевод главы: `/home/user/gauranga-private/charitavali-en/NNN-<имя>.md` (части `-partN`
  или сводный файл); метки `[B N]` — печатные страницы; печатная + 20…24 = PDF (смещение растёт по книге: ≈ +20 в начале,
  +22 около с. 190, +24 с ~с. 700 — проверяй по колонтитулу). Бенгальский OCR — `/home/user/gauranga-private/ocr/B/pNNNN.txt`
  (NNNN — PDF). Картинка страницы — `pdftoppm -f N -l N -r 90 -png /home/user/Gauranga/sources/associates/files/B.pdf <tmp>/p`.
- **T** (Тиртха, англ.) и **M** (Махайоги, англ.) — OCR `/home/user/gauranga-private/ocr/{T,M}/pNNNN.txt`; оглавления —
  T pdf 18–21 (печатная T = pdf − 32), M pdf 5 (печатный номер M — «Lives of the Saints page N»). Главы о лице в T и M
  найти по оглавлению и колонтитулам (у T колонтитул — имя лица крупными буквами; у M — «Lives of the Saints <имя>»).
- **Подборка без ИИ** (главы целиком + упоминания вне глав, абзац с именем и соседние):
  `python3 parshadas/tools/bundle.py <tmp>/bundle.md --ocr /home/user/gauranga-private/ocr --T '<regex>' --M '<regex>'
  --B '<бенг. regex>' --T-chapter a-b --M-chapter a-b --B-chapter a-b` (главу B в бандле можно не читать — она в
  переводе). Regex — с вариантами написания; отличать тёзок.
- Сведения о лице в готовых реестрах других лиц (`parshadas/facts/*.md`) — сверить и ссылаться («см. @тег F…»).
- Цитаты ЧЧ/ЧБ — `python3 parshadas/tools/verse.py "CC Madhya 1.1" "CB Adi 1.1"` (в переводе B они даны ссылкой и
  первыми/последними словами — проверять, верна ли ссылка автора). События — `lila-db/events*.yaml`, `python3 lila-db/query.py`.

## Этап А — реестр и карточка (один исполнитель)
1. **Проверка перевода B.** OCR теряет целые строки, а перевод в таких местах «сглаживает» текст выдумкой (в главах
   003–004 — на многих страницах). Каждую страницу главы сравнить с бенгальским OCR; где обрыв, пропуск или перевод
   подозрителен — смотреть картинку. Короткие главы (до ~15 с.) — сверить **все** страницы с картинкой; длинные —
   все по OCR + картинки там, где нужно, и не реже каждой 3-й страницы. Факт — по скану, с пометкой «(по скану;
   в рабочем переводе — иначе)». Расхождения — в конец реестра («Где рабочий перевод расходится со сканом») **и** в
   `/home/user/gauranga-private/charitavali-en/NOTES.md` (раздел `## NNN <Имя> — расхождения…`, коммит в приватный
   репозиторий: `git -C /home/user/gauranga-private pull -q origin main`, затем add/commit/push в `main`).
2. **Реестр** `parshadas/facts/<тег>.md` — формат как `parshadas/facts/vishnupriya.md`; все факты всех трёх книг; «лишь
   присутствие» — одной строкой; в конце «Не взято (и почему)». Если в главе B много о другом лице (как глава 004 о
   Гададхаре дасе) — это в «Не взято» с указанием реестра того лица.
3. **Карточка** `parshadas/cards/<тег>.yaml`; `python3 parshadas/tools/cards.py` → 0 ошибок; новые теги — в конец своих
   разделов `lila-db/PERSONS.md` / `PLACES.md`, дубли — `grep -o '^| @[a-z0-9-]*' lila-db/PERSONS.md | sort | uniq -d` → пусто.
4. Очень большие главы (Рупа, Санатана): реестр по частям `parshadas/facts/parts/<тег>-B|T|M.md` (параллельно), затем
   слияние с таблицей соответствия (как у Нитьянанды).

## Этап Б — статья (другой исполнитель, только по реестру и карточке)
`parshadas/ru/<тег>.md`, `parshadas/en/<тег>.md`, `parshadas/review/<тег>-notes.md`; `python3 parshadas/check.py <тег>` → OK;
PDF: `parshadas/tools/build-pdf.sh parshadas/ru/<тег>.md parshadas/<Имя>-ru "<Имя по-русски>"`. Образец стиля — статьи
о Вишнуприи и Гададхаре. Очень большие — в две смены (как у Нитьянанды).

## Сохранность и параллельность
Пиши порциями; после каждой порции — коммит **только своих файлов** (`git add <ф> && git commit -m "…" -- <ф>`), затем
`git pull -q --rebase --autostash origin claude/gracious-shannon-knppn0 && git push -q -u origin claude/gracious-shannon-knppn0`
(при занятом индексе/незавершённом чужом rebase — подождать и повторить). Подпись коммитов:
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` / `Claude-Session: https://claude.ai/code/session_01BwcRnu5BQdqmrpCubezm5n`.
Временное — `/tmp/claude-0/parshadas/<тег>/`.
