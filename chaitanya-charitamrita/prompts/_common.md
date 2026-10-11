Сохранять порциями одной командой (только свои файлы): `git add <файлы> && git commit -q -m "…" -- <файлы> && git pull -q --rebase origin {{BRANCH}} && git push -q origin {{BRANCH}}` (без --autostash; если pull отказывает — просто push). В конце сообщений коммитов:
{{TRAILER}}
Если обрыв — продолжить с места остановки по своим файлам.
