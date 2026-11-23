# Веб-версия серого уровня (Three.js)

Тот же уровень, что `game/godot/`, для браузера: страница-артефакт https://claude.ai/artifact/AK1Rn5z9HzNj86oLxuonQZ.
- `index.html` — вся игра (Three.js 0.160 с jsDelivr); фон — `bg/`, прокси-геометрия — `proxy/courtyard_proxy.json`
  (glTF со встроенным буфером: платформа не раздаёт .glb), данные — `data/` (копии из `game/godot/`), `nav.json` —
  сетка проходимости, выгруженная из навмеша Godot (`godot --path game/godot -- --dump-nav=...`).
- Автотест: `?autoplay` в адресе (локально).
