/* Без интернета и установка — сайт «Гаура-лила» (site/README.md, «Без интернета и установка»). Код сайта (app.js) не трогает.
   • Регистрирует помощника sw.js: основа сайта и всё открытое сохраняются сами, с интернетом всегда берётся свежее.
   • Кнопка в шапке (рядом с музыкой и языком) → окошко: есть ли связь, что сохранено, «Скачать все писания»
     (главы, стихи к лилам, жизнеописания — по описи data/files.json), «Освободить место», «Установить приложение».
   • Если писания скачаны целиком — при каждом заходе с интернетом тихо подтягивает изменившиеся и новые файлы
     (сверка по отпечаткам из описи), удалённые с сайта — убирает.
   • Приглашение установить внизу экрана (Android и компьютер — системное окно, iPhone — подсказка «Поделиться →
     На экран „Домой“»); не показывается в рамке (harekrishna.info/apps/gaura-lila/), со значка и после «×».
     ?install=1 — показать сразу (так ведут кнопки «Установить» на harekrishna.info).
   Язык — как на сайте (localStorage gl-prefs, кнопки RU/EN). */
(function () {
  'use strict';
  var DATA = 'gl-data', BASE = new URL('./', location.href).href;
  var K_ALL = 'gl-offline-all', K_OFF = 'appInviteOff:gaura-lila', K_DONE = 'appInstalled:gaura-lila';
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} }
  function lang() { try { var p = JSON.parse(get('gl-prefs') || 'null'); return p && p.lang === 'en' ? 'en' : 'ru'; } catch (e) { return 'ru'; } }
  var T = {
    ru: {
      btn: 'Без интернета', title: 'Без интернета', on: 'Есть подключение — показываю свежую версию сайта.',
      offNow: 'Нет подключения — показываю сохранённое.',
      base: 'Лента лил, спутники, места и всё, что вы открывали, сохраняются на этом устройстве сами.',
      all: function (mb) { return 'Скачать все писания (≈ ' + mb + ' МБ)'; },
      allWhat: 'Все главы переводов, стихи к лилам и жизнеописания — чтобы читать без интернета.',
      busy: function (p) { return 'Скачиваю… ' + p + ' %'; },
      done: function (mb) { return 'Все писания сохранены (' + mb + ' МБ). Новые главы и правки подтягиваются сами, когда есть интернет.'; },
      part: function (a, b) { return 'Сохранено ' + a + ' из ' + b + ' МБ — докачаю, когда будет интернет.'; },
      free: 'Освободить место', freed: 'Скачанные писания удалены. Основа сайта осталась.',
      fail: 'Не всё скачалось — попробую снова при следующем заходе с интернетом.',
      noSpace: 'На устройстве не хватает места для всех писаний.',
      music: 'Музыка без интернета не играет.',
      ios: 'На iPhone и iPad сохранённое надёжно хранится у установленного приложения: «Поделиться» → «На экран „Домой“».',
      install: 'Установить как приложение', instTitle: 'Установить «Гаура-лилу»',
      instSub: 'Своим значком на экране, во весь экран — и без интернета.', go: 'Установить', how: 'Как?', offInv: 'Не предлагать',
      menu: 'В меню браузера: «Установить приложение» или «Добавить на главный экран».', mac: 'Меню «Файл» → «Добавить в Dock».',
      help: 'Как установить «Гаура-лилу»', s1: 'Нажмите <span class="s">⬆︎</span> «Поделиться» — внизу экрана в Safari или в адресной строке.',
      s2: 'Выберите «На экран „Домой“» (если не видно — прокрутите список вниз).', s3: 'Нажмите «Добавить».',
      after: 'Значок появится на экране телефона, приложение будет открываться во весь экран, без адресной строки.', ok: 'Понятно', close: 'Закрыть'
    },
    en: {
      btn: 'Offline', title: 'Offline', on: 'Online — showing the latest version of the site.',
      offNow: 'No connection — showing what is saved.',
      base: 'The lila ribbon, associates, places and everything you have opened are saved on this device automatically.',
      all: function (mb) { return 'Download all scriptures (≈ ' + mb + ' MB)'; },
      allWhat: 'All translated chapters, verses for the lilas and biographies — to read without internet.',
      busy: function (p) { return 'Downloading… ' + p + ' %'; },
      done: function (mb) { return 'All scriptures are saved (' + mb + ' MB). New chapters and corrections arrive by themselves when online.'; },
      part: function (a, b) { return 'Saved ' + a + ' of ' + b + ' MB — the rest will follow when online.'; },
      free: 'Free up space', freed: 'Downloaded scriptures removed. The site itself stays saved.',
      fail: 'Not everything downloaded — will retry on the next visit with internet.',
      noSpace: 'Not enough space on this device for all scriptures.',
      music: 'Music does not play offline.',
      ios: 'On iPhone and iPad saved content is kept reliably by the installed app: Share → Add to Home Screen.',
      install: 'Install as an app', instTitle: 'Install “Gaura-lila”',
      instSub: 'Its own icon, full screen — and offline.', go: 'Install', how: 'How?', offInv: 'Don’t suggest',
      menu: 'In the browser menu: “Install app” or “Add to Home screen”.', mac: 'File menu → “Add to Dock”.',
      help: 'How to install “Gaura-lila”', s1: 'Tap <span class="s">⬆︎</span> “Share” — at the bottom of Safari or in the address bar.',
      s2: 'Choose “Add to Home Screen” (scroll down if you don’t see it).', s3: 'Tap “Add”.',
      after: 'The icon will appear on your home screen; the app opens full screen, without the address bar.', ok: 'Got it', close: 'Close'
    }
  };
  function t() { return T[lang()]; }

  var inFrame = false; try { inFrame = window.self !== window.top; } catch (e) { inFrame = true; }
  var STANDALONE = navigator.standalone === true || (window.matchMedia && (matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches));
  var ua = navigator.userAgent;
  var IOS = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  var MAC_SAFARI = !IOS && /Macintosh/.test(ua) && /Safari\//.test(ua) && !/Chrome|Chromium|Edg|Firefox/.test(ua);
  var CAN = 'serviceWorker' in navigator && 'caches' in window && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1');

  var css = '.offl-pop{position:fixed;z-index:60;width:min(380px,calc(100vw - 24px));box-sizing:border-box;padding:16px 18px 14px;' +
    'background:#f3e2bd url(assets/img/paper.webp) center/cover;color:#3b2412;border-radius:10px;border:1px solid rgba(138,90,43,.55);' +
    'box-shadow:0 14px 40px rgba(0,0,0,.55);font:16px/1.4 "EB Garamond",Georgia,serif;text-shadow:none}' +
    '.offl-pop h3{margin:0 0 6px;font:600 21px/1.2 "Cormorant Garamond","EB Garamond",Georgia,serif;color:#5a3415}' +
    '.offl-pop p{margin:6px 0}.offl-pop .st{color:#6b4a2b;font-style:italic}.offl-pop .st.off{color:#8a2f1d}' +
    '.offl-pop .act{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}' +
    '.offl-pop button.b{appearance:none;cursor:pointer;font:600 15px/1.2 "EB Garamond",Georgia,serif;padding:8px 14px;border-radius:999px;' +
    'border:1px solid #8a5a2b;background:#5a3415;color:#f6e3bd}.offl-pop button.b2{background:none;color:#5a3415}' +
    '.offl-pop button.b:disabled{opacity:.6;cursor:default}.offl-pop .x{position:absolute;top:6px;right:8px;appearance:none;border:0;background:none;' +
    'font:24px/1 Georgia,serif;color:#8a5a2b;cursor:pointer;width:32px;height:32px}' +
    '.offl-pop .bar{height:6px;border-radius:6px;background:rgba(138,90,43,.2);overflow:hidden;margin-top:8px}.offl-pop .bar i{display:block;height:100%;background:#8a5a2b;width:0}' +
    '.offl-pop small{display:block;color:#6b4a2b;margin-top:8px;font-size:14px}' +
    '.corner .music.offl svg{width:17px;height:17px}.music.offl[data-state="off"]{box-shadow:0 0 0 2px rgba(180,60,40,.8)}' +
    '.ainst{position:fixed;left:50%;bottom:calc(14px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:61;display:flex;align-items:center;gap:12px;' +
    'width:min(500px,calc(100vw - 24px));box-sizing:border-box;padding:10px 8px 10px 12px;border-radius:10px;background:#f3e2bd url(assets/img/paper.webp) center/cover;' +
    'color:#3b2412;border:1px solid rgba(138,90,43,.55);box-shadow:0 10px 32px rgba(0,0,0,.5);font:16px/1.3 "EB Garamond",Georgia,serif;text-shadow:none}' +
    '.ainst img{width:42px;height:42px;border-radius:9px;flex:none}.ainst .t{flex:1;min-width:0}.ainst .t b{display:block;font-weight:600}' +
    '.ainst .t span{color:#6b4a2b;font-style:italic;font-size:14.5px}.ainst .go{appearance:none;cursor:pointer;font:600 15px/1 "EB Garamond",Georgia,serif;' +
    'background:#5a3415;color:#f6e3bd;border:1px solid #8a5a2b;border-radius:999px;padding:0 16px;min-height:40px;flex:none}' +
    '.ainst .x{appearance:none;border:0;background:none;cursor:pointer;color:#8a5a2b;font:24px/1 Georgia,serif;width:34px;height:40px;flex:none}' +
    '.ainst-ios{position:fixed;inset:0;z-index:62;background:rgba(20,13,7,.6);display:flex;align-items:flex-end;justify-content:center;padding:12px;box-sizing:border-box}' +
    '.ainst-ios>div{width:min(500px,100%);box-sizing:border-box;background:#f3e2bd url(assets/img/paper.webp) center/cover;color:#3b2412;border-radius:12px;' +
    'border:1px solid rgba(138,90,43,.55);padding:18px 18px 14px;font:16px/1.45 "EB Garamond",Georgia,serif;margin-bottom:env(safe-area-inset-bottom,0px);text-shadow:none}' +
    '.ainst-ios b.h{display:block;font:600 21px/1.2 "Cormorant Garamond","EB Garamond",Georgia,serif;color:#5a3415;margin-bottom:8px}' +
    '.ainst-ios ol{margin:0 0 10px;padding-left:1.4em}.ainst-ios li{margin:4px 0}.ainst-ios p{color:#6b4a2b;font-style:italic;margin:0 0 12px}' +
    '.ainst-ios .ok{appearance:none;cursor:pointer;font:600 15px/1 "EB Garamond",Georgia,serif;background:#5a3415;color:#f6e3bd;border:1px solid #8a5a2b;' +
    'border-radius:999px;padding:0 20px;min-height:42px;float:right}.ainst-ios .s{display:inline-block;padding:0 6px;border-radius:4px;border:1px solid #8a5a2b;font-style:normal}';
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function addCss() { if (document.getElementById('offl-css')) return; var s = el('style'); s.id = 'offl-css'; s.textContent = css; document.head.appendChild(s); }
  var MB = function (b) { return Math.max(1, Math.round(b / 1048576)); };

  // ── помощник ──
  if (CAN && !inFrame) navigator.serviceWorker.register('sw.js').catch(function () {});

  // ── опись и скачанное ──
  var LIST = null;
  function files() {
    if (LIST) return Promise.resolve(LIST);
    return fetch('data/files.json', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (j) { LIST = j; return j; });
  }
  function have() { // путь → отпечаток у сохранённой копии
    return caches.open(DATA).then(function (c) {
      return c.keys().then(function (ks) {
        return Promise.all(ks.map(function (rq) { return c.match(rq).then(function (r) { return [rq.url.slice(BASE.length), r && r.headers.get('x-gl-h')]; }); }));
      });
    }).then(function (pairs) { var m = {}; pairs.forEach(function (p) { m[p[0]] = p[1] || ''; }); return m; });
  }
  var job = null; // идущая закачка: {p: 0..1}
  function download(onProg) {
    if (job) return job.promise;
    job = { p: 0 };
    job.promise = Promise.all([files(), have(), caches.open(DATA)]).then(function (a) {
      var j = a[0], got = a[1], c = a[2];
      var want = {}; (j.data || []).forEach(function (f) { want[f[0]] = f; });
      var stale = Object.keys(got).filter(function (p) { return !want[p]; });
      var todo = (j.data || []).filter(function (f) { return got[f[0]] !== f[2]; });
      var total = todo.reduce(function (s, f) { return s + f[1]; }, 0) || 1, doneB = 0, failed = 0, full = false, i = 0;
      function one() {
        if (i >= todo.length || full) return Promise.resolve();
        var f = todo[i++];
        return fetch(f[0] + '?v=' + encodeURIComponent(j.v), { cache: 'no-cache', headers: { 'x-gl-sync': '1' } }).then(function (r) {
          if (!r.ok) throw new Error(r.status);
          return r.blob().then(function (b) {
            var h = new Headers(r.headers); h.set('x-gl-h', f[2]);
            return c.put(BASE + f[0], new Response(b, { status: 200, headers: h }));
          });
        }).catch(function (e) { failed++; if (e && e.name === 'QuotaExceededError') full = true; })
          .then(function () { doneB += f[1]; job.p = doneB / total; if (onProg) onProg(job.p); return one(); });
      }
      return Promise.all(stale.map(function (p) { return c.delete(BASE + p); }))
        .then(function () { return Promise.all([one(), one(), one(), one(), one(), one()]); })
        .then(function () { return { failed: failed, full: full }; });
    }).then(function (res) { job = null; return res; }, function (e) { job = null; throw e; });
    return job.promise;
  }
  function savedSize() {
    return Promise.all([files(), have()]).then(function (a) {
      var j = a[0], got = a[1], all = 0, ok = 0;
      (j.data || []).forEach(function (f) { all += f[1]; if (got[f[0]] === f[2]) ok += f[1]; });
      return { all: all, ok: ok };
    });
  }

  // есть ли связь на самом деле (navigator.onLine бывает «да» при Wi-Fi без интернета): запрос мимо помощника
  var NET = { ok: navigator.onLine, at: 0 };
  function probe() {
    if (!navigator.onLine) { NET = { ok: false, at: Date.now() }; return Promise.resolve(false); }
    if (Date.now() - NET.at < 10000) return Promise.resolve(NET.ok);
    return fetch('data/files.json?probe=' + Date.now(), { cache: 'no-store', headers: { 'x-gl-sync': '1' } })
      .then(function (r) { return r.ok; }, function () { return false; })
      .then(function (ok) { NET = { ok: ok, at: Date.now() }; paintBtn(); return ok; });
  }

  // ── окошко ──
  var pop = null, btn = null, msg = '';
  function place() {
    if (!pop || !btn) return;
    var r = btn.getBoundingClientRect(), w = pop.offsetWidth;
    pop.style.top = Math.round(r.bottom + 8) + 'px';
    pop.style.left = Math.round(Math.max(12, Math.min(r.left, window.innerWidth - w - 12))) + 'px';
  }
  function close() { if (pop) { pop.remove(); pop = null; } }
  function render() {
    if (!pop) return;
    var L = t();
    pop.innerHTML = '';
    var x = el('button', 'x', '×'); x.type = 'button'; x.setAttribute('aria-label', L.close); x.onclick = close; pop.appendChild(x);
    pop.appendChild(el('h3', '', L.title));
    var st = el('p', NET.ok ? 'st' : 'st off', NET.ok ? L.on : L.offNow); pop.appendChild(st);
    probe().then(function (ok) { st.className = ok ? 'st' : 'st off'; st.textContent = ok ? L.on : L.offNow; var g = pop && pop.querySelector('[data-all]'); if (g) g.disabled = !ok; });
    pop.appendChild(el('p', '', L.base));
    var info = el('p', ''), act = el('div', 'act'), bar = el('div', 'bar'); bar.appendChild(el('i'));
    var act2 = el('div', 'act');
    pop.appendChild(info); pop.appendChild(act); pop.appendChild(act2);
    files().then(savedSize).then(function (s) {
      if (!pop) return;
      if (job) {
        info.textContent = L.busy(Math.round(job.p * 100)); info.appendChild(bar); bar.firstChild.style.width = Math.round(job.p * 100) + '%';
      } else if (get(K_ALL) === '1') {
        info.textContent = s.ok >= s.all ? L.done(MB(s.all)) : L.part(MB(s.ok), MB(s.all));
        var fr = el('button', 'b b2', L.free); fr.type = 'button';
        fr.onclick = function () { set(K_ALL, null); caches.delete(DATA).then(function () { msg = L.freed; render(); }); };
        act.appendChild(fr);
      } else {
        info.textContent = L.allWhat;
        var go = el('button', 'b', L.all(MB(s.all))); go.type = 'button'; go.disabled = !NET.ok; go.setAttribute('data-all', '');
        go.onclick = function () {
          set(K_ALL, '1'); msg = '';
          if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(function () {});
          var p = download(function (f) { if (pop) { info.textContent = L.busy(Math.round(f * 100)); info.appendChild(bar); bar.firstChild.style.width = Math.round(f * 100) + '%'; } });
          render();
          p.then(function (r) { msg = r.full ? L.noSpace : r.failed ? L.fail : ''; render(); }, function () { msg = L.fail; render(); });
        };
        act.appendChild(go);
      }
    }).catch(function () { info.textContent = ''; });
    if (canInstall()) { var ib = el('button', 'b b2', L.install); ib.type = 'button'; ib.onclick = install; act2.appendChild(ib); }
    if (msg) pop.appendChild(el('small', '', msg));
    pop.appendChild(el('small', '', (IOS && !STANDALONE ? L.ios + ' ' : '') + L.music));
    place();
  }
  function open() {
    if (pop) { close(); return; }
    addCss(); pop = el('div', 'offl-pop'); pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', t().title);
    document.body.appendChild(pop); render();
  }
  function mountBtn() {
    var corner = document.querySelector('.corner'), music = document.getElementById('music');
    if (!corner || btn) return;
    addCss();
    btn = el('button', 'music offl'); btn.type = 'button';
    btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v11m0 0l-4.5-4.5M12 14l4.5-4.5M5 17.5v2h14v-2" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    btn.onclick = open;
    if (music && music.parentNode === corner) corner.insertBefore(btn, music.nextSibling); else corner.appendChild(btn);
    paintBtn();
  }
  function paintBtn() {
    if (!btn) return;
    var L = t(); btn.setAttribute('aria-label', L.btn); btn.title = L.btn; btn.dataset.state = NET.ok ? 'on' : 'off';
  }
  window.addEventListener('online', function () { NET.at = 0; probe().then(function () { render(); sync(); }); });
  window.addEventListener('offline', function () { NET = { ok: false, at: Date.now() }; paintBtn(); render(); });
  window.addEventListener('resize', place);
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('[data-lang]')) setTimeout(function () { paintBtn(); render(); }, 0);
    // путь щелчка — на момент щелчка: кнопка внутри окошка к этому времени могла быть уже перерисована
    var path = e.composedPath ? e.composedPath() : [e.target];
    if (pop && path.indexOf(pop) < 0 && !(btn && path.indexOf(btn) > -1)) close();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

  // писания скачаны целиком — подтянуть изменения с последней публикации
  function sync() {
    if (!CAN || get(K_ALL) !== '1' || job) return;
    probe().then(function (ok) { if (ok && !job) download().then(function () { render(); }, function () {}); });
  }

  // ── установка ──
  var evt = null, ibar = null, forced = /[?&]install=1\b/.test(location.search);
  if (forced) { try { var u = new URL(location.href); u.searchParams.delete('install'); history.replaceState(history.state, '', u.pathname + u.search + u.hash); } catch (e) {} }
  function canInstall() { return !inFrame && !STANDALONE && (!!evt || IOS); }
  function iosHelp() {
    addCss(); var L = t();
    var wrap = el('div', 'ainst-ios'), box = el('div');
    box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', L.help);
    box.innerHTML = '<b class="h"></b><ol><li>' + L.s1 + '</li><li>' + L.s2 + '</li><li>' + L.s3 + '</li></ol><p></p>';
    box.querySelector('.h').textContent = L.help; box.querySelector('p').textContent = L.after;
    var ok = el('button', 'ok', L.ok); ok.type = 'button'; ok.onclick = function () { wrap.remove(); };
    box.appendChild(ok); box.appendChild(el('div')).style.clear = 'both';
    wrap.appendChild(box); wrap.onclick = function (e) { if (e.target === wrap) wrap.remove(); };
    document.body.appendChild(wrap);
  }
  function install() {
    close();
    if (evt) { var ev = evt; evt = null; ev.prompt(); (ev.userChoice || Promise.resolve({})).then(function (c) { if (c && c.outcome === 'accepted') installed(); else hideBar(); }); return; }
    if (IOS) iosHelp();
  }
  function installed() { set(K_DONE, '1'); hideBar(); }
  function hideBar() { if (ibar) { ibar.remove(); ibar = null; } }
  function showBar(kind) {
    if (ibar || inFrame || STANDALONE || !document.body) return;
    addCss(); var L = t();
    ibar = el('div', 'ainst'); ibar.setAttribute('role', 'dialog'); ibar.setAttribute('aria-label', L.instTitle);
    var ic = el('img'); ic.src = 'icons/icon-192.png'; ic.alt = ''; ibar.appendChild(ic);
    var tx = el('div', 't'); tx.appendChild(el('b', '', L.instTitle));
    tx.appendChild(el('span', '', kind === 'menu' ? (MAC_SAFARI ? L.mac : L.menu) : L.instSub)); ibar.appendChild(tx);
    if (kind !== 'menu') { var go = el('button', 'go', kind === 'ios' ? L.how : L.go); go.type = 'button'; go.onclick = install; ibar.appendChild(go); }
    var x = el('button', 'x', '×'); x.type = 'button'; x.setAttribute('aria-label', L.offInv);
    x.onclick = function () { set(K_OFF, '1'); hideBar(); }; ibar.appendChild(x);
    document.body.appendChild(ibar);
  }
  var allowed = !inFrame && !STANDALONE && (forced || (get(K_OFF) !== '1' && get(K_DONE) !== '1'));
  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); evt = e; render(); if (allowed) setTimeout(function () { showBar('prompt'); }, forced ? 0 : 2500); });
  window.addEventListener('appinstalled', installed);

  function start() {
    if (!inFrame && CAN) mountBtn();
    if (allowed) {
      if (IOS) { if (forced) iosHelp(); else setTimeout(function () { showBar('ios'); }, 2500); }
      else if (forced) setTimeout(function () { if (!evt && !ibar) showBar('menu'); }, 2500);
    }
    probe(); setTimeout(sync, 6000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
