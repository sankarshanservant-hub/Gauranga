/* Лента эпизодов и лил, окно чтения. Данные — data/timeline.json и data/verses/*.json (site/tools/build_data.py). */
(function () {
  'use strict';

  const T = {
    ru: {
      title: 'Гаура-лила', subtitle: 'Лилы Шри Чайтаньи Махапрабху по писаниям',
      jumpLabel: 'Перейти к лиле', ribbon: 'Лента лил',
      hint: 'Листайте ленту. Нажмите на эпизод, чтобы раскрыть его лилы, а на название лилы — чтобы увидеть писания.',
      legend: 'Достоверность источника:', authA: 'канонический', authB: 'принятый традицией', authC: 'с оговорками', authD: 'сомнительный',
      layers: { orig: 'Оригинал', translit: 'Транслитерация', wbw: 'Пословный', text: 'Перевод', notes: 'Примечания' },
      wbw: 'пословно', before: 'до явления', atBirth: 'при рождении',
      yearsOld: (a, b) => a === b ? `${a} ${plural(a, 'год', 'года', 'лет')}` : `${a}–${b} ${plural(b, 'год', 'года', 'лет')}`,
      approx: '≈', yr: ' г.', sources: n => `${n} ${plural(n, 'писание', 'писания', 'писаний')}`,
      lilas: n => `${n} ${plural(n, 'лила', 'лилы', 'лил')}`,
      open: 'раскрыть', fold: 'свернуть',
      noEn: '', close: 'Закрыть', illus: 'Иллюстрация готовится', prev: 'Назад', next: 'Вперёд',
      passages: n => `${n} ${plural(n, 'отрывок', 'отрывка', 'отрывков')}`, loading: 'Загружаю стихи…', failed: 'Не удалось загрузить стихи. Обновите страницу.',
    },
    en: {
      title: 'Gaura-lila', subtitle: 'Pastimes of Sri Chaitanya Mahaprabhu in the scriptures',
      jumpLabel: 'Go to a pastime', ribbon: 'Timeline of pastimes',
      hint: 'Swipe the scroll. Tap an episode to unfold its pastimes, and a pastime’s name to see the scriptures.',
      legend: 'Source reliability:', authA: 'canonical', authB: 'accepted by tradition', authC: 'with reservations', authD: 'doubtful',
      layers: { orig: 'Original', translit: 'Transliteration', wbw: 'Word for word', text: 'Translation', notes: 'Notes' },
      wbw: 'word for word', before: 'before the advent', atBirth: 'at birth',
      yearsOld: (a, b) => a === b ? `age ${a}` : `age ${a}–${b}`,
      approx: 'c.', yr: ' CE', sources: n => `${n} scripture${n === 1 ? '' : 's'}`,
      lilas: n => `${n} pastime${n === 1 ? '' : 's'}`,
      open: 'unfold', fold: 'fold',
      noEn: 'No English translation yet — shown in Russian.', close: 'Close', illus: 'Illustration in preparation', prev: 'Back', next: 'Forward',
      passages: n => `${n} passage${n === 1 ? '' : 's'}`, loading: 'Loading verses…', failed: 'Could not load the verses. Please reload the page.',
    },
  };
  function plural(n, one, few, many) {
    return n % 10 === 1 && n % 100 !== 11 ? one : (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) ? few : many;
  }

  // Иллюстрации: id лилы или эпизода → файл (PNG/WebP с прозрачным фоном). Пока пусто — везде заглушки.
  const IMAGES = {};
  const LAYERS = ['orig', 'translit', 'wbw', 'text', 'notes'];
  const ORN = '<svg class="orn-line" viewBox="0 0 200 10" aria-hidden="true"><path d="M0 5h86M114 5h86" stroke="currentColor" stroke-width=".8"/><path d="M100 1l4 4-4 4-4-4z" fill="currentColor"/></svg>';
  const LOTUS = '<svg class="ph" viewBox="0 0 100 100" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"><circle cx="50" cy="50" r="46" stroke-dasharray="2 4"/><path d="M50 22c8 10 10 22 0 40-10-18-8-30 0-40Z"/><path d="M50 62c5-14 16-22 30-22-3 14-14 23-30 22Z"/><path d="M50 62C34 63 23 54 20 40c14 0 25 8 30 22Z"/><path d="M28 70h44M34 76h32"/></g></svg>';
  const PETALS = Array.from({ length: 16 }, (_, i) => `<path transform="rotate(${i * 22.5} 60 60)" d="M60 4c3 4 3 7 0 10-3-3-3-6 0-10Z" stroke-width=".8"/>`).join('');
  const MEDALLION = n => `<svg class="ph ph--ep" viewBox="0 0 120 120" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-linecap="round"><circle cx="60" cy="60" r="56" stroke-width="1.4"/><circle cx="60" cy="60" r="50" stroke-width=".7" stroke-dasharray="1.5 3.5"/>${PETALS}<path d="M60 30c8 9 10 20 0 36-10-16-8-27 0-36Z" stroke-width="1.2"/><path d="M60 66c5-12 15-19 27-19-3 12-13 20-27 19Z" stroke-width="1.2"/><path d="M60 66c-14 1-24-7-27-19 12 0 22 7 27 19Z" stroke-width="1.2"/><path d="M42 73h36" stroke-width="1.2"/></g><text x="60" y="92" text-anchor="middle" fill="currentColor" font-size="13" font-family="Cormorant Garamond, Georgia, serif" font-weight="600" letter-spacing="1.5">${n}</text></svg>`;

  const S = { data: null, lang: 'ru', layers: { orig: true, translit: false, wbw: false, text: true, notes: false }, ep: null, open: null, reader: null, chunks: {} };
  try {
    const saved = JSON.parse(localStorage.getItem('gl-prefs') || 'null');
    if (saved) { if (saved.lang) S.lang = saved.lang; if (saved.layers) Object.assign(S.layers, saved.layers); }
  } catch (e) { /* хранилище недоступно */ }
  function savePrefs() { try { localStorage.setItem('gl-prefs', JSON.stringify({ lang: S.lang, layers: S.layers })); } catch (e) { /* ничего */ } }

  const $ = id => document.getElementById(id);
  const ribbon = $('ribbon'), track = $('track'), jump = $('jump'), mbooks = $('mbooks');
  const t = () => T[S.lang];
  const L = (o, k) => (S.lang === 'en' && o[k + '_en']) || o[k];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const findEv = id => { for (const ep of S.data.episodes) { const ev = ep.events.find(e => e.id === id); if (ev) return [ep, ev]; } return [null, null]; };
  const findEp = id => S.data.episodes.find(e => e.id === id);
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  function when(o) {
    const y = o.years, a = o.age, tt = t();
    const ys = y ? (y[0] === y[1] ? `${y[0]}` : `${y[0]}–${y[1]}`) : '';
    const approx = o.date_conf === 'оценка' ? tt.approx + ' ' : '';
    let age = '';
    if (o.before) age = tt.before;
    else if (a && a[1] === 0) age = tt.atBirth;
    else if (a) age = tt.yearsOld(a[0], a[1]);
    else if (y) { const a0 = Math.max(0, y[0] - 1486), a1 = Math.max(0, y[1] - 1486); age = a1 === 0 ? tt.atBirth : tt.yearsOld(a0, a1); }
    return [age, ys && approx + ys + tt.yr].filter(Boolean).join(' · ');
  }

  /* ——— лента ——— */
  function fig(id, ph) {
    const img = IMAGES[id];
    return img ? `<img src="${img}" alt="" draggable="false">` : ph + `<span class="sr">${t().illus}</span>`;
  }
  function booksHtml(ev) {
    return ev.sources.map(s => `<li><button type="button" class="book" data-ev="${ev.id}" data-src="${s.id}"><b class="auth auth--${s.authority}" title="${s.authority}">${s.authority}</b><span class="book__t">${esc(L(s, 'title'))}</span><span class="book__author">${esc(L(s, 'author'))}</span></button></li>`).join('');
  }
  function lilaCard(ev) {
    const on = S.open === ev.id, tt = t();
    return `<div class="card${on ? ' is-open' : ''}" id="card-${ev.id}" data-ev="${ev.id}">
      <figure class="card__fig">${fig(ev.id, LOTUS)}</figure>
      <div class="card__cap"><button type="button" class="card__name" aria-expanded="${on}">${esc(L(ev, 'title'))}</button>
      <p class="card__when">${when(ev)}</p><p class="card__count">${tt.sources(ev.sources.length)}</p></div>
      <ul class="books">${on ? booksHtml(ev) : ''}</ul></div>`;
  }
  function roman(n) {
    return [['X', 10], ['IX', 9], ['V', 5], ['IV', 4], ['I', 1]].reduce((s, [r, v]) => { while (n >= v) { s += r; n -= v; } return s; }, '');
  }
  function renderRibbon() {
    const tt = t();
    let h = '<div class="cap cap--start" aria-hidden="true"></div><div class="paper">';
    S.data.episodes.forEach((ep, i) => {
      const on = S.ep === ep.id;
      h += `<div class="episode${on ? ' is-open' : ''}" id="card-${ep.id}" data-ep="${ep.id}">
        <figure class="card__fig">${fig(ep.id, MEDALLION(roman(i + 1)))}</figure>
        <div class="card__cap"><button type="button" class="episode__name" aria-expanded="${on}">${esc(L(ep, 'title'))}</button>
        <p class="card__when">${when(ep)}</p>
        <p class="episode__more">${tt.lilas(ep.events.length)} · <span>${on ? tt.fold : tt.open}</span></p></div></div>`;
      if (on) h += `<div class="chapter" role="group" aria-label="${esc(L(ep, 'title'))}">${ep.events.map(lilaCard).join('')}</div>`;
    });
    h += '</div><div class="cap cap--end" aria-hidden="true"></div>';
    track.innerHTML = h;
    renderMobileBooks();
    jump.innerHTML = `<option value="" disabled>${tt.jumpLabel}…</option>` + S.data.episodes.map(ep => `<optgroup label="${esc(L(ep, 'title'))}">` + ep.events.map(e => `<option value="${e.id}">${esc(L(e, 'title'))}</option>`).join('') + '</optgroup>').join('');
    jump.value = S.open || '';
  }
  function renderMobileBooks() {
    const [, ev] = S.open ? findEv(S.open) : [null, null];
    mbooks.innerHTML = ev ? booksHtml(ev) : '';
    markCurrentBook();
  }

  function xOf(el) { return el.getBoundingClientRect().left - ribbon.getBoundingClientRect().left + ribbon.scrollLeft; }
  function centerOn(id, smooth) {
    const card = $('card-' + id);
    if (!card) return;
    ribbon.scrollTo({ left: xOf(card) + card.offsetWidth / 2 - ribbon.clientWidth / 2, behavior: smooth && !reduced() ? 'smooth' : 'auto' });
  }
  function keepPlace(id, fn) { // перерисовать, не сдвинув элемент id на экране
    const before = id && $('card-' + id), x0 = before ? before.getBoundingClientRect().left : null;
    fn();
    const after = id && $('card-' + id);
    if (after && x0 !== null) ribbon.scrollLeft += after.getBoundingClientRect().left - x0;
  }

  function toggleEpisode(id) {
    const opening = S.ep !== id;
    keepPlace(id, () => { S.ep = opening ? id : null; S.open = null; renderRibbon(); });
    if (S.reader) closeReader();
    history.replaceState(null, '', '#' + id);
    if (opening) {
      const first = $('card-' + findEp(id).events[0].id), ep = $('card-' + id);
      ribbon.scrollTo({ left: xOf(ep) - 24, behavior: reduced() ? 'auto' : 'smooth' });
      if (first) first.querySelector('.card__name').focus({ preventScroll: true });
    }
    updateCenter();
  }
  function openLila(id, smooth = true, force = false) {
    const [ep] = findEv(id);
    if (!ep) return;
    S.open = (S.open === id && !force) ? null : id;
    if (S.ep !== ep.id) { S.ep = ep.id; renderRibbon(); }
    else {
      document.querySelectorAll('.card').forEach(c => {
        const on = c.dataset.ev === S.open;
        c.classList.toggle('is-open', on);
        c.querySelector('.card__name').setAttribute('aria-expanded', on);
        c.querySelector('.books').innerHTML = on ? booksHtml(findEv(c.dataset.ev)[1]) : '';
      });
      renderMobileBooks();
    }
    if (S.open) { jump.value = S.open; history.replaceState(null, '', '#' + S.open); }
    setTimeout(() => S.open && centerOn(S.open, smooth), reduced() ? 0 : 470);
  }

  function updateCenter() {
    const mid = ribbon.getBoundingClientRect().left + ribbon.clientWidth / 2;
    let best = null, bd = Infinity;
    document.querySelectorAll('.card, .episode').forEach(c => {
      const r = c.getBoundingClientRect(), d = Math.abs(r.left + r.width / 2 - mid);
      if (d < bd) { bd = d; best = c; }
    });
    document.querySelectorAll('.is-center').forEach(c => c !== best && c.classList.remove('is-center'));
    if (best) best.classList.add('is-center');
  }

  // перетаскивание мышью; на сенсорных экранах — родная прокрутка
  let drag = null, justDragged = false;
  ribbon.addEventListener('pointerdown', e => {
    if (e.pointerType !== 'mouse' || e.button !== 0) return;
    drag = { x: e.clientX, left: ribbon.scrollLeft, moved: false };
  });
  window.addEventListener('pointermove', e => {
    if (!drag) return;
    const dx = e.clientX - drag.x;
    if (!drag.moved && Math.abs(dx) > 5) { drag.moved = true; ribbon.classList.add('is-drag'); }
    if (drag.moved) ribbon.scrollLeft = drag.left - dx;
  });
  window.addEventListener('pointerup', () => {
    if (drag && drag.moved) { ribbon.classList.remove('is-drag'); justDragged = true; setTimeout(() => { justDragged = false; }, 0); }
    drag = null;
  });
  ribbon.addEventListener('click', e => {
    if (justDragged) { e.preventDefault(); e.stopPropagation(); return; }
    const book = e.target.closest('.book');
    if (book) { openReader(book.dataset.ev, book.dataset.src); return; }
    const name = e.target.closest('.card__name');
    if (name) { openLila(name.closest('.card').dataset.ev); return; }
    const ep = e.target.closest('.episode');
    if (ep) toggleEpisode(ep.dataset.ep);
  }, true);
  ribbon.addEventListener('wheel', e => {
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX) && !e.target.closest('.books')) { ribbon.scrollLeft += e.deltaY; e.preventDefault(); }
  }, { passive: false });
  let raf = 0;
  ribbon.addEventListener('scroll', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(updateCenter); });
  ribbon.addEventListener('keydown', e => {
    if (e.target !== ribbon) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { step(e.key === 'ArrowRight' ? 1 : -1); e.preventDefault(); }
  });
  function step(dir) {
    const items = [...document.querySelectorAll('.card, .episode')];
    let i = Math.max(0, items.indexOf(document.querySelector('.is-center')));
    i = Math.max(0, Math.min(items.length - 1, i + dir));
    centerOn(items[i].dataset.ev || items[i].dataset.ep, true);
  }
  $('prev').addEventListener('click', () => step(-1));
  $('next').addEventListener('click', () => step(1));
  jump.addEventListener('change', () => openLila(jump.value, true, true));
  mbooks.addEventListener('click', e => { const b = e.target.closest('.book'); if (b) openReader(b.dataset.ev, b.dataset.src); });

  /* ——— окно чтения ——— */
  function loadChunk(name) {
    if (!S.chunks[name]) {
      S.chunks[name] = fetch(`data/verses/${name}.json`)
        .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
        .catch(err => { delete S.chunks[name]; throw err; });
    }
    return S.chunks[name];
  }
  function verses(p) {
    if (S.lang === 'en' && p.verses_en && p.verses_en.length) return { list: p.verses_en, fallback: false };
    return { list: p.verses, fallback: S.lang === 'en' };
  }
  function present(passages, layer) {
    return passages.some(p => verses(p).list.some(v => v[layer] && (layer !== 'notes' || v.notes.length)));
  }

  function openReader(evId, srcId) {
    const same = S.reader && S.reader.ev === evId;
    S.reader = { ev: evId, src: srcId, all: same ? S.reader.all : null };
    $('reader').hidden = false;
    renderReader(); $('r-body').scrollTop = 0;
    markCurrentBook();
    $('r-close').focus({ preventScroll: true });
    if (same && S.reader.all) return;
    const [, ev] = findEv(evId);
    loadChunk(ev.chunk).then(d => {
      if (!S.reader || S.reader.ev !== evId) return;
      S.reader.all = d[evId] || {};
      renderReader(); $('r-body').scrollTop = 0;
    }).catch(() => { if (S.reader && S.reader.ev === evId) $('r-body').innerHTML = `<p class="scroll__msg">${t().failed}</p>`; });
  }
  function closeReader() {
    const r = S.reader;
    $('reader').hidden = true; S.reader = null; markCurrentBook();
    if (r) { const b = document.querySelector(`.book[data-ev="${r.ev}"][data-src="${r.src}"]`); if (b) b.focus({ preventScroll: true }); }
  }
  function markCurrentBook() {
    document.querySelectorAll('.book').forEach(b => b.setAttribute('aria-current', !!S.reader && b.dataset.ev === S.reader.ev && b.dataset.src === S.reader.src));
  }

  function renderReader() {
    if (!S.reader) return;
    const [, ev] = findEv(S.reader.ev), tt = t();
    const idx = ev.sources.findIndex(s => s.id === S.reader.src);
    const src = ev.sources[idx];
    const passages = S.reader.all ? S.reader.all[src.id] || [] : null;
    $('r-lila').textContent = L(ev, 'title') + ' · ' + when(ev);
    $('r-title').textContent = L(src, 'title');
    $('r-author').textContent = L(src, 'author');
    $('layers').innerHTML = LAYERS.map(k => {
      const has = passages ? present(passages, k) : k === 'text';
      return `<button type="button" data-layer="${k}" aria-pressed="${has && S.layers[k]}" ${has ? '' : 'disabled'}>${tt.layers[k]}</button>`;
    }).join('');
    $('r-prev').disabled = idx <= 0; $('r-next').disabled = idx >= ev.sources.length - 1;
    $('r-prev').dataset.src = idx > 0 ? ev.sources[idx - 1].id : '';
    $('r-next').dataset.src = idx < ev.sources.length - 1 ? ev.sources[idx + 1].id : '';
    if (!passages) { $('r-body').innerHTML = `<p class="scroll__msg">${tt.loading}</p>`; $('r-ref').textContent = ''; return; }
    const showText = S.layers.text || !LAYERS.some(k => k !== 'text' && S.layers[k] && present(passages, k));
    const multi = passages.length > 1 || src.id === 'padas';
    $('r-body').innerHTML = passages.map(p => {
      const vs = verses(p);
      const head = multi ? `<div class="passage__head"><h3>${esc(p.poet || p.title)}</h3><p>${esc(p.ref)}</p></div>` : '';
      const note = vs.fallback && tt.noEn ? `<p class="passage__noen">${tt.noEn}</p>` : '';
      const body = vs.list.map(v => {
        let h = '';
        if (S.layers.orig && v.orig) h += `<p class="verse__orig" lang="${/[ঀ-৿]/.test(v.orig) ? 'bn' : 'sa'}">${v.orig}</p>`;
        if (S.layers.translit && v.translit) h += `<p class="verse__translit">${v.translit}</p>`;
        if (S.layers.wbw && v.wbw) h += `<p class="verse__wbw" data-label="${tt.wbw}">${v.wbw}</p>`;
        if (showText) h += `<p class="verse__text">${v.n ? `<span class="verse__n">${esc(v.n)}</span>` : ''}${v.text}</p>`;
        if (S.layers.notes && v.notes && v.notes.length) h += `<div class="verse__notes">${v.notes.map(n => `<p>${n}</p>`).join('')}</div>`;
        return h ? `<div class="verse">${h}</div>` : '';
      }).filter(Boolean).join(ORN);
      return `<section class="passage">${head}${note}${body}</section>`;
    }).join(ORN);
    $('r-ref').textContent = passages.length === 1 ? passages[0].ref : tt.passages(passages.length);
  }
  $('layers').addEventListener('click', e => {
    const b = e.target.closest('button[data-layer]');
    if (!b || b.disabled) return;
    S.layers[b.dataset.layer] = !S.layers[b.dataset.layer];
    savePrefs(); renderReader();
  });
  $('r-close').addEventListener('click', closeReader);
  ['r-prev', 'r-next'].forEach(id => $(id).addEventListener('click', e => {
    const s = e.currentTarget.dataset.src; if (s) { S.reader.src = s; renderReader(); $('r-body').scrollTop = 0; markCurrentBook(); }
  }));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && S.reader) closeReader(); });

  /* ——— язык ——— */
  function applyLang() {
    document.documentElement.lang = S.lang;
    document.querySelectorAll('[data-i18n]').forEach(el => { const v = t()[el.dataset.i18n]; if (typeof v === 'string') el.textContent = v; });
    document.querySelectorAll('.lang button').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === S.lang));
    musicLabel();
    $('prev').setAttribute('aria-label', t().prev); $('next').setAttribute('aria-label', t().next); $('r-close').setAttribute('aria-label', t().close);
    const c = document.querySelector('.is-center');
    keepPlace(c ? c.id.slice(5) : '', renderRibbon);
    updateCenter();
    renderReader();
  }
  document.querySelectorAll('.lang button').forEach(b => b.addEventListener('click', () => { S.lang = b.dataset.lang; savePrefs(); applyLang(); }));

  /* ——— фоновая музыка: «Prema Dhama», 8 частей по 10 мин, по кругу. Звук браузер разрешает только после
     действия пользователя, поэтому при включённой музыке она начинается с первого нажатия на странице. ——— */
  const MUSIC = Array.from({ length: 8 }, (_, i) => `assets/audio/prema-dhama-${i + 1}.mp3`);
  const M = { on: true, part: 0, time: 0, el: null, next: null, started: false, fade: 0 };
  try {
    const m = JSON.parse(localStorage.getItem('gl-music') || 'null');
    if (m) { M.on = m.on !== false; M.part = (m.part | 0) % MUSIC.length; M.time = +m.time || 0; }
  } catch (e) { /* ничего */ }
  const musicBtn = $('music');
  function musicSave() { try { localStorage.setItem('gl-music', JSON.stringify({ on: M.on, part: M.part, time: M.el ? M.el.currentTime : M.time })); } catch (e) { /* ничего */ } }
  function musicLabel() {
    musicBtn.setAttribute('aria-pressed', M.on);
    musicBtn.setAttribute('aria-label', S.lang === 'en' ? (M.on ? 'Turn music off' : 'Turn music on') : (M.on ? 'Выключить музыку' : 'Включить музыку'));
    musicBtn.title = musicBtn.getAttribute('aria-label');
  }
  function audioFor(i) { const a = new Audio(MUSIC[i]); a.preload = 'auto'; a.volume = 0; return a; }
  function fadeTo(a, v, ms, done) {
    clearInterval(M.fade);
    const from = a.volume, t0 = performance.now();
    M.fade = setInterval(() => {
      const k = Math.min(1, (performance.now() - t0) / ms);
      a.volume = from + (v - from) * k;
      if (k === 1) { clearInterval(M.fade); if (done) done(); }
    }, 50);
  }
  const VOL = 0.35;
  function musicPlay() {
    if (!M.el) {
      M.el = audioFor(M.part);
      M.el.currentTime = M.time;
      M.el.addEventListener('ended', musicNext);
      M.el.addEventListener('timeupdate', () => {
        if (!M.next && M.el.duration && M.el.duration - M.el.currentTime < 20) M.next = audioFor((M.part + 1) % MUSIC.length);
      });
    }
    M.el.play().then(() => { M.started = true; fadeTo(M.el, VOL, 2500); }).catch(() => { M.started = false; });
  }
  function musicNext() {
    M.part = (M.part + 1) % MUSIC.length;
    const n = M.next || audioFor(M.part);
    M.next = null; M.el = null; M.time = 0;
    M.el = n; n.volume = VOL;
    n.addEventListener('ended', musicNext);
    n.addEventListener('timeupdate', () => {
      if (!M.next && n.duration && n.duration - n.currentTime < 20) M.next = audioFor((M.part + 1) % MUSIC.length);
    });
    n.play().catch(() => { /* ничего */ });
    musicSave();
  }
  function musicPause() { if (M.el) fadeTo(M.el, 0, 600, () => M.el && M.el.pause()); musicSave(); }
  musicBtn.addEventListener('click', e => {
    e.stopPropagation();
    if (M.on && !M.started) { musicPlay(); return; } // была включена, но браузер ждал нажатия
    M.on = !M.on; musicLabel(); musicSave();
    if (M.on) musicPlay(); else musicPause();
  });
  function firstGesture() {
    if (M.on && !M.started) musicPlay();
  }
  ['pointerdown', 'keydown'].forEach(ev => document.addEventListener(ev, firstGesture, { capture: true }));
  setInterval(() => { if (M.el && !M.el.paused) musicSave(); }, 5000);
  window.addEventListener('pagehide', musicSave);
  musicLabel();
  if (M.on) musicPlay(); // если браузер разрешит — сразу, иначе с первого нажатия

  /* ——— запуск: по умолчанию раскрыт эпизод «Явление Господа» и лила рождения ——— */
  fetch('data/timeline.json').then(r => r.json()).then(d => {
    S.data = d;
    const h = location.hash.slice(1);
    if (findEp(h)) S.ep = h;
    else { S.open = findEv(h)[0] ? h : 'ev-gaura-appearance'; S.ep = findEv(S.open)[0].id; }
    applyLang();
    requestAnimationFrame(() => { centerOn(S.open || S.ep, false); updateCenter(); });
  });
})();
