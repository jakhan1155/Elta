// Звук интро
/* ---------- звук интро: синтезируется в браузере, без файлов ---------- */
// Telegram/браузер может запретить звук без касания экрана — тогда интро идёт молча.
// Звук интро: лес (ветер в деревьях, шелест листвы, редкие далёкие птицы) и мягкий далёкий гром,
// который нарастает, когда загораются буквы (0.85 с), и ещё раз — под слоган. Без резких щелчков и ударов.
function createIntroSound(ctx = null) {
  if (!ctx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    try { ctx = new AC(); } catch (e) { return null; }
  }
  const sr = ctx.sampleRate;

  const master = ctx.createGain();
  master.gain.value = 0.75;
  const comp = ctx.createDynamicsCompressor();  // мягко держит громкость, без резких пиков
  comp.threshold.value = -20; comp.knee.value = 18; comp.ratio.value = 3;
  comp.attack.value = 0.02; comp.release.value = 0.5;
  master.connect(comp);
  comp.connect(ctx.destination);

  // тёмная длинная реверберация — гром звучит далеко, в пространстве леса
  const reverb = ctx.createConvolver();
  const irLen = Math.floor(sr * 3.2), ir = ctx.createBuffer(2, irLen, sr);
  for (let ch = 0; ch < 2; ch++) {
    const d = ir.getChannelData(ch);
    let lp = 0;
    for (let i = 0; i < irLen; i++) { lp += 0.12 * ((Math.random() * 2 - 1) - lp); d[i] = lp * Math.pow(1 - i / irLen, 2.4); }
  }
  reverb.buffer = ir;
  const wet = ctx.createGain(); wet.gain.value = 0.9;
  reverb.connect(wet); wet.connect(master);
  const send = (node, amount) => { const g = ctx.createGain(); g.gain.value = amount; node.connect(g); g.connect(reverb); };

  // шумы: розовый (ветер, листва) и коричневый (гром)
  const noise = (kind, sec) => {
    const len = Math.floor(sr * sec), buf = ctx.createBuffer(2, len, sr);
    for (let ch = 0; ch < 2; ch++) {
      const d = buf.getChannelData(ch);
      let b0 = 0, b1 = 0, b2 = 0, br = 0;
      for (let i = 0; i < len; i++) {
        const w = Math.random() * 2 - 1;
        if (kind === "brown") { br = (br + 0.02 * w) / 1.02; d[i] = br * 3.5; }
        else { b0 = 0.99765 * b0 + w * 0.099046; b1 = 0.963 * b1 + w * 0.2965164; b2 = 0.57 * b2 + w * 1.0526913; d[i] = (b0 + b1 + b2 + w * 0.1848) * 0.11; }
      }
    }
    return buf;
  };
  const pink = noise("pink", 5), brown = noise("brown", 5);
  const nodes = [];
  const play = (buf, t, offset = 0) => { const s = ctx.createBufferSource(); s.buffer = buf; s.loop = true; s.start(t, offset); nodes.push(s); return s; };

  function wind(t) {  // ветер в кронах: медленно «дышит»
    const src = play(pink, t);
    const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 650; lp.Q.value = 0.5;
    const lfo = ctx.createOscillator(); lfo.frequency.value = 0.22;
    const lfoG = ctx.createGain(); lfoG.gain.value = 260;
    lfo.connect(lfoG); lfoG.connect(lp.frequency); lfo.start(t); nodes.push(lfo);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(0.5, t + 0.9);
    src.connect(lp); lp.connect(g); g.connect(master);
  }
  function leaves(t) {  // тихий шелест листвы
    const src = play(pink, t, 2.1);
    const bp = ctx.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 3200; bp.Q.value = 0.6;
    const am = ctx.createGain(); am.gain.value = 0.5;
    const lfo = ctx.createOscillator(); lfo.frequency.value = 0.45;
    const lfoG = ctx.createGain(); lfoG.gain.value = 0.35;
    lfo.connect(lfoG); lfoG.connect(am.gain); lfo.start(t); nodes.push(lfo);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(0.11, t + 1.2);
    src.connect(bp); bp.connect(am); am.connect(g); g.connect(master);
  }
  function bird(t, pan, base) {  // далёкая птица: 2–3 коротких мягких свиста
    const out = ctx.createGain(); out.gain.value = 0.045;
    let node = out;
    if (ctx.createStereoPanner) { const p = ctx.createStereoPanner(); p.pan.value = pan; out.connect(p); node = p; }
    node.connect(master); send(out, 0.6);
    for (let k = 0; k < 3; k++) {
      const t0 = t + k * 0.14, o = ctx.createOscillator(); o.type = "sine";
      o.frequency.setValueAtTime(base, t0);
      o.frequency.exponentialRampToValueAtTime(base * 1.35, t0 + 0.05);
      o.frequency.exponentialRampToValueAtTime(base * 1.1, t0 + 0.1);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(1, t0 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.11);
      o.connect(g); g.connect(out); o.start(t0); o.stop(t0 + 0.12);
    }
  }
  function thunder(t, peak, dur, rolls) {  // далёкий раскатистый гром: мягкая атака, несколько «перекатов»
    const src = play(brown, t, Math.random() * 3);
    const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.Q.value = 0.6;
    lp.frequency.setValueAtTime(110, t);
    lp.frequency.linearRampToValueAtTime(320, t + 0.35);
    lp.frequency.exponentialRampToValueAtTime(90, t + dur);
    const n = 256, curve = new Float32Array(n);
    const bumps = Array.from({ length: rolls }, (_, i) => ({ at: 0.1 + i * 0.22 + Math.random() * 0.08, w: 0.12 + Math.random() * 0.1, a: 1 - i * 0.18 }));
    for (let i = 0; i < n; i++) {
      const x = i / (n - 1);
      const env = Math.min(1, x / 0.1) * Math.exp(-x * 2.4);     // мягкое нарастание и долгий спад
      let roll = 0.45;
      for (const b of bumps) roll += b.a * Math.exp(-Math.pow((x - b.at) / b.w, 2));
      curve[i] = Math.max(0.0001, peak * env * Math.min(roll, 1.6) / 1.6);
    }
    const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t);
    g.gain.setValueCurveAtTime(curve, t + 0.001, dur);
    src.connect(lp); lp.connect(g); g.connect(master); send(g, 0.5);
    src.stop(t + dur + 0.1);
  }
  function gust(t) {  // мягкий порыв ветра, когда логотип улетает в шапку (без щелчков)
    const src = play(pink, t, 1.3);
    const bp = ctx.createBiquadFilter(); bp.type = "bandpass"; bp.Q.value = 0.7;
    bp.frequency.setValueAtTime(400, t);
    bp.frequency.exponentialRampToValueAtTime(1400, t + 0.45);
    bp.frequency.exponentialRampToValueAtTime(600, t + 1);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(0.32, t + 0.35);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 1.1);
    src.connect(bp); bp.connect(g); g.connect(master); send(g, 0.3);
    src.stop(t + 1.2);
  }

  // синхронно с картинкой: буквы стягиваются → загораются на 0.85 с → линия и слоган (~1.5 с)
  const schedule = t => {
    wind(t); leaves(t);
    bird(t + 0.3, -0.5, 3300);
    thunder(t + 0.6, 0.95, 2.6, 4);   // раскат нарастает к моменту, когда загораются буквы
    thunder(t + 1.45, 0.45, 2.2, 3);  // второй, тише — под слоган
    bird(t + 2.1, 0.55, 3700);
  };
  const finaleAt = t => {  // порыв ветра и всё плавно стихает
    gust(t);
    master.gain.cancelScheduledValues(t);
    master.gain.setValueAtTime(master.gain.value, t);
    master.gain.setTargetAtTime(0.0001, t + 0.35, 0.4);
    nodes.forEach(n => { try { n.stop(t + 2.6); } catch (e) {} });
  };

  let playing = false;
  return {
    schedule(t, finale) { schedule(t); if (finale != null) finaleAt(finale); },  // для проверки без воспроизведения
    async play() {  // если звук запрещён — интро просто идёт молча
      if (ctx.state !== "running") {
        const t0 = performance.now();
        try { await Promise.race([ctx.resume(), new Promise(r => setTimeout(r, 250))]); } catch (e) {}
        if (ctx.state !== "running" || performance.now() - t0 > 300) return;
      }
      schedule(ctx.currentTime + 0.02);
      playing = true;
    },
    finale() {  // логотип улетает в шапку
      if (playing) finaleAt(ctx.currentTime + 0.01);
      setTimeout(() => ctx.close().catch(() => {}), 3200);
    },
  };
}
