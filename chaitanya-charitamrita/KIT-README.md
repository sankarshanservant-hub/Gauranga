# Автономный комплект: «Шри Чайтанья-чаритамрита» в VS Code (Claude Code), без GitHub

Комплект (`cc-kit-*.zip`) содержит всё, чтобы вести работу над Мадхья-лилой (и остальными главами) на своём
компьютере в том же качестве, что и в облачной сессии: правила, скрипты, шаблоны заданий, глоссарии, все готовые
главы Ади-лилы (образцы и источник цитат), базу лил и **заранее подготовленные сетевые данные** (vedabase, второй OCR
CCBSST, распознанные страницы скана Мадхьи). Сеть при работе нужна только Claude.

## Что внутри
```
cc-kit/
  KIT-README.md            ← этот файл
  gauranga/                ← рабочая папка проекта (открыть её в VS Code)
    CLAUDE.md              ← правила проекта (Claude читает автоматически)
    chaitanya-charitamrita/
      COORDINATOR.md       ← полная инструкция координатора (§ 2а — локальный режим)
      START-local.md       ← первое сообщение для Claude
      MADHYA-NOTES.md      ← карта страниц скана и особенности нумерации по главам Мадхьи
      PLAN.md, TASK-*.md, STYLE-commentary.md, WORKFLOW.md, глоссарии
      vcd/txt/             ← исходники перевода ВЧД (все главы)
      ed/                  ← готовые главы Ади, правки, переводы комментариев, глоссарий
      tools/, tools/coord/, prompts/
      src/                 ← СЮДА положить скан CC_SS.pdf (см. ниже)
    lila-db/               ← база лил
    fonts/                 ← шрифты для PDF
  cc-work/                 ← заранее подготовленное: OCR страниц скана (tsv/txt), CCBSST, атрибуция
```

## Установка (один раз)
1. Распакуйте архив(ы) в одну папку (например, `~/cc-kit`). Если архив разбит на части — распакуйте все в одно место.
2. Положите скан издания Гаудия Матха **`CC_SS.pdf`** (71 872 685 байт, 1079 страниц; ваш Google Диск) в
   `gauranga/chaitanya-charitamrita/src/CC_SS.pdf`. Имя и номера страниц важны: все ссылки «скан с. N» — по нему.
3. Программы:
   - **macOS:** установите Homebrew (brew.sh), затем `brew install python tesseract tesseract-lang poppler git`;
     Google Chrome (для PDF).
   - **Windows:** лучше всего через WSL: `wsl --install` (Ubuntu), в VS Code расширение «WSL», открыть папку
     внутри WSL; дальше всё как в Linux. (Чистый Windows с Git Bash тоже возможен, но tesseract/poppler/python
     придётся ставить вручную.)
   - **Linux / WSL:** `sudo apt install python3 python3-pip tesseract-ocr tesseract-ocr-ben poppler-utils git chromium`
     (или Google Chrome).
   - Затем в папке `gauranga`: `bash chaitanya-charitamrita/tools/coord/setup.sh` — проверит всё и доставит
     Python-пакеты (Pillow, PyYAML, python-docx, PyMuPDF). Последние строки должны показать: tesseract с ben,
     размер CC_SS.pdf, путь к Chrome. Если Chrome не найден — `export CHROME="/путь/к/chrome"`.
4. **История и сохранность без GitHub:** в папке `gauranga` выполните `git init && git add -A && git commit -m "Комплект"`
   (если папка уже не git-репозиторий). Скрипты коммитят каждый шаг локально; пушат, только если вы сами подключите
   удалённый репозиторий. Регулярно копируйте папку `cc-kit` в облако/на диск — это ваша резервная копия.
5. **VS Code:** установите расширение Claude Code, войдите в свой аккаунт, откройте папку `gauranga`.
   Для долгой работы удобно разрешить Claude запускать команды без подтверждения в этой папке
   (режим «auto»/«accept edits» — по вкусу).
6. Первое сообщение Claude — текст из `gauranga/chaitanya-charitamrita/START-local.md`.

## Где результат
- Книги: `gauranga/chaitanya-charitamrita/ed/pdf/CC_<Глава>-full.pdf` (RU) и `…-full-en.pdf` (EN), а также `…-text…` (PDF готовых глав Ади в комплект не входят — пересобрать любую: `bash tools/coord/finish.sh Adi05`).
- Тексты: `ed/vcd/CC_<Глава>.md` (RU), `ed/en/CC_<Глава>.md` (EN), комментарии — `ed/ru|en/<Глава>-apb.md`, `-anu.md`.
- Вернуть работу в общий репозиторий позже: заархивировать папку `gauranga` (или `git bundle`) и передать.
