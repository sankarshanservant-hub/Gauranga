/* Работа без интернета — сайт «Гаура-лила» (site/README.md, раздел «Без интернета и установка»).
   С интернетом всё берётся с сайта (свежая версия) и попутно сохраняется; без интернета — сохранённое.
   • gl-core — основа: страница, стили, код, лента лил, спутники, места, картинки, карта-библиотека. Кладётся при установке
     помощника по описи data/files.json (её пишет site/tools/files_list.py при публикации) и обновляется каждой новой публикацией.
   • gl-data — главы писаний, стихи к лилам, жизнеописания: сохраняются, когда их открывают, или все сразу кнопкой
     «Скачать все писания» (offline.js). У каждой копии — метка x-gl-h (отпечаток файла из описи): по ней offline.js
     подтягивает изменившиеся файлы после новой публикации.
   • gl-ext — шрифты Google; gl-tiles — увиденные куски карты (не больше TILES_MAX).
   Музыку (assets/audio, 48 МБ) не сохраняем: она идёт частями (Range), без интернета её просто нет.
   Ключ сохранённой копии — адрес без ?v=… (одна копия на файл, всегда последняя полученная).
   V подставляет site/tools/publish_pages.sh — от неё зависит, что браузер заметит новую публикацию. */
const V = 'dev';
const CORE = 'gl-core', DATA = 'gl-data', EXT = 'gl-ext', TILES = 'gl-tiles', TILES_MAX = 2500;
const BASE = new URL('./', self.location).href;
const DATA_DIRS = ['data/library/', 'data/verses/', 'data/parshadas/'];

function key(href) {
  const u = new URL(href); u.search = ''; u.hash = '';
  return u.href === BASE + 'index.html' ? BASE : u.href;
}
const rel = (href) => href.slice(BASE.length);
const isData = (href) => { const r = rel(href); return DATA_DIRS.some((d) => r.startsWith(d)) && !r.endsWith('library/index.json'); };

let HASH = null; // путь → отпечаток, из сохранённой описи
async function hashes() {
  if (HASH) return HASH;
  HASH = {};
  try {
    const r = await caches.match(BASE + 'data/files.json');
    if (r) for (const [p, , h] of (await r.json()).data || []) HASH[p] = h;
  } catch (e) { /* без описи — без меток */ }
  return HASH;
}
async function tagged(r, href) {
  const h = (await hashes())[rel(href)];
  if (!h) return r;
  const headers = new Headers(r.headers); headers.set('x-gl-h', h);
  return new Response(await r.blob(), { status: r.status, statusText: r.statusText, headers });
}

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CORE);
    let core = [];
    try {
      const r = await fetch('data/files.json', { cache: 'no-store' });
      if (r.ok) { await c.put(BASE + 'data/files.json', r.clone()); core = (await r.json()).core || []; }
    } catch (err) { /* локальный запуск без описи */ }
    await Promise.all(['./', ...core].map(async (p) => {
      try { const r = await fetch(p, { cache: 'no-cache' }); if (r.ok) await c.put(key(new URL(p, BASE).href), r); } catch (err) { /* следующая попытка — при открытии */ }
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    HASH = null;
    for (const n of await caches.keys()) if (![CORE, DATA, EXT, TILES].includes(n)) await caches.delete(n);
    await self.clients.claim();
  })());
});

let tilePuts = 0;
async function trimTiles() {
  const c = await caches.open(TILES), ks = await c.keys();
  for (let i = 0; i < ks.length - TILES_MAX; i++) await c.delete(ks[i]);
}

// сначала сеть (свежая версия), при неудаче — сохранённое; wait > 0 — сколько ждать сеть, если копия уже есть
async function networkFirst(e, k, store, wait) {
  const c = await caches.open(store);
  const net = fetch(e.request).then(async (r) => {
    if (r.ok && (r.type === 'basic' || r.type === 'cors')) {
      const copy = store === DATA ? await tagged(r.clone(), k) : r.clone();
      e.waitUntil(c.put(k, copy).then(() => { if (store === TILES && ++tilePuts % 100 === 0) return trimTiles(); }));
    }
    return r;
  });
  if (wait > 0) {
    const old = await c.match(k);
    if (old) {
      const timer = new Promise((res) => setTimeout(() => res(null), wait));
      const r = await Promise.race([net.catch(() => null), timer]);
      e.waitUntil(net.catch(() => {}));
      return r || old;
    }
  }
  try { return await net; } catch (err) {
    const old = (await c.match(k)) || (await caches.match(k));
    if (old) return old;
    throw err;
  }
}
async function cacheFirst(e, store) {
  const c = await caches.open(store), old = await c.match(e.request);
  if (old) return old;
  const r = await fetch(e.request);
  if (r.ok || r.type === 'opaque') e.waitUntil(c.put(e.request, r.clone()));
  return r;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || req.headers.has('range')) return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin) {
    if (!url.href.startsWith(BASE) || /\.mp3$/i.test(url.pathname)) return;
    if (req.mode === 'navigate') { e.respondWith(networkFirst(e, BASE, CORE, 4000)); return; }
    const k = key(url.href);
    e.respondWith(networkFirst(e, k, isData(k) ? DATA : CORE, 0));
    return;
  }
  if (/(^|\.)fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) { e.respondWith(cacheFirst(e, EXT)); return; }
  if (/(^|\.)tiles\.openfreemap\.org$|(^|\.)arcgisonline\.com$/.test(url.hostname)) { e.respondWith(networkFirst(e, req.url, TILES, 0)); return; }
});
