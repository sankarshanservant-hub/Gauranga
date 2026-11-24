# Выгрузка веб-версии игры в отдельную папку сайта (например HareKrishna public/apps/unseen-guest/app/).
# python3 game/tools/export_site.py <папка назначения>
# Берёт game/web без отладочного (_*.html, .gitignore), index.html оборачивает в полноценный документ
# (в артефакте Claude оболочку добавляет сам артефакт). Сторонних обращений нет: three.js и шрифты — в vendor/.
import os, shutil, sys
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web')
DST = os.path.abspath(sys.argv[1])
KEEP = ['audio.js', 'bg', 'chars', 'codex', 'data', 'masks', 'mcimg', 'portraits', 'proxy', 'snd', 'vendor', 'vision']
os.makedirs(DST, exist_ok=True)
for k in KEEP:
    s, d = os.path.join(SRC, k), os.path.join(DST, k)
    if os.path.isdir(d): shutil.rmtree(d)
    if os.path.isdir(s): shutil.copytree(s, d, ignore=shutil.ignore_patterns('*.md', '.gitignore', '_*'))
    elif os.path.exists(s): shutil.copy2(s, d)
page = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
head = ('<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#140d07">\n'
        '<meta name="description" content="Незримый гость — игра по Гаура-лиле: лила о брахмане-паломнике в доме Джаганнатхи Мишры (Шри Чайтанья-бхагавата, Ади 5).">\n')
open(os.path.join(DST, 'index.html'), 'w', encoding='utf-8').write(head + page + '\n</html>\n')
n = sum(len(f) for _, _, f in os.walk(DST)); sz = sum(os.path.getsize(os.path.join(r, x)) for r, _, f in os.walk(DST) for x in f)
print(f'{DST}: {n} файлов, {sz / 1048576:.1f} МБ')
