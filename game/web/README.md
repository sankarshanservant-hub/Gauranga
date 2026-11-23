# Веб-версия серого уровня (Three.js)

Тот же уровень, что `game/godot/`, для браузера: страница-артефакт https://claude.ai/artifact/AK1Rn5z9HzNj86oLxuonQZ.
- `index.html` — вся игра (Three.js 0.160 с jsDelivr); фон — `bg/`, прокси-геометрия — `proxy/courtyard_proxy.json`
  (glTF со встроенным буфером: платформа не раздаёт .glb), данные — `data/` (копии из `game/godot/`), `nav.json` —
  сетка проходимости, выгруженная из навмеша Godot (`godot --path game/godot -- --dump-nav=...`).
- Автотест: `?autoplay` в адресе (локально).

## Персонажи (Mixamo)
`chars/ybot.json` — Y Bot и 28 анимаций Mixamo, собранные `game/tools/pack_mixamo.py` из FBX в папке пользователя на
Google Диске (Gauranga-game, файлы Mixamo). **В репозиторий не кладётся**: по условиям Mixamo ассеты можно использовать в
игре, но не распространять отдельными файлами; репозиторий публичный. Пересобрать: скачать FBX с Диска (имена — как в
`pack_mixamo.py`/`index.html`, клип = имя файла), затем `blender -b -P game/tools/pack_mixamo.py -- <папка> ybot.glb`
и упаковать в JSON (см. историю: glTF с base64-буфером).
