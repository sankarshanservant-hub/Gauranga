/* Постраничная вёрстка в браузере: стихи по одному заливаются во фрейм страницы, пока не переполнят его.
   Специальные директивы плана: spread (панорама на двух страницах), float (вырезная фигура с обтеканием),
   page (страница со сценой), break. Чётность: стр. 1 — правая (recto), далее чередование. */
const MM = 96 / 25.4;
const G = { W: 210, H: 297, top: 25, bot: 26, inner: 26, outer: 19 };
const P = DATA.profiles;
const root = document.getElementById('book');
const pages = [];
const log = [];
let cur = null, pendingSpread = null, spreadRight = null, pendingFloats = [];

const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const sideOf = i => (i % 2 === 0 ? 'recto' : 'verso');
const A = f => `art/${f}`;

function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

function poly(name, side) {
  const p = P[name], n = p.L.length, pts = [];
  if (side === 'fl') {
    pts.push('0% 0%');
    for (let i = 0; i < n; i++) { const y0 = i / n * 100, y1 = (i + 1) / n * 100, x = p.R[i] * 100; pts.push(`${x.toFixed(2)}% ${y0.toFixed(2)}%`, `${x.toFixed(2)}% ${y1.toFixed(2)}%`); }
    pts.push('0% 100%');
  } else {
    pts.push('100% 0%');
    for (let i = 0; i < n; i++) { const y0 = i / n * 100, y1 = (i + 1) / n * 100, x = p.L[i] * 100; pts.push(`${x.toFixed(2)}% ${y0.toFixed(2)}%`, `${x.toFixed(2)}% ${y1.toFixed(2)}%`); }
    pts.push('100% 100%');
  }
  return `polygon(${pts.join(',')})`;
}

/* ---------- декор специальных страниц ---------- */
function titlePage(page) {
  const sky = el('div', 'layer sky'); page.el.appendChild(sky);
  const r = rng(7);
  for (let i = 0; i < 170; i++) {
    const s = el('div', 'star'); const sz = 0.25 + r() * 0.75 * (r() < .1 ? 2 : 1);
    s.style.cssText = `left:${(r() * 100).toFixed(2)}%;top:${(r() * 62).toFixed(2)}%;width:${sz}mm;height:${sz}mm;opacity:${(.35 + r() * .65).toFixed(2)}`;
    page.el.appendChild(s);
  }
  // тёплое свечение факелов
  [[ 34, 150, 60, 'rgba(255,170,70,.55)' ], [ 112, 142, 70, 'rgba(255,150,60,.5)' ], [ 168, 150, 55, 'rgba(255,170,90,.45)' ], [ 105, 175, 130, 'rgba(255,120,120,.22)' ]].forEach(([x, y, d, c]) => {
    const g = el('div', 'glow'); g.style.cssText = `left:${x - d / 2}mm;top:${y - d / 2}mm;width:${d}mm;height:${d}mm;background:${c}`; page.el.appendChild(g);
  });
  page.el.appendChild(el('div', 'ground'));
  const asp = P.nab_devotees.aspect, w = 200, h = w / asp;
  const im = el('img', ''); im.src = A('nab_devotees.png'); im.style.cssText = `position:absolute;left:5mm;width:${w}mm;bottom:19mm;`;
  page.el.appendChild(im);
  const m = DATA.meta;
  page.el.appendChild(el('div', 'tt', `<div class="kick">${m.book}</div><div class="lila">${m.lila}</div>
    <div class="orn"><i></i><s></s><i></i></div><div class="glava">${m.chapter}</div><div class="name">${m.title}</div><div class="by">${m.by}</div>`));
}

function goswamisStage(page, H) {
  const st = el('div', 'stage'); st.style.height = H + 'mm';
  st.style.background = 'linear-gradient(180deg, rgba(246,239,221,0) 0%, #e4d7ee 22%, #b9a6dc 52%, #6f5fb8 82%, #2d2870 100%)';
  const figs = [
    { f: 'rupa_sanatana', h: 56, x: 9, y: 82, cap: 'Рупа и Санатана', halo: '#ffe2a8' },
    { f: 'gopal_bhatta', h: 62, x: 150, y: 80, cap: 'Гопала Бхатта', halo: '#ffd9c8' },
    { f: 'raghunath_bhatta', h: 56, x: 30, y: 16, cap: 'Рагхунатха Бхатта', halo: '#d6e6ff' },
    { f: 'raghunath_jiva', h: 50, x: 103, y: 14, cap: 'Рагхунатха дас и Джива', halo: '#ffe2a8' },
  ];
  figs.forEach(o => {
    const w = o.h * P[o.f].aspect;
    const hl = el('div', 'halo'); const d = Math.max(w, o.h) * 1.15;
    hl.style.cssText = `left:${o.x + w / 2 - d / 2}mm;bottom:${o.y + o.h / 2 - d / 2}mm;width:${d}mm;height:${d}mm;background:radial-gradient(circle, ${o.halo}cc 0%, ${o.halo}00 68%)`;
    st.appendChild(hl);
    const im = el('img', ''); im.src = A(o.f + '.png'); im.style.cssText = `left:${o.x}mm;bottom:${o.y}mm;height:${o.h}mm;filter:drop-shadow(0 1.2mm 1.6mm rgba(30,20,80,.35))`;
    st.appendChild(im);
    const c = el('div', 'cap', o.cap); c.style.cssText = `position:absolute;left:${o.x + w / 2 - 28}mm;width:56mm;bottom:${o.y - 7}mm;color:#ffe9b8`;
    st.appendChild(c);
  });
  page.el.appendChild(st);
}

function panoDecor(page, cfg, half) {
  const asp = P[cfg.pan].aspect, imgH = 420 / asp;
  const bandH = Math.max(cfg.band || 0, imgH);
  const box = el('div', 'pano'); box.style.height = bandH + 'mm';
  const off = half === 'l' ? 0 : -210;
  if (bandH - imgH > 0.5) {
    const ex = el('div', 'ext'); ex.style.cssText = `height:${bandH - imgH + 0.4}mm;left:${off}mm;background-image:url(${A(cfg.pan + '_ext.png')})`; box.appendChild(ex);
  }
  const im = el('img', ''); im.src = A(cfg.pan + '.jpg'); im.style.left = off + 'mm'; box.appendChild(im);
  page.el.appendChild(box);
  return bandH;
}

/* ---------- страницы ---------- */
function makePage(o = {}) {
  const idx = pages.length, sd = sideOf(idx);
  const dark = o.profile === 'finale';
  const e = el('div', 'page ' + (o.kind || 'text') + ' ' + sd + (dark ? ' dark' : ''));
  const pg = { el: e, idx, side: sd, kind: o.kind || 'text', verses: [], reserve: 0, maxV: o.maxV || 99, profile: o.profile || null, tag: [] };
  root.appendChild(e); pages.push(pg);
  if (o.kind === 'title') { titlePage(pg); return pg; }
  let reserve = 0;
  if (o.spread) { reserve = panoDecor(pg, o.spread.cfg, o.spread.half) + 7; pg.tag.push('pano:' + o.spread.cfg.pan + ':' + o.spread.half); }
  if (o.profile === 'goswamis') { goswamisStage(pg, 168); reserve = 168 - 8; pg.tag.push('goswamis'); }
  if (o.profile === 'finale') {
    const bg = el('img', 'layer'); bg.src = A('full_kk_writer.jpg'); bg.style.cssText = 'object-fit:cover'; e.appendChild(bg);
    e.appendChild(el('div', 'layer scrim')); reserve = 120; pg.tag.push('finale');
  }
  pg.reserve = reserve;
  const left = sd === 'recto' ? G.inner : G.outer, right = sd === 'recto' ? G.outer : G.inner;
  const top = o.profile === 'finale' ? 30 : G.top;
  const fr = el('div', 'frame'); fr.style.cssText = `left:${left}mm;right:${right}mm;top:${top}mm;bottom:${G.bot + reserve}mm`;
  e.appendChild(fr); pg.frame = fr;
  if (!dark) {
    const n = idx + 1, m = DATA.meta;
    if (sd === 'verso') e.appendChild(el('div', 'rh l', `<b>${n}</b>&emsp;${m.book} · ${m.lila}`));
    else e.appendChild(el('div', 'rh r', `${m.chapter} · ${m.title}&emsp;<b>${n}</b>`));
    const ln = el('div', 'rhline'); ln.style.cssText = `left:${G.outer}mm;right:${G.outer}mm;`; e.appendChild(ln);
  }
  return pg;
}

function startTextPage() {
  const idx = pages.length;
  if (spreadRight) { const cfg = spreadRight; spreadRight = null; return makePage({ spread: { cfg, half: 'r' } }); }
  if (pendingSpread && sideOf(idx) === 'verso') {
    const cfg = pendingSpread; pendingSpread = null; spreadRight = cfg; return makePage({ spread: { cfg, half: 'l' } });
  }
  return makePage({});
}

function maxBottom(pg) {
  let m = 0;
  pg.frame.querySelectorAll('.verse, .cut').forEach(x => { m = Math.max(m, x.getBoundingClientRect().bottom); });
  return m;
}
const frameBottom = pg => pg.frame.getBoundingClientRect().bottom;
const overflows = pg => maxBottom(pg) > frameBottom(pg) + 0.6;

function finalize(pg, justify) {
  if (!pg) return;
  const vs = [...pg.frame.querySelectorAll(':scope > .verse')];
  const left = (frameBottom(pg) - maxBottom(pg)) / MM;
  pg.leftover = +left.toFixed(1);
  if (justify && vs.length >= 2 && left > 1 && left < 60) {
    const extra = Math.min(left / (vs.length - 1), 8);
    vs.slice(0, -1).forEach(v => { v.style.marginBottom = (7.5 + extra) + 'mm'; });
    pg.justified = +extra.toFixed(1);
  }
}

function buildVerse(v, cfg) {
  const e = el('section', 'verse');
  e.dataset.n = v.n;
  let h = `<div class="vhead"><i></i><b>${v.n}</b><i></i></div>
    <div class="bn">${v.bn.map(l => `<div>${esc(l)}</div>`).join('')}</div>
    <div class="tl">${v.tl.map(esc).join('<br>')}</div><p class="tr">${v.tr}</p>`;
  if (v.note) h += `<p class="note">${esc(v.note)}</p>`;
  e.innerHTML = h;
  (cfg.floats || []).forEach(f => {
    const side = f.side === 'right' ? 'fr' : 'fl';
    let node;
    if (f.arch) {
      node = el('div', `cut arch ${side}`);
      const im = el('img', ''); im.src = A(f.fig + '.jpg'); node.appendChild(im);
      node.style.cssText = `width:${f.w}mm;height:${f.w / P[f.fig].aspect}mm;shape-outside:border-box;shape-margin:${f.sm ?? 5}mm;`;
    } else {
      node = el('img', `cut ${side}`); node.src = A(f.fig + '.png');
      node.style.cssText = `width:${f.w}mm;shape-outside:${poly(f.fig, side)} border-box;shape-margin:${f.sm ?? 4}mm;`;
    }
    node.style.marginTop = (f.mt ?? 0) + 'mm';
    node.style.marginBottom = (f.mb ?? 2) + 'mm';
    if (side === 'fl') node.style.marginLeft = (-(f.hang ?? 0)) + 'mm'; else node.style.marginRight = (-(f.hang ?? 0)) + 'mm';
    if (f.tilt) node.style.transform = `rotate(${f.tilt}deg)`;
    e.insertBefore(node, e.firstChild);
  });
  return e;
}

function place(vEl, v) {
  if (!cur) cur = startTextPage();
  cur.frame.appendChild(vEl);
  if (overflows(cur)) {
    cur.frame.removeChild(vEl);
    if (!cur.frame.children.length) { log.push('ПЕРЕПОЛНЕНИЕ пустой страницы: стих ' + v.n); cur.frame.appendChild(vEl); }
    else {
      finalize(cur, true); cur = startTextPage(); cur.frame.appendChild(vEl);
      if (overflows(cur)) log.push('ПЕРЕПОЛНЕНИЕ новой страницы: стих ' + v.n);
    }
  }
  cur.verses.push(v.n);
  if (cur.verses.length >= cur.maxV) { finalize(cur, false); cur = null; }
}

async function run() {
  // шрифты
  const probe = el('div', '', '<span style="font-family:Gentium">Аа ӣ</span><i style="font-family:Gentium">Аа</i><b style="font-family:Gentium">Аа</b><span style="font-family:NotoBn">বন্দে</span><span style="font-family:Cormorant">Аа</span>');
  document.body.appendChild(probe);
  await document.fonts.ready; await new Promise(r => setTimeout(r, 400)); await document.fonts.ready;
  probe.remove();

  makePage({ kind: 'title' });
  for (const it of DATA.plan) {
    if (it.t === 'verse') {
      const cfg = { floats: pendingFloats }; pendingFloats = [];
      place(buildVerse(it.v, cfg), it.v);
    } else if (it.t === 'spread') {
      if (it.force) { finalize(cur, false); cur = null; }
      pendingSpread = it.cfg;
    } else if (it.t === 'float') {
      pendingFloats.push(it.cfg);
    } else if (it.t === 'break') {
      finalize(cur, false); cur = null;
    } else if (it.t === 'page') {
      finalize(cur, false); cur = null;
      cur = makePage({ profile: it.profile, maxV: it.maxV });
    }
  }
  finalize(cur, false);
  // подгрузка картинок
  await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  window.__report = {
    pages: pages.map(p => ({ n: p.idx + 1, side: p.side, kind: p.kind, verses: p.verses, tag: p.tag, leftover: p.leftover, justified: p.justified })),
    log,
  };
  window.__done = true;
}
run();
