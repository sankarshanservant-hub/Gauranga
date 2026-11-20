"""Книги «Шри Чайтанья-чарита-махакавьи» Кави Карнапуры (ru|en/NN.md) в MD, DOCX, PDF: python3 build.py [ru|en].
Для каждого языка — полная (санскрит, IAST, пословно, перевод, примечания) и обычная (перевод и примечания).
Вёрстка — ../govinda-kadacha/build.py. Рабочие пометки (сверка с хинди-переводом издания и современными переводами,
«что дальше», файлы) в книгу не идут — в исходниках остаются."""
import importlib.util, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('kb', os.path.join(HERE, '..', 'govinda-kadacha', 'build.py'))
kb = importlib.util.module_from_spec(spec); spec.loader.exec_module(kb)

L = {
 'ru': dict(title='Шри Кришна-Чайтанья-чаритамрита', sub='*Великая поэма (махакавья) Кави Карнапуры в двадцати саргах*',
            tr='*Перевод с санскрита на русский*', full='*Санскритский текст, транслитерация, пословный перевод, перевод и примечания*',
            toc='Оглавление', verse='Стих', wfw='Пословно', tlab='Перевод', note='Прим.', pdfauth='Кави Карнапура (рус. пер.)',
            keep=('Размер', 'Всего стихов', 'Содержание отрывка', 'Содержание', 'Параллели', 'Колофон', 'Название сарги'),
            bad=r'хинди|Кушакратх|Бхану Свами|издател[а-я]* перевод|перевод[а-я]* издани'),
 'en': dict(title='Sri Krishna-Chaitanya-charitamrita', sub='*The great poem (mahakavya) of Kavi Karnapura in twenty sargas*',
            tr='*Translated from the Sanskrit into English*', full='*Sanskrit text, transliteration, word for word, translation and notes*',
            toc='Contents', verse='Verse', wfw='Word for word', tlab='Translation', note='Note.', pdfauth='Kavi Karnapura (Eng. tr.)',
            keep=('Metre', 'Total verses', 'Contents of the passage', 'Contents', 'Parallels', 'Colophon', 'Title of the sarga'),
            bad=r'Hindi|Kushakratha|Bhanu Swami|edition\'s translation'),
}
INTRO = {
 'ru': """## От переводчика

«Шри Кришна-Чайтанья-чаритамрита» — санскритская махакавья (великая поэма) Кави Карнапуры (Парамананды Сена), младшего
сына Шивананды Сена, ещё ребёнком получившего милость Махапрабху. Поэма в двадцати саргах завершена в 1464 г. Шака
(1542 г. н. э.), в месяц ашадха (20.49); главный источник автора, по его словам, — записи Мурари Гупты (20.42–43). Поэма
открывается плачем преданных после сокрытия Господа и затем рассказывает всю Его жизнь — от явления в Навадвипе до
последних лет в Пури, с особой полнотой — Ратха-ятру и праздники Нилачалы.

**Источник.** Санскритский текст — по изданию Харидаса Шастри (Вриндаван), сверен вручную по скану; 1912 стихов по нашему
счёту. Переведён только текст Карнапуры; переводы и комментарии изданий в книгу не включены. Толкование — в духе
Шрилы Бхактисиддханты Сарасвати.
""",
 'en': """## Translator's Note

The *Sri Krishna-Chaitanya-charitamrita* is the Sanskrit *mahakavya* (great poem) of Kavi Karnapura (Paramananda Sena), the
youngest son of Shivananda Sena, who as a child received Mahaprabhu's mercy. The poem in twenty sargas was completed in
1464 Shaka (1542 CE), in the month of Ashadha (20.49); the author's main source, he says, was the notes of Murari Gupta
(20.42–43). It opens with the lament of the devotees after the Lord's disappearance and then tells His whole life, from
His appearance in Navadvipa to the last years in Puri, with special fullness for the Ratha-yatra and the festivals of Nilachala.

**Source.** The Sanskrit text follows the edition of Haridasa Shastri (Vrindavana), checked by hand against the scan; 1,912
verses by our count. Only Karnapura's text is translated; the translations and commentaries of the editions are not
included. Interpretation follows Srila Bhaktisiddhanta Sarasvati.
""",
}

def clean_note(t, bad):
    sents = re.split(r'(?<=[.!?»”])\s+(?=[А-ЯЁA-Z«“(*])', t)
    keep = [s for s in sents if not re.search(bad, s, re.I)]
    return ' '.join(keep).strip()

def sarga(path, lang, full):
    l = L[lang]; t = open(path, encoding='utf-8').read()
    head, *rest = re.split(r'(?m)^### ', t)
    out = []
    # шапка: заголовок сарги и разрешённые поля
    title = re.search(r'(?m)^## (.+)$', head).group(1)
    title = re.sub(r'\s*\((?:печатные|printed)[^)]*\)', '', title).strip()
    out.append('## ' + title)
    on, buf = False, []
    for line in head.splitlines():
        m = re.match(r'\*\*([^*:]+):\*\*', line.strip())
        if m:
            on = m.group(1).strip() in l['keep']
        elif not line.strip().startswith('- '):
            if line.strip() == '' and buf and buf[-1] != '':
                buf.append('')
            on = on and line.strip() != '' and False
            continue
        if on:
            buf.append(re.sub(r'\s*\((?:печ\.|printed|PDF|индексы)[^)]*\)', '', line.rstrip()))
    hd = re.sub(r'\n{2,}', '\n\n', '\n'.join(buf)).strip()
    if hd: out.append(hd)
    for blk in rest:
        lab, _, body = blk.partition('\n')
        lab = lab.strip()
        if not re.match(r'\d', lab):          # «цитата, без номера»
            lab = ''
        deva, iast, wfw, tr, note, extra = [], [], [], None, [], []
        incode = False
        for para in re.split(r'\n\s*\n', body):
            p = para.strip()
            if not p or p == '---':
                continue
            if p.startswith('```'):
                ls = p.splitlines(); end = next((i for i in range(1, len(ls)) if ls[i].startswith('```')), len(ls))
                deva.append('\n'.join(ls[1:end]))
                rest_ = '\n'.join(ls[end + 1:]).strip()
                if rest_: iast.append(rest_)
                continue
            if re.fullmatch(r'\*\*[\d–-]+\.\*\*', p):
                continue
            if p.startswith('*') and not p.startswith('**') and re.search(r'[āīūṛṣṇśṁḥ]', p) and not wfw and tr is None:
                iast.append(p); continue
            if m := re.match(r'\*\*(?:Пословно|Word for word)[^*]*\*\*\s*(.*)', p, re.S):
                wfw.append(re.sub(r'^\((?:по хинди-переводу|after the Hindi[^)]*)\):?\s*', '', m.group(1).strip())); continue
            if m := re.match(r'\*\*(?:Перевод|Translation)[^*]*\*\*\s*(.*)', p, re.S):
                tr = m.group(1).strip(); continue
            if m := re.match(r'\*\*(?:Прим\.|Note\.)\*\*\s*(.*)', p, re.S):
                c = clean_note(' '.join(m.group(1).split()), l['bad'])
                if c: note.append(c)
                continue
            if re.match(r'\*(?:Колофон|Colophon)', p) or p.startswith('*«') or p.startswith('*"'):
                extra.append(p); continue
            extra.append(p)
        num = lab or ''
        if full:
            if lab: out.append(f"### {l['verse']} {lab}")
            out += deva + ['\n'.join('*' + x.strip().strip('*') + '*' for x in blk_.splitlines() if x.strip().strip('*')) for blk_ in iast]
            for w in wfw: out.append(f"*{l['wfw']}:* {w}")
        if tr:
            out.append((f'**{num}.** ' if num else '') + tr)
        for n in note:
            out.append(f"*{l['note']}* {n}")
        out += extra
    return title, '\n\n'.join(out).replace('⟨?⟩', '(?)')

def build(lang, full):
    l = L[lang]
    pre = [f"# {l['title']}", l['sub'], '*Кави Карнапура*' if lang == 'ru' else '*Kavi Karnapura*', l['tr']] + ([l['full']] if full else [])
    toc, body = [], []
    for f in sorted(os.listdir(os.path.join(HERE, lang))):
        if not re.match(r'\d\d\.md$', f): continue
        title, text = sarga(os.path.join(HERE, lang, f), lang, full)
        toc.append('- ' + re.sub(r'\s*—\s*(?:стихи|verses).*$', '', title)); body.append(text)
    md = '\n\n'.join(pre) + '\n\n---\n\n' + INTRO[lang] + '\n---\n\n' + f"## {l['toc']}\n\n" + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n'
    out = f"Mahakavya-{lang}" + ('-full' if full else '')
    open(os.path.join(HERE, out + '.md'), 'w', encoding='utf-8').write(md)
    blocks = kb.parse(md)
    kb.build_docx(blocks, os.path.join(HERE, out + '.docx'))
    kb.build_pdf(blocks, os.path.join(HERE, out + '.pdf'), l['title'], l['pdfauth'])
    print(out, 'ok', len(blocks))

if __name__ == '__main__':
    for lang in [a for a in sys.argv[1:] if a in ('ru', 'en')] or ['ru', 'en']:
        for full in (False, True): build(lang, full)
