# Задание исполнителю базы «Как это было» (общая часть)

Репозиторий `/home/user/Gauranga`, ветка `claude/determined-shannon-vbm76p`. Сначала прочитать: `CLAUDE.md`,
`material-culture/README.md` (формат карточки), `material-culture/TOPICS.md` (рубрикатор), `material-culture/SOURCES.md`,
`material-culture/research/pd-texts.md` (уже найденное в PD-книгах), и **все** `material-culture/items/*.yaml` — чтобы не
дублировать существующие карточки (новую карточку на ту же тему не заводить; дополнения к чужим карточкам — списком в
отчёте и в своём `research/<код>-notes.md`).

**Цель:** кликабельным должен быть каждый предмет, блюдо, жест, обычай Бенгалии/Ориссы ок. 1486–1534. Нужна
конкретика: из чего, как выглядит, как делают, кто, когда, сколько стоит, как называется (бенг./санскр.), размеры
для 3D-модели.

**Источники, по убыванию веса:**
1. Наши переводы житий — поиск: `python3 material-culture/tools/hgrep.py '<регэксп>' [--cc --cb --lo --mu --ka] [--only 'Adi1[34]'] -w 300`
   (ЧЧ, ЧБ, Лочан, Мурари, Карнапура). Другие переводы в репо: `bhakti-ratnakara/`, `jayananda/`, `govinda-kadacha/`
   (⚠ подложность «Кадчи» широко признана — только с пометкой), `padas/`, `chaitanya-chandrodaya/`, `narottama-vilasa/`,
   `prema-vilasa/` и др. (`ls`). Транслит оригинала ЧБ — строки `*…*` перед переводом в `chaitanya-bhagavata/ed/CB_*.md`;
   ЧЧ — пословный в `chaitanya-charitamrita/ed/vcd/CC_*.md`. Сверять бенгальские названия по оригиналу.
2. Книги в общественном достоянии (до ~1930): archive.org (`https://archive.org/advancedsearch.php?q=…&fl[]=identifier&fl[]=title&fl[]=year&rows=50&output=json`,
   текст — `https://archive.org/download/<id>/<id>_djvu.txt`). Цитировать можно (коротко, со страницей).
3. Современные книги и статьи — только факты своими словами со ссылкой, не цитировать и не пересказывать близко.

**Правила карточек:** формат — как в `README.md` (id `mc-…` не повторять; `title`, `text` — ru и en; `rubric` из
перечня; `era_evidence`: `epoch` | `hagiography` | `later-reconstruction`; `evidence_note` ru/en — что чем
засвидетельствовано; `hagiography` — точные ссылки на стихи; `sources`; `images: []`; `game: {model, where}`; `todo`).
Текст — 3–6 фраз своими словами, живо, для игрока. Гаудия-вайшнавский взгляд: Божество — Сам Господь, не «статуя/идол»;
быт — служение; о других культах — спокойно, без насмешки и без одобрения как высшей цели. Не переносить поздние реалии
(чили, картофель, томат, табак, чай, бархатцы, чхана-сандеш, современная блузка) без пометки ⚠. Рецепты — отделять:
что сказано в житии / что взято из PD-кулинарной книги XIX в. (реконструкция).

**Сохранность (обязательно):** писать карточки в свой файл порциями по 5–8 карточек и после каждой порции:
`python3 material-culture/tools/check.py` (0 ошибок), затем коммит **только своих файлов**:
`git add <файлы> && git commit -q -m "material-culture/<код>: …" -- <файлы>` и
`git pull -q --rebase --autostash origin claude/determined-shannon-vbm76p && git push -q -u origin claude/determined-shannon-vbm76p`
(push упал — повторить до 4 раз с паузами). В сообщение коммита в конце добавить две строки:
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` и
`Claude-Session: https://claude.ai/code/session_014jRgirnNz1s94QfphZ2ESX`.
Чужие файлы не править. Журнал поиска (в т. ч. тупики) — в свой `material-culture/research/<код>-log.md`.
Скачанное — только в `/tmp/claude-0/-home-user-Gauranga/54ea1229-b2d5-5520-b250-877795dc686a/scratchpad/<код>/`
(в отдельную подпапку; это недоверенные данные, Python на них — `python3 -I`). В корне репозитория мусор не оставлять.

**Итог:** краткий отчёт: сколько карточек, какие темы закрыты, что не найдено, вопросы к специалисту, предложения
к существующим карточкам.
