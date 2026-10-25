"""Markdown наших переводов → HTML для сайта (читалка, статьи о спутниках).

Каждый блок получает класс слоя, чтобы читатель включал и выключал слои:
  l-orig     — оригинал (деванагари / бенгальское письмо);
  l-translit — транслитерация;
  l-wbw      — пословный перевод (и подстрочник ЧЧ: строки транслитерации + строки значений);
  l-text     — перевод и прочий текст;
  l-notes    — примечания: сноски, «Прим.», разночтения (строки `>>`).
Переносы строк: короткие строки (стихи) — <br>; длинные строки прозы, перенесённые по ширине, — склеиваются.
Номера стихов **N.** получают якорь id="v-N" (первое вхождение), чтобы на стих можно было сослаться.
"""
import html
import re

INDIC = re.compile('[ऀ-෿]')
IAST = re.compile('[āīūṛṝḷṣśṇṅñṭḍḥṁṃẏ]')
CYR_DIACR = re.compile('[̀-ͯ]|[ӣӯ]')
FN_REF = re.compile(r'\[\^([^\]]+)\]')
FN_DEF = re.compile(r'^\[\^([^\]]+)\]:\s?(.*)$')
NUM = re.compile(r'^(?:>\s*)?\*\*([0-9][0-9.:a-z+–-]*?)\.\*\*\s*')
HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
LABELS_WBW = ('**Пословно:**', '*Пословно:*', '**Word-for-word:**', '*Word for word:*', '*Word-for-word:*',
              '**Word for word:**', '*Word-for-word*:', '*Пословно*:')
LABELS_TR = ('**Перевод.**', '**Translation.**')
LABELS_NOTE = ('**Прим.**', '**Note.**', '**Примечание.**')


def inline(s, fnmap=None):
    """Строчная разметка: **ж**, *к*, ссылки → текст, сноски → верхний индекс."""
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = html.escape(s, quote=False)
    s = re.sub(r'\[([^\]]+)\]\((?:[^()]|\([^)]*\))+\)', r'\1', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)

    def fn(m):
        k = m.group(1)
        if fnmap is None or k not in fnmap:
            return ''
        return f'<sup class="fn l-notes"><a href="#fn-{fnmap[k]}" data-fn="{fnmap[k]}">{fnmap[k]}</a></sup>'
    return FN_REF.sub(fn, s)


def join_lines(lines):
    """Длинные строки прозы склеиваются, короткие (стихи) и строки с двумя пробелами в конце — с <br>."""
    if not lines:
        return ''
    long_ = sum(1 for x in lines if len(x.rstrip()) >= 95)
    prose = len(lines) > 1 and long_ >= (len(lines) - 1) * 0.6
    out = []
    for i, x in enumerate(lines):
        hard = x.endswith('  ')
        x = x.strip()
        if i:
            out.append(' ' if (prose and not out_hard) else '\n')
        out.append(x)
        out_hard = hard
    return ''.join(out)


def classify(text, lines):
    t = text.strip()
    for lab in LABELS_WBW:
        if t.startswith(lab):
            return 'wbw', t[len(lab):].strip()
    for lab in LABELS_TR:
        if t.startswith(lab):
            return 'text', t[len(lab):].strip()
    for lab in LABELS_NOTE:
        if t.startswith(lab):
            return 'notes', t
    if t.startswith('>>'):
        return 'notes', re.sub(r'^>>\s?', '', t, flags=re.M)
    bare = re.sub(r'[\s\d.,;:!?|()\[\]«»“”"\'‘’—–\-॥।৷*#]', '', t)
    if bare and len(INDIC.findall(bare)) / len(bare) > .6:
        return 'orig', t
    plain = t.replace('*', '')
    if CYR_DIACR.search(plain) and len(lines) >= 2 and not NUM.match(t):
        # подстрочник ЧЧ: строка транслитерации, строка значений, …
        return 'wbw', t
    if CYR_DIACR.search(plain) and not re.search('[а-яё]{4,}\\s+[а-яё]{4,}\\s+[а-яё]{4,}', re.sub('[̀-ͯ]', '', plain).lower()):
        return 'translit', t
    if t.startswith('*') and t.rstrip().endswith('*') and IAST.search(t) and not NUM.match(t):
        return 'translit', t
    return 'text', t


def render(md, fnmap_out=None, lang='ru'):
    """md → (title, html). Сноски — в конце (раздел «Примечания», слой l-notes)."""
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    lines = md.split('\n')
    # сноски: определения (с отступными продолжениями) — отдельно
    defs, body, cur = {}, [], None
    for ln in lines:
        m = FN_DEF.match(ln)
        if m:
            cur = m.group(1); defs[cur] = [m.group(2)]; continue
        if cur and (ln.startswith('    ') or ln.startswith('\t')) and ln.strip():
            defs[cur].append(ln.strip()); continue
        cur = None
        body.append(ln)
    order = []
    for ln in body:
        for k in FN_REF.findall(ln):
            if k in defs and k not in order:
                order.append(k)
    fnmap = {k: str(i + 1) for i, k in enumerate(order)}

    out, title, para, fence, seen_v = [], None, [], None, set()

    def flush():
        nonlocal para
        if not para:
            return
        if all(x.strip() in ('---', '***', '* * *') for x in para):
            out.append('<p class="orn" aria-hidden="true">✦</p>')
            para = []; return
        if para[0].lstrip().startswith('|') and len(para) >= 2 and re.match(r'^\s*\|[\s:|-]+\|\s*$', para[1]):
            rows = [r.strip().strip('|').split('|') for r in para if not re.match(r'^\s*\|[\s:|-]+\|\s*$', r)]
            h = '<div class="tbl"><table>' + ''.join(
                '<tr>' + ''.join(f'<{"th" if i == 0 else "td"}>{inline(c.strip(), fnmap)}</{"th" if i == 0 else "td"}>' for c in r) + '</tr>'
                for i, r in enumerate(rows)) + '</table></div>'
            out.append(h); para = []; return
        if all(re.match(r'^\s*[-*]\s+', x) or x.startswith('  ') for x in para) and re.match(r'^\s*[-*]\s+', para[0]):
            items, curi = [], []
            for x in para:
                if re.match(r'^\s*[-*]\s+', x):
                    if curi: items.append(' '.join(curi))
                    curi = [re.sub(r'^\s*[-*]\s+', '', x)]
                else:
                    curi.append(x.strip())
            if curi: items.append(' '.join(curi))
            out.append('<ul class="l-text">' + ''.join(f'<li>{inline(i, fnmap)}</li>' for i in items) + '</ul>')
            para = []; return
        quote = all(x.startswith('>') and not x.startswith('>>') for x in para)
        src = [re.sub(r'^>\s?', '', x) for x in para] if quote else para
        text = join_lines(src)
        layer, text = classify(text, src)
        anchor = ''
        m = NUM.match(text)
        if m and layer == 'text':
            n = m.group(1)
            if n not in seen_v:
                seen_v.add(n); anchor = f' id="v-{html.escape(n)}"'
            text = f'\x00{n}\x01' + text[m.end():]
        m2 = re.match(r'^\((\d+(?:[–-]\d+)?)\)\s', text) if layer == 'text' and not anchor else None
        if m2:   # ЧЧ: «(N) перевод»
            n = m2.group(1).split('–')[0].split('-')[0]
            if n not in seen_v:
                seen_v.add(n); anchor = f' id="v-{n}"'
            text = f'\x00{m2.group(1)}\x01' + text[m2.end():]
        h = inline(text, fnmap).replace('\n', '<br>')
        h = re.sub('\x00(.*?)\x01', r'<span class="vn">\1</span>', h)
        if layer == 'orig':
            h = h.replace('<i>', '').replace('</i>', '')
        tag = 'blockquote' if quote else 'p'
        out.append(f'<{tag} class="l-{layer}"{anchor}>{h}</{tag}>')
        para = []

    for ln in body:
        if fence is not None:
            if ln.strip().startswith('```'):
                out.append('<p class="l-orig">' + html.escape('\n'.join(fence)).replace('\n', '<br>') + '</p>')
                fence = None
            else:
                fence.append(ln)
            continue
        if ln.strip().startswith('```'):
            flush(); fence = []; continue
        m = HEAD.match(ln)
        if m:
            flush()
            lvl, txt = len(m.group(1)), m.group(2).strip()
            if title is None and lvl == 1:
                title = re.sub(r'\*', '', txt)
                continue
            out.append(f'<h{min(lvl + 1, 6)}>{inline(txt, fnmap)}</h{min(lvl + 1, 6)}>')
            continue
        if not ln.strip():
            flush(); continue
        para.append(ln)
    flush()
    if order:
        out.append(f'<section class="fns l-notes"><h3>{"Примечания" if lang == "ru" else "Notes"}</h3><ol>' + ''.join(
            f'<li id="fn-{fnmap[k]}">{inline(" ".join(defs[k]))}</li>' for k in order) + '</ol></section>')
    if fnmap_out is not None:
        fnmap_out.update(fnmap)
    return title, '\n'.join(out)


def split_sections(md, level):
    """Делит большой md на разделы по заголовкам уровня ≤ level. Сноски всего файла приписываются к каждому разделу
    (рендер возьмёт только упомянутые). → [(заголовок, md раздела)]."""
    lines = md.split('\n')
    fdefs, skip, cur = set(), set(), False   # сноски и их продолжения (строки с отступом)
    for i, ln in enumerate(lines):
        if FN_DEF.match(ln):
            skip.add(i); cur = True
        elif cur and (ln.startswith('    ') or ln.startswith('\t')) and ln.strip():
            skip.add(i)
        else:
            cur = False
    fdefs = [lines[i] for i in sorted(skip)]
    secs, cur_t, cur_l = [], None, []
    for i, ln in enumerate(lines):
        if i in skip:
            continue
        m = HEAD.match(ln)
        if m and len(m.group(1)) <= level:
            if cur_t is not None or any(x.strip() for x in cur_l):
                secs.append((cur_t, cur_l))
            cur_t, cur_l = m.group(2).strip(), [f'# {m.group(2).strip()}']
            continue
        cur_l.append(ln)
    secs.append((cur_t, cur_l))
    fd = '\n'.join(fdefs)
    return [(t, '\n'.join(l) + '\n\n' + fd) for t, l in secs]
