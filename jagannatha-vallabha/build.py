"""Собирает перевод «Шри Джаганнатха-валлабха-натаки» Рамананды Рая в MD, DOCX и PDF.

Лёгкая версия: ru|en/00.md (предисловие) + 01–05.md (акты) — только перевод.
Полная версия (-full): то же, но перед каждым стихом и песней — санскрит (деванагари), IAST и пословный
перевод из skt/s01–s05.md (поля SKT, WFW — русский пословный, WFW-EN — английский).

Использует функции разбора и вёрстки из ../govinda-kadacha/build.py.
Запуск: python3 build.py [ru|en] (по умолчанию оба).
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

ACTS = ['01', '02', '03', '04', '05']

META = {
    'ru': dict(
        out='Jagannatha-Vallabha-ru',
        title='Шри Джаганнатха-валлабха', author='Рамананда Рай (рус. пер.)',
        head="""# Шри Джаганнатха-валлабха-натака

*«Драма о Возлюбленном Джаганнатхи»*

*Музыкальная драма в пяти актах Рамананды Рая*

*Перевод с санскрита и пракрита на русский*
""",
        full_sub='*Санскритский текст, транслитерация и пословный перевод стихов и песен*',
        toc='Оглавление', verse='Стих', song='Песня', wfw='Пословно', unnum='(Без номера.)', key_unnum='25a',
        unnum_label='Полустишие без номера (3.25а)'),
    'en': dict(
        out='Jagannatha-Vallabha-en',
        title='Sri Jagannatha-vallabha', author='Ramananda Raya (Eng. tr.)',
        head="""# Sri Jagannatha-vallabha-nataka

*"The Drama of the Beloved of Jagannatha"*

*A musical drama in five acts by Ramananda Raya*

*Translated from the Sanskrit and Prakrit*
""",
        full_sub='*Sanskrit text, transliteration and word-for-word translation of the verses and songs*',
        toc='Contents', verse='Verse', song='Song', wfw='Word for word', unnum='(Unnumbered.)', key_unnum='25a',
        unnum_label='Unnumbered half-verse (3.25a)'),
}


def load_skt(act):
    """{ключ: {'skt': [строки], 'wfw': str, 'wfw-en': str, 'song': str}} из skt/sNN.md."""
    res = {}
    path = os.path.join(HERE, 'skt', f's{act}.md')
    if not os.path.exists(path):
        return res
    text = open(path, encoding='utf-8').read()
    for part in re.split(r'^### ', text, flags=re.M)[1:]:
        head, _, body = part.partition('\n')
        rec, cur = {'skt': []}, None
        for line in body.split('\n'):
            if m := re.match(r'^(SKT|VAR|WFW-EN|WFW|SONG):\s*(.*)', line):
                cur = m.group(1).lower()
                if cur != 'skt':
                    rec[cur] = m.group(2).strip()
            elif cur == 'skt' and line.strip():
                rec['skt'].append(line.strip())
            elif cur and cur != 'skt' and line.strip():
                rec[cur] += ' ' + line.strip()
        res[head.strip()] = rec
    return res


def iast(lines):
    from indic_transliteration import sanscript
    return [sanscript.transliterate(l, 'devanagari', 'iast').replace('ṃ', 'ṁ') for l in lines]


def with_skt(text, sk, m, lang):
    out, unnum_done = [], False
    for para in re.split(r'\n\s*\n', text):
        key = None
        if mm := re.match(r'^> \*\*(\d+)\.\*\*', para.strip()):
            key = mm.group(1)
        elif para.strip().startswith('> *' + m['unnum'] + '*') and not unnum_done and m['key_unnum'] in sk:
            key, unnum_done = m['key_unnum'], True
        rec = sk.get(key) if key else None
        if rec and rec['skt']:
            if key == m['key_unnum'] and not key.isdigit():
                out.append(f"### {m['unnum_label']}")
            elif rec.get('song'):
                num = rec['song'].split('—')[0].strip()
                out.append(f"### {m['song']} {num} ({key})")
            else:
                out.append(f"### {m['verse']} {key}")
            out.append('\n'.join(rec['skt']))
            out.append('\n'.join(f'*{l}*' for l in iast(rec['skt'])))
            w = rec.get('wfw-en' if lang == 'en' else 'wfw')
            if w:
                out.append(f"*{m['wfw']}:* {w}")
        out.append(para)
    return '\n\n'.join(out)


def build(lang, full=False):
    m = META[lang]
    out = m['out'] + ('-full' if full else '')
    head = m['head'] + ('\n' + m['full_sub'] + '\n' if full else '')
    pre = open(os.path.join(HERE, lang, '00.md'), encoding='utf-8').read().strip()
    pre = re.sub(r'^# .+\n', '', pre, count=1)
    title0 = open(os.path.join(HERE, lang, '00.md'), encoding='utf-8').read().splitlines()[0].lstrip('# ').strip()
    toc, body = [], []
    for key in ACTS:
        text = open(os.path.join(HERE, lang, key + '.md'), encoding='utf-8').read().strip()
        text = re.sub(r'\[\^([^\]]+)\]', lambda mm: f'[^{key}-{mm.group(1)}]', text)
        toc.append('- ' + text.splitlines()[0].lstrip('# ').strip())
        if full:
            text = with_skt(text, load_skt(key), m, lang)
        body.append(text)
    md = (head + '\n---\n\n## ' + title0 + '\n\n' + pre.replace('\n## ', '\n### ') + '\n\n---\n\n## ' + m['toc'] + '\n\n'
          + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n')
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), m['title'], m['author'])
    print(out, 'ok', len(blocks))


if __name__ == '__main__':
    for lang in sys.argv[1:] or ['ru', 'en']:
        build(lang)
        build(lang, full=True)
