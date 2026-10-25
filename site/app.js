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
      people: 'Участники лилы', peopleEp: 'Участники эпизода', bio: 'Кратко',
      draft: 'Временный текст — будет заменён описанием из выбранных источников.', noBio: 'Описание готовится.',
      ggd: '«Гаура-ганоддеша-дипика» Кави Карнапуры — кем был прежде', ggdOnlyRu: '',
      of: (i, n) => `${i} из ${n}`,
      tabLilas: 'Лилы', tabMap: 'Карта', tabPeople: 'Спутники', tabLib: 'Писания',
      libToc: 'Оглавление', libAll: '← Все писания', libTitle: 'Писания', libIntro: 'Все наши переводы — целиком, по главам. Выберите писание слева.',
      libChapters: n => `${n} ${plural(n, 'глава', 'главы', 'глав')}`, libEn: '', libNoEn: '', libStart: 'Читать с начала',
      libRuOnly: '', libAbout: 'О писании', libFacts: 'Кратко', toBio: 'Жизнеописание', toLilas: n => `Лилы · ${n}`, readChapter: 'Читать главу целиком →', hintLib: 'Выберите писание и главу. Кнопки над текстом включают оригинал, транслитерацию, пословный перевод и примечания.',
      article: 'Жизнеописание', loadingArticle: 'Загружаю жизнеописание…', withArticle: 'Только с жизнеописанием',
      appearance: 'Явление', disappearance: 'Уход', hasArticle: 'жизнеописание',
      mapNote: 'Прототип. Координаты мест предварительные (OpenStreetMap) и ещё сверяются по топокартам 1955 г.',
      amsLayer: 'Топокарта 1955 г. (лист «Бурдван»)', peopleTitle: 'Спутники и участники лил', search: 'Поиск',
      searchPh: 'Поиск по имени', place: 'Место лил', allLilas: n => `Лилы · ${n}`, allPlaces: n => `Места · ${n}`,
      onMap: 'Места на карте', openPerson: 'Все лилы и места спутника →', noPlaces: 'Мест с координатами пока нет.',
      geoStatus: { tradition: 'место по традиции', approx: 'приблизительно', unverified: 'координата предварительная, не сверена' },
      within: 'Святые места внутри', focus: n => `Места: ${n}`, clear: 'Показать все места',
      sections: { 'Семья': 'Семья Господа', 'Спутники': 'Спутники', 'Ачарьи-предшественники': 'Ачарьи-предшественники', 'Ачарьи-преемники': 'Ачарьи-преемники', 'Небожители и мудрецы': 'Небожители и мудрецы', 'Господь и Его формы': 'Божества и формы Господа' },
      hintMap: 'Нажмите на место, чтобы увидеть его лилы. Колесо или щипок — масштаб.',
      hintPeople: 'Нажмите на имя, чтобы увидеть лилы спутника и его места на карте.',
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
      people: 'Participants', peopleEp: 'Participants of the episode', bio: 'In brief',
      draft: 'Provisional text — to be replaced with descriptions from the chosen sources.', noBio: 'Description in preparation.',
      ggd: 'Gaura-ganoddesha-dipika of Kavi Karnapura — who they were before', ggdOnlyRu: 'Translated into Russian only so far.',
      of: (i, n) => `${i} of ${n}`,
      tabLilas: 'Pastimes', tabMap: 'Map', tabPeople: 'Associates', tabLib: 'Scriptures',
      libToc: 'Contents', libAll: '← All scriptures', libTitle: 'Scriptures', libIntro: 'All our translations, complete, chapter by chapter. Choose a scripture on the left.',
      libChapters: n => `${n} chapter${n === 1 ? '' : 's'}`, libEn: 'EN', libNoEn: 'Russian only so far', libStart: 'Start reading',
      libRuOnly: 'No English translation yet — shown in Russian.', libAbout: 'About the scripture', libFacts: 'In brief', toBio: 'Life', toLilas: n => `Pastimes · ${n}`, readChapter: 'Read the whole chapter →', hintLib: 'Choose a scripture and a chapter. The buttons above the text turn on the original, transliteration, word-for-word and notes.',
      article: 'Life', loadingArticle: 'Loading the life…', withArticle: 'Only with a full life',
      appearance: 'Appearance', disappearance: 'Departure', hasArticle: 'life',
      mapNote: 'Prototype. Place coordinates are provisional (OpenStreetMap) and are being checked against 1955 topographic maps.',
      amsLayer: 'Topographic map, 1955 (sheet “Burdwan”)', peopleTitle: 'Associates and participants of the pastimes', search: 'Search',
      searchPh: 'Search by name', place: 'Place of pastimes', allLilas: n => `Pastimes · ${n}`, allPlaces: n => `Places · ${n}`,
      onMap: 'Places on the map', openPerson: 'All pastimes and places →', noPlaces: 'No places with coordinates yet.',
      geoStatus: { tradition: 'place according to tradition', approx: 'approximate', unverified: 'provisional coordinate, not yet checked' },
      within: 'Holy places within', focus: n => `Places: ${n}`, clear: 'Show all places',
      sections: { 'Семья': 'The Lord’s family', 'Спутники': 'Associates', 'Ачарьи-предшественники': 'Earlier acharyas', 'Ачарьи-преемники': 'Acharyas of the succession', 'Небожители и мудрецы': 'Celestials and sages', 'Господь и Его формы': 'Deities and forms of the Lord' },
      hintMap: 'Tap a place to see its pastimes. Wheel or pinch to zoom.',
      hintPeople: 'Tap a name to see the associate’s pastimes and places on the map.',
    },
  };
  function plural(n, one, few, many) {
    return n % 10 === 1 && n % 100 !== 11 ? one : (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) ? few : many;
  }

  // Иллюстрации: id лилы или эпизода → файл (PNG/WebP с прозрачным фоном). Пока пусто — везде заглушки.
  const IMAGES = {
    'ev-gaura-appearance': 'assets/img/ev-gaura-appearance.webp',
  };
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
  function peopleBtn(kind, o) {
    const n = (o.persons || []).length;
    return n ? `<button type="button" class="people-btn" data-people="${kind}:${o.id}"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3.2"/><circle cx="16.5" cy="9" r="2.6"/><path d="M3.5 19c.6-3.4 2.8-5.3 5.5-5.3s4.9 1.9 5.5 5.3M14 14.2c.8-.5 1.6-.7 2.5-.7 2.2 0 3.8 1.5 4.3 4.5"/></svg>${kind === 'ep' ? t().peopleEp : t().people} · ${n}</button>` : '';
  }
  function booksHtml(ev) {
    const pb = peopleBtn('ev', ev);
    return (pb ? `<li>${pb}</li>` : '') + ev.sources.map(s => `<li><button type="button" class="book" data-ev="${ev.id}" data-src="${s.id}"><b class="auth auth--${s.authority}" title="${s.authority}">${s.authority}</b><span class="book__t">${esc(L(s, 'title'))}</span><span class="book__author">${esc(L(s, 'author'))}</span></button></li>`).join('');
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
        <p class="episode__more">${tt.lilas(ep.events.length)} · <span>${on ? tt.fold : tt.open}</span></p>
        ${on ? peopleBtn('ep', ep) : ''}</div></div>`;
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
    const pbtn = e.target.closest('.people-btn');
    if (pbtn) { openPeople(pbtn.dataset.people); return; }
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
  mbooks.addEventListener('click', e => {
    const pb = e.target.closest('.people-btn'); if (pb) { openPeople(pb.dataset.people); return; }
    const b = e.target.closest('.book'); if (b) openReader(b.dataset.ev, b.dataset.src);
  });

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
    const same = S.reader && S.reader.mode === 'books' && S.reader.ev === evId;
    S.reader = { mode: 'books', ev: evId, src: srcId, all: same ? S.reader.all : null };
    $('reader').hidden = false; document.body.classList.add('is-reading');
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
    $('reader').hidden = true; document.body.classList.remove('is-reading'); S.reader = null; markCurrentBook();
    if (r) { const b = document.querySelector(`.book[data-ev="${r.ev}"][data-src="${r.src}"]`); if (b) b.focus({ preventScroll: true }); }
  }
  function markCurrentBook() {
    const r = S.reader && S.reader.mode === 'books' ? S.reader : null;
    document.querySelectorAll('.book').forEach(b => b.setAttribute('aria-current', !!r && b.dataset.ev === r.ev && b.dataset.src === r.src));
    const pk = S.reader && S.reader.mode === 'people' ? S.reader.key : '';
    document.querySelectorAll('.people-btn').forEach(b => b.setAttribute('aria-current', b.dataset.people === pk));
  }

  /* ——— участники лилы / эпизода: тот же свиток; сверху — кнопки с именами, ниже — описание выбранного ——— */
  function peopleOf(key) {
    const [kind, id] = key.split(':');
    const o = kind === 'ep' ? findEp(id) : findEv(id)[1];
    return { kind, o, list: (o && o.persons) || [] };
  }
  function openPeople(key) {
    const { list } = peopleOf(key);
    if (!list.length) return;
    S.reader = { mode: 'people', key, person: list[0] };
    $('reader').hidden = false; document.body.classList.add('is-reading');
    renderReader(); $('r-body').scrollTop = 0;
    markCurrentBook();
    $('r-close').focus({ preventScroll: true });
  }
  function lifeLine(p) {
    const tt = t(), l = p.life;
    if (!l) return '';
    const part = (k, lab) => {
      const v = l[k]; if (!v) return '';
      const pl = v.place && S.places && S.places[v.place] ? L(S.places[v.place], 'name') : '';
      return `<span><b>${lab}:</b> ${esc([v.date, pl].filter(Boolean).join(' · '))}</span>`;
    };
    return `<p class="person__life">${part('appearance', tt.appearance)}${part('disappearance', tt.disappearance)}</p>`;
  }
  const ARTICLES = {};
  function loadArticle(tag) {
    const p = (S.persons || {})[tag] || {}, lang = S.lang === 'en' && (p.article || []).includes('en') ? 'en' : 'ru';
    const key = tag.slice(1) + '-' + lang;
    if (!ARTICLES[key]) ARTICLES[key] = fetch(`data/parshadas/${key}.json`).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .catch(err => { delete ARTICLES[key]; throw err; });
    return ARTICLES[key];
  }
  function personBody(tag) {
    const tt = t(), p = (S.persons || {})[tag] || {};
    if (p.article) {
      const box = `art-${tag.slice(1)}-${Date.now()}`;
      loadArticle(tag).then(a => { const el = document.getElementById(box); if (el) el.innerHTML = a.html; })
        .catch(() => { const el = document.getElementById(box); if (el) el.innerHTML = `<p class="person__draft">${tt.failed}</p>`; });
      let h = lifeLine(p) + `<div class="article" id="${box}"><p class="person__draft">${tt.loadingArticle}</p></div>`;
      if (p.ggd && p.ggd.length) {
        h += ORN + `<h4 class="person__src">${tt.ggd}</h4>` + (tt.ggdOnlyRu ? `<p class="passage__noen">${tt.ggdOnlyRu}</p>` : '');
        h += p.ggd.map(v => `<p class="verse__text"><span class="verse__n">${esc(v.n)}</span>${v.text}</p>`).join('');
      }
      return h;
    }
    const bio = (S.lang === 'en' && p.bio_en) || p.bio;
    let h = lifeLine(p) + `<h4 class="person__src">${tt.bio}</h4>`;
    h += bio ? bio.map(x => `<p class="verse__text">${x}</p>`).join('') + `<p class="person__draft">${tt.draft}</p>` : `<p class="person__draft">${tt.noBio}</p>`;
    if (p.ggd && p.ggd.length) {
      h += ORN + `<h4 class="person__src">${tt.ggd}</h4>` + (tt.ggdOnlyRu ? `<p class="passage__noen">${tt.ggdOnlyRu}</p>` : '');
      h += p.ggd.map(v => `<p class="verse__text"><span class="verse__n">${esc(v.n)}</span>${v.text}</p>`).join('');
    }
    return h;
  }
  function renderPeople() {
    const tt = t(), { kind, o, list } = peopleOf(S.reader.key);
    const P = S.persons || {};
    const name = tag => (P[tag] ? L(P[tag], 'name') : tag.slice(1));
    const cur = S.reader.person, idx = list.indexOf(cur), p = P[cur] || {};
    $('r-lila').innerHTML = esc(L(o, 'title'));
    $('r-title').textContent = kind === 'ep' ? tt.peopleEp : tt.people;
    $('r-author').textContent = '';
    $('layers').innerHTML = list.map(tag => `<button type="button" data-person="${tag}" aria-pressed="${tag === cur}">${esc(name(tag))}</button>`).join('');
    $('r-body').innerHTML = `<section class="person"><h3 class="person__name">${esc(name(cur))}</h3>` + personBody(cur) +
      `<p class="person__more"><button type="button" class="link-btn" data-open-person="${cur}">${tt.openPerson}</button></p></section>`;
    $('r-ref').textContent = tt.of(idx + 1, list.length);
    $('r-prev').disabled = idx <= 0; $('r-next').disabled = idx >= list.length - 1;
    $('r-prev').dataset.person = idx > 0 ? list[idx - 1] : '';
    $('r-next').dataset.person = idx < list.length - 1 ? list[idx + 1] : '';
  }

  function renderReader() {
    if (!S.reader) return;
    $('reader').classList.toggle('is-people', S.reader.mode === 'people');
    if (S.reader.mode === 'people') return renderPeople();
    if (S.reader.mode === 'person') return renderPerson();
    if (S.reader.mode === 'place') return renderPlace();
    const [, ev] = findEv(S.reader.ev), tt = t();
    const idx = ev.sources.findIndex(s => s.id === S.reader.src);
    const src = ev.sources[idx];
    const passages = S.reader.all ? S.reader.all[src.id] || [] : null;
    $('r-lila').innerHTML = esc(L(ev, 'title')) + `<span class="scroll__when"> · ${when(ev)}</span>`;
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
      const loc = LIB.index && p.file && LIB.index.files[p.file];
      const more = loc ? `<p class="passage__more"><button type="button" class="link-btn" data-lib="${loc[0]}|${loc[1]}|${loc[2]}|${esc(p.from || '')}">${tt.readChapter}</button></p>` : '';
      return `<section class="passage">${head}${note}${body}${more}</section>`;
    }).join(ORN);
    $('r-ref').textContent = passages.length === 1 ? passages[0].ref : tt.passages(passages.length);
  }
  $('layers').addEventListener('click', e => {
    const pb = e.target.closest('button[data-person]');
    if (pb) { S.reader.person = pb.dataset.person; renderReader(); $('r-body').scrollTop = 0; return; }
    const b = e.target.closest('button[data-layer]');
    if (!b || b.disabled) return;
    S.layers[b.dataset.layer] = !S.layers[b.dataset.layer];
    savePrefs(); renderReader();
  });
  $('r-close').addEventListener('click', closeReader);
  ['r-prev', 'r-next'].forEach(id => $(id).addEventListener('click', e => {
    if (S.reader && S.reader.mode === 'people') {
      const p = e.currentTarget.dataset.person; if (p) { S.reader.person = p; renderReader(); $('r-body').scrollTop = 0; }
      return;
    }
    const s = e.currentTarget.dataset.src; if (s) { S.reader.src = s; renderReader(); $('r-body').scrollTop = 0; markCurrentBook(); }
  }));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && S.reader) closeReader(); });

  /* ——— общее для карты и спутников: списки лил по эпизодам ——— */
  const pname = tag => { const p = (S.persons || {})[tag]; return p ? L(p, 'name') : tag.slice(1); };
  const plname = tag => { const p = (S.places || {})[tag]; return p ? L(p, 'name') : tag.slice(1); };
  function lilasOfPerson(tag) { return S.data.episodes.flatMap(ep => ep.events.filter(e => (e.persons || []).includes(tag))); }
  function lilaList(ids) {
    const set = new Set(ids);
    return S.data.episodes.map(ep => {
      const evs = ep.events.filter(e => set.has(e.id));
      if (!evs.length) return '';
      return `<h4 class="person__src">${esc(L(ep, 'title'))}</h4><ul class="lila-list">` +
        evs.map(e => `<li><button type="button" class="link-btn" data-goto-lila="${e.id}">${esc(L(e, 'title'))}</button><span class="lila-list__when">${when(e)}</span></li>`).join('') + '</ul>';
    }).join('');
  }
  function openSide(state) {
    S.reader = state;
    $('reader').hidden = false; document.body.classList.add('is-reading');
    renderReader(); $('r-body').scrollTop = 0; markCurrentBook();
  }
  function openPerson(tag) { openSide({ mode: 'person', tag }); }
  function renderPerson() {
    const tt = t(), tag = S.reader.tag, p = (S.persons || {})[tag] || {};
    const evs = lilasOfPerson(tag);
    const places = placesOfEvents(evs);
    $('r-lila').textContent = (tt.sections[p.section] || '') + (p.note ? ' · ' + p.note : '');
    $('r-title').textContent = pname(tag);
    $('r-author').textContent = '';
    $('layers').innerHTML = (p.article ? `<button type="button" data-act="goto-bio">${tt.toBio}</button>` : '') +
      (evs.length ? `<button type="button" data-act="goto-lilas">${tt.toLilas(evs.length)}</button>` : '') +
      (places.length ? `<button type="button" data-act="person-map">${tt.onMap} · ${places.length}</button>` : '');
    $('r-body').innerHTML = `<section class="person"><div id="p-bio">${personBody(tag)}</div>${ORN}<h3 class="person__name" id="p-lilas">${tt.allLilas(evs.length)}</h3>${lilaList(evs.map(e => e.id))}</section>`;
    $('r-ref').textContent = ''; $('r-prev').disabled = $('r-next').disabled = true;
    $('r-prev').dataset.person = $('r-next').dataset.person = '';
  }
  function placesOfEvents(evs) {
    const P = S.places || {}, out = [];
    for (const e of evs) for (let tag of e.places || []) {
      if (P[tag] && P[tag].parent) tag = P[tag].parent;
      if (P[tag] && P[tag].lat != null && !out.includes(tag)) out.push(tag);
    }
    return out;
  }
  function openPlace(tag) { openSide({ mode: 'place', tag }); }
  function renderPlace() {
    const tt = t(), tag = S.reader.tag, P = S.places || {}, p = P[tag] || {};
    $('r-lila').textContent = tt.place + (p.status ? ' · ' + tt.geoStatus[p.status] : '');
    $('r-title').textContent = plname(tag);
    $('r-author').textContent = p.note || '';
    $('layers').innerHTML = '';
    let h = p.geo_note ? `<p class="person__draft">${esc(p.geo_note)}</p>` : '';
    h += `<h3 class="person__name">${tt.allLilas((p.lilas || []).length)}</h3>` + lilaList(p.lilas || []);
    const subs = Object.entries(P).filter(([, v]) => v.parent === tag && (v.lilas || []).length);
    if (subs.length) {
      h += ORN + `<h3 class="person__name">${tt.within}</h3>`;
      h += subs.map(([k, v]) => `<h4 class="person__src">${esc(L(v, 'name'))}</h4>` + lilaList(v.lilas).replace(/<h4 class="person__src">[^<]*<\/h4>/g, '')).join('');
    }
    $('r-body').innerHTML = `<section class="person">${h}</section>`;
    $('r-ref').textContent = ''; $('r-prev').disabled = $('r-next').disabled = true;
  }
  $('r-body').addEventListener('click', e => {
    const lb = e.target.closest('[data-lib]');
    if (lb) {
      const [book, lang, idx, from] = lb.dataset.lib.split('|');
      closeReader(); showTab('lib'); openLib(book, +idx, from, lang); return;
    }
    const fa = e.target.closest('.article sup.fn a');
    if (fa) { e.preventDefault(); const el = $('r-body').querySelector('#fn-' + fa.dataset.fn); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' }); return; }
    const g = e.target.closest('[data-goto-lila]');
    if (g) { closeReader(); showTab('lilas'); openLila(g.dataset.gotoLila, true, true); return; }
    const op = e.target.closest('[data-open-person]');
    if (op) openPerson(op.dataset.openPerson);
  });

  /* ——— вкладки ——— */
  const TABS = ['lilas', 'lib', 'map', 'people'];
  function showTab(tab, push = true) {
    S.tab = tab;
    TABS.forEach(x => { $('view-' + x).hidden = x !== tab; });
    document.querySelectorAll('.tabs button').forEach(b => b.setAttribute('aria-current', b.dataset.tab === tab ? 'page' : 'false'));
    document.body.dataset.tab = tab;
    const hint = document.querySelector('.foot .hint');
    hint.textContent = tab === 'map' ? t().hintMap : tab === 'people' ? t().hintPeople : tab === 'lib' ? t().hintLib : t().hint;
    if (tab === 'map') initMap();
    if (tab === 'people') renderPeopleList();
    if (tab === 'lib') renderLib();
    if (push && tab === 'lib') libHash();
    else if (push && tab !== 'lilas') history.replaceState(null, '', '#' + tab);
    if (push && tab === 'lilas') history.replaceState(null, '', '#' + (S.open || S.ep || ''));
  }
  document.querySelectorAll('.tabs button').forEach(b => b.addEventListener('click', () => {
    if (S.reader && S.reader.mode === 'books') closeReader();
    showTab(b.dataset.tab);
  }));
  jump.addEventListener('change', () => { if (S.tab !== 'lilas') showTab('lilas'); }, true);

  /* ——— спутники ——— */
  const SECTION_ORDER = ['Семья', 'Спутники', 'Ачарьи-предшественники', 'Ачарьи-преемники', 'Небожители и мудрецы', 'Господь и Его формы'];
  function renderPeopleList() {
    if (!S.persons || !S.data) return;
    const q = ($('people-q').value || '').trim().toLowerCase();
    $('people-q').placeholder = t().searchPh;
    const count = {};
    S.data.episodes.forEach(ep => ep.events.forEach(e => (e.persons || []).forEach(p => { count[p] = (count[p] || 0) + 1; })));
    const groups = {}, onlyArt = $('people-art') && $('people-art').checked;
    if ($('people-art-l')) $('people-art-l').textContent = t().withArticle;
    Object.entries(S.persons).forEach(([tag, p]) => {
      if (q && !(p.name + ' ' + p.name_en + ' ' + (p.note || '')).toLowerCase().includes(q)) return;
      if (onlyArt && !p.article) return;
      (groups[p.section] = groups[p.section] || []).push(tag);
    });
    $('people-list').innerHTML = SECTION_ORDER.filter(s => groups[s]).map(sec => {
      const art = tag => (S.persons[tag].article ? 1 : 0);
      const tags = groups[sec].sort((a, b) => art(b) - art(a) || (count[b] || 0) - (count[a] || 0) || pname(a).localeCompare(pname(b)));
      return `<section class="people-group"><h3>${t().sections[sec]} <span>· ${tags.length}</span></h3><div class="people-grid">` +
        tags.map(tag => `<button type="button" class="book person-card" data-person-open="${tag}"><span class="book__t">${esc(pname(tag))}</span><span class="book__author">${S.persons[tag].article ? `<b class="art-badge">✦ ${t().hasArticle}</b> · ` : ''}${t().allLilas(count[tag] || 0)}</span></button>`).join('') +
        '</div></section>';
    }).join('');
  }
  $('people-q').addEventListener('input', renderPeopleList);
  if ($('people-art')) $('people-art').addEventListener('change', renderPeopleList);
  $('people-list').addEventListener('click', e => { const b = e.target.closest('[data-person-open]'); if (b) openPerson(b.dataset.personOpen); });

  /* ——— карта ——— */
  const MAPC = { map: null, markers: {}, focus: null, line: null, ams: null };
  function initMap() {
    if (MAPC.map) { setTimeout(() => MAPC.map.invalidateSize(), 50); return; }
    if (!window.L || !window.L.map) return;   // Leaflet не загрузился
    const Lf = window.L;
    const BOUNDS = [[0, 60], [37, 101]];   // как у подложки (maps/tools/build_basemap.py)
    const map = Lf.map('map', { zoomSnap: 0.25, minZoom: 4.5, maxZoom: 13, attributionControl: true, zoomControl: true,
      maxBounds: BOUNDS, maxBoundsViscosity: 1 });
    MAPC.map = map;
    map.createPane('ams').style.zIndex = 450;     // старая топокарта — над подложкой
    map.createPane('places').style.zIndex = 620;  // места — над всем
    map.attributionControl.setPrefix('');
    map.attributionControl.addAttribution('Natural Earth · © OpenStreetMap contributors · AMS U502 (1955)');
    map.fitBounds([[18.5, 77], [27.8, 92]]);
    Promise.all([
      fetch('data/basemap.json').then(r => r.json()),
      S.places ? Promise.resolve(S.places) : fetch('data/places.json').then(r => r.json()),
    ]).then(([bm, pl]) => {
      S.places = pl;
      Lf.rectangle(BOUNDS, { stroke: false, fillColor: '#5d7a80', fillOpacity: .22, interactive: false }).addTo(map);
      Lf.geoJSON(bm.land, { interactive: false, style: { color: '#7a5326', weight: 1.1, opacity: .7, fillColor: '#f3e2b8', fillOpacity: .55 } }).addTo(map);
      Lf.geoJSON(bm.lakes, { interactive: false, style: { stroke: false, fillColor: '#5d7a80', fillOpacity: .35 } }).addTo(map);
      Lf.geoJSON(bm.rivers, {
        style: f => ({ color: '#4d727b', weight: f.properties.rank <= 3 ? 2.4 : f.properties.rank <= 6 ? 1.5 : 1, opacity: .8 }),
        onEachFeature: (f, layer) => layer.bindTooltip(S.lang === 'en' ? f.properties.name_en : f.properties.name, { sticky: true, className: 'map-tip map-tip--river' }),
      }).addTo(map);
      MAPC.ams = Lf.imageOverlay('assets/img/ams-nf-45-03.jpg', [[23, 87], [24, 88.5]], { opacity: .92, pane: 'ams' });
      drawPlaces();
    });
    $('ams-toggle').addEventListener('change', e => {
      if (e.target.checked) { MAPC.ams.addTo(map); map.flyToBounds([[23, 87], [24, 88.5]], { duration: .8 }); } else MAPC.ams.remove();
    });
  }
  function drawPlaces() {
    const Lf = window.L, map = MAPC.map, P = S.places;
    Object.values(MAPC.markers).forEach(m => m.remove()); MAPC.markers = {};
    const focus = MAPC.focus;
    Object.entries(P).forEach(([tag, p]) => {
      if (p.lat == null || p.type !== 'point') return;
      const subs = Object.values(P).filter(v => v.parent === tag).reduce((n, v) => n + (v.lilas || []).length, 0);
      const n = (p.lilas || []).length + subs;
      if (!n) return;
      const on = !focus || focus.places.includes(tag);
      const m = Lf.circleMarker([p.lat, p.lon], { pane: 'places',
        radius: 3.5 + Math.sqrt(n) * 1.1, weight: p.status === 'unverified' ? 1.5 : 2.2,
        dashArray: p.status === 'unverified' ? '3 2' : null,
        color: '#4a250b', fillColor: p.status === 'tradition' ? '#b5541b' : '#8a3b12',
        fillOpacity: on ? .85 : .15, opacity: on ? 1 : .25,
      }).addTo(map);
      m.bindTooltip(esc(L(p, 'name')) + (n ? ` · ${n}` : ''), {
        permanent: on && (focus ? n >= 3 : n >= 30), direction: 'right', offset: [6, 0], className: 'map-tip',
      });
      m.on('click', () => openPlace(tag));
      MAPC.markers[tag] = m;
    });
    if (MAPC.line) { MAPC.line.remove(); MAPC.line = null; }
    if (focus && focus.places.length > 1) {
      MAPC.line = Lf.polyline(focus.places.map(t => [P[t].lat, P[t].lon]), { pane: 'places', color: '#7a3d0e', weight: 1.2, dashArray: '4 6', opacity: .55, interactive: false }).addTo(map);
    }
  }
  function focusPerson(tag) {
    const places = placesOfEvents(lilasOfPerson(tag));   // по порядку лил — путь спутника
    MAPC.focus = { tag, places };
    const box = $('map-focus');
    box.hidden = false;
    box.innerHTML = `<span>${esc(t().focus(pname(tag)))}</span><button type="button" class="link-btn" id="map-clear">${t().clear}</button>`;
    $('map-clear').onclick = () => { MAPC.focus = null; box.hidden = true; drawPlaces(); };
    drawPlaces();
    if (places.length) MAPC.map.flyToBounds(places.map(p => [S.places[p].lat, S.places[p].lon]), { padding: [60, 60], maxZoom: 9, duration: .8 });
  }
  $('layers').addEventListener('click', e => {
    const jb = e.target.closest('[data-act="goto-lilas"], [data-act="goto-bio"]');
    if (jb) {
      const el = $(jb.dataset.act === 'goto-lilas' ? 'p-lilas' : 'p-bio'), body = $('r-body');
      if (el) body.scrollTo({ top: body.scrollTop + el.getBoundingClientRect().top - body.getBoundingClientRect().top - 8, behavior: reduced() ? 'auto' : 'smooth' });
      return;
    }
    const b = e.target.closest('[data-act="person-map"]');
    if (!b) return;
    const tag = S.reader.tag;
    showTab('map');
    const go = () => (MAPC.map && S.places && MAPC.markers && Object.keys(MAPC.markers).length) ? focusPerson(tag) : setTimeout(go, 120);
    go();
  });

  /* ——— читалка: все наши переводы целиком ——— */
  const LIB = { index: null, book: null, ch: null, cache: {}, toc: false };
  fetch('data/library/index.json').then(r => r.json()).then(ix => { LIB.index = ix; renderReader(); if (S.tab === 'lib') renderLib(); }).catch(() => {});
  const libBook = id => LIB.index && LIB.index.books.find(b => b.id === id);
  function libLang(b) { return S.lang === 'en' && b.en && b.en.length ? 'en' : 'ru'; }
  function libHash() { history.replaceState(null, '', '#lib' + (LIB.book ? '/' + LIB.book + (LIB.ch != null ? '/' + (LIB.ch + 1) : '') : '')); }
  function openLib(bookId, idx, from, lang) {
    LIB.book = bookId; LIB.ch = idx; LIB.anchor = from || null; LIB.toc = false;
    if (lang === 'en' && S.lang !== 'en') { /* ссылка из английской версии */ }
    renderLib(); libHash();
  }
  function renderLib() {
    if (!LIB.index) { $('lib-read').innerHTML = `<p class="scroll__msg">${t().loading}</p>`; return; }
    const tt = t(), side = $('lib-side');
    const b = LIB.book && libBook(LIB.book);
    $('view-lib').classList.toggle('is-reading-book', !!(b && LIB.ch != null) && !LIB.toc);
    if (!b) {
      side.innerHTML = `<h2 class="lib-h">${tt.libTitle}</h2>` + LIB.index.groups.map(g => {
        const books = LIB.index.books.filter(x => x.group === g.id);
        return books.length ? `<h3 class="lib-group">${esc(L(g, 'title'))}</h3>` + books.map(x =>
          `<button type="button" class="book lib-book" data-book="${x.id}"><span class="book__t">${esc(L(x, 'title'))}</span>` +
          `<span class="book__author">${esc(L(x, 'author'))}${x.author ? ' · ' : ''}${tt.libChapters(x.ru.length)}${S.lang === 'en' && !x.en.length ? ' · ' + tt.libNoEn : ''}</span></button>`).join('') : '';
      }).join('');
      $('lib-bar').hidden = true;
      $('lib-read').innerHTML = `<div class="lib-cover"><h2>${tt.libTitle}</h2><p>${tt.libIntro}</p>${ORN}</div>`;
      return;
    }
    const lang = libLang(b), chs = b[lang];
    if (LIB.ch != null) LIB.ch = Math.max(0, Math.min(chs.length - 1, LIB.ch));
    side.innerHTML = `<button type="button" class="link-btn lib-back" data-book="">${tt.libAll}</button>` +
      `<h2 class="lib-h">${esc(L(b, 'title'))}</h2><p class="lib-author">${esc(L(b, 'author'))}</p>` +
      (L(b, 'note') ? `<p class="person__draft">${esc(L(b, 'note'))}</p>` : '') +
      (S.lang === 'en' && lang === 'ru' ? `<p class="passage__noen">${tt.libRuOnly}</p>` : '') +
      (b.info ? `<p class="lib-about-link"><button type="button" class="link-btn${LIB.ch == null ? ' is-cur' : ''}" data-about="1">${tt.libAbout}</button></p>` : '') +
      `<ol class="lib-toc">` + chs.map((c, i) => `<li><button type="button" class="link-btn${i === LIB.ch ? ' is-cur' : ''}" data-ch="${i}">${esc(c.t)}</button></li>`).join('') + '</ol>';
    const cur = side.querySelector('.is-cur'); if (cur) cur.scrollIntoView({ block: 'center' });
    if (LIB.ch == null) {
      $('lib-bar').hidden = true;
      const inf = b.info, en = S.lang === 'en';
      const facts = inf ? (en ? inf.facts_en : inf.facts_ru) : [], about = inf ? (en ? inf.about_en : inf.about_ru) : [];
      const fact = f => { const i = f.indexOf(': '); return i > 0 && i < 40 ? `<li><b>${f.slice(0, i)}.</b> ${f.slice(i + 2)}</li>` : `<li>${f}</li>`; };
      $('lib-read').innerHTML = `<div class="lib-cover lib-cover--book"><h2>${esc(L(b, 'title'))}</h2><p class="lib-author">${esc(L(b, 'author'))}</p>` +
        `${ORN}<p>${tt.libChapters(chs.length)}</p><button type="button" class="people-btn lib-start" data-ch="0">${tt.libStart}</button></div>` +
        (inf ? `<article class="lib-text lib-about"><h3>${tt.libAbout}</h3>${about.map(x => `<p>${x}</p>`).join('')}` +
          `<h4>${tt.libFacts}</h4><ul class="lib-facts">${facts.map(fact).join('')}</ul></article>` : '');
      $('lib-read').scrollTop = 0;
      return;
    }
    $('lib-bar').hidden = false;
    const c = chs[LIB.ch];
    $('lib-layers').innerHTML = LAYERS.map(k => {
      const has = k === 'text' || (c.layers || []).includes(k);
      return `<button type="button" data-layer="${k}" aria-pressed="${has && S.layers[k]}" ${has ? '' : 'disabled'}>${tt.layers[k]}</button>`;
    }).join('');
    $('lib-prev').disabled = LIB.ch <= 0; $('lib-next').disabled = LIB.ch >= chs.length - 1;
    applyLibLayers();
    const key = `${b.id}/${lang}-${String(LIB.ch + 1).padStart(3, '0')}`, want = key, anchor = LIB.anchor;
    $('lib-read').innerHTML = `<p class="scroll__msg">${tt.loading}</p>`;
    if (!LIB.cache[key]) LIB.cache[key] = fetch(`data/library/${key}.json`).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .catch(err => { delete LIB.cache[key]; throw err; });
    LIB.cache[key].then(d => {
      const now = libBook(LIB.book); if (!now || `${now.id}/${libLang(now)}-${String(LIB.ch + 1).padStart(3, '0')}` !== want) return;
      $('lib-read').innerHTML = `<article class="lib-text"><p class="lib-kicker">${esc(L(b, 'title'))}</p><h2 class="lib-ch">${esc(d.title)}</h2>${d.html}` +
        `<p class="lib-end">${LIB.ch < chs.length - 1 ? `<button type="button" class="people-btn" data-ch="${LIB.ch + 1}">${esc(chs[LIB.ch + 1].t)} →</button>` : ''}</p></article>`;
      $('lib-read').scrollTop = 0;
      if (anchor) {
        LIB.anchor = null;
        const el = $('lib-read').querySelector('#v-' + CSS.escape(String(anchor).replace(/^\D+/, '').split(/[^0-9.a-z]/)[0]));
        if (el) { el.scrollIntoView({ block: 'start' }); $('lib-read').scrollTop -= 60; el.classList.add('is-hl'); }
      }
    }).catch(() => { $('lib-read').innerHTML = `<p class="scroll__msg">${tt.failed}</p>`; });
  }
  function applyLibLayers() {
    const box = $('lib-read');
    LAYERS.forEach(k => box.classList.toggle('hide-' + k, !S.layers[k]));
    if (!LAYERS.some(k => S.layers[k])) box.classList.remove('hide-text');
  }
  $('lib-side').addEventListener('click', e => {
    const bk = e.target.closest('[data-book]');
    if (bk) { LIB.book = bk.dataset.book || null; LIB.ch = null; renderLib(); libHash(); return; }
    if (e.target.closest('[data-about]')) { LIB.ch = null; LIB.toc = false; renderLib(); libHash(); $('view-lib').classList.add('is-reading-book'); return; }
    const ch = e.target.closest('[data-ch]');
    if (ch) { LIB.ch = +ch.dataset.ch; LIB.toc = false; renderLib(); libHash(); }
  });
  $('lib-read').addEventListener('click', e => {
    const ch = e.target.closest('[data-ch]');
    if (ch) { LIB.ch = +ch.dataset.ch; renderLib(); libHash(); return; }
    const fa = e.target.closest('sup.fn a');
    if (fa) { e.preventDefault(); const el = $('lib-read').querySelector('#fn-' + fa.dataset.fn); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
  });
  $('lib-layers').addEventListener('click', e => {
    const b = e.target.closest('button[data-layer]');
    if (!b || b.disabled) return;
    S.layers[b.dataset.layer] = !S.layers[b.dataset.layer];
    savePrefs();
    $('lib-layers').querySelectorAll('button[data-layer]').forEach(x => { if (!x.disabled) x.setAttribute('aria-pressed', S.layers[x.dataset.layer]); });
    applyLibLayers();
  });
  $('lib-prev').addEventListener('click', () => { LIB.ch--; renderLib(); libHash(); });
  $('lib-next').addEventListener('click', () => { LIB.ch++; renderLib(); libHash(); });
  $('lib-toc-btn').addEventListener('click', () => { LIB.toc = !LIB.toc; $('view-lib').classList.toggle('is-reading-book', !LIB.toc); });

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
    if (S.tab) showTab(S.tab, false);
    if (MAPC.map && S.places) drawPlaces();
    if (S.tab === 'lib') renderLib();
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
  fetch('data/persons.json').then(r => r.json()).then(p => { S.persons = p; renderReader(); if (S.tab === 'people') renderPeopleList(); }).catch(() => { S.persons = {}; });
  fetch('data/places.json').then(r => r.json()).then(p => { if (!S.places) S.places = p; }).catch(() => {});
  fetch('data/timeline.json').then(r => r.json()).then(d => {
    S.data = d;
    const h = location.hash.slice(1);
    if (findEp(h)) S.ep = h;
    else { S.open = findEv(h)[0] ? h : 'ev-gaura-appearance'; S.ep = findEv(S.open)[0].id; }
    S.tab = TABS.includes(h) ? h : h.startsWith('lib/') ? 'lib' : 'lilas';
    if (h.startsWith('lib/')) { const [, b, n] = h.split('/'); LIB.book = b || null; LIB.ch = n ? +n - 1 : null; }
    applyLang();
    requestAnimationFrame(() => { centerOn(S.open || S.ep, false); updateCenter(); });
  });
})();
