// Звук игры: тихая генеративная музыка (тампура + редкие фразы арфы в раге), фоны природы, шаги, двери, колокольчик.
// Записи — свободные (CC0): см. snd/CREDITS.md. Шаги босыми ногами синтезируются под поверхность.
const SA = 311.13;                     // Са = ре-диез (тампура записана на 77.7 Гц — та же нота двумя октавами ниже)
const RAGAS = {                        // ступени в полутонах от Са; home — где фраза любит останавливаться
  day: { deg: [0, 2, 4, 7, 9], home: [0, 4, 7] },             // Бхупали — светлая, дневная
  dusk: { deg: [0, 2, 4, 6, 7, 9, 11], home: [4, 11, 0] },    // Ямань — вечерняя, сумерки
  night: { deg: [0, 3, 5, 8, 10], home: [0, 5] },             // Малькаунс — глубокая ночь
};
const NOTES = [['harp-11', 196.0], ['harp-6', 293.66], ['harp-10', 349.23], ['harp-1', 440.0], ['harp-4', 523.25], ['harp-8', 659.26], ['harp-12', 783.99]];
const FILES = ['tanpura', 'amb_day', 'amb_dusk', 'amb_night', 'bn_dusk_mynas', 'bn_night_pond', 'bn_peafowl', 'fire', 'shimmer', 'bell1', 'bell2', 'bell3', 'kartal', 'grass_1', 'grass_2',
  'creak1', 'creak2', 'doorOpen_1', 'bookFlip1', 'bookFlip2', 'bookOpen', ...NOTES.map((n) => n[0])];
// фоны по времени суток: слои [запись, громкость]; bn_* — полевые записи Бенгалии и Индии из исторической базы (PD)
const AMB = { day: [['amb_day', 1]], dusk: [['bn_dusk_mynas', 0.85], ['amb_dusk', 0.4]], night: [['bn_night_pond', 1], ['amb_night', 0.35]] };
const rnd = (a, b) => a + Math.random() * (b - a), pick = (a) => a[Math.floor(Math.random() * a.length)];

export function createAudio(base = 'snd/') {
  let ctx = null, buf = {}, started = false, time = 'day', muted = false, ready = false;
  try { muted = localStorage.getItem('gaura.sound') === 'off'; } catch (e) { /* нет хранилища — звук включён */ }
  let master, music, amb, sfx, verb, ambLP, beds = {}, fireG, duckG;

  function bus(to, g = 1) { const n = ctx.createGain(); n.gain.value = g; n.connect(to); return n; }
  function impulse(sec = 3.2) {
    const n = Math.floor(ctx.sampleRate * sec), b = ctx.createBuffer(2, n, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = b.getChannelData(c); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 2.6); }
    return b;
  }
  // бесконечная «постель» из записи: перекрывающиеся проигрывания с плавной сменой
  function bed(name, out, fade = 4) {
    const b = buf[name]; if (!b) return null;
    const g = ctx.createGain(); g.gain.value = 0; g.connect(out);
    let stop = false;
    const play = (t) => {
      if (stop) return;
      const s = ctx.createBufferSource(); s.buffer = b; const e = ctx.createGain(); s.connect(e); e.connect(g);
      const off = rnd(0, Math.max(b.duration * 0.3, 0)), dur = b.duration - off;
      e.gain.setValueAtTime(0, t); e.gain.linearRampToValueAtTime(1, t + fade);
      e.gain.setValueAtTime(1, t + dur - fade); e.gain.linearRampToValueAtTime(0, t + dur);
      s.start(t, off); s.stop(t + dur + 0.05);
      setTimeout(() => play(t + dur - fade), Math.max((t + dur - fade - ctx.currentTime - 2) * 1000, 0));
    };
    play(ctx.currentTime + 0.05);
    return { g, stop: () => { stop = true; } };
  }
  function one(name, { gain = 1, rate = 1, pan = 0, to = sfx, when = 0, lp = 0 } = {}) {
    const b = buf[name]; if (!b || !ctx) return;
    const s = ctx.createBufferSource(); s.buffer = b; s.playbackRate.value = rate;
    let n = s; if (lp) { const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = lp; n.connect(f); n = f; }
    const g = ctx.createGain(); g.gain.value = gain; const p = ctx.createStereoPanner(); p.pan.value = Math.max(-1, Math.min(1, pan));
    n.connect(g); g.connect(p); p.connect(to); s.start(ctx.currentTime + when);
  }

  // ------------------------------------------------ музыка
  function note(freq, gain, when) {
    const cand = NOTES.filter((n) => buf[n[0]]); if (!cand.length) return;
    const [name, f0] = cand.reduce((a, n) => Math.abs(Math.log(n[1] / freq)) < Math.abs(Math.log(a[1] / freq)) ? n : a);
    one(name, { gain: gain * 1.4, rate: freq / f0, pan: rnd(-0.35, 0.35), to: music, when, lp: 3200 });
  }
  const freqOf = (deg, oct) => SA * Math.pow(2, (deg + 12 * oct) / 12);
  function phrase() {
    const r = RAGAS[time] ?? RAGAS.day, D = r.deg, n = D.length;
    let i = D.indexOf(pick(r.home)), oct = Math.random() < 0.35 ? 1 : 0, t = 0;
    const len = 2 + Math.floor(Math.random() * 4);
    for (let k = 0; k < len; k++) {
      note(freqOf(D[i], oct), rnd(0.09, 0.15) * (k === len - 1 ? 1.1 : 1), t);
      t += rnd(0.55, 1.35) * (k === len - 2 ? 1.4 : 1);
      const st = Math.random() < 0.7 ? pick([-1, 1]) : Math.random() < 0.85 ? pick([-2, 2]) : 0;
      i += st; if (i < 0) { i += n; oct--; } if (i >= n) { i -= n; oct++; } oct = Math.max(0, Math.min(1, oct));
    }
    if (k3++ % 3 === 2) { i = D.indexOf(pick(r.home)); note(freqOf(D[i], 0), 0.12, t + 0.3); }
  }
  let k3 = 0;
  function glide() {               // редкий тихий перебор, как на сварамандале
    const D = (RAGAS[time] ?? RAGAS.day).deg;
    let t = 0; for (let o = 0; o < 2; o++) for (const d of D) { note(freqOf(d, o), 0.035, t); t += 0.07; }
    note(freqOf(0, 2), 0.04, t);
  }
  function peafowl() {             // днём изредка — далёкий крик павлина
    if (time === 'day' && !muted) one('bn_peafowl', { gain: rnd(0.07, 0.12), pan: rnd(-0.8, 0.8), to: amb, lp: 2600 });
    setTimeout(peafowl, rnd(110, 260) * 1000);
  }
  function scheduler() {
    if (!started) return;
    const roll = Math.random();
    if (roll < 0.12) glide(); else if (roll < 0.2) one('kartal', { gain: 0.07, to: music, pan: rnd(-0.3, 0.3) });
    else if (roll < 0.85) phrase();
    setTimeout(scheduler, rnd(8, 18) * 1000);
  }

  async function load() {
    await Promise.all(FILES.map(async (f) => {
      try { const r = await fetch(base + f + '.mp3'); buf[f] = await ctx.decodeAudioData(await r.arrayBuffer()); } catch (e) { /* без этого звука */ }
    }));
  }
  function setMute(m) {
    muted = m; try { localStorage.setItem('gaura.sound', m ? 'off' : 'on'); } catch (e) { /* ничего */ }
    if (ctx) master.gain.setTargetAtTime(m ? 0 : 0.9, ctx.currentTime, 0.3);
  }

  // шаги: короткий шорох, «вылепленный» фильтром под поверхность, + глухой удар пятки
  let noise = null;
  const SURF = { earth: [380, 0.09, 80, 1], clay: [620, 0.07, 95, 0.9], mud: [460, 0.1, 75, 1], brick: [1500, 0.05, 125, 0.7] };
  function step(surface, gain, pan) {
    if (!ready || muted || gain < 0.01) return;
    const t = ctx.currentTime;
    if (surface === 'grass') { one(pick(['grass_1', 'grass_2']), { gain: gain * 0.55, rate: rnd(0.85, 1.15), pan, lp: 5000 }); gain *= 0.4; surface = 'earth'; }
    const [f, dec, th, gm] = SURF[surface] ?? SURF.earth, k = rnd(0.85, 1.2), g0 = gain * gm * rnd(0.8, 1.1);
    const s = ctx.createBufferSource(); s.buffer = noise; s.playbackRate.value = rnd(0.8, 1.2);
    const fl = ctx.createBiquadFilter(); fl.type = surface === 'brick' ? 'bandpass' : 'lowpass'; fl.frequency.value = f * k; fl.Q.value = 0.8;
    const g = ctx.createGain(), p = ctx.createStereoPanner(); p.pan.value = Math.max(-1, Math.min(1, pan));
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(g0 * 0.9, t + 0.004); g.gain.exponentialRampToValueAtTime(0.0005, t + dec * k);
    s.connect(fl); fl.connect(g); g.connect(p); p.connect(sfx); s.start(t); s.stop(t + 0.3);
    const o = ctx.createOscillator(), og = ctx.createGain(); o.frequency.setValueAtTime(th * k, t); o.frequency.exponentialRampToValueAtTime(th * 0.6, t + 0.06);
    og.gain.setValueAtTime(g0 * 0.5, t); og.gain.exponentialRampToValueAtTime(0.0005, t + 0.07); o.connect(og); og.connect(p); o.start(t); o.stop(t + 0.1);
  }

  return {
    get muted() { return muted; }, get ready() { return ready; },
    get loaded() { return Object.keys(buf).length; },
    tap() { const d = ctx.createMediaStreamDestination(); master.connect(d); return d.stream; },   // для записи пробы
    async start() {
      if (started) return; started = true;
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      ctx = new AC(); master = bus(ctx.destination, 0); duckG = bus(master, 1);
      music = bus(duckG, 0.8); verb = ctx.createConvolver(); verb.buffer = impulse(); const wet = bus(duckG, 0.38); verb.connect(wet);
      music.connect(verb);
      ambLP = ctx.createBiquadFilter(); ambLP.type = 'lowpass'; ambLP.frequency.value = 16000; ambLP.connect(master); amb = bus(ambLP, 0.5);
      sfx = bus(master, 0.8); const sv = bus(verb, 0.25); sfx.connect(sv);
      noise = ctx.createBuffer(1, Math.floor(ctx.sampleRate * 0.3), ctx.sampleRate);
      { const d = noise.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; }
      await load(); ready = true;
      const dl = ctx.createBiquadFilter(); dl.type = 'lowpass'; dl.frequency.value = 2400; dl.connect(music);
      const dr = bed('tanpura', dl, 6); if (dr) dr.g.gain.setTargetAtTime(0.2, ctx.currentTime, 3);
      for (const t in AMB) { const g = bus(amb, 0); beds[t] = { g }; for (const [n, v] of AMB[t]) bed(n, g, 5)?.g.gain.setValueAtTime(v, ctx.currentTime); }
      beds[time]?.g.gain.setTargetAtTime(1, ctx.currentTime, 2);
      setTimeout(peafowl, rnd(40, 90) * 1000);
      const fb = bed('fire', sfx, 3); fireG = fb?.g;
      master.gain.setTargetAtTime(muted ? 0 : 0.9, ctx.currentTime, 1.5);
      setTimeout(scheduler, 5000);
    },
    resume() { if (ctx && ctx.state === 'suspended') ctx.resume(); },
    toggle() { setMute(!muted); return muted; },
    setTime(t, sec = 2) {
      time = t; if (!ready) return;
      for (const k in beds) beds[k]?.g.gain.setTargetAtTime(k === t ? 1 : 0, ctx.currentTime, Math.max(sec, 0.5) / 2);
    },
    setCelestial(on) {             // небесное зрение: земное приглушается, звенит тонкий отзвук
      if (!ready) return;
      ambLP.frequency.setTargetAtTime(on ? 650 : 16000, ctx.currentTime, 0.4);
      amb.gain.setTargetAtTime(on ? 0.3 : 0.5, ctx.currentTime, 0.4);
      if (on) one('shimmer', { gain: 0.45, to: music });
    },
    duck(on) { if (ready) duckG.gain.setTargetAtTime(on ? 0.6 : 1, ctx.currentTime, 0.6); },
    fire(v) { if (fireG) fireG.gain.setTargetAtTime(v * 0.55, ctx.currentTime, 0.3); },
    step,
    door(gain, pan) { if (ready) one(pick(['creak1', 'creak2', 'doorOpen_1']), { gain: gain * 0.35, rate: rnd(0.85, 1.05), pan, lp: 4000 }); },
    bell(gain, pan, sec = 5) {     // ручной колокольчик при подношении: частый мягкий звон
      if (!ready) return;
      let t = 0; while (t < sec) { one(pick(['bell1', 'bell2', 'bell3']), { gain: gain * rnd(0.35, 0.55), rate: rnd(0.98, 1.02), pan, when: t }); t += rnd(0.28, 0.42); }
    },
    ui(name) {
      if (!ready) return;
      if (name === 'card') one(pick(['bookFlip1', 'bookFlip2']), { gain: 0.22, lp: 6000 });
      if (name === 'journal') one('bookOpen', { gain: 0.3, lp: 6000 });
    },
  };
}
