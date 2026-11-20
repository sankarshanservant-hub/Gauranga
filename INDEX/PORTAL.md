# Книги Gauranga для портала (harekrishna.info) — что выкладывать (решения пользователя, 2026-11-20)

Ветка с готовыми книгами: `claude/book-translation-tesseract-bengali-yaygag`. Книги — собранные файлы
`<папка>/<Имя>-{ru,en}[-full].{md,docx,pdf}`: в них сноски уже очищены от рабочих пометок (OCR, «по скану», PDF, файлы).
Если брать тексты прямо из `<папка>/{ru,en}/*.md` — прогнать сноски через `clean_md(md, lang)` из `rasika-mangala/build.py`.
Полка «Жизнь Шри Чайтаньи» — по категориям достоверности (буквы A–D — в `site/content/books.yaml` ветки
`claude/sweet-mccarthy-zc94y0` и в `lila-db/SOURCES.md`).

## Выкладывать (основное)
| Книга | Папка / файлы | RU | EN | Достов. |
|---|---|---|---|---|
| Шри Чайтанья-чаритамрита (выверенный перевод ВЧД, все лилы) | `chaitanya-charitamrita/ed/vcd-rev/`, `ed/en-rev/`; книги — `ed/docx`, `ed/pdf` | да | да | A |
| Кадача Мурари Гупты | `murari-gupta/Murari-Gupta-Kadacha-*` | да | да | A |
| Махакавья Кави Карнапуры | `karnapura-mahakavya/Mahakavya-*` | да | да | A |
| Чайтанья-чандродая | `chaitanya-chandrodaya/Chaitanya-Chandrodaya-*` | да | да | A |
| Гаура-ганоддеша-дипика | `gaura-ganoddesha/Gaura-Ganoddesha-Dipika-*` | да | да | A |
| Чайтанья-чандрамрита | `chaitanya-chandramrita/Chaitanya-Chandramrita-*` | да | да | A |
| Джаганнатха-валлабха | `jagannatha-vallabha/Jagannatha-Vallabha-*` | да | да | A |
| Стотры о Гауре | `stotras/Gaura-Stotras-*` | да | да | A |
| Чайтанья-мангала Лочана Даса | `lochana/Lochana-Chaitanya-Mangala-*` | да | да | B |
| Бхакти-ратнакара | `bhakti-ratnakara/Bhakti-Ratnakara-*` | да | да | B |
| Нароттама-виласа | `narottama-vilasa/Narottama-Vilasa-*` | да | да | B |
| Расика-мангала | `rasika-mangala/Rasika-Mangala-*` | да | да | B |
| Сарвабхаума-шатака | `sarvabhauma-shataka/Sarvabhauma-Shataka-*` | да | да | D |

## Выкладывать с предисловием-оговоркой (поздние жития, предания линий)
Джаянанда, Адвайта-пракаша, Према-виласа, Нитьянанда-вамша-вистара, Карнананда, Анурагавалли, Гаура-чарита-чинтамани,
Джагадиша-чаритра-виджая, Гаура-кришнодая, Махабхава-пракаша, Вайшнава-лиламрита, Пата-нирная, Шакха-нирнаямрита
(папки — одноимённые; оговорки — в предисловии каждой книги).

## Гаудия Матх
- Саньял, «Sree Krishna Chaitanya» (1933): `sanyal/Sanyal-Sree-Krishna-Chaitanya-{ru,en}.*`. Пометки «[?]» разобраны
  (журнал — `sanyal/review/QMARKS-resolved.md`); обложка — титульный лист изд. 1933 г. `sanyal/cover-1933-title.png`
  (на нём библиотечный штамп).

## Не выкладывать сейчас
- Пады современников (`padas/`) — решение пользователя: не выкладывать (в т. ч. нагари-пады, главы 27–34).
- Говинда-кадача (`govinda-kadacha/`) — подлинность спорная (D).
- Дивакара Дас (`divakara-jagannatha-charitamrita/`) — D, переведена часть.
- Иные традиции (`vallabha/`) — не о Махапрабху.
- Очерки о спутниках (`parshadas/`) — наши своды, не переводы: отдельная полка, если понадобится.
