#!/usr/bin/env python3
"""Ади-кханда «Шри Чайтанья-бхагаваты» (изд. Шри Чайтанья Сарасват Матха, рус.) → ed/CB_AdiNN.md.

Из PDF издания (две колонки, InDesign; шрифты Gita*) берутся только стихи: транслитерация (GitaItalic 10.4) и
перевод (GitaBold) с нумерацией «Стих N» / «Стихи N–M». Пояснения (Гаудия-бхашья и др.) не берутся.
Бенгальский текст в PDF — только картинками; распознавание tesseract (ben) даёт ошибки в ~15–20 % строк, поэтому
по умолчанию он в md не включается (флаг --ocr включает распознанный текст — только для черновой сверки).

Запуск (pymupdf — вне репозитория):
  PYTHONPATH=<scratch>/py python3 chaitanya-bhagavata/tools/prep_cb_adi.py CB_Adi_all.pdf [--ocr] [--work DIR]
Без --ocr бенгальский текст берётся из кэша распознавания в --work (если он есть).
"""
import sys, os, re, json, subprocess, argparse
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(HERE, '..', 'ed')

# Шрифт Gita (кодировка cp1251 с заменами) → кириллическая транслитерация с диакритикой (как в ed/vcd ЧЧ)
GITA = {'№': 'а̄', 'Ў': 'ш́', 'ў': 'ш̣', '+': 'н̣', '\\': 'р̣', '=': 'м̇', '%': 'н̇', '{': 'д̣', 'Ї': 'х̣',
        '}': 'т̣', '*': 'н̃', 'Ё': 'ӯ', 'ё': 'ӣ', 'ї': 'А̄', 'Ѕ': 'Ш́', 'ѕ': 'Ш̣', 'ґ': 'Р̣', 'і': 'Ӣ',
        '§': 'Т̣', '™': 'р̣̄'}
LAT2CYR = dict(zip('aceopxyACEOPXKMTHB', 'асеорхуАСЕОРХКМТНВ'))


def norm(t):
    out = []
    for ch in t:
        o = ord(ch)
        if 0xA1 <= o <= 0xFF and ch not in '«»§\xad':        # текст в «латинской» кодировке шрифта → cp1251
            ch = bytes([o]).decode('cp1251')
        out.append(GITA.get(ch, ch))
    t = ''.join(out).replace('\xad', '').replace(' ', ' ').replace('\xa0', ' ').replace('\t', ' ')
    # латинские буквы-двойники внутри кириллических слов
    t = re.sub(r'(?<=[а-яА-ЯёЁ̀-ͯ])[aceopxyACEOPXKMTHB]|[aceopxyACEOPXKMTHB](?=[а-яА-ЯёЁ])',
               lambda m: LAT2CYR[m.group()], t)
    return t


def page_lines(d, pn):
    """строки страницы в порядке чтения: (кол, y, kind, text, info)"""
    p = d[pn]
    raw = []
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            spans = [s for s in l['spans'] if s['text'].strip() or s['text']]
            if not spans: continue
            s0 = spans[0]
            if s0['font'].startswith('CharlemagneStd'): continue           # номер страницы
            if s0['font'].startswith('DSIzmir') and round(s0['size']) == 13: continue  # колонтитул
            if max(s['size'] for s in spans) < 9: continue                  # сноски
            raw.append((l['bbox'], spans))
    imgs = [im for im in p.get_image_info(xrefs=True)]
    xs = [bb[0] for bb, sp in raw if sp[0]['font'].startswith('Gita')]
    L = min(xs) if xs else 43
    thr = 288 if L < 65 else 316
    out = []
    for bb, spans in raw:
        col = 0 if bb[0] < thr else 1
        f0 = spans[0]['font']
        txt = ''.join(s['text'] for s in spans if not s['font'].startswith('Helvetica'))
        if f0.startswith('DSIzmir'):
            out.append((col, bb[1], 'head%d' % round(spans[0]['size']), txt.strip(), None)); continue
        w = {'b': 0, 'n': 0, 'i': 0, 'it': 0}
        for s in spans:
            n = len(s['text'].strip())
            if 'Bold' in s['font']: w['b'] += n
            elif s['size'] < 10.8: w['it'] += n
            elif s['font'] == 'GitaItalic': w['i'] += n
            else: w['n'] += n
        if not txt.strip(): continue
        if w['it'] and not w['b'] and not w['n'] and not w['i']: kind = 'translit'
        elif w['b'] and w['b'] >= w['n']: kind = 'bold'
        elif w['n']: kind = 'normal'
        else: kind = 'italic'
        size = max(s['size'] for s in spans)
        if f0 == 'GitaNormal' and round(size) == 15: kind = 'title'
        out.append((col, bb[1], kind, txt, [round(x) for x in bb]))
    for im in imgs:
        bb = im['bbox']
        if bb[3] - bb[1] < 8 or bb[2] - bb[0] < 40: continue
        col = 0 if (bb[0] + bb[2]) / 2 < thr + 10 else 1
        out.append((col, bb[1], 'img', '', {'xref': im['xref'], 'bbox': [round(x) for x in bb], 'page': pn + 1}))
    out.sort(key=lambda r: (r[0], r[1]))
    return out


def parse(d, first=16, last=724):
    chapters, ch, cur, state = [], None, None, None
    stream = []
    for pn in range(first - 1, last):
        for r in page_lines(d, pn): stream.append((pn + 1,) + r)
    i = 0
    def close():
        nonlocal cur
        if cur: ch['verses'].append(cur)
        cur = None
    while i < len(stream):
        pg, col, y, kind, txt, info = stream[i]
        if kind == 'head24' and txt.startswith('Глава'):
            close(); ch = {'n': int(txt.split()[1]), 'title': '', 'verses': [], 'page': pg}; chapters.append(ch); state = None
        elif kind == 'title' and ch and not ch['title']:
            ch['title'] = norm(txt.strip()).rstrip('.')
        elif kind.startswith('head') and txt.startswith('Конец'):
            pass                                    # «Конец … главы» — в вёрстке может стоять раньше последних стихов
        elif kind.startswith('head') and ch is not None:
            m = re.match(r'Стих[иИ5]?\s*(\d+)(?:\s*[–-]\s*(\d+))?\s*$', txt)
            close()
            if m:
                a, b = int(m.group(1)), int(m.group(2) or m.group(1))
                cur = {'a': a, 'b': b, 'imgs': [], 'translit': [], 'trans': [], 'page': pg}; state = 'verse'
            else: state = None
        elif cur is not None and state in ('verse', 'trans'):
            if kind == 'img' and state == 'verse': cur['imgs'].append(info)
            elif kind in ('translit', 'italic') and state == 'verse': cur['translit'].append(norm(txt).strip())
            elif kind == 'normal' and state == 'verse' and not (cur['imgs'] or cur['translit']):
                pass                                # вводные слова в скобках перед цитатой-стихом — не стих
            elif kind == 'bold': cur['trans'].append(txt); state = 'trans'
            elif kind == 'italic' and state == 'trans':
                # курсивная строка внутри перевода — если дальше снова жирное
                nxt = next((s for s in stream[i + 1:] if s[4] != 'img'), None)
                if nxt and nxt[4] == 'bold': cur['trans'].append(txt)
                else: close(); state = None
            elif kind == 'img' and state == 'trans': pass
            elif state == 'trans': close(); state = None
            elif kind in ('normal', 'italic') and state == 'verse':
                close(); state = None
        i += 1
    close()
    return chapters


WORDS = None
def dehyph(lines, vocab):
    t = ''
    for raw in lines:
        soft = raw.rstrip().endswith('\xad')
        l = norm(raw).rstrip()
        if t.endswith('\x00'):                                   # мягкий перенос в конце прошлой строки
            t = t[:-1] + l.lstrip()
        elif t.endswith('-') and re.search(r'[а-яё\u0300-\u036f]-$', t) and re.match(r'[а-яё]', l):
            a = re.search(r'([\w\u0300-\u036f]+)-$', t).group(1); b = re.match(r'[\w\u0300-\u036f]+', l).group()
            A, B, AB = a.lower(), b.lower(), (a + b).lower()
            if ((A + '-' + B) in vocab['hy'] and len(B) > 2) or (len(A) >= 5 and len(B) >= 5 and A in vocab['w'] and B in vocab['w']
                                                and AB not in vocab['w']):
                t = t + l
            else: t = t[:-1] + l
        else:
            t = (t + ' ' + l.lstrip()) if t else l.lstrip()
        if soft: t = t.rstrip() + '\x00'
    return re.sub(r'\s+', ' ', t.replace('\x00', '')).strip()


def vocab_of(d):
    """слова и пары через дефис, встреченные внутри строк (не на краях) — для решения о переносах"""
    w, hy = set(), set()
    for pn in range(len(d)):
        for line in d[pn].get_text('text').split('\n'):
            line = norm(line).strip()
            toks = list(re.finditer(r'[\w\u0300-\u036f]+(?:-[\w\u0300-\u036f]+)*', line))
            for j, m in enumerate(toks):
                tok = m.group().lower()
                parts = tok.split('-')
                if not (j == len(toks) - 1 and line.endswith('-')):
                    for k in range(len(parts) - 1): hy.add(parts[k] + '-' + parts[k + 1])
                if len(parts) == 1 and 0 < j < len(toks) - 1: w.add(tok)
    return {'w': w, 'hy': hy}


def ocr(d, info, work):
    os.makedirs(work, exist_ok=True)
    key = 'p%d_x%d' % (info['page'], info['xref'])
    txtf = os.path.join(work, key + '.txt')
    if os.path.exists(txtf): return open(txtf, encoding='utf-8').read()
    pix = fitz.Pixmap(d, info['xref'])
    if pix.n > 1 or pix.alpha: pix = fitz.Pixmap(fitz.csGRAY, pix)
    png = os.path.join(work, key + '.png'); pix.save(png)
    subprocess.run(['convert', png, '-resize', '200%', png], check=False)
    r = subprocess.run(['tesseract', png, '-', '-l', 'ben', '--psm', '6'], capture_output=True, text=True)
    t = r.stdout.strip()
    open(txtf, 'w', encoding='utf-8').write(t)
    return t


ORD = ['', 'первая', 'вторая', 'третья', 'четвёртая', 'пятая', 'шестая', 'седьмая', 'восьмая', 'девятая', 'десятая',
       'одиннадцатая', 'двенадцатая', 'тринадцатая', 'четырнадцатая', 'пятнадцатая', 'шестнадцатая', 'семнадцатая']


def clean_bn(t):
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    return lines


def write(chapters, d, work, do_ocr):
    vocab = vocab_of(d)
    stats = []
    for ch in chapters:
        n = ch['n']
        out = ['“Шри Чайтанья-бхагавата”  ', 'Ади-кханда  ', 'Глава %d  ' % n, '**%s**  ' % ch['title'],
               '(Вриндаван Дас Тхакур; рус. пер. — изд. Шри Чайтанья Сарасват Матха)', '',
               '<!-- Стихи по изданию: транслитерация и перевод — текст издания без правок (бенгальский шрифт в PDF — '
               'картинками, не включён). Пояснения издания не включены. Собрано chaitanya-bhagavata/tools/prep_cb_adi.py. -->', '']
        nums = []
        for v in ch['verses']:
            lab = str(v['a']) if v['a'] == v['b'] else '%d–%d' % (v['a'], v['b'])
            nums += list(range(v['a'], v['b'] + 1))
            bn = []
            for im in v['imgs']:
                t = ocr(d, im, work) if do_ocr else ''
                bn += clean_bn(t)
            if bn: out += [l + '  ' for l in bn[:-1]] + [bn[-1], '']
            if v['translit']:
                out += ['*' + l + '*  ' for l in v['translit'][:-1]] + ['*' + v['translit'][-1] + '*', '']
            out += ['**%s.** %s' % (lab, dehyph(v['trans'], vocab)), '']
        open(os.path.join(ED, 'CB_Adi%02d.md' % n), 'w', encoding='utf-8').write('\n'.join(out).rstrip() + '\n')
        gaps = [k for k in range(1, max(nums) + 1) if k not in nums]
        dup = sorted({k for k in nums if nums.count(k) > 1})
        stats.append((n, ch['title'], len(ch['verses']), max(nums), gaps, dup))
    return stats


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('--ocr', action='store_true'); ap.add_argument('--work', default='ocr')
    a = ap.parse_args()
    d = fitz.open(a.pdf)
    chs = parse(d)
    for s in write(chs, d, a.work, a.ocr): print(*s, sep='\t')
