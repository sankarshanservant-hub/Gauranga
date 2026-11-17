/* Прототип: писания раскрытой лилы на телефоне — три разных варианта и переключатель (скилл prototype).
   Включается ?proto=sheet (выключается ?proto=off), грузится из index.html только тогда; рабочий код не трогает —
   app.js отдаёт сюда отрисовку (window.GLProto.render) и действия (window.GLApp). Вариант — ?v=1..3, клавиши 1–3, ←/→, R.
   1 «Детенты»  — лист с тремя высотами, как в Картах iPhone: тянуть за полоску (или за список) — выше или ниже.
   2 «Страница» — лила открывается отдельной страницей: большая картинка, крупные строки писаний, смахнуть — назад.
   3 «Полка»    — низкая полка внизу, писания — карточками в ряд, листаются вбок; лента лил остаётся видна целиком. */
(function () {
  'use strict';
  const A = () => window.GLApp, F = () => window.HKFeel;
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  const NAMES = ['Детенты', 'Страница', 'Полка'];
  const en = () => A() && A().lang() === 'en';
  const tr = (ru, e) => (en() ? e : ru);
  let cur = 0, state = null, lastEv = null;

  // ── стили прототипа ──
  const css = `
#gp-root{position:fixed;inset:0;z-index:30;pointer-events:none}
body.is-reading #gp-root{visibility:hidden}
#gp-root>*{pointer-events:auto}
.gp-dim{position:absolute;inset:0;background:#0b0603;opacity:0;pointer-events:none}
.gp-sheet{position:absolute;left:0;right:0;bottom:0;display:flex;flex-direction:column;color:var(--ink);
  background:linear-gradient(#f6e7c4,#eed8a8);border-radius:22px 22px 0 0;box-shadow:0 -14px 44px rgba(0,0,0,.55);
  border-top:1px solid rgba(138,90,43,.45);will-change:transform}
.gp-grip{flex:none;height:22px;display:grid;place-items:center;cursor:grab}
.gp-grip span{width:44px;height:5px;border-radius:3px;background:rgba(107,63,23,.38)}
.gp-hd{flex:none;display:grid;grid-template-columns:1fr auto;align-items:center;gap:2px 10px;padding:0 12px 8px 18px}
.gp-hd b{display:block;font:600 20px/1.12 var(--display);text-wrap:balance}
.gp-hd small{display:block;margin-top:3px;font:italic 14.5px/1.25 var(--body);color:var(--ink-soft)}
.gp-x{width:40px;height:40px;border:0;border-radius:50%;background:rgba(107,63,23,.1);color:var(--ink);font:24px/1 var(--display)}
.gp-x:active{transform:scale(.92)}
.gp-list{list-style:none;margin:0;padding:4px 14px calc(18px + env(safe-area-inset-bottom,0px));display:grid;gap:8px;align-content:start;min-height:0;overscroll-behavior:contain}
.gp-list .book{background:rgba(255,250,236,.78);padding-block:10px;transform:none}
.gp-list .book__t{font-size:17px}.gp-list .book__author{font-size:13.5px}
.gp-list .people-btn{padding-block:10px}
.gp-det .gp-list{flex:1;overflow-y:hidden}
.gp-det.is-top .gp-list{overflow-y:auto}
/* 2 — страница */
.gp-page{position:absolute;inset:0;background:radial-gradient(120% 50% at 50% 22%,#fff1d2,rgba(255,241,210,0) 70%),linear-gradient(#f8ebcd,#efdcb2 60%,#ead3a4);color:var(--ink);will-change:transform;box-shadow:0 -10px 40px rgba(0,0,0,.5)}
.gp-scroll{position:absolute;inset:0;overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch}
.gp-hero{margin:0;box-sizing:border-box;overflow:hidden;height:min(52dvh,440px);display:flex;align-items:center;justify-content:center;padding:calc(env(safe-area-inset-top,0px) + 54px) 24px 10px;;will-change:transform}
.gp-hero img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 18px 26px rgba(80,40,5,.35))}
.gp-hero .ph{width:60%;color:#8a5a2b}
.gp-ph{padding:4px 22px 6px;text-align:center}
.gp-ph .k{margin:0;font:600 12.5px/1 var(--body);letter-spacing:.18em;text-transform:uppercase;color:#8a5a2b}
.gp-ph h2{margin:8px 0 4px;font:600 30px/1.08 var(--display);letter-spacing:-.01em;text-wrap:balance}
.gp-ph p{margin:0;font:italic 16px/1.3 var(--body);color:var(--ink-soft)}
.gp-sec{padding:18px 16px calc(28px + env(safe-area-inset-bottom,0px))}
.gp-sec h3{margin:0 6px 10px;font:600 13px/1 var(--body);letter-spacing:.14em;text-transform:uppercase;color:#8a5a2b}
.gp-sec .gp-list{padding:0;gap:10px}
.gp-sec .book{padding-block:14px;border-radius:12px}
.gp-sec .book__t{font-size:19px}.gp-sec .book__author{font-size:14.5px}
.gp-bar{position:absolute;left:0;right:0;top:0;z-index:2;display:flex;align-items:center;gap:10px;
  padding:calc(env(safe-area-inset-top,0px) + 8px) 12px 8px;transition:background-color .2s,box-shadow .2s}
.gp-bar.is-solid{background:rgba(246,231,196,.86);-webkit-backdrop-filter:blur(16px) saturate(1.5);backdrop-filter:blur(16px) saturate(1.5);box-shadow:0 1px 0 rgba(138,90,43,.25)}
.gp-back{display:inline-flex;align-items:center;gap:4px;height:40px;padding:0 14px 0 8px;border:0;border-radius:999px;background:rgba(255,248,230,.75);color:var(--ink);font:600 17px/1 var(--display)}
.gp-back:active{transform:scale(.95)}
.gp-bar b{flex:1;min-width:0;font:600 18px/1.1 var(--display);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;opacity:0;transition:opacity .2s}
.gp-bar.is-solid b{opacity:1}
/* 3 — полка */
.gp-shelf .gp-hd{padding-bottom:4px}
.gp-rail{display:flex;gap:10px;overflow-x:auto;overscroll-behavior-x:contain;scroll-snap-type:x proximity;scroll-padding-inline:16px;
  padding:6px 16px calc(16px + env(safe-area-inset-bottom,0px));scrollbar-width:none;touch-action:pan-x;
  -webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 28px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 28px),transparent)}
.gp-rail::-webkit-scrollbar{display:none}
.gp-tile{flex:none;scroll-snap-align:start;width:148px;min-height:132px;display:flex;flex-direction:column;align-items:flex-start;gap:6px;text-align:left;
  padding:12px;border-radius:14px;border:1px solid rgba(138,90,43,.35);background:rgba(255,250,236,.82);color:var(--ink);
  box-shadow:0 1px 0 rgba(255,255,255,.5) inset,1px 3px 8px rgba(80,45,10,.16)}
.gp-tile:active{transform:scale(.97)}
.gp-tile .auth{grid-row:auto}
.gp-tile .t{font:600 17px/1.12 var(--display)}
.gp-tile .a{margin-top:auto;font:13px/1.2 var(--body);color:var(--ink-soft)}
.gp-tile--people{background:linear-gradient(rgba(122,61,14,.14),rgba(122,61,14,.24));justify-content:center}
.gp-tile--people .t{font-size:18px}
.gp-tile[aria-current="true"]{background:#5a3416;color:#f8e6c2}
.gp-tile[aria-current="true"] .a{color:#e4c99a}
body.gp-open .ainst,body.gp-open .foot{visibility:hidden}
@media (prefers-reduced-motion:reduce){.gp-bar,.gp-bar b{transition:none}}
/* переключатель вариантов — PICKER.md (скилл prototype), без изменений; сверху, раз варианты живут внизу */
.proto-picker{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:2147483647;display:flex;align-items:center;gap:2px;padding:4px;border-radius:999px;background:rgba(10,10,10,.82);-webkit-backdrop-filter:blur(12px) saturate(1.4);backdrop-filter:blur(12px) saturate(1.4);box-shadow:0 0 0 1px rgba(255,255,255,.08) inset,0 8px 24px rgba(0,0,0,.24),0 2px 6px rgba(0,0,0,.12);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px;line-height:1;-webkit-font-smoothing:antialiased;user-select:none;-webkit-user-select:none}
.proto-picker-highlight{position:absolute;top:4px;left:0;height:28px;border-radius:999px;background:rgba(255,255,255,.12)}
.proto-picker[data-ready] .proto-picker-highlight{transition:transform 250ms cubic-bezier(.23,1,.32,1),width 250ms cubic-bezier(.23,1,.32,1)}
@media (prefers-reduced-motion:reduce){.proto-picker[data-ready] .proto-picker-highlight{transition:none}}
.proto-picker-item{position:relative;display:flex;align-items:center;height:28px;padding:0 12px;border:0;border-radius:999px;background:transparent;color:rgba(255,255,255,.55);font:inherit;cursor:pointer;transition:color 150ms ease-out,transform 160ms cubic-bezier(.23,1,.32,1)}
@media (hover:hover) and (pointer:fine){.proto-picker-item:hover{color:rgba(255,255,255,.85)}}
.proto-picker-item:active{transform:scale(.97)}
.proto-picker-item:focus-visible{outline:2px solid rgba(255,255,255,.4);outline-offset:2px}
.proto-picker-item[data-active]{color:#fff}
.proto-picker-divider{width:1px;height:16px;margin:0 4px;background:rgba(255,255,255,.12)}
.proto-picker-replay{padding:0 10px;font-size:14px}
.proto-picker[data-position="top"]{bottom:auto;top:24px}
.proto-picker[data-position="top"]{top:calc(env(safe-area-inset-top,0px) + 10px)}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  const root = document.createElement('div'); root.id = 'gp-root';
  const ready = () => { if (!root.isConnected) document.body.appendChild(root); };

  // ── общее ──
  function head(ev) {
    const a = A(), tt = a.t();
    return `<header class="gp-hd"><div><b>${a.esc(a.L(ev, 'title'))}</b><small>${[a.when(ev), tt.sources(ev.sources.length)].filter(Boolean).join(' · ')}</small></div>` +
      `<button type="button" class="gp-x" data-gpx aria-label="${tr('Закрыть', 'Close')}">×</button></header>`;
  }
  const velo = (h, ts, k) => { if (h.length < 2 || ts - h[h.length - 1][1] > 80) return 0; const a = h[0], b = h[h.length - 1]; return b[1] > a[1] ? (b[k] - a[k]) / (b[1] - a[1]) * 1000 : 0; };
  // закрыть по жесту/«×»: сначала уйти, потом свернуть лилу (а лента позовёт render(null) — уже пусто)
  function dismiss() { if (!state) return; const s = state; s.hide(() => { s.destroy(); if (state === s) state = null; A().closeLila(); }); }
  root.addEventListener('click', (e) => {
    const t = e.target instanceof Element ? e.target : null; if (!t) return;
    if (t.closest('[data-gpx], .gp-back')) { dismiss(); return; }
    const p = t.closest('[data-people]'); if (p) { A().openPeople(p.dataset.people); return; }
    const b = t.closest('[data-ev][data-src]'); if (b) A().openReader(b.dataset.ev, b.dataset.src);
  });

  // ── 1. Детенты: три высоты, пружина к ближайшей по броску ──
  function mountDetents(ev) {
    ready();
    const dim = document.createElement('div'); dim.className = 'gp-dim';
    const el = document.createElement('section'); el.className = 'gp-sheet gp-det';
    const H = () => Math.round(innerHeight * 0.94);
    el.style.height = H() + 'px';
    root.append(dim, el);
    const fill = (e) => { el.innerHTML = `<div class="gp-grip" aria-hidden="true"><span></span></div>${head(e)}<ul class="gp-list">${A().booksHtml(e)}</ul>`; };
    fill(ev);
    const STOPS = [0.27, 0.52, 0.94];  // видимая доля экрана: заглянуть · обычная · во весь рост
    const yOf = (k) => H() - innerHeight * k;
    let y = H(), anim = null, stop = 1, tch = null;
    const paint = (v) => {
      y = v; el.style.transform = `translate3d(0,${v.toFixed(1)}px,0)`;
      const vis = (H() - v) / innerHeight;  // затемнение ленты — только когда лист выше обычной высоты
      dim.style.opacity = String(Math.max(0, Math.min(1, (vis - STOPS[1]) / (STOPS[2] - STOPS[1]))) * 0.45);
      dim.style.pointerEvents = vis > STOPS[1] + 0.05 ? 'auto' : 'none';
    };
    const go = (k, v, done) => {
      if (anim) anim.stop(); stop = k;
      el.classList.toggle('is-top', k === STOPS.length - 1);
      const to = k < 0 ? H() : yOf(STOPS[k]);
      if (reduced()) { paint(to); if (done) done(); return; }
      anim = F().spring({ from: y, to, velocity: v || 0, response: 0.36, damping: Math.abs(v || 0) > 600 ? 0.86 : 1, onUpdate: paint, onDone: () => { anim = null; if (done) done(); } });
    };
    paint(H()); go(1);
    dim.addEventListener('click', () => go(1));
    const list = () => el.querySelector('.gp-list');
    el.addEventListener('touchstart', (e) => {
      const t = e.touches[0], tg = e.target instanceof Element ? e.target : null;
      tch = { y0: t.clientY, x0: t.clientX, base: y, on: false, dead: false, inList: !!(tg && tg.closest('.gp-list')), h: [] };
      if (anim) { anim.stop(); anim = null; tch.on = true; tch.h.push([0, e.timeStamp, t.clientY]); }
    }, { passive: true });
    el.addEventListener('touchmove', (e) => {
      if (!tch || tch.dead) return;
      const t = e.touches[0], dy = t.clientY - tch.y0;
      if (!tch.on) {
        if (Math.abs(t.clientX - tch.x0) > Math.abs(dy) && Math.abs(t.clientX - tch.x0) > 8) { tch.dead = true; return; }
        // во весь рост список листается сам; лист тянется, только когда список в самом верху и палец идёт вниз
        if (tch.inList && stop === STOPS.length - 1 && !(list().scrollTop <= 0 && dy > 0)) { if (Math.abs(dy) > 6) tch.dead = true; return; }
        if (e.cancelable) e.preventDefault();
        if (Math.abs(dy) < 8) return;
        tch.on = true; tch.y0 = t.clientY; tch.base = y;
      }
      if (e.cancelable) e.preventDefault();
      const raw = tch.base + (t.clientY - tch.y0), top = yOf(STOPS[STOPS.length - 1]);
      paint(raw < top ? top - F().rubber(top - raw, innerHeight) : raw);
      tch.h.push([0, e.timeStamp, t.clientY]); while (tch.h.length > 2 && e.timeStamp - tch.h[0][1] > 100) tch.h.shift();
    }, { passive: false });
    const end = (e) => {
      const c = tch; tch = null; if (!c || !c.on) return;
      const v = velo(c.h, e.timeStamp, 2), proj = (H() - (y + F().project(v))) / innerHeight;
      if (proj < STOPS[0] * 0.55) { dismiss(); return; }
      let best = 0; STOPS.forEach((k, i) => { if (Math.abs(k - proj) < Math.abs(STOPS[best] - proj)) best = i; });
      go(best, v);
    };
    el.addEventListener('touchend', end); el.addEventListener('touchcancel', end);
    return {
      kind: 0,
      update: (e) => { const keep = stop; fill(e); el.classList.toggle('is-top', keep === STOPS.length - 1); },
      hide: (done) => go(-1, 0, done),
      destroy: () => { el.remove(); dim.remove(); },
    };
  }

  // ── 2. Страница: лила во весь экран, большая картинка, крупные строки ──
  function mountPage(ev) {
    ready();
    const el = document.createElement('section'); el.className = 'gp-page';
    root.append(el);
    const fill = (e) => {
      const a = A();
      el.innerHTML = `<div class="gp-scroll"><figure class="gp-hero">${a.figHtml(e.id)}</figure>
        <div class="gp-ph"><p class="k">${tr('Лила', 'Lila')}</p><h2>${a.esc(a.L(e, 'title'))}</h2><p>${a.esc(a.when(e))}</p></div>
        <div class="gp-sec"><h3>${a.esc(a.t().sources(e.sources.length))}</h3><ul class="gp-list">${a.booksHtml(e)}</ul></div></div>
        <header class="gp-bar"><button type="button" class="gp-back" aria-label="${tr('Назад к ленте', 'Back to the ribbon')}">‹ ${tr('Лилы', 'Lilas')}</button><b>${a.esc(a.L(e, 'title'))}</b></header>`;
      const sc = el.querySelector('.gp-scroll'), bar = el.querySelector('.gp-bar'), hero = el.querySelector('.gp-hero');
      sc.addEventListener('scroll', () => {
        const y = sc.scrollTop;
        bar.classList.toggle('is-solid', y > hero.offsetHeight - 70);
        if (!reduced()) hero.style.transform = `translate3d(0,${(y * 0.35).toFixed(1)}px,0)`;  // картинка уходит медленнее текста
      }, { passive: true });
    };
    fill(ev);
    const ctl = F().sheet({ el, size: () => innerHeight, threshold: 0.28, scroller: () => el.querySelector('.gp-scroll'), skip: '.gp-back',
      onClosed: () => { if (!ctl.open && state && state.el === el) { const s = state; s.destroy(); state = null; A().closeLila(); } } });
    ctl.show();
    return {
      kind: 1, el,
      update: (e) => fill(e),
      hide: (done) => { ctl.hide(0, done); },
      destroy: () => el.remove(),
    };
  }

  // ── 3. Полка: низкая, писания — карточками в ряд ──
  function mountShelf(ev) {
    ready();
    const el = document.createElement('section'); el.className = 'gp-sheet gp-shelf';
    root.append(el);
    const fill = (e) => {
      const a = A(), n = (e.persons || []).length;
      const tiles = (n ? `<button type="button" class="gp-tile gp-tile--people" data-people="ev:${e.id}"><span class="t">${tr('Участники', 'Participants')}</span><span class="a">${n} ${tr('спутников', 'associates')}</span></button>` : '') +
        e.sources.map((s) => `<button type="button" class="gp-tile book" data-ev="${e.id}" data-src="${s.id}"><b class="auth auth--${s.authority}">${s.authority}</b><span class="t">${a.esc(a.L(s, 'title'))}</span><span class="a">${a.esc(a.L(s, 'author'))}</span></button>`).join('');
      el.innerHTML = `<div class="gp-grip" aria-hidden="true"><span></span></div>${head(e)}<div class="gp-rail">${tiles}</div>`;
    };
    fill(ev);
    const ctl = F().sheet({ el, threshold: 0.35, skip: '.gp-rail',
      onClosed: () => { if (!ctl.open && state && state.el === el) { const s = state; s.destroy(); state = null; A().closeLila(); } } });
    ctl.show();
    return {
      kind: 2, el,
      update: (e) => { const r = el.querySelector('.gp-rail'); fill(e); if (r) el.querySelector('.gp-rail').scrollLeft = 0; },
      hide: (done) => { ctl.hide(0, done); },
      destroy: () => el.remove(),
    };
  }
  const MOUNT = [mountDetents, mountPage, mountShelf];

  // ── связь с лентой ──
  window.GLProto = {
    render(ev) {
      if (!F() || !A()) return false;
      lastEv = ev || null;
      if (!ev) { if (state) { const s = state; state = null; s.hide(() => s.destroy()); } document.body.classList.remove('gp-open'); return true; }
      document.body.classList.add('gp-open');
      if (state && state.kind === cur) { state.update(ev); return true; }
      if (state) { state.destroy(); state = null; }
      state = MOUNT[cur](ev);
      return true;
    },
  };

  // ── переключатель (PICKER.md) ──
  function picker() {
    const nav = document.createElement('nav'); nav.className = 'proto-picker'; nav.setAttribute('aria-label', 'Prototype variants'); nav.dataset.position = 'top';
    nav.innerHTML = '<span class="proto-picker-highlight" aria-hidden="true"></span>' + NAMES.map((n) => `<button class="proto-picker-item">${n}</button>`).join('') +
      '<span class="proto-picker-divider" aria-hidden="true"></span><button class="proto-picker-item proto-picker-replay" aria-label="Replay animation (R)">↻</button>';
    document.body.appendChild(nav);
    const hl = nav.querySelector('.proto-picker-highlight'), items = [...nav.querySelectorAll('.proto-picker-item:not(.proto-picker-replay)')];
    const move = () => { const el = items[cur]; hl.style.width = el.offsetWidth + 'px'; hl.style.transform = `translateX(${el.offsetLeft}px)`; };
    const remount = () => { if (state) { state.destroy(); state = null; } if (lastEv) window.GLProto.render(lastEv); };
    const set = (i) => {
      if (i < 0 || i >= NAMES.length) return;
      cur = i;
      items.forEach((el, j) => { el.toggleAttribute('data-active', j === i); if (j === i) el.setAttribute('aria-current', 'true'); else el.removeAttribute('aria-current'); });
      nav.dataset.position = i === 1 ? 'bottom' : 'top';  // «Страница» занимает верх (кнопка «Лилы») — переключатель вниз
      move();
      try { const u = new URL(location.href); u.searchParams.set('v', i + 1); history.replaceState(history.state, '', u); localStorage.setItem('glProtoV', String(i + 1)); } catch (e) {}
      remount();
    };
    items.forEach((el, i) => el.addEventListener('click', () => set(i)));
    nav.querySelector('.proto-picker-replay').addEventListener('click', remount);
    addEventListener('resize', move);
    document.addEventListener('keydown', (e) => {
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable || e.metaKey || e.ctrlKey || e.altKey) return;
      const n = parseInt(e.key, 10);
      if (n >= 1 && n <= NAMES.length) set(n - 1);
      else if (e.key === 'ArrowRight') set((cur + 1) % NAMES.length);
      else if (e.key === 'ArrowLeft') set((cur - 1 + NAMES.length) % NAMES.length);
      else if (e.key === 'r' || e.key === 'R') remount();
    });
    let want = 1; try { want = parseInt(new URLSearchParams(location.search).get('v'), 10) || parseInt(localStorage.getItem('glProtoV'), 10) || 1; } catch (e) {}
    set(want >= 1 && want <= NAMES.length ? want - 1 : 0);
    requestAnimationFrame(() => requestAnimationFrame(() => nav.setAttribute('data-ready', '')));
  }
  if (document.body) picker(); else document.addEventListener('DOMContentLoaded', picker);
})();
