/* Вёрстка в браузере: две колонки на странице A4. Поток блоков (ядро стиха, абзацы комментария, рисунки)
   заливается в колонки по очереди; абзацы и перевод стиха переносятся между колонками (не менее 2 строк с каждой
   стороны). Иллюстрации-«якоря» (панорама на развороте, полосы-сцены) привязаны к номеру стиха: вёрстка
   повторяется несколько проходов, пока стих и его иллюстрация не окажутся на одном развороте/странице.
   Стр. 1 — правая (recto). */
const MM = 96 / 25.4;
const G = { top: 20, bot: 17, inner: 21, outer: 17, gap: 7 };
const P = DATA.profiles;
const root = document.getElementById('book');
let pages, log, cur, deferred, versePage, CFG, TIGHT = 1e9;

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const sideOf = i => (i % 2 === 0 ? 'recto' : 'verso');
const A = f => `art/${f}`;
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function img(src, css) { const i = el('img', ''); i.src = src; if (css) i.style.cssText = css; return i; }

function poly(name, side) {
  const p = P[name], n = p.L.length, pts = [side === 'fl' ? '0% 0%' : '100% 0%'];
  for (let i = 0; i < n; i++) {
    const y0 = (i / n * 100).toFixed(2), y1 = ((i + 1) / n * 100).toFixed(2), x = ((side === 'fl' ? p.R[i] : p.L[i]) * 100).toFixed(2);
    pts.push(`${x}% ${y0}%`, `${x}% ${y1}%`);
  }
  pts.push(side === 'fl' ? '0% 100%' : '100% 100%');
  return `polygon(${pts.join(',')})`;
}

/* ---------------- декор ---------------- */
function opener(page) {
  const H = 160;
  const b = el('div', 'op'); b.style.height = H + 'mm';
  b.appendChild(el('div', 'sky'));
  const r = rng(7);
  for (let i = 0; i < 120; i++) {
    const s = el('div', 'star'); const sz = 0.25 + r() * 0.7;
    s.style.cssText = `left:${(r() * 100).toFixed(2)}%;top:${(r() * 70).toFixed(2)}%;width:${sz}mm;height:${sz}mm;opacity:${(.3 + r() * .6).toFixed(2)}`;
    b.appendChild(s);
  }
  const w = 132, h = w / P.nab_devotees.aspect, x = (210 - w) / 2, top = H - 7 - h;
  // свечение факелов (доли ширины/высоты рисунка, измерено по картинке)
  [[0.29, 0.07, 30, 'rgba(255,170,70,.8)'], [0.70, 0.13, 28, 'rgba(255,170,70,.75)'], [0.5, 0.55, 120, 'rgba(255,130,150,.16)']].forEach(([fx, fy, d, c]) => {
    const g = el('div', 'glow'); g.style.cssText = `left:${x + fx * w - d / 2}mm;top:${top + fy * h - d / 2}mm;width:${d}mm;height:${d}mm;background:${c}`; b.appendChild(g);
  });
  const gr = el('div', 'ground'); gr.style.top = (H - 18) + 'mm'; b.appendChild(gr);
  b.appendChild(img(A('nab_devotees.png'), `position:absolute;left:${x}mm;top:${top}mm;width:${w}mm;aspect-ratio:${P.nab_devotees.aspect}`));
  const m = DATA.meta;
  b.appendChild(el('div', 'tt', `<div class="kick">${m.book}</div><div class="lila">${m.lila}</div><div class="glava">${m.chapter}</div><div class="name">${m.title}</div><div class="by">${m.by}</div>`));
  b.appendChild(el('div', 'edge'));
  page.el.appendChild(b);
  return H;
}

function panoDecor(page, c) {
  const asp = P[c.pan].aspect, imgH = 420 / asp, bandH = Math.max(c.band || 0, imgH);
  const box = el('div', 'pano'); box.style.height = bandH + 'mm';
  const off = c.half === 'l' ? 0 : -210;
  if (bandH - imgH > 0.5) { const ex = el('div', 'ext'); ex.style.cssText = `height:${bandH - imgH + 0.4}mm;left:${off}mm;background-image:url(${A(c.pan + '_ext.png')})`; box.appendChild(ex); }
  box.appendChild(img(A(c.pan + '.jpg'), `left:${off}mm`));
  page.el.appendChild(box);
  return bandH;
}

function goswamisBand(page, left, width, compact) {
  const H = compact ? 60 : 76, bottom = G.bot;
  const b = el('div', 'band goswamis'); b.style.cssText = `left:${left}mm;width:${width}mm;height:${H}mm;bottom:${bottom}mm`;
  const figs = [
    { f: 'rupa_sanatana', h: 50, cap: 'Рупа и Санатана' },
    { f: 'raghunath_bhatta', h: 55, cap: 'Рагхунатха Бхатта' },
    { f: 'gopal_bhatta', h: 53, cap: 'Гопала Бхатта' },
    { f: 'raghunath_jiva', h: 47, cap: 'Рагхунатха дас и Джива' },
  ];
  if (compact) figs.forEach(o => { o.h *= 0.76; });
  let ws = figs.map(o => o.h * P[o.f].aspect), gap = 4;
  let tot = ws.reduce((a, c) => a + c, 0) + gap * (figs.length - 1);
  const k = Math.min(1, (width - 10) / tot); ws = ws.map(w => w * k); tot = tot * k;
  let x = (width - tot) / 2;
  figs.forEach((o, i) => {
    const h = o.h * k, w = ws[i];
    const hl = el('div', 'halo'); const d = Math.max(w, h) * 1.1;
    hl.style.cssText = `left:${x + w / 2 - d / 2}mm;bottom:${11 + h / 2 - d / 2}mm;width:${d}mm;height:${d}mm;background:radial-gradient(circle, rgba(255,235,190,.75) 0%, rgba(255,235,190,0) 66%)`;
    b.appendChild(hl);
    b.appendChild(img(A(o.f + '.png'), `left:${x}mm;bottom:11mm;height:${h}mm;filter:drop-shadow(0 1mm 1.2mm rgba(30,20,80,.35))`));
    const cw2 = Math.max(w + 4, 27); const c = el('div', 'cap', o.cap); c.style.cssText = `left:${x + w / 2 - cw2 / 2}mm;width:${cw2}mm;bottom:2mm;line-height:1.15;font-size:7pt`; b.appendChild(c);
    x += w + gap * k;
  });
  page.el.appendChild(b);
  return H + 5;
}

function vaishnavaBanner(page) {
  const H = 58;
  const b = el('div', 'band banner'); b.style.cssText = `left:0;top:0;width:210mm;height:${H}mm;overflow:visible`;
  b.appendChild(el('div', 'bg'));
  const r = rng(11);
  for (let k = 0; k < 70; k++) { const s = el('div', 'star'); const sz = .3 + r() * .5; s.style.cssText = `left:${(r() * 100).toFixed(1)}%;top:${(r() * 34).toFixed(1)}mm;width:${sz}mm;height:${sz}mm;opacity:${(.3 + r() * .6).toFixed(2)}`; b.appendChild(s); }
  b.appendChild(el('div', 'edge'));
  const ids = ['va_1', 'vb_3', 'va_2', 'vb_6', 'va_4', 'vb_1'], hs = [41, 38, 44, 39, 42, 38];
  const ws = ids.map((f, i) => hs[i] * P[f].aspect), gap = 1, tot = ws.reduce((a, c) => a + c, 0) + gap * 5;
  let x = (210 - tot) / 2;
  ids.forEach((f, i) => { b.appendChild(img(A(f + '.png'), `left:${x}mm;top:${H - hs[i] + 5}mm;height:${hs[i]}mm;filter:drop-shadow(0 1.2mm 1.2mm rgba(20,10,60,.45))`)); x += ws[i] + gap; });
  page.el.appendChild(b); page.el.classList.add('lightrh');
  return H + 9;
}

function finalPage() {
  const idx = pages.length;
  const e = el('div', 'page final ' + sideOf(idx)); root.appendChild(e);
  pages.push({ el: e, idx, side: sideOf(idx), tag: ['final'], cols: [] });
  e.appendChild(img(A('full_kk_writer.jpg'), 'position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover'));
  e.appendChild(el('div', 'layer scrim'));
  const v = DATA.verses[DATA.verses.length - 1];
  const cm = (v.comm || []).map(c => c.items.map((it, i) => `<p class="qc">${i === 0 ? `<span class="lbl">${c.label}.</span> ` : ''}${it.h}</p>`).join('')).join('');
  e.appendChild(el('div', 'quote', `<div class="vh"><span>Стих ${v.n}</span></div><div class="bnq">${v.bn.map(esc).join('<br>')}</div><div class="tlq">${v.tl.map(esc).join('<br>')}</div><div class="ruq">${v.tr}</div>${cm}`));
  pages[pages.length - 1].colVerses = [[v.n], []];
}

/* ---------------- страницы и колонки ---------------- */
function makePage(idx) {
  const sd = sideOf(idx);
  const e = el('div', 'page ' + sd);
  root.appendChild(e);
  const pg = { el: e, idx, side: sd, tag: [], cols: [], colVerses: [[], []] };
  pages.push(pg);
  let top = G.top, bottom = G.bot, headers = true;
  const left = sd === 'recto' ? G.inner : G.outer, right = sd === 'recto' ? G.outer : G.inner;
  const width = 210 - left - right;
  if (idx === 0) { top = opener(pg) + 6; headers = false; pg.tag.push('opener'); }
  for (const d of (CFG[idx] || [])) {
    if (d.type === 'pano') { bottom = G.bot - 8 + panoDecor(pg, d) + 6; pg.tag.push('pano:' + d.pan + ':' + d.half); }
    if (d.type === 'goswamis') { bottom = G.bot + goswamisBand(pg, left, width, d.compact); pg.tag.push('goswamis'); }
    if (d.type === 'banner') { top = vaishnavaBanner(pg); pg.tag.push('banner'); }
  }
  const cw = (width - G.gap) / 2;
  [left, left + cw + G.gap].forEach(l => {
    const c = el('div', 'col'); c.style.cssText = `left:${l}mm;width:${cw}mm;top:${top}mm;bottom:${bottom}mm`; e.appendChild(c); pg.cols.push(c);
  });
  if (headers) {
    const n = idx + 1, m = DATA.meta;
    if (sd === 'verso') e.appendChild(el('div', 'rh l', `<b>${n}</b>&emsp;${m.book} · ${m.lila}`));
    else e.appendChild(el('div', 'rh r', `${m.chapter} · ${m.title}&emsp;<b>${n}</b>`));
    const ln = el('div', 'rhline'); ln.style.cssText = `left:17mm;right:17mm`; e.appendChild(ln);
  }
  return pg;
}

function colBottom(c) { return c.getBoundingClientRect().bottom; }
function contentBottom(c) {
  let m = c.getBoundingClientRect().top;
  c.querySelectorAll(':scope > *, .cut').forEach(x => { m = Math.max(m, x.getBoundingClientRect().bottom); });
  return m;
}
const fits = c => contentBottom(c) <= colBottom(c) + 0.6;

function justifyCol(c) {
  if (cur.page.idx >= TIGHT) return;
  const slack = (colBottom(c) - contentBottom(c)) / MM;
  if (slack <= 0.5 || slack > 45) return;
  let pts = [...c.querySelectorAll(':scope > .vend, :scope > .colfig')];
  const last = c.lastElementChild; let usable = pts.filter(p => p !== last);
  // нет межстиховых пробелов — растягиваем перед разделами комментария
  const secs = [...c.querySelectorAll(':scope > .cm.first, :scope > .vcore')].filter(p => p !== c.firstElementChild);
  if (!usable.length || slack / usable.length > 12) usable = usable.concat(secs);
  if (!usable.length) return;
  const add = Math.min(slack / usable.length, 10);
  const set = (p, v) => { if (p.classList.contains('vend')) p.style.height = v ? (4.2 + v) + 'mm' : ''; else if (p.classList.contains('colfig')) p.style.marginBottom = v ? (3.5 + v) + 'mm' : ''; else p.style.marginTop = v ? (parseFloat(getComputedStyle(p).marginTop) / MM + v) + 'mm' : ''; };
  usable.forEach(p => set(p, add));
  if (!fits(c)) usable.forEach(p => set(p, 0));
}

function nextCol() {
  justifyCol(cur.col);
  if (cur.ci === 0) cur = { page: cur.page, ci: 1, col: cur.page.cols[1] };
  else { const pg = makePage(pages.length); cur = { page: pg, ci: 0, col: pg.cols[0] }; }
  // отложенные рисунки — в начало новой колонки
  const keep = [];
  for (const b of deferred) { cur.col.appendChild(b.el); if (!fits(cur.col)) { cur.col.removeChild(b.el); keep.push(b); } }
  deferred = keep;
}

/* разбиение HTML абзаца по словам с сохранением тегов */
function tokens(html) { return html.match(/<[^>]+>|[^<\s]+|\s+/g) || []; }
function cutHTML(tk, k) { // первые k слов | остальное
  let words = 0, i = 0; const stack = [];
  for (; i < tk.length; i++) {
    const t = tk[i];
    if (/^\s+$/.test(t)) { if (words >= k) break; continue; }
    if (t[0] === '<') { if (t[1] === '/') stack.pop(); else if (!t.endsWith('/>')) stack.push(t); continue; }
    words++;
  }
  const head = tk.slice(0, i).join('') + stack.slice().reverse().map(o => '</' + o.match(/^<(\w+)/)[1] + '>').join('');
  const tail = stack.join('') + tk.slice(i + 1).join('');
  return [head, tail];
}
const lineH = p => parseFloat(getComputedStyle(p).lineHeight);
const linesOf = p => Math.round(p.getBoundingClientRect().height / lineH(p));

function splitBlock(col, node, kind, free) {
  if (kind === 'head' || kind === 'gloss') return null;
  const p = kind === 'core' ? node.querySelector('.tr') : node;
  if (!p) return null;
  const r = splitText(col, node, kind, p);
  if (r || kind !== 'core' || free < 30) return r;
  // крайняя мера: стих (оригинал + транслитерация) внизу колонки, перевод — в начале следующей
  const note = node.querySelector('.note');
  p.remove(); if (note) note.remove();
  if (fits(col)) { const wrap = el('div', 'vcore cont'); wrap.appendChild(p); if (note) wrap.appendChild(note); return wrap; }
  node.appendChild(p); if (note) node.appendChild(note);
  const tl = node.querySelector('.tl');
  if (tl && free >= 34) {
    const moved = [...node.children].slice([...node.children].indexOf(tl));
    moved.forEach(x => x.remove());
    if (fits(col)) { const wrap = el('div', 'vcore cont'); moved.forEach(x => wrap.appendChild(x)); return wrap; }
    moved.forEach(x => node.appendChild(x));
  }
  return null;
}

function splitText(col, node, kind, p) {
  const full = p.innerHTML, tk = tokens(full);
  const nWords = tk.filter(t => !/^\s+$/.test(t) && t[0] !== '<').length;
  const L = linesOf(p);
  if (L < 4) return null;
  const ok = k => { p.innerHTML = cutHTML(tk, k)[0]; return fits(col) && linesOf(p) >= 2 && linesOf(p) <= L - 2; };
  let lo = 0, hi = nWords - 1;
  while (lo < hi) { const mid = Math.ceil((lo + hi) / 2); if (ok(mid)) lo = mid; else hi = mid - 1; }
  if (lo < 2 || !ok(lo)) { p.innerHTML = full; return null; }
  const [head, tail] = cutHTML(tk, lo);
  p.innerHTML = head; p.classList.add('split-a');
  const rest = el('p', kind === 'core' ? 'tr cont' : 'cm cont', tail);
  if (kind === 'core') {
    const note = node.querySelector('.note');
    if (note) { const wrap = el('div', 'vcore cont'); wrap.appendChild(rest); wrap.appendChild(note); return wrap; }
  }
  return rest;
}

function place(b) {
  if (b.kind === 'gap') { if (!cur.col.children.length) return; if (cur.page.idx >= TIGHT) b.el.style.height = '1.6mm'; cur.col.appendChild(b.el); if (!fits(cur.col)) cur.col.removeChild(b.el); return; }
  if (b.kind === 'fig') { cur.col.appendChild(b.el); if (!fits(cur.col)) { cur.col.removeChild(b.el); deferred.push(b); } return; }
  let node = b.el;
  for (let g = 0; g < 12; g++) {
    const free = (colBottom(cur.col) - contentBottom(cur.col)) / MM;
    cur.col.appendChild(node);
    const isStart = node === b.el;
    if (fits(cur.col)) { if (isStart && b.v) mark(b.v); return; }
    const rest = splitBlock(cur.col, node, isStart ? b.kind : 'para', free);
    if (rest) { if (isStart && b.v) mark(b.v); nextCol(); node = rest; continue; }
    cur.col.removeChild(node);
    if (!cur.col.children.length) { log.push('не помещается в пустую колонку: ' + (b.v ? 'стих ' + b.v.n : b.kind)); cur.col.appendChild(node); if (isStart && b.v) mark(b.v); return; }
    nextCol();
  }
}
function mark(v) { versePage[v.n] = cur.page.idx; cur.page.colVerses[cur.ci].push(v.n); }

/* ---------------- блоки ---------------- */
function floatNode(f) {
  const side = f.side === 'right' ? 'fr' : 'fl';
  let node;
  if (f.arch) {
    node = el('div', `cut arch ${side}`); node.appendChild(img(A(f.fig + '.jpg')));
    node.style.cssText = `width:${f.w}mm;height:${f.w / P[f.fig].aspect}mm;shape-outside:border-box;shape-margin:${f.sm ?? 3.5}mm;`;
  } else {
    node = img(A(f.fig + '.png'), `width:${f.w}mm;aspect-ratio:${P[f.fig].aspect};shape-outside:${poly(f.fig, side)} border-box;shape-margin:${f.sm ?? 3}mm;`);
    node.className = `cut ${side}`;
  }
  node.style.marginTop = (f.mt ?? 0) + 'mm'; node.style.marginBottom = (f.mb ?? 1.5) + 'mm';
  return node;
}

function itemBlocks(items, label, out) {
  items.forEach((it, i) => {
    const lab = (i === 0 && label) ? `<span class="lbl">${label}.</span> ` : '';
    if (it.t === 'poem') {
      if (lab) out.push({ kind: 'head', el: el('p', 'cm first', lab) });
      out.push({ kind: 'head', el: el('p', 'poem', it.h) });
    } else out.push({ kind: it.t === 'gloss' ? 'gloss' : 'para', el: el('p', 'cm' + (i === 0 ? ' first' : '') + (it.t === 'gloss' ? ' gloss' : ''), lab + it.h) });
  });
}

function buildBlocks() {
  const out = [];
  const I = DATA.intro || {};
  if (I.summary && I.summary.length) {
    out.push({ kind: 'head', el: el('div', '', `<div class="sumh">Краткое содержание главы</div><div class="sums">«Амрита-праваха-бхашья» Шрилы Бхактивиноды Тхакура</div>`) });
    I.summary.forEach((it, i) => out.push({ kind: 'para', el: el('p', 'cm' + (i === 0 ? ' drop' : ''), it.h) }));
  }
  if (I.apbPoem && I.apbPoem.length) {
    out.push({ kind: 'head', el: el('div', 'sums poemh', 'Вступительные стихи «Амрита-праваха-бхашьи»') });
    I.apbPoem.forEach(it => out.push({ kind: 'head', el: el('p', 'poem', it.h) }));
  }
  if (I.anuPoem && I.anuPoem.length) {
    out.push({ kind: 'head', el: el('div', 'sums poemh', 'Вступительные стихи «Анубхашьи» Шрилы Бхактисиддханты Сарасвати') });
    I.anuPoem.forEach(it => out.push({ kind: 'head', el: el('p', 'poem', it.h) }));
  }
  if (out.length) out.push({ kind: 'gap', el: el('div', 'vend') });
  const list = DATA.final ? DATA.verses.slice(0, -1) : DATA.verses;
  for (const v of list) {
    const core = el('section', 'vcore');
    core.innerHTML = (v.sub ? `<div class="sub">${v.sub}</div>` : '') +
      `<div class="vh"><span>Стих ${v.n}</span></div><div class="bn">${v.bn.map(l => `<div>${esc(l)}</div>`).join('')}</div>` +
      `<div class="tl">${v.tl.map(l => `<div>${esc(l)}</div>`).join('')}</div><p class="tr">${v.tr}</p>` +
      (v.note ? `<p class="note">${esc(v.note)}</p>` : '');
    if (v.floats && v.floats.length) { core.classList.add('hasfloat'); const vh = core.querySelector('.vh'); v.floats.forEach(f => vh.after(floatNode(f))); }
    out.push({ kind: 'core', el: core, v });
    for (const c of (v.comm || [])) itemBlocks(c.items, c.label, out);
    (v.figs || []).forEach(f => {
      const d = el('div', 'colfig'); d.appendChild(img(A(f.fig + '.png'), `aspect-ratio:${P[f.fig].aspect}`));
      if (f.cap) d.appendChild(el('div', 'cap', f.cap));
      out.push({ kind: 'fig', el: d });
    });
    out.push({ kind: 'gap', el: el('div', 'vend') });
  }
  return out;
}

/* ---------------- проходы ---------------- */
function layout() {
  root.innerHTML = ''; pages = []; log = []; deferred = []; versePage = {};
  const p0 = makePage(0); cur = { page: p0, ci: 0, col: p0.cols[0] };
  for (const b of buildBlocks()) place(b);
  let guard = 0; while (deferred.length && guard++ < 5) nextCol();
  if (DATA.final) finalPage();
}

const spreadOf = i => Math.floor((i + 1) / 2);   // 0 — открытие; далее пары (1,2), (3,4)…
function withAnchor(cfg, a, c) {
  const n = JSON.parse(JSON.stringify(cfg));
  if (a.type === 'spread') {
    (n[c] ||= []).push({ type: 'pano', pan: a.pan, band: a.band, half: 'l' });
    (n[c + 1] ||= []).push({ type: 'pano', pan: a.pan, band: a.band, half: 'r' });
  } else (n[c.p ?? c] ||= []).push({ type: a.type, compact: !!c.compact });
  return n;
}
const busy = (cfg, i) => (cfg[i] || []).length > 0;
function okAnchor(a, c, q) { return a.type === 'spread' ? (q === c || q === c + 1) : spreadOf(q) === spreadOf(c.p); }

/* якоря — по порядку текста; для каждого перебираем ближайшие варианты и берём первый, где стих и иллюстрация
   оказались на одном развороте */
function placeAnchors() {
  CFG = {}; const status = []; let runs = 0;
  for (const a of DATA.anchors) {
    layout(); runs++;
    const p = versePage[a.verse];
    let cands;
    if (a.type === 'spread') { const L = p % 2 === 1 ? p : p - 1; cands = [L, L + 2, L - 2]; }
    else cands = [{ p }, { p, compact: 1 }, { p: p - 1 }, { p: p - 1, compact: 1 }, { p: p + 1 }];
    cands = cands.filter(c => { const q = c.p ?? c; return q >= 1 && !busy(CFG, q) && !(a.type === 'spread' && busy(CFG, q + 1)); });
    let best = null, bestQ = null, bestD = 1e9;
    const base = CFG;
    for (const c of cands) {
      CFG = withAnchor(base, a, c); layout(); runs++;
      const q = versePage[a.verse];
      if (okAnchor(a, c, q)) { best = c; bestQ = q; bestD = 0; break; }
      const d = Math.abs(spreadOf(q) - spreadOf(c.p ?? c));
      if (d < bestD) { best = c; bestQ = q; bestD = d; }
    }
    CFG = best == null ? base : withAnchor(base, a, best);
    status.push(`${a.id}: стих ${a.verse} → стр. ${bestQ + 1}; иллюстрация на стр. ${(best?.p ?? best) + 1}${a.type === 'spread' ? '–' + (best + 2) : (best?.compact ? ' (компактная)' : '')}${bestD ? ' (НЕ СОВПАЛО)' : ''}`);
  }
  layout(); runs++;
  return { status, runs };
}

async function run() {
  const probe = el('div', '', '<span style="font-family:Gentium">Аа ӣ</span><i style="font-family:Gentium">Аа</i><b style="font-family:Gentium">Аа</b><span style="font-family:NotoBn">বন্দে</span><span style="font-family:Cormorant">Аа</span>');
  document.body.appendChild(probe);
  await document.fonts.ready; await new Promise(r => setTimeout(r, 300)); await document.fonts.ready;
  probe.remove();
  const { status, runs } = placeAnchors();
  const passes = runs;
  // хвост главы: если последняя текстовая страница почти пуста — уплотнить две предыдущие
  const lastText = pages.filter(p => !p.tag.includes('final')).pop();
  const used = lastText.cols.reduce((a, c) => a + (contentBottom(c) - c.getBoundingClientRect().top) / MM, 0);
  if (lastText.idx > 2 && used < 45) { TIGHT = lastText.idx - 2; layout(); log.push('хвост уплотнён со стр. ' + (TIGHT + 1)); }
  await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  window.__report = {
    passes, anchors: status, log,
    pages: pages.map(p => ({ n: p.idx + 1, side: p.side, tag: p.tag, cols: p.colVerses || [],
      fill: (p.cols || []).map(c => +((colBottom(c) - contentBottom(c)) / MM).toFixed(1)) })),
  };
  window.__done = true;
}
run();
