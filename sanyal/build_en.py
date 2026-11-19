"""Английский оригинал Саньяла «Sree Krishna Chaitanya» (1933) по набранному тексту (фрагменты tools/split.py) — MD, DOCX, PDF.
Без SN-I-09-05 (заметки наборщика, которых нет в издании 1933 г.). Запуск: python3 build_en.py"""
import importlib.util, os, re, subprocess, sys, tempfile, glob
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rm', os.path.join(HERE, '..', 'rasika-mangala', 'build.py'))
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
NAMES = {'00-title': 'Title', '00-publisher': 'Publisher’s Preface', '00-preface': 'Preface', '00-contents': 'Contents',
         '00-foreword': 'Foreword (Srila Bhaktisiddhanta Sarasvati)', 'II-00': 'Auspicatory Observance'}
ORDER = ['00-title', '00-publisher', '00-preface', '00-contents', '00-foreword'] + [f'I-{i:02d}' for i in range(1, 10)] + \
        ['II-00'] + [f'II-{i:02d}' for i in range(1, 25)]
def main():
    t = tempfile.mkdtemp()
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'tools', 'split.py'), t], check=True, stdout=subprocess.DEVNULL)
    parts = ['# Sree Krishna Chaitanya', '*Nisikanta Sanyal. Vols. I–II (Sree Gaudiya Math, Madras, 1933), with a Foreword by Srila Bhaktisiddhanta Sarasvati Gosvami*',
             '*The English original, from the retyped text collated with the 1933 scan; later typist’s notes omitted.*', '---']
    for sec in ORDER:
        if sec.startswith('I-'): title = f'Vol. I, Chapter {int(sec[2:])}'
        elif sec.startswith('II-') and sec != 'II-00': title = f'Vol. II, Chapter {int(sec[3:])}'
        else: title = NAMES[sec]
        if sec == 'I-01': parts.append('# Volume I. Introductory')
        if sec == 'II-00': parts.append('# Volume II')
        parts.append(f'## {title}')
        for f in sorted(glob.glob(f'{t}/SN-{sec}-*.txt')):
            if os.path.basename(f) == 'SN-I-09-05.txt': continue
            parts += [p for p in re.findall(r'(?m)^\[\d+\] (.*)$', open(f, encoding='utf-8').read())]
    md = '\n\n'.join(parts) + '\n'
    out = os.path.join(HERE, 'Sanyal-Sree-Krishna-Chaitanya-en')
    open(out + '.md', 'w', encoding='utf-8').write(md)
    rm.kb.build_docx(rm.parse(md), out + '.docx'); rm.lo_pdf(out + '.docx', out + '.pdf')
    print('ok', len(md.split()))
if __name__ == '__main__': main()
