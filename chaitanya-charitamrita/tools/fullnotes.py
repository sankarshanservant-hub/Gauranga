#!/usr/bin/env python3
# Сноски выверки (ed/vcd-rev, ed/en-rev) для полного издания с комментариями: убрать то, что пересказывает
# «Анубхашью», «Амрита-праваха-бхашью» и заголовки издания (сами комментарии идут сразу после стиха),
# оставить редакторское (разночтения изданий, источник цитаты, расхождения с ВЧД, игра слов и т. п.).
import re

COMM = re.compile(r'''^[«“*(]*(
    Анубхашь|АПБ|Амрита-праваха|Заголов(ок|ки|ку)\s+издани|В\s+издании\s+(стих|стихи|шлок\w*)\s+предвар|
    По\s+(«Анубхашь|«Амрита|АПБ|заголовк)|Подзаголов|
    У\s+ВЧД|В\s+ed\s+был|Прежде\s+—|Стих\s+пропущен\s+у|Перевод\s+шлоки\s+\(=|В\s+заголовке\s+издани|Катхасар|
    В\s+издании\s+(этот\s+)?(стих|стихи|шлок\w*)\s+([\d–]+\s+)?предвар|
    \*?Anubhāṣya|\*?Amṛta-pravāha|In\s+the\s+edition,?\s+(this\s+)?(verse|verses)\s+([\d–]+\s+)?(is|are)\s+headed|
    The\s+\*|Vṛndāvana\s+Candra|(The\s+)?[Ee]dition[’']s\s+heading|(The\s+)?[Hh]eadings?\s+(in|of)\s+the\s+edition|
    Edition\s+heading|In\s+the\s+edition\s+the\s+(verse|verses|heading)\s+(is|are)\s+head|In\s+the\s+edition,?\s+the\s+heading|
    By\s+the\s+heading|According\s+to\s+the\s+(Anubhāṣya|Amṛta|heading|edition[’']s\s+heading)|The\s+Anubhāṣya|The\s+Amṛta
)''', re.X)
SPLIT = re.compile(r'(?<=[.;!?»”)])\s+(?=[«“*(]*[A-ZА-ЯЁĀŚṢṚ])')

def trim(text):
    """-> текст сноски для полного издания ('' — сноску снять)"""
    out, drop = [], False
    for seg in SPLIT.split(text.strip()):
        if COMM.match(seg): drop = True
        elif drop and re.match(r'^[«“*(]*(По\s+изданию|В\s+ряде|В\s+других\s+издани|У\s+ВЧД|Источник|Игра\s+слов|'
                                r'Тот\s+же\s+стих|Бенгальский\s+текст|В\s+оригинале|Нумерац|As\s+in\s+the\s+Gau|'
                                r'The\s+Gau|In\s+other\s+editions|Other\s+editions|The\s+source|A\s+play\s+on|'
                                r'The\s+same\s+verse|Numbering|The\s+Bengali|In\s+the\s+original)', seg):
            drop = False
        if not drop: out.append(seg)
    return ' '.join(out).strip()

def apply(md):
    """md главы (тело + '\\n---\\n' + сноски) -> то же, с урезанными сносками; снятые сноски убираются и из текста"""
    body, sep, foot = md.partition('\n---\n')
    if not sep: return md
    keep = {}
    def f(m):
        t = trim(m.group(2))
        if t: keep[m.group(1)] = t; return '[^%s]: %s' % (m.group(1), t)
        return ''
    foot = re.sub(r'^\[\^([\w-]+)\]:\s*(.*)$', f, foot, flags=re.M)
    foot = re.sub(r'\n{3,}', '\n\n', foot)
    body = re.sub(r'\[\^([\w-]+)\](?!:)', lambda m: m.group(0) if m.group(1) in keep else '', body)
    return body + sep + foot

if __name__ == '__main__':
    import sys, glob
    for f in sys.argv[1:]:
        foot = open(f, encoding='utf-8').read().partition('\n---\n')[2]
        for m in re.finditer(r'^\[\^([\w-]+)\]:\s*(.*)$', foot, re.M):
            t = trim(m.group(2))
            print('%s %s\n  WAS: %s\n  NOW: %s' % (f.split('/')[-1], m.group(1), m.group(2)[:300], t[:300] or '—'))
