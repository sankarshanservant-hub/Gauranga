/* Лента лил и окно чтения. Данные — data/lilas.json (site/tools/build_data.py). */
(function () {
  'use strict';

  const T = {
    ru: {
      title: 'Гаура-лила', subtitle: 'Лилы Шри Чайтаньи Махапрабху по писаниям',
      jumpLabel: 'Перейти к лиле', ribbon: 'Лента лил',
      hint: 'Листайте ленту. Нажмите на название лилы, чтобы увидеть писания, где она описана.',
      legend: 'Достоверность источника:', authA: 'канонический', authB: 'принятый традицией', authC: 'с оговорками', authD: 'сомнительный',
      layers: { orig: 'Оригинал', translit: 'Транслитерация', wbw: 'Пословный', text: 'Перевод', notes: 'Примечания' },
      wbw: 'пословно', before: 'до явления', atBirth: 'при рождении', yearsOld: (a, b) => a === b ? `${a} ${plural(a)}` : `${a}–${b} лет`,
      approx: '≈', sources: n => `${n} ${n % 10 === 1 && n % 100 !== 11 ? 'писание' : (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) ? 'писания' : 'писаний'}`,
      noEn: '', close: 'Закрыть', illus: 'Иллюстрация готовится', prev: 'Назад', next: 'Вперёд',
      group: 'Лилы', groupSub: 'Пхалгуна-пурнима, 1486 г.',
    },
    en: {
      title: 'Gaura-lila', subtitle: 'Pastimes of Sri Chaitanya Mahaprabhu in the scriptures',
      jumpLabel: 'Go to a pastime', ribbon: 'Timeline of pastimes',
      hint: 'Swipe the scroll. Tap a pastime’s name to see the scriptures that describe it.',
      legend: 'Source reliability:', authA: 'canonical', authB: 'accepted by tradition', authC: 'with reservations', authD: 'doubtful',
      layers: { orig: 'Original', translit: 'Transliteration', wbw: 'Word for word', text: 'Translation', notes: 'Notes' },
      wbw: 'word for word', before: 'before the advent', atBirth: 'at birth', yearsOld: (a, b) => a === b ? `age ${a}` : `age ${a}–${b}`,
      approx: 'c.', sources: n => `${n} scripture${n === 1 ? '' : 's'}`,
      noEn: 'No English translation yet — shown in Russian.', close: 'Close', illus: 'Illustration in preparation', prev: 'Back', next: 'Forward',
      group: 'Pastimes', groupSub: 'Phalguna Purnima, 1486',
    },
  };
  function plural(a) { return a % 10 === 1 && a % 100 !== 11 ? 'год' : (a % 10 >= 2 && a % 10 <= 4 && (a % 100 < 10 || a % 100 >= 20)) ? 'года' : 'лет'; }

  const IMAGES = { 'ev-gaura-appearance': 'assets/img/lila-birth-draft.jpg' };
  const LAYERS = ['orig', 'translit', 'wbw', 'text', 'notes'];
  const ORN = '<svg class="orn-line" viewBox="0 0 200 10" aria-hidden="true"><path d="M0 5h86M114 5h86" stroke="currentColor" stroke-width=".8"/><path d="M100 1l4 4-4 4-4-4z" fill="currentColor"/></svg>';
  const LOTUS = '<svg class="card__ph" viewBox="0 0 100 100" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"><circle cx="50" cy="50" r="46" stroke-dasharray="2 4"/><path d="M50 22c8 10 10 22 0 40-10-18-8-30 0-40Z"/><path d="M50 62c5-14 16-22 30-22-3 14-14 23-30 22Z"/><path d="M50 62C34 63 23 54 20 40c14 0 25 8 30 22Z"/><path d="M28 70h44M34 76h32"/></g></svg>';

  const S = { data: null, lang: 'ru', layers: { orig: true, translit: false, wbw: false, text: true, notes: false }, open: null, reader: null };
  try {
    const saved = JSON.parse(localStorage.getItem('gl-prefs') || 'null');
    if (saved) { if (saved.lang) S.lang = saved.lang; if (saved.layers) Object.assign(S.layers, saved.layers); }
  } catch (e) { /* хранилище недоступно */ }
  function savePrefs() { try { localStorage.setItem('gl-prefs', JSON.stringify({ lang: S.lang, layers: S.layers })); } catch (e) { /* ничего */ } }

  const $ = id => document.getElementById(id);
  const ribbon = $('ribbon'), track = $('track'), jump = $('jump');
  const t = () => T[S.lang];
  const L = (o, k) => (S.lang === 'en' && o[k + '_en']) || o[k];
  const events = () => S.data.groups.flatMap(g => g.events);
  const findEv = id => events().find(e => e.id === id);

  function when(ev) {
    const y = ev.years, a = ev.age, tt = t();
    const ys = y ? (y[0] === y[1] ? `${y[0]}` : `${y[0]}–${y[1]}`) : '';
    const approx = ev.date_conf === 'оценка' ? tt.approx + ' ' : '';
    let age = '';
    if (a && a[1] === 0) age = tt.atBirth;
    else if (a) age = tt.yearsOld(a[0], a[1]);
    else if (ev.before) age = tt.before;
    return [age, approx + ys + (S.lang === 'en' ? ' CE' : ' г.')].filter(Boolean).join(' · ');
  }

  /* ——— лента ——— */
  function renderRibbon() {
    const tt = t();
    let h = '<div class="cap cap--start" aria-hidden="true"></div><div class="paper">';
    for (const g of S.data.groups) {
      h += `<div class="group-title"><svg class="orn" viewBox="0 0 160 12" aria-hidden="true"><path d="M0 6h66M94 6h66" stroke="currentColor" stroke-width=".8"/><path d="M80 1l5 5-5 5-5-5z" fill="currentColor"/></svg><h3>${L(g, 'title')}</h3><p>${tt.groupSub}</p><svg class="orn" viewBox="0 0 160 12" aria-hidden="true"><path d="M0 6h66M94 6h66" stroke="currentColor" stroke-width=".8"/><path d="M80 1l5 5-5 5-5-5z" fill="currentColor"/></svg></div>`;
      for (const ev of g.events) {
        const img = IMAGES[ev.id];
        const fig = img ? `<img src="${img}" alt="" draggable="false">` : LOTUS + `<span class="sr">${tt.illus}</span>`;
        const books = booksHtml(ev);
        h += `<div class="card${S.open === ev.id ? ' is-open' : ''}" id="card-${ev.id}" data-ev="${ev.id}">
          <figure class="card__fig">${fig}</figure>
          <div class="card__cap"><button type="button" class="card__name" aria-expanded="${S.open === ev.id}">${L(ev, 'title')}</button>
          <p class="card__when">${when(ev)}</p><p class="card__count">${tt.sources(ev.sources.length)}</p></div>
          <ul class="books">${books}</ul></div>`;
      }
    }
    h += '</div><div class="cap cap--end" aria-hidden="true"></div>';
    track.innerHTML = h;
    markCurrentBook();
    jump.innerHTML = S.data.groups.map(g => `<optgroup label="${L(g, 'title')}">` + g.events.map(e => `<option value="${e.id}">${L(e, 'title')}</option>`).join('') + '</optgroup>').join('');
    if (S.open) jump.value = S.open;
  }

  function booksHtml(ev) {
    return ev.sources.map(s => `<li><button type="button" class="book" data-ev="${ev.id}" data-src="${s.id}"><b class="auth auth--${s.authority}" title="${s.authority}">${s.authority}</b><span class="book__t">${L(s, 'title')}</span><span class="book__author">${L(s, 'author')}</span></button></li>`).join('');
  }
  // на узком экране писания показываются под лентой
  function renderMobileBooks() {
    const ev = S.open && findEv(S.open);
    mbooks.innerHTML = ev ? booksHtml(ev) : '';
    markCurrentBook();
  }
  const mbooks = $('mbooks');
  mbooks.addEventListener('click', e => { const b = e.target.closest('.book'); if (b) openReader(b.dataset.ev, b.dataset.src); });

  function centerOn(id, smooth) {
    const card = $('card-' + id);
    if (!card) return;
    const left = card.offsetLeft + card.offsetWidth / 2 - ribbon.clientWidth / 2;
    ribbon.scrollTo({ left, behavior: smooth && !reduced() ? 'smooth' : 'auto' });
  }
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  function openCard(id, smooth = true) {
    S.open = S.open === id ? null : id;
    document.querySelectorAll('.card').forEach(c => {
      const on = c.dataset.ev === S.open;
      c.classList.toggle('is-open', on);
      c.querySelector('.card__name').setAttribute('aria-expanded', on);
    });
    if (S.open) { jump.value = S.open; history.replaceState(null, '', '#' + S.open); }
    renderMobileBooks();
    // ширина меняется с анимацией — центрируем по её окончании
    setTimeout(() => S.open && centerOn(S.open, smooth), reduced() ? 0 : 470);
  }

  function updateCenter() {
    const mid = ribbon.scrollLeft + ribbon.clientWidth / 2;
    let best = null, bd = Infinity;
    document.querySelectorAll('.card').forEach(c => {
      const d = Math.abs(c.offsetLeft + c.offsetWidth / 2 - mid);
      if (d < bd) { bd = d; best = c; }
    });
    document.querySelectorAll('.card.is-center').forEach(c => c !== best && c.classList.remove('is-center'));
    if (best) best.classList.add('is-center');
  }

  // перетаскивание мышью; на сенсорных экранах — родная прокрутка
  let drag = null;
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
    if (drag && drag.moved) { ribbon.classList.remove('is-drag'); ribbon.dataset.justDragged = '1'; setTimeout(() => delete ribbon.dataset.justDragged, 0); }
    drag = null;
  });
  ribbon.addEventListener('click', e => {
    if (ribbon.dataset.justDragged) { e.preventDefault(); e.stopPropagation(); return; }
    const book = e.target.closest('.book');
    if (book) { openReader(book.dataset.ev, book.dataset.src); return; }
    const name = e.target.closest('.card__name');
    if (name) openCard(name.closest('.card').dataset.ev);
  }, true);
  ribbon.addEventListener('wheel', e => {
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX) && !e.target.closest('.books')) {
      ribbon.scrollLeft += e.deltaY; e.preventDefault();
    }
  }, { passive: false });
  let raf = 0;
  ribbon.addEventListener('scroll', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(updateCenter); });
  ribbon.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { step(e.key === 'ArrowRight' ? 1 : -1); e.preventDefault(); }
  });
  function step(dir) {
    const ids = events().map(e => e.id);
    const cur = document.querySelector('.card.is-center');
    let i = cur ? ids.indexOf(cur.dataset.ev) : 0;
    i = Math.max(0, Math.min(ids.length - 1, i + dir));
    centerOn(ids[i], true);
  }
  $('prev').addEventListener('click', () => step(-1));
  $('next').addEventListener('click', () => step(1));
  jump.addEventListener('change', () => { if (S.open !== jump.value) openCard(jump.value); else centerOn(jump.value, true); });

  /* ——— окно чтения ——— */
  function present(src, layer) {
    return src.passages.some(p => (verses(p).list).some(v => v[layer] && (layer !== 'notes' || v.notes.length)));
  }
  function verses(p) {
    if (S.lang === 'en' && p.verses_en && p.verses_en.length) return { list: p.verses_en, fallback: false };
    return { list: p.verses, fallback: S.lang === 'en' };
  }

  function openReader(evId, srcId) {
    S.reader = { ev: evId, src: srcId };
    if (S.open !== evId) openCard(evId);
    renderReader();
    $('reader').hidden = false;
    $('r-body').scrollTop = 0;
    markCurrentBook();
    $('r-close').focus({ preventScroll: true });
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
    const ev = findEv(S.reader.ev), tt = t();
    const idx = ev.sources.findIndex(s => s.id === S.reader.src);
    const src = ev.sources[idx];
    $('r-lila').textContent = L(ev, 'title') + ' · ' + when(ev);
    $('r-title').textContent = L(src, 'title');
    $('r-author').textContent = L(src, 'author');
    $('layers').innerHTML = LAYERS.map(k => {
      const has = present(src, k);
      return `<button type="button" data-layer="${k}" aria-pressed="${has && S.layers[k]}" ${has ? '' : 'disabled'}>${tt.layers[k]}</button>`;
    }).join('');
    const showText = S.layers.text || !LAYERS.some(k => k !== 'text' && S.layers[k] && present(src, k));
    const multi = src.passages.length > 1 || src.id === 'padas';
    $('r-body').innerHTML = src.passages.map(p => {
      const vs = verses(p);
      const head = multi ? `<div class="passage__head"><h3>${p.poet || p.title}</h3><p>${p.ref}</p></div>` : '';
      const note = vs.fallback && tt.noEn ? `<p class="passage__noen">${tt.noEn}</p>` : '';
      const body = vs.list.map(v => {
        let h = '';
        if (S.layers.orig && v.orig) h += `<p class="verse__orig" lang="${/[ঀ-৿]/.test(v.orig) ? 'bn' : 'sa'}">${v.orig}</p>`;
        if (S.layers.translit && v.translit) h += `<p class="verse__translit">${v.translit}</p>`;
        if (S.layers.wbw && v.wbw) h += `<p class="verse__wbw" data-label="${tt.wbw}">${v.wbw}</p>`;
        if (showText) h += `<p class="verse__text">${v.n ? `<span class="verse__n">${v.n}</span>` : ''}${v.text}</p>`;
        if (S.layers.notes && v.notes && v.notes.length) h += `<div class="verse__notes">${v.notes.map(n => `<p>${n}</p>`).join('')}</div>`;
        return h ? `<div class="verse">${h}</div>` : '';
      }).filter(Boolean).join(ORN);
      return `<section class="passage">${head}${note}${body}</section>`;
    }).join(ORN);
    $('r-ref').textContent = src.passages.length === 1 ? src.passages[0].ref : `${src.passages.length} ${S.lang === 'en' ? 'passages' : 'отрывка(ов)'}`;
    $('r-prev').disabled = idx <= 0; $('r-next').disabled = idx >= ev.sources.length - 1;
    $('r-prev').dataset.src = idx > 0 ? ev.sources[idx - 1].id : '';
    $('r-next').dataset.src = idx < ev.sources.length - 1 ? ev.sources[idx + 1].id : '';
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
    $('prev').setAttribute('aria-label', t().prev); $('next').setAttribute('aria-label', t().next); $('r-close').setAttribute('aria-label', t().close);
    const keep = ribbon.scrollLeft;
    renderRibbon(); renderMobileBooks(); ribbon.scrollLeft = keep; updateCenter();
    renderReader();
  }
  document.querySelectorAll('.lang button').forEach(b => b.addEventListener('click', () => { S.lang = b.dataset.lang; savePrefs(); applyLang(); }));

  /* ——— запуск ——— */
  fetch('data/lilas.json').then(r => r.json()).then(d => {
    S.data = d;
    const fromHash = location.hash.slice(1);
    S.open = findEv(fromHash) ? fromHash : 'ev-gaura-appearance';
    applyLang();
    requestAnimationFrame(() => { centerOn(S.open, false); updateCenter(); });
  });
})();
