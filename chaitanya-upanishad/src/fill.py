"""Заменяет в ru/*.md и en/*.md строки-метки `@@mula N@@` блоком: девангари + транслитерация
(EN — IAST, RU — кириллица с диакритикой по ../chaitanya-charitamrita/tools/cyr.py). Запуск: python3 src/fill.py"""
import importlib.util, os, re, sys
from indic_transliteration import sanscript
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mula import MULA
spec = importlib.util.spec_from_file_location('cyr', os.path.join(HERE, '..', '..', 'chaitanya-charitamrita', 'tools', 'cyr.py'))
cyr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cyr)
DIG = str.maketrans('0123456789', '०१२३४५६७८९')
VOW = set('aāiīuūṛṝḷeoṁḥ')


def deva_line(s):
    s = s.replace('—', '').strip()
    out = ''
    for i, ch in enumerate(s):          # слитное письмо после согласного на конце слова
        if ch in ' -' and out and out[-1].isalpha() and out[-1] not in VOW and i + 1 < len(s) and s[i + 1].isalpha() \
                and not (out[-1] == 't' and s[i + 1] == 'r'):
            continue
        out += '' if ch == '-' else ch
    out = out.replace(" '", "'").replace("'", 'ऽ')
    out = out.replace('ṁ', 'ṃ')
    d = sanscript.transliterate(out, sanscript.IAST, sanscript.DEVANAGARI)
    return d.replace('|', '।').replace(' ,', ',')


def block(n, lang):
    lines = MULA[n]
    dev = [deva_line(l) for l in lines]
    dev[-1] = dev[-1].rstrip(' ।') + f' ॥ {str(n).translate(DIG)} ॥'
    tr = [l if lang == 'en' else cyr.conv(l)[0] for l in lines]
    tr[-1] = tr[-1].rstrip(' |') + f' || {n} ||'
    return '\n'.join(dev) + '\n\n' + '\n'.join(f'*{t}*' for t in tr)


for lang in ('ru', 'en'):
    d = os.path.join(HERE, '..', lang)
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        t = open(p, encoding='utf-8').read()
        t2 = re.sub(r'^@@mula (\d+)@@$', lambda m: block(int(m.group(1)), lang), t, flags=re.M)
        if t2 != t:
            open(p, 'w', encoding='utf-8').write(t2); print('filled', p)
