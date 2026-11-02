#!/usr/bin/env python3
"""Подготовка иллюстраций для художественного издания ЧЧ (Ади 1).

Исходники (папка пользователя на Google Drive «Gauralila new», см. README.md) лежат в SRC (по умолчанию —
каталог рядом с этим файлом: art-edition/_src/). Скрипт делает из них рабочие файлы в art/:
  * панорамы (JPEG, 6000 px по ширине) — для разворотов;
  * фигуры на прозрачном фоне (PNG) — из слоёв PSD (нижний чёрный слой «Фон» отбрасывается),
    групповые листы режутся на отдельные фигуры по связным компонентам;
  * profiles.json — по каждой фигуре: пропорции и левый/правый контур по строкам (для обтекания текстом).

Запуск:  python3 -I prepare_art.py [SRC]
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_src')
OUT = os.path.join(HERE, 'art')
os.makedirs(OUT, exist_ok=True)
PROFILES = {}


def psd_cutout(path):
    """Все слои PSD, кроме нижнего слоя-фона, на прозрачном холсте; обрезка по контенту."""
    from psd_tools import PSDImage
    p = PSDImage.open(path)
    W, H = p.size
    layers = list(p)
    drop = set()
    b = layers[0].bbox
    if b[0] <= 0 and b[1] <= 0 and b[2] >= W and b[3] >= H:
        drop.add(id(layers[0]))
    im = p.composite(layer_filter=lambda l: id(l) not in drop and l.is_visible(), force=True).convert('RGBA')
    return im.crop(im.getchannel('A').getbbox())


def flat_psd_rgba(path):
    im = Image.open(path).convert('RGBA')
    return im.crop(im.getchannel('A').getbbox())


def fit(im, m):
    if max(im.size) > m:
        r = m / max(im.size)
        im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)
    return im


def profile(im, rows=60):
    """Левая/правая граница силуэта по рядам (доли ширины, 0..1) и пропорция."""
    a = np.array(im.getchannel('A')) > 24
    h, w = a.shape
    L, R = [], []
    for i in range(rows):
        y0, y1 = int(i * h / rows), int((i + 1) * h / rows)
        band = a[y0:max(y1, y0 + 1)].any(axis=0)
        xs = np.where(band)[0]
        if len(xs):
            L.append(round(xs[0] / w, 4)); R.append(round((xs[-1] + 1) / w, 4))
        else:
            L.append(None); R.append(None)
    # пустые ряды — берём ближайшие
    def fill(v):
        last = None
        for i in range(len(v)):
            if v[i] is None: v[i] = last
            else: last = v[i]
        nxt = None
        for i in reversed(range(len(v))):
            if v[i] is None: v[i] = nxt
            else: nxt = v[i]
        return v
    return {'aspect': round(w / h, 4), 'L': fill(L), 'R': fill(R)}


def save_fig(name, im, m=1800):
    im = fit(im, m)
    im.save(os.path.join(OUT, name + '.png'), optimize=True)
    PROFILES[name] = profile(im)
    print('fig', name, im.size)
    return im


def split_components(im, expect=None, dil=2):
    """Разрез листа на отдельные фигуры. Метки считаются на маске, уменьшенной в 6 раз (быстро);
    dil — расклейка в пикселях уменьшенной маски (фигуры, у которых части не соприкасаются, склеиваются)."""
    K = 6
    A = im.getchannel('A')
    small = np.array(A.resize((max(1, im.width // K), max(1, im.height // K)), Image.BOX)) > 8
    d = ndi.binary_dilation(small, structure=np.ones((3, 3)), iterations=dil)
    lab, n = ndi.label(d)
    areas = ndi.sum(small, lab, index=range(1, n + 1))
    order = sorted(range(1, n + 1), key=lambda i: -areas[i - 1])
    if expect: order = order[:expect]
    print('   компонент:', n, 'берём', len(order), [int(areas[i - 1]) for i in order])
    lab_full = np.array(Image.fromarray(lab.astype(np.int32)).resize(im.size, Image.NEAREST))
    out = []
    for lbl in order:
        mask = lab_full == lbl
        arr = np.array(im)
        arr[..., 3] = np.where(mask, arr[..., 3], 0)
        piece = Image.fromarray(arr)
        piece = piece.crop(piece.getchannel('A').getbbox())
        ys, xs = np.where(small & (lab == lbl))
        out.append((int(xs.min()) * K, int(ys.min()) * K, piece))
    return out


def src(*p):
    return os.path.join(SRC, *p)


def crops():
    """Вырезки из панорам в полном разрешении: полностраничная иллюстрация и арка с Божеством."""
    im = Image.open(src('kk_writes_chch.jpg')).convert('RGB')
    H = im.height
    w = round(H * 210 / 297)
    x0 = 11250
    im.crop((x0, 0, x0 + w, H)).save(os.path.join(OUT, 'full_kk_writer.jpg'), quality=92, optimize=True)
    print('full_kk_writer', w, H)
    im = Image.open(src('dhameshvar_.jpg')).convert('RGB')
    H = im.height
    c = im.crop((3720, 0, 5800, H))
    c.save(os.path.join(OUT, 'arch_deity.jpg'), quality=92, optimize=True)
    PROFILES['arch_deity'] = {'aspect': round(c.width / c.height, 4)}
    print('arch_deity', c.size)


def main():
    if len(sys.argv) > 2 and sys.argv[2] == 'split':
        old = os.path.join(OUT, 'profiles.json')
        if os.path.exists(old): PROFILES.update(json.load(open(old)))
        for tag, f in [('va', 'vaishnavas.psd')]:
            sheet = psd_cutout(src(f))
            ps = split_components(sheet, 6, dil=1)
            ps.sort(key=lambda t: (round(t[1] / (sheet.height / 2.2)), t[0]))
            for i, (x, y, p) in enumerate(ps): save_fig(f'{tag}_{i+1}', p, 1500)
            del sheet
        ms = psd_cutout(src('murali_svarupa.psd'))
        for i, (x, y, p) in enumerate(sorted(split_components(ms, 2, dil=1), key=lambda t: t[0])): save_fig(f'ms_{i+1}', p)
        crops(); json.dump(PROFILES, open(old, 'w'), ensure_ascii=False); return
    if len(sys.argv) > 2 and sys.argv[2] == 'crops':
        old = os.path.join(OUT, 'profiles.json')
        if os.path.exists(old): PROFILES.update(json.load(open(old)))
        crops(); json.dump(PROFILES, open(old, 'w'), ensure_ascii=False); return
    # ---- панорамы ----
    for name, f, w in [('pan_kk', 'kk_writes_cc.jpg', 6000), ('pan_dhameshvar', 'dhameshvar_.jpg', 6000),
                       ('pan_kazi', 'kazi.jpg', 6000)]:
        im = Image.open(src(f)).convert('RGB')
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(os.path.join(OUT, name + '.jpg'), quality=90, optimize=True)
        PROFILES[name] = {'aspect': round(im.width / im.height, 4)}
        print('pan', name, im.size)
        if name == 'pan_kazi':
            # «надставка» неба над узкой панорамой: верхний ряд пикселей, растянутый вверх с затуханием в прозрачность
            row = im.crop((0, 0, im.width, 6)).resize((im.width, 1), Image.BOX)
            row = row.filter(ImageFilter.GaussianBlur(40)) if False else row
            arr = np.array(row.resize((im.width, 1)))[0].astype(np.float32)
            k = 150
            arr = np.stack([ndi.uniform_filter1d(arr[:, c], k, mode='nearest') for c in range(3)], axis=1)
            H = 520
            ext = np.zeros((H, im.width, 4), np.uint8)
            ext[..., :3] = arr[None, :, :].astype(np.uint8)
            t = np.linspace(0, 1, H) ** 1.6
            ext[..., 3] = (t * 255).astype(np.uint8)[:, None]
            Image.fromarray(ext).save(os.path.join(OUT, 'pan_kazi_ext.png'), optimize=True)

    # ---- Кришнадас: молится / пишет ----
    k = psd_cutout(src('krishnadas.psd'))
    parts = split_components(k, 2)
    parts.sort(key=lambda t: t[0])
    save_fig('krishnadas_pray', parts[0][2])
    save_fig('krishnadas_write', parts[1][2])

    # ---- шесть Госвами ----
    save_fig('rupa_sanatana', flat_psd_rgba(src('rupa_sanatana.psd')))
    rj = psd_cutout(src('raghunath_jiva.psd'))
    save_fig('raghunath_jiva', rj)
    for i, (x, y, p) in enumerate(sorted(split_components(rj, 2), key=lambda t: t[0])):
        save_fig(f'rj_{i+1}', p)
    save_fig('gopal_bhatta', psd_cutout(src('gopal_bhatta.psd')))
    save_fig('raghunath_bhatta', flat_psd_rgba(src('raghunath_bhatta.psd')))
    rs = flat_psd_rgba(src('rupa_sanatana.psd'))
    for i, (x, y, p) in enumerate(sorted(split_components(rs, 2), key=lambda t: t[0])):
        save_fig(f'rs_{i+1}', p)

    # ---- вайшнавы (по 6 фигур на листе) ----
    for tag, f in [('va', 'vaishnavas.psd'), ('vb', 'vaishnavas2.psd')]:
        sheet = psd_cutout(src(f))
        ps = split_components(sheet, 6, dil=1)
        # порядок: ряды сверху вниз, слева направо
        ps.sort(key=lambda t: (round(t[1] / (sheet.height / 2.2)), t[0]))
        for i, (x, y, p) in enumerate(ps):
            save_fig(f'{tag}_{i+1}', p, 1500)

    # ---- Мурари Гупта и Сварупа Дамодара ----
    ms = psd_cutout(src('murali_svarupa.psd'))
    save_fig('murari_svarupa', ms)
    for i, (x, y, p) in enumerate(sorted(split_components(ms, 2), key=lambda t: t[0])):
        save_fig(f'ms_{i+1}', p)

    # ---- прочее ----
    save_fig('haridas', psd_cutout(src('haridas.psd')))
    save_fig('shachi', psd_cutout(src('shashi.psd')))
    save_fig('nab_devotees', psd_cutout(src('nab_devotees1.psd')), 3200)

    crops()
    json.dump(PROFILES, open(os.path.join(OUT, 'profiles.json'), 'w'), ensure_ascii=False)
    print('done')


if __name__ == '__main__':
    main()
