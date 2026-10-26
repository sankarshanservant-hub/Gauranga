// Раздел «Путешествие» (2026-10-16): карты /travel/ (мир) и /travel/india/ (святая Индия).
// Обычный (не модульный) скрипт из public/ — «мягкая навигация» (src/scripts/base/11.js)
// пересоздаёт <script src> новой страницы, и он выполняется заново; модуль выполнился бы
// только один раз. Поэтому всё здесь идемпотентно, а карта снимается в AM_SOFTNAV.onCleanup.
// Данные страницы — <script type="application/json" id="tvData"> (см. src/lib/travel.ts).
// Библиотека — MapLibre GL из /vendor/maplibre-gl-<версия>/ (scripts/copy-maplibre.mjs),
// подложка — OpenFreeMap (бесплатно, без ключа), спутник — Esri World Imagery.
(function () {
  var root = document.getElementById('tvRoot');
  var dataEl = document.getElementById('tvData');
  if (!root || !dataEl) return;
  var D = JSON.parse(dataEl.textContent || '{}');
  var MODE = root.getAttribute('data-mode'); // world | india
  var LIB = '/vendor/maplibre-gl-' + D.lib + '/';
  var alive = true;
  var map = null;

  // ── мелочи ────────────────────────────────────────────────────────────────
  var MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
  function ruDate(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || '');
    return m ? (+m[3]) + ' ' + MONTHS[+m[2] - 1] + ' ' + m[1] : '';
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function plural(n, one, few, many) {
    var a = n % 10, b = n % 100;
    return n + ' ' + (a === 1 && b !== 11 ? one : a >= 2 && a <= 4 && (b < 12 || b > 14) ? few : many);
  }
  function lectCount(n) { return plural(n, 'лекция', 'лекции', 'лекций'); }
  function isDark() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t === 'dark') return true;
    if (t === 'light') return false;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function styleUrl() { return 'https://tiles.openfreemap.org/styles/' + (isDark() ? 'dark' : 'positron'); }

  var KIND_ICON = {
    temple: 'M12 3l2 3h-4zM8 9h8l1 3H7zM6 12h12v8H6zM10 20v-4h4v4',
    kund: 'M3 10c2 1.5 4 1.5 6 0s4-1.5 6 0 4 1.5 6 0M3 15c2 1.5 4 1.5 6 0s4-1.5 6 0 4 1.5 6 0M5 5h14',
    ghat: 'M3 20h18M5 20v-3h4v-3h4v-3h4V8h2M3 8c1.5 1 3 1 4.5 0',
    samadhi: 'M12 3c-2 3-2 5 0 7 2-2 2-4 0-7zM6 12h12M8 12v8h8v-8M5 20h14',
    hill: 'M3 19l6-9 4 5 3-4 5 8z',
    forest: 'M12 3l5 7h-3l4 5H6l4-5H7zM12 15v6',
    birthplace: 'M12 3l2.5 5.5 6 .6-4.5 4 1.3 6L12 16l-5.3 3.1 1.3-6-4.5-4 6-.6z',
    math: 'M4 11l8-6 8 6M6 10v10h12V10M10 20v-5h4v5',
    river: 'M3 7c3 2 6-2 9 0s6 2 9 0M3 12c3 2 6-2 9 0s6 2 9 0M3 17c3 2 6-2 9 0s6 2 9 0',
    other: 'M12 7a5 5 0 100 10 5 5 0 000-10z',
  };
  function kindSvg(kind) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + (KIND_ICON[kind] || KIND_ICON.other) + '"/></svg>';
  }

  function lectureList(ids, opts) {
    opts = opts || {};
    if (!ids || !ids.length) return '';
    var byYear = {};
    ids.forEach(function (id) {
      var l = D.lectures[id]; if (!l) return;
      var y = (l.d || '').slice(0, 4) || 'без даты';
      (byYear[y] = byYear[y] || []).push(id);
    });
    return Object.keys(byYear).sort().map(function (y) {
      return '<div class="tv-year mono">' + esc(y) + '</div><ul class="tv-lects">' + byYear[y].map(function (id) {
        var l = D.lectures[id];
        var extra = opts.extra ? opts.extra(id, l) : '';
        // after — то, что стоит рядом со ссылкой на лекцию (своя ссылка внутри ссылки недопустима)
        var after = opts.after ? opts.after(id, l) : '';
        return '<li><a href="/lectures/' + esc(id) + '/"><span class="tv-lt">' + esc(l.t) + '</span>' +
          '<span class="tv-ld mono">' + esc(ruDate(l.d)) + extra + '</span></a>' + after + '</li>';
      }).join('') + '</ul>';
    }).join('');
  }

  // ── загрузка MapLibre и подложки ───────────────────────────────────────────
  function loadLib() {
    if (!document.querySelector('link[data-maplibre]')) {
      var css = document.createElement('link');
      css.rel = 'stylesheet'; css.href = LIB + 'maplibre-gl.css'; css.setAttribute('data-maplibre', '');
      document.head.appendChild(css);
    }
    return import(LIB + 'maplibre-gl.js');
  }

  // Подписи на подложке — по-русски, где в OpenStreetMap есть name:ru
  function localize(m) {
    var layers = (m.getStyle() && m.getStyle().layers) || [];
    layers.forEach(function (ly) {
      if (ly.type !== 'symbol' || !ly.layout || !ly.layout['text-field']) return;
      if (JSON.stringify(ly.layout['text-field']).indexOf('name') < 0) return;
      try { m.setLayoutProperty(ly.id, 'text-field', ['coalesce', ['get', 'name:ru'], ['get', 'name:latin'], ['get', 'name']]); } catch (e) {}
    });
  }
  var satOn = false;
  function addSatellite(m) {
    if (m.getSource('tv-sat')) return;
    m.addSource('tv-sat', {
      type: 'raster', tileSize: 256, maxzoom: 19,
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
      attribution: 'Спутник: Esri, Maxar, Earthstar Geographics',
    });
    var firstSymbol = ((m.getStyle().layers) || []).find(function (l) { return l.type === 'symbol'; });
    m.addLayer({ id: 'tv-sat', type: 'raster', source: 'tv-sat', layout: { visibility: satOn ? 'visible' : 'none' } }, firstSymbol && firstSymbol.id);
  }
  function setSatellite(on) {
    satOn = on;
    if (map && map.getLayer('tv-sat')) map.setLayoutProperty('tv-sat', 'visibility', on ? 'visible' : 'none');
    root.classList.toggle('is-sat', on);
    root.querySelectorAll('[data-sat]').forEach(function (b) { b.setAttribute('aria-pressed', String((b.getAttribute('data-sat') === '1') === on)); });
  }

  var onStyle = null; // свои слои страницы (парикрамы) — добавляются заново после каждой смены стиля
  function makeMap(ml, opts) {
    var m = new ml.Map(Object.assign({
      container: 'tvMap', style: styleUrl(), attributionControl: { compact: true },
      dragRotate: true, pitchWithRotate: true, cooperativeGestures: false,
    }, opts));
    m.addControl(new ml.NavigationControl({ visualizePitch: true }), 'top-right');
    m.on('style.load', function () { localize(m); addSatellite(m); if (onStyle) onStyle(m); });
    m.on('error', function (e) {
      // подложка недоступна (нет сети/блокировка) — маркеры и панель работают и без неё
      if (e && e.error && /Failed to fetch|NetworkError|AJAXError/i.test(String(e.error.message || e.error))) root.classList.add('no-tiles');
    });
    // смена темы сайта — меняем подложку (маркеры — HTML, переживают смену стиля)
    var mo = new MutationObserver(function () { m.setStyle(styleUrl()); });
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    if (window.AM_SOFTNAV) window.AM_SOFTNAV.onCleanup(function () { alive = false; mo.disconnect(); try { m.remove(); } catch (e) {} });
    root.querySelectorAll('[data-sat]').forEach(function (b) {
      b.addEventListener('click', function () { setSatellite(b.getAttribute('data-sat') === '1'); });
    });
    return m;
  }

  var panel = document.getElementById('tvPanel');
  function showPanel(html) {
    panel.innerHTML = html;
    panel.scrollTop = 0;
    root.classList.add('panel-open');
  }

  // ═══ МИР ═══════════════════════════════════════════════════════════════════
  function initWorld(ml) {
    var places = D.places || [];
    var bounds = new ml.LngLatBounds();
    places.forEach(function (p) { bounds.extend(p.coords); });
    map = makeMap(ml, places.length ? { bounds: bounds, fitBoundsOptions: { padding: 60, maxZoom: 5 } } : { center: [60, 50], zoom: 2.3 });
    var max = places.reduce(function (n, p) { return Math.max(n, p.lectures.length); }, 1);
    var markers = {};
    places.forEach(function (p) {
      var el = document.createElement('button');
      el.type = 'button';
      el.className = 'tv-wp' + (p.india ? ' is-india' : '');
      var size = Math.round(14 + 26 * Math.sqrt(p.lectures.length / max));
      el.style.setProperty('--s', size + 'px');
      el.innerHTML = '<span class="tv-wp-dot"></span><span class="tv-wp-l">' + esc(p.name) + ' <b>' + p.lectures.length + '</b></span>';
      el.setAttribute('aria-label', p.name + ': ' + lectCount(p.lectures.length));
      el.addEventListener('click', function (e) { e.stopPropagation(); location.hash = p.id; });
      markers[p.id] = new ml.Marker({ element: el, anchor: 'center' }).setLngLat(p.coords).addTo(map);
    });
    var overview = panel.innerHTML;
    function route() {
      if (!alive) return;
      var id = decodeURIComponent(location.hash.slice(1));
      Object.keys(markers).forEach(function (k) { markers[k].getElement().classList.toggle('is-active', k === id); });
      var p = places.find(function (x) { return x.id === id; });
      if (!p) { panel.innerHTML = overview; root.classList.remove('panel-open'); return; }
      map.flyTo({ center: p.coords, zoom: Math.max(map.getZoom(), 4.5), speed: 0.9 });
      var venues = {};
      p.venues.forEach(function (v) { venues[v.id] = v.name; });
      var html = '<div class="tv-crumbs mono"><a href="#">Все города</a> · ' + esc(p.country) + '</div>' +
        '<h2 class="display tv-h">' + esc(p.name) + '</h2>' +
        '<p class="tv-sub mono">' + lectCount(p.lectures.length) + '</p>';
      if (p.india) html += '<a class="tv-cta" href="/travel/india/#' + esc(p.id) + '">Святая Индия: войти в ' + esc(p.name) + ' →</a>';
      html += lectureList(p.lectures.map(function (l) { return l.id; }), {
        extra: function (id) {
          var l = p.lectures.find(function (x) { return x.id === id; });
          return (l && l.v && venues[l.v] ? ' · ' + esc(venues[l.v]) : '') + (l && l.c === 'low' ? ' · <span title="Место определено по соседним датам">предположительно</span>' : '');
        },
      });
      showPanel(html);
    }
    window.addEventListener('hashchange', route);
    if (window.AM_SOFTNAV) window.AM_SOFTNAV.onCleanup(function () { window.removeEventListener('hashchange', route); });
    map.on('load', route);
  }

  // ═══ СВЯТАЯ ИНДИЯ ═══════════════════════════════════════════════════════════
  var SPOT_ZOOM = 11;
  function initIndia(ml) {
    var cities = D.cities || [], spots = D.spots || [];
    var cityById = {}, spotById = {}, regionById = {};
    cities.forEach(function (c) { cityById[c.id] = c; });
    spots.forEach(function (s) { spotById[s.id] = s; });
    (D.regions || []).forEach(function (r) { regionById[r.id] = r; });
    var INDIA = { center: [80.5, 22.5], zoom: 4.2, pitch: 0, bearing: 0 };
    var routes = D.routes || [], routeById = {};
    routes.forEach(function (r) { routeById[r.id] = r; });
    var activeRoute = '';
    // Парикрамы — линиями под подписями подложки; выбранная — ярче и толще.
    // GPS-трек — сплошной, схема по местам из книги — пунктиром (это не реальная тропа).
    var ROUTE_LAYERS = ['tv-routes-case', 'tv-routes-track', 'tv-routes-scheme'];
    onStyle = function (m) {
      if (!routes.length || m.getSource('tv-routes')) return;
      m.addSource('tv-routes', { type: 'geojson', data: { type: 'FeatureCollection', features: routes.map(function (r) {
        return { type: 'Feature', properties: { id: r.id, scheme: r.kind === 'scheme' }, geometry: { type: 'MultiLineString', coordinates: r.lines } };
      }) } });
      var firstSymbol = ((m.getStyle().layers) || []).find(function (l) { return l.type === 'symbol'; });
      var before = firstSymbol && firstSymbol.id;
      var col = getComputedStyle(root).getPropertyValue('--saffron').trim() || '#C2701D';
      var acc = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#7A1F1F';
      var isActive = ['==', ['get', 'id'], activeRoute];
      var paint = {
        'line-color': ['case', isActive, acc, col],
        'line-opacity': ['case', isActive, 1, activeRoute ? 0.45 : 0.9],
        'line-width': ['interpolate', ['linear'], ['zoom'], 11, ['case', isActive, 2.5, 1.5], 16, ['case', isActive, 6, 4]],
      };
      m.addLayer({ id: 'tv-routes-case', type: 'line', source: 'tv-routes', minzoom: 10, filter: ['!', ['get', 'scheme']],
        layout: { 'line-cap': 'round', 'line-join': 'round' },
        paint: { 'line-color': '#ffffff', 'line-opacity': 0.85, 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 3, 16, 9] } }, before);
      m.addLayer({ id: 'tv-routes-track', type: 'line', source: 'tv-routes', minzoom: 10, filter: ['!', ['get', 'scheme']],
        layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: paint }, before);
      m.addLayer({ id: 'tv-routes-scheme', type: 'line', source: 'tv-routes', minzoom: 10, filter: ['get', 'scheme'],
        layout: { 'line-join': 'round' }, paint: Object.assign({ 'line-dasharray': [2, 1.6] }, paint) }, before);
    };
    function setActiveRoute(id) {
      if ((id || '') === activeRoute) return;
      activeRoute = id || '';
      if (map && map.getSource('tv-routes')) {
        ROUTE_LAYERS.forEach(function (l) { if (map.getLayer(l)) map.removeLayer(l); });
        map.removeSource('tv-routes');
        onStyle(map);
      }
    }
    function kmText(r) { return (r.kind === 'scheme' ? '≈ ' : '') + String(r.km).replace('.', ',') + ' км'; }
    function fitRoute(r) {
      var b = new ml.LngLatBounds();
      r.lines.forEach(function (l) { l.forEach(function (c) { b.extend(c); }); });
      map.fitBounds(b, { padding: 50, pitch: 0, bearing: 0, duration: 1600, maxZoom: 16 });
    }
    map = makeMap(ml, { center: INDIA.center, zoom: INDIA.zoom, maxPitch: 70 });

    var cityMarkers = {}, spotMarkers = {};
    cities.forEach(function (c) {
      var el = document.createElement('button');
      el.type = 'button';
      el.className = 'tv-city' + (c.lectures.length ? ' has-l' : '');
      el.setAttribute('data-id', c.id);
      el.innerHTML = '<span class="tv-city-dot"></span><span class="tv-city-l">' + esc(c.name) + (c.lectures.length ? ' <b>' + c.lectures.length + '</b>' : '') + '</span>';
      el.addEventListener('click', function (e) { e.stopPropagation(); location.hash = c.id; });
      cityMarkers[c.id] = new ml.Marker({ element: el, anchor: 'center' }).setLngLat(c.center).addTo(map);
    });
    spots.forEach(function (s) {
      var el = document.createElement('button');
      el.type = 'button';
      el.className = 'tv-spot k-' + s.kind + (s.lectures.length ? ' has-l' : '');
      el.setAttribute('data-id', s.id);
      el.innerHTML = '<span class="tv-pin">' + kindSvg(s.kind) + (s.lectures.length ? '<i>' + s.lectures.length + '</i>' : '') + '</span><span class="tv-spot-l">' + esc(s.name) + '</span>';
      el.setAttribute('aria-label', s.name + (s.lectures.length ? ': ' + lectCount(s.lectures.length) : ''));
      el.addEventListener('click', function (e) { e.stopPropagation(); location.hash = s.id; });
      // Остриё булавки (угол квадрата, повёрнутого на 45°) выступает на ~6 px ниже её рамки —
      // поднимаем, чтобы на координате было именно остриё. Подпись — вне потока (travel.css),
      // иначе её появление при приближении сдвигало бы булавку.
      spotMarkers[s.id] = new ml.Marker({ element: el, anchor: 'bottom', offset: [0, -6] }).setLngLat(s.coords).addTo(map);
    });
    function syncZoom() {
      var z = map.getZoom();
      root.classList.toggle('z-spots', z >= SPOT_ZOOM);
      root.classList.toggle('z-labels', z >= 14.5);
      root.classList.toggle('z-labels-all', z >= 16.5);
    }
    map.on('zoom', syncZoom);
    ['tv-routes-track', 'tv-routes-scheme'].forEach(function (layer) {
      map.on('click', layer, function (e) { var f = e.features && e.features[0]; if (f) location.hash = 'route:' + f.properties.id; });
      map.on('mouseenter', layer, function () { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', layer, function () { map.getCanvas().style.cursor = ''; });
    });
    syncZoom();

    var overview = panel.innerHTML;
    // ссылки «паломничество» в обзоре — подсветить города поездки
    function markTrip(tripId) {
      var ids = {};
      if (tripId) (D.trips || []).forEach(function (t) {
        if (t.id === tripId) t.lectures.forEach(function (lid) { var l = D.lectures[lid]; if (l) ids[l.c] = 1; });
      });
      Object.keys(cityMarkers).forEach(function (k) { cityMarkers[k].getElement().classList.toggle('is-trip', !!ids[k]); });
      return Object.keys(ids);
    }

    function spotRow(s) {
      return '<li><a href="#' + esc(s.id) + '" class="tv-srow k-' + esc(s.kind) + (s.lectures.length ? ' has-l' : '') + '">' +
        '<span class="tv-pin sm">' + kindSvg(s.kind) + '</span><span class="tv-sn">' + esc(s.name) + '</span>' +
        (s.lectures.length ? '<span class="tv-sc mono">' + s.lectures.length + '</span>' : '') + '</a></li>';
    }
    function cityView(c) {
      var region = regionById[c.region];
      var cs = spots.filter(function (s) { return s.city === c.id; })
        .sort(function (a, b) { return b.lectures.length - a.lectures.length || a.name.localeCompare(b.name, 'ru'); });
      var html = '<div class="tv-crumbs mono"><a href="#">Святая Индия</a>' + (region ? ' · ' + esc(region.name) : '') + '</div>' +
        '<h2 class="display tv-h">' + esc(c.name) + '</h2>' +
        (c.lectures.length ? '<p class="tv-sub mono">' + lectCount(c.lectures.length) + '</p>' : '') +
        (c.summary ? '<p class="tv-p">' + esc(c.summary) + '</p>' : '');
      var cr = routes.filter(function (r) { return r.city === c.id; });
      if (cr.length) html += '<h3 class="tv-h3 mono">Парикрамы</h3><ul class="tv-routes">' + cr.map(function (r) {
        return '<li><a href="#route:' + esc(r.id) + '"><span class="tv-rl' + (r.kind === 'scheme' ? ' is-scheme' : '') + '" aria-hidden="true"></span><span class="tv-sn">' + esc(r.name) + '</span><span class="tv-sc mono">' + esc(kmText(r)) + '</span></a></li>';
      }).join('') + '</ul>';
      if (cs.length) html += '<h3 class="tv-h3 mono">Святые места</h3><ul class="tv-spots">' + cs.map(spotRow).join('') + '</ul>';
      if (c.lectures.length) html += '<h3 class="tv-h3 mono">Лекции, прочитанные здесь</h3>' + lectureList(c.lectures, {
        extra: function (id, l) { return l.s && spotById[l.s] ? ' · ' + esc(spotById[l.s].name) : ''; },
      });
      return html;
    }
    function spotView(s) {
      var c = cityById[s.city];
      var ll = s.coords[1].toFixed(6) + ',' + s.coords[0].toFixed(6);
      var quote = '';
      s.lectures.some(function (id) { var l = D.lectures[id]; if (l && l.q) { quote = '<blockquote class="tv-q">«' + esc(l.q) + '»<a href="/lectures/' + esc(id) + '/" class="mono">' + esc(ruDate(l.d)) + '</a></blockquote>'; return true; } return false; });
      return '<div class="tv-crumbs mono"><a href="#">Святая Индия</a> · <a href="#' + esc(c.id) + '">' + esc(c.name) + '</a></div>' +
        '<div class="tv-kind mono"><span class="tv-pin sm k-' + esc(s.kind) + '">' + kindSvg(s.kind) + '</span>' + esc(D.kinds[s.kind] || D.kinds.other) + '</div>' +
        '<h2 class="display tv-h">' + esc(s.name) + '</h2>' +
        (s.nameEn ? '<p class="tv-sub mono">' + esc(s.nameEn) + '</p>' : '') +
        (s.ph ? '<figure class="tv-photo"><img src="' + esc(s.ph) + '" alt="' + esc(s.name) + '" loading="lazy" decoding="async"></figure>' : '') +
        (s.summary ? '<p class="tv-p">' + esc(s.summary) + '</p>' : '') +
        (s.more ? '<div class="tv-more" data-more-for="' + esc(s.id) + '"></div>' : '') + quote +
        (s.lectures.length ? '<h3 class="tv-h3 mono">Лекции здесь · ' + s.lectures.length + '</h3>' + lectureList(s.lectures) : '') +
        '<div class="tv-ext">' +
          '<a class="sbtn ghost" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=' + ll + '">Google Карты</a>' +
          '<a class="sbtn ghost" target="_blank" rel="noopener" href="https://yandex.ru/maps/?pt=' + s.coords[0] + ',' + s.coords[1] + '&z=17&l=sat,skl">Яндекс Карты</a>' +
        '</div>' +
        (s.approx ? '<p class="tv-note">Точка на карте приблизительная.</p>' : '');
    }

    // Подробности места (описание и все фото из Holy Spots) — /travel/india-spots.json, один раз
    var moreP = null;
    function loadMore(s) {
      if (!s.more) return;
      moreP = moreP || fetch('/travel/india-spots.json').then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { moreP = null; return {}; });
      moreP.then(function (all) {
        var box = panel.querySelector('[data-more-for="' + s.id + '"]');
        var m = all[s.id];
        if (!box || !m) return;
        var html = '';
        if (m.p && m.p.length > 1) {
          html += '<div class="tv-thumbs">' + m.p.map(function (u, i) {
            return '<button type="button" data-ph="' + esc(u) + '"' + (i === 0 ? ' aria-pressed="true"' : '') + '><img src="' + esc(u) + '" alt="" loading="lazy" decoding="async"></button>';
          }).join('') + '</div>';
        }
        if (m.d && m.d.replace(/\s+/g, ' ').trim() !== (s.summary || '').trim()) {
          var paras = m.d.split(/\n\s*\n/).map(function (t) { return '<p>' + esc(t.trim()).replace(/\n/g, '<br>') + '</p>'; }).join('');
          html += '<details class="tv-details"><summary class="mono">Читать подробнее</summary>' + paras + '</details>';
        }
        if (m.hs) html += '<p class="tv-src mono">Описание и фото: <a href="https://holyspots.vedareader.ru/" target="_blank" rel="noopener">Holy Spots</a></p>';
        box.innerHTML = html;
        box.querySelectorAll('[data-ph]').forEach(function (b) {
          b.addEventListener('click', function () {
            var img = panel.querySelector('.tv-photo img');
            if (img) img.src = b.getAttribute('data-ph');
            box.querySelectorAll('[data-ph]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
          });
        });
      });
    }

    function setActive(cityId, spotId) {
      Object.keys(cityMarkers).forEach(function (k) { cityMarkers[k].getElement().classList.toggle('is-active', k === cityId); });
      Object.keys(spotMarkers).forEach(function (k) {
        var el = spotMarkers[k].getElement();
        el.classList.toggle('is-active', k === spotId);
        el.classList.toggle('in-city', spotById[k].city === cityId);
      });
    }

    function route() {
      if (!alive) return;
      var h = decodeURIComponent(location.hash.slice(1));
      if (h.indexOf('route:') === 0 && routeById[h.slice(6)]) {
        var r = routeById[h.slice(6)], rc = cityById[r.city];
        markTrip(null);
        setActive(rc.id, null);
        setActiveRoute(r.id);
        fitRoute(r);
        showPanel('<div class="tv-crumbs mono"><a href="#">Святая Индия</a> · <a href="#' + esc(rc.id) + '">' + esc(rc.name) + '</a> · Парикрама</div>' +
          '<h2 class="display tv-h">' + esc(r.name) + '</h2>' +
          '<p class="tv-sub mono">' + esc(kmText(r)) + (r.kind === 'scheme' ? ' по прямой между местами' : ' по GPS-треку') + (r.stops.length ? ' · ' + plural(r.stops.length, 'место', 'места', 'мест') : '') + '</p>' +
          (r.summary ? '<p class="tv-p">' + esc(r.summary) + '</p>' : '') +
          (r.stops.length ? '<h3 class="tv-h3 mono">Места на пути</h3><ol class="tv-spots tv-stops">' + r.stops.map(function (id) { return spotRow(spotById[id]); }).join('') + '</ol>' : '') +
          (r.kind === 'scheme'
            ? '<p class="tv-src mono">Схема: места по порядку ' + esc(r.source || 'обхода') + '. Пунктир соединяет места по прямой — это не тропа; настоящий путь идёт вокруг холма.</p>'
            : '<p class="tv-src mono">Трек: <a href="https://holyspots.vedareader.ru/" target="_blank" rel="noopener">Holy Spots</a>. Записан в несколько заходов — между отрезками бывают разрывы.</p>'));
        return;
      }
      setActiveRoute(null);
      if (h.indexOf('trip:') === 0) {
        var t = (D.trips || []).find(function (x) { return 'trip:' + x.id === h; });
        if (t) {
          setActive(null, null);
          var ids = markTrip(t.id);
          if (ids.length) {
            var b = new ml.LngLatBounds();
            ids.forEach(function (id) { b.extend(cityById[id].center); });
            map.fitBounds(b, { padding: 80, maxZoom: 9, pitch: 0, bearing: 0, duration: 1800 });
          }
          showPanel('<div class="tv-crumbs mono"><a href="#">Святая Индия</a> · Паломничество</div>' +
            '<h2 class="display tv-h">' + esc(t.title) + '</h2>' +
            '<p class="tv-sub mono">' + esc(ruDate(t.from)) + (t.to && t.to !== t.from ? ' — ' + esc(ruDate(t.to)) : '') + ' · ' + lectCount(t.lectures.length) + '</p>' +
            (t.summary ? '<p class="tv-p">' + esc(t.summary) + '</p>' : '') +
            lectureList(t.lectures, { after: function (id, l) {
              var where = l.s && spotById[l.s] ? spotById[l.s].name : (cityById[l.c] || {}).name;
              return where ? '<a href="#' + esc(l.s || l.c) + '" class="tv-where mono">↳ ' + esc(where) + '</a>' : '';
            } }));
          return;
        }
      }
      markTrip(null);
      var s = spotById[h], c = s ? cityById[s.city] : cityById[h];
      if (s) {
        setActive(c.id, s.id);
        map.flyTo({ center: s.coords, zoom: Math.max(16.3, c.zoom), pitch: 50, bearing: map.getBearing(), speed: 0.8, curve: 1.5 });
        showPanel(spotView(s));
        loadMore(s);
      } else if (c) {
        setActive(c.id, null);
        map.flyTo({ center: c.center, zoom: c.zoom, pitch: 40, bearing: 0, speed: 0.7, curve: 1.6 });
        showPanel(cityView(c));
      } else {
        setActive(null, null);
        map.flyTo(Object.assign({ speed: 0.9 }, INDIA));
        panel.innerHTML = overview;
        root.classList.remove('panel-open');
      }
    }
    window.addEventListener('hashchange', route);
    if (window.AM_SOFTNAV) window.AM_SOFTNAV.onCleanup(function () { window.removeEventListener('hashchange', route); });
    root.querySelectorAll('[data-home]').forEach(function (b) { b.addEventListener('click', function () { location.hash = ''; route(); }); });
    map.on('load', route);
  }

  loadLib().then(function (ml) {
    if (!alive) return;
    ml = ml.default || ml;
    if (MODE === 'india') initIndia(ml); else initWorld(ml);
    root.classList.add('is-ready');
    root.__map = map; // для отладки и автопроверок (позиции маркеров)
  }).catch(function (e) {
    root.classList.add('no-map');
    var ld = root.querySelector('.tv-loading');
    if (ld) ld.textContent = 'Карта не загрузилась — список мест ' + (window.innerWidth > 860 ? 'справа' : 'ниже') + '.';
    console.error('travel map', e);
  });
})();
