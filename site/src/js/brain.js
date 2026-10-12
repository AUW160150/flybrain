/* brain.js — the FlyWorld sub-circuit, simulated in the browser.
 *
 * A direct port of projects/flyworld-game/flyworld/brain.py (batched leaky integrate-and-fire,
 * event-driven propagation) and decoder.py (descending-neuron readout) to plain JavaScript.
 * The circuit itself is the real extraction: 10,203 MaleCNS v1.0 neurons and 401,680 edges with
 * at least 5 synapses, exported by scripts/export_circuit.py. Nothing here is a cartoon of a brain;
 * it is the same arrays the Python game steps on the GPU, stepped here on one CPU thread.
 */

const OUT_PANEL = ['DNp01', 'DNp09', 'MDN', 'DNa01', 'DNa02', 'DNg11', 'MN9', 'DNp10', 'DNg13', 'DNg100', 'DNg02', 'DNa_all', 'HS',
  'LC4', 'LPLC2', 'LC16', 'LC6', 'LC11', 'ORN_DM1', 'ORN_DM4', 'ORN_DC1', 'ORN_DA1', 'ORN_VA1v', 'LB3c', 'PPL101', 'KC', 'MBON', 'DN_all'];
const RASTER_ROWS = ['LC4', 'LPLC2', 'LC16', 'LC6', 'LC11', 'ORN_DM1', 'ORN_DA1', 'LB3c', 'PPL101', 'KC', 'MBON',
  'DNp01_L', 'DNp01_R', 'DNp09_L', 'DNp09_R', 'MDN', 'DNa01_L', 'DNa01_R', 'DNa02_L', 'DNa02_R', 'DNg11', 'MN9', 'DN_all'];
const SUPERCLASS_COLOR = {
  visual_projection: '#6a8fb5', visual_centrifugal: '#6a8fb5', ol_intrinsic: '#9db3c9',
  cb_sensory: '#c9a35b', cb_sensory_tbc: '#c9a35b', cb_intrinsic: '#9a9a90', cb_endocrine: '#9a9a90',
  descending_neuron: '#c2412a', cb_motor: '#c2412a', vnc_efferent: '#c2412a', vnc_intrinsic: '#8a8a80', ascending_neuron: '#8a8a80',
};

export async function loadCircuit(base) {
  const [meta, buf] = await Promise.all([
    fetch(base + 'circuit-meta.json').then(r => r.json()),
    fetch(base + 'circuit.bin').then(r => r.arrayBuffer()),
  ]);
  const N = meta.N, E = meta.E; let o = 0;
  const indptr = new Int32Array(buf, o, N + 1); o += (N + 1) * 4;
  const post = new Int32Array(buf, o, E); o += E * 4;
  const weight = new Int16Array(buf, o, E); o += E * 2;
  const pos = new Uint16Array(buf, o, N * 2); o += N * 4;
  const depth = new Uint8Array(buf, o, N);
  return { meta, N, E, indptr, post, weight, pos, depth };
}

export class LIF {
  constructor(c) {
    const p = c.meta.params; this.c = c; this.p = p; this.N = c.N;
    this.decay = Math.exp(-p.dt_ms / p.tau_ms);
    const N = c.N;
    this.v = new Float32Array(N); this.inp = new Float32Array(N); this.refr = new Uint8Array(N);
    this.mask = new Uint8Array(N).fill(1); this.drive = new Float32Array(N);
    this.spikes = new Int32Array(N); this.nSpikes = 0;
    this.activity = new Float32Array(N);            // display only: decays each frame
    this.names = Object.keys(c.meta.groups).sort();
    this.index = Object.fromEntries(this.names.map((n, i) => [n, i]));
    this.groups = this.names.map(n => Int32Array.from(c.meta.groups[n]));
    this.sizes = this.groups.map(g => g.length);
    const G = this.names.length; this.G = G;
    // neuron -> groups (CSR), so each spike can be counted into every group it belongs to
    const cnt = new Int32Array(N + 1);
    this.groups.forEach(g => { for (const i of g) cnt[i + 1]++; });
    for (let i = 0; i < N; i++) cnt[i + 1] += cnt[i];
    this.membPtr = cnt; this.memb = new Int32Array(cnt[N]);
    const fill = new Int32Array(N);
    this.groups.forEach((g, gi) => { for (const i of g) this.memb[cnt[i] + fill[i]++] = gi; });
    this.R = p.ring_ms; this.ring = new Float32Array(G * this.R); this.ptr = 0; this.t = 0;
    this.amp = new Float32Array(G); this.clamp = new Uint8Array(G); this.dirty = true;
    this.run = 0; this.lastFrac = 0; this.damped = 0;
  }
  reset() { this.v.fill(0); this.refr.fill(0); this.nSpikes = 0; this.ring.fill(0); this.activity.fill(0); this.run = 0; this.t = 0; }
  setAmp(name, value) { const g = this.index[name]; if (g === undefined) return; this.amp[g] = value; this.dirty = true; }
  addAmp(name, value) { const g = this.index[name]; if (g === undefined) return; this.amp[g] += value; this.dirty = true; }
  clearAmps() { this.amp.fill(0); this.dirty = true; }
  setClamp(name, on) { const g = this.index[name]; if (g === undefined) return; this.clamp[g] = on ? 1 : 0; this.dirty = true; }
  refreshDrive() {
    this.drive.fill(0); this.mask.fill(1);
    for (let g = 0; g < this.G; g++) {
      const a = this.amp[g]; const idx = this.groups[g];
      if (a !== 0) for (let k = 0; k < idx.length; k++) this.drive[idx[k]] += a;
      if (this.clamp[g]) for (let k = 0; k < idx.length; k++) this.mask[idx[k]] = 0;
    }
    this.dirty = false;
  }
  step(n) {
    if (this.dirty) this.refreshDrive();
    const { N, v, inp, refr, mask, drive, spikes, activity, indptr, post, weight, membPtr, memb, ring, R, G } = Object.assign({ indptr: this.c.indptr, post: this.c.post, weight: this.c.weight }, this);
    const decay = this.decay, gain = this.p.gain, thr = this.p.thr, reset = this.p.reset, refrMs = this.p.refr_ms;
    const govFrac = this.p.governor_frac, govSteps = this.p.governor_steps;
    for (let s = 0; s < n; s++) {
      inp.fill(0);
      for (let k = 0; k < this.nSpikes; k++) {
        const u = spikes[k];
        for (let e = indptr[u], end = indptr[u + 1]; e < end; e++) inp[post[e]] += weight[e];
      }
      const col = this.ptr;
      for (let g = 0; g < G; g++) ring[g * R + col] = 0;
      let cnt = 0;
      for (let i = 0; i < N; i++) {
        let x = decay * v[i] + gain * inp[i] + drive[i];
        if (refr[i] > 0 || mask[i] === 0) x = 0;
        if (x >= thr) {
          x = reset; refr[i] = refrMs; spikes[cnt++] = i; activity[i] = 1;
          for (let m = membPtr[i], me = membPtr[i + 1]; m < me; m++) ring[memb[m] * R + col] += 1;
        } else if (refr[i] > 0) refr[i]--;
        v[i] = x;
      }
      this.nSpikes = cnt;
      const frac = cnt / N; this.lastFrac = frac;
      this.run = frac > govFrac ? this.run + 1 : 0;
      if (this.run >= govSteps) { for (let i = 0; i < N; i++) v[i] *= 0.5; this.damped++; }
      this.ptr = (col + 1) % R; this.t += this.p.dt_ms;
    }
  }
  /* mean firing rate per neuron of each group over the last window (Hz) */
  rates(windowMs = 50) {
    const w = Math.min(windowMs, this.R), out = new Float32Array(this.G), R = this.R;
    for (let g = 0; g < this.G; g++) {
      let s = 0; for (let k = 1; k <= w; k++) s += this.ring[g * R + ((this.ptr - k + R) % R)];
      out[g] = s / (this.sizes[g] * (w / 1000));
    }
    return out;
  }
  rate(name, windowMs = 50) {
    const g = this.index[name]; if (g === undefined) return 0;
    const w = Math.min(windowMs, this.R), R = this.R; let s = 0;
    for (let k = 1; k <= w; k++) s += this.ring[g * R + ((this.ptr - k + R) % R)];
    return s / (this.sizes[g] * (w / 1000));
  }
  count(name, windowMs) {
    const g = this.index[name]; if (g === undefined) return 0;
    const w = Math.min(windowMs, this.R), R = this.R; let s = 0;
    for (let k = 1; k <= w; k++) s += this.ring[g * R + ((this.ptr - k + R) % R)];
    return s;
  }
}

/* Port of flyworld/decoder.py: descending-neuron rates -> a body command with hysteresis. */
export class MotorDecoder {
  constructor(calib) {
    this.p = { ema_ms: 100, walk_thr: 10, walk_sat: 100, v_forward: 3, v_back: 2, turn_deg: 180, turn_scale: 50, turn_dead: 10,
      jump_cooldown_s: .5, jump_turn_deg: 45, jump_speed: 8, jump_dur_s: .15, groom_on: 20, groom_off: 10, eat_thr: 20, idle_s: 2, idle_speed: .4, lowpass_s: .1 };
    this.turnBias = calib?.turn_bias_per_dnp09_hz ?? 0;
    this.ema = {}; this.v = 0; this.omega = 0; this.jumpTimer = 0; this.cooldown = 0; this.groom = false; this.quiet = 0; this.idleDir = 0; this.idleT = 0;
  }
  r(n) { return Math.max(0, this.ema[n] ?? 0); }
  update(brain, dnp01Spikes, dt, onFood, bioMs) {
    const p = this.p, a = 1 - Math.exp(-bioMs / p.ema_ms);
    for (const n of ['DNp09', 'MDN', 'DNa02_L', 'DNa02_R', 'DNa01_L', 'DNa01_R', 'DNg11', 'MN9', 'DNp01_L', 'DNp01_R']) {
      const v = brain.rate(n); this.ema[n] = (this.ema[n] ?? 0) + a * (v - (this.ema[n] ?? 0));
    }
    const cmd = { v: 0, omega: 0, jump: false, jumpTurn: 0, groom: false, eat: false, idle: false, label: 'still' };
    const r09 = this.r('DNp09'), rmdn = this.r('MDN');
    const clamp01 = x => Math.min(Math.max(x, 0), 1);
    const vf = p.v_forward * clamp01((r09 - p.walk_thr) / (p.walk_sat - p.walk_thr));
    const vb = p.v_back * clamp01((rmdn - p.walk_thr) / (p.walk_sat - p.walk_thr));
    let vT = vf - vb;
    const right = this.r('DNa02_R') + .5 * this.r('DNa01_R'), left = this.r('DNa02_L') + .5 * this.r('DNa01_L');
    let delta = (right - left) + this.turnBias * r09;
    if (Math.abs(delta) < p.turn_dead) delta = 0;
    let oT = -(p.turn_deg * Math.PI / 180) * Math.tanh(delta / p.turn_scale);
    const rg = this.r('DNg11');
    if (!this.groom && rg > p.groom_on) this.groom = true; else if (this.groom && rg < p.groom_off) this.groom = false;
    cmd.groom = this.groom; if (this.groom) { vT = 0; oT = 0; }
    this.cooldown = Math.max(0, this.cooldown - dt);
    if (dnp01Spikes > 0 && this.cooldown <= 0 && this.jumpTimer <= 0) {
      const side = this.r('DNp01_L') - this.r('DNp01_R');
      cmd.jump = true; cmd.jumpTurn = (side > 0 ? -1 : 1) * p.jump_turn_deg * Math.PI / 180;
      this.jumpTimer = p.jump_dur_s; this.cooldown = p.jump_cooldown_s;
    }
    if (this.jumpTimer > 0) {
      this.jumpTimer -= dt; this.v = p.jump_speed; this.omega = 0;
      cmd.v = this.v; cmd.omega = 0; cmd.label = 'jump'; return cmd;
    }
    const dnMax = Math.max(0, ...['DNp09', 'MDN', 'DNa02_L', 'DNa02_R', 'DNg11', 'MN9', 'DNp01_L', 'DNp01_R'].map(n => this.r(n)));
    this.quiet = dnMax < 5 ? this.quiet + dt : 0;
    cmd.idle = this.quiet >= p.idle_s;
    if (cmd.idle) {
      this.idleT -= dt;
      if (this.idleT <= 0) { this.idleT = 1 + Math.random() * 2; this.idleDir = (Math.random() - .5) * 1.2; }
      vT = p.idle_speed; oT = this.idleDir;
    }
    const k = Math.min(1, dt / p.lowpass_s);
    this.v += (vT - this.v) * k; this.omega += (oT - this.omega) * k;
    cmd.v = this.v; cmd.omega = this.omega;
    cmd.eat = onFood && this.r('MN9') > p.eat_thr;
    cmd.label = cmd.groom ? 'groom' : cmd.eat ? 'eat' : cmd.idle ? 'wander' :
      Math.abs(cmd.v) < .25 && Math.abs(cmd.omega) < .35 ? 'still' :
      cmd.v < -.25 ? 'back' : Math.abs(cmd.omega) > .6 && Math.abs(cmd.v) < .8 ? (cmd.omega > 0 ? 'turn left' : 'turn right') : 'walk';
    return cmd;
  }
}

/* Scenarios: the same geometric proxies encoders.py uses, played as short scripts. */
export const SCENARIOS = {
  loomLeft:  { title: 'Loom from the left',  run: loom(+0.7) },
  loomRight: { title: 'Loom from the right', run: loom(-0.7) },
  odour:     { title: 'Food odour ahead',    run: odour() },
  taste:     { title: 'Standing on food',    run: taste() },
  conspecific: { title: 'Another fly nearby', run: nearbyFly() },
};
function binocular(phi) { return [Math.min(Math.max(1 + Math.sin(phi), 0), 1), Math.min(Math.max(1 - Math.sin(phi), 0), 1)]; }
function hemifield(phi) { return [Math.min(Math.max(.5 + Math.sin(phi), 0), 1), Math.min(Math.max(.5 - Math.sin(phi), 0), 1)]; }
function loom(phi) {
  // an object of radius 0.9 approaching from 6 units to 1 unit in 0.6 s, like the big fly walking at a small one
  return (t, add) => {
    const T = .6; if (t > T) return false;
    const d0 = 6, d1 = 1.0, d = d0 + (d1 - d0) * (t / T), dprev = d0 + (d1 - d0) * Math.max(0, t - 1 / 60) / T;
    const theta = 2 * Math.atan2(.9, Math.max(d, .9)), prev = 2 * Math.atan2(.9, Math.max(dprev, .9));
    const thetaDot = (theta - prev) * 60;
    const vel = .2 * Math.min(Math.max(thetaDot / 1.5, 0), 1);
    const size = .2 * Math.min(Math.max((theta - .15) / .6, 0), 1) * (thetaDot > 0 ? 1 : 0);
    const [wl, wr] = binocular(phi);
    add('LC4_L', vel * wl); add('LC6_L', vel * wl); add('LPLC2_L', size * wl); add('LC16_L', size * wl);
    add('LC4_R', vel * wr); add('LC6_R', vel * wr); add('LPLC2_R', size * wr); add('LC16_R', size * wr);
    add('ORN_DA1', .1 * Math.exp(-d / 4));   // the big fly also smells like a fly
    return true;
  };
}
function odour() {
  return (t, add) => {
    if (t > 2.0) return false;
    const d = Math.max(.5, 4 - 3.5 * t / 2.0), c = Math.exp(-d / 2); const [wl, wr] = hemifield(0);
    add('ORN_DM1_L', .15 * c * (.5 + .5 * wl)); add('ORN_DM1_R', .15 * c * (.5 + .5 * wr));
    for (const g of ['ORN_DM4', 'ORN_DC1']) { add(g + '_L', .075 * c * (.5 + .5 * wl)); add(g + '_R', .075 * c * (.5 + .5 * wr)); }
    return true;
  };
}
function taste() { return (t, add) => { if (t > 1.5) return false; add('LB3c_L', .2); add('LB3c_R', .2); return true; }; }
function nearbyFly() { return (t, add) => { if (t > 1.0) return false; const [wl, wr] = binocular(.3); add('LC11_L', .1 * wl); add('LC11_R', .1 * wr); return true; }; }

/* ---------- a running simulation with scenarios, panel stimulation and the decoder ---------- */
export class Sim {
  constructor(circuit, { speed = 1, onFoodDuringTaste = true } = {}) {
    this.c = circuit; this.brain = new LIF(circuit); this.dec = new MotorDecoder(circuit.meta.calibration);
    this.speed = speed; this.panelAmp = circuit.meta.params.panel_amp; this.stim = new Set(); this.silence = new Set();
    this.scenario = null; this.scenarioT = 0; this.onFood = false; this.onFoodDuringTaste = onFoodDuringTaste;
    this.cmd = { v: 0, omega: 0, label: 'still' }; this.fly = { x: 0, y: 0, h: 0 }; this.lastStepsPerS = 0;
    this.carry = 0; this.running = true;
  }
  play(key) { this.scenario = SCENARIOS[key] ? key : null; this.scenarioT = 0; }
  toggleStim(name) { if (this.stim.has(name)) this.stim.delete(name); else { this.stim.add(name); this.silence.delete(name); } }
  toggleSilence(name) { if (this.silence.has(name)) this.silence.delete(name); else { this.silence.add(name); this.stim.delete(name); } }
  clearPanel() { this.stim.clear(); this.silence.clear(); }
  /* advance by `dt` wall seconds; biological time runs at `speed` x wall time (capped per frame) */
  advance(dt) {
    const b = this.brain; b.clearAmps();
    for (const n of b.names) b.setClamp(n, this.silence.has(n));
    for (const n of this.stim) b.addAmp(n, this.panelAmp);
    this.onFood = false;
    if (this.scenario) {
      const add = (n, v) => { if (v > 0) b.addAmp(n, Math.min(v, .25)); };
      const alive = SCENARIOS[this.scenario].run(this.scenarioT, add);
      if (this.scenario === 'taste' && this.onFoodDuringTaste) this.onFood = true;
      this.scenarioT += dt; if (!alive) this.scenario = null;
    }
    const ms = Math.min(50, dt * 1000 * this.speed) + this.carry;
    const steps = Math.floor(ms); this.carry = ms - steps;
    const t0 = performance.now(); b.step(steps); const el = performance.now() - t0;
    if (el > 0) this.lastStepsPerS = steps / (el / 1000);
    const jumpSpikes = b.count('DNp01', 20);
    this.cmd = this.dec.update(b, jumpSpikes, dt, this.onFood, steps);
    // move the little fly in a 2-unit box (same units as the game arena)
    const f = this.fly; if (this.cmd.jump) f.h += this.cmd.jumpTurn;
    f.h += this.cmd.omega * dt; f.x += Math.cos(f.h) * this.cmd.v * dt; f.y += Math.sin(f.h) * this.cmd.v * dt;
    const L = 4; if (f.x > L) { f.x = L; f.h = Math.PI - f.h; } if (f.x < -L) { f.x = -L; f.h = Math.PI - f.h; }
    if (f.y > L) { f.y = L; f.h = -f.h; } if (f.y < -L) { f.y = -L; f.h = -f.h; }
    const act = b.activity; for (let i = 0; i < act.length; i++) if (act[i] > 0) act[i] *= 0.82;
  }
}

/* ---------- drawing ---------- */
export class GraphView {
  constructor(canvas, circuit, { width = 760, height = 420 } = {}) {
    this.cv = canvas; this.c = circuit; this.w = width; this.h = height;
    const dpr = Math.min(2, window.devicePixelRatio || 1); this.dpr = dpr;
    canvas.width = width * dpr; canvas.height = height * dpr;
    this.ctx = canvas.getContext('2d'); this.ctx.scale(dpr, dpr);
    this.base = document.createElement('canvas'); this.base.width = canvas.width; this.base.height = canvas.height;
    this.theme = null;
  }
  colors() {
    const cs = getComputedStyle(document.documentElement);
    return { paper: cs.getPropertyValue('--paper').trim(), ink3: cs.getPropertyValue('--ink-3').trim(), accent: cs.getPropertyValue('--accent').trim(), line: cs.getPropertyValue('--line').trim() };
  }
  px(i) { const pos = this.c.pos; return [14 + (pos[i * 2] / 65535) * (this.w - 28), 12 + (pos[i * 2 + 1] / 65535) * (this.h - 40)]; }
  drawBase() {
    const t = this.colors(); this.theme = t; const g = this.base.getContext('2d'); g.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    g.fillStyle = t.paper; g.fillRect(0, 0, this.w, this.h);
    // a thin sample of real edges for texture (4,000 of 401,680)
    const { indptr, post, N } = this.c; g.strokeStyle = t.line; g.globalAlpha = .35; g.lineWidth = .5; g.beginPath();
    let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (let k = 0; k < 4000; k++) {
      const u = Math.floor(rnd() * N), a = indptr[u], b = indptr[u + 1]; if (b <= a) continue;
      const e = a + Math.floor(rnd() * (b - a)); const [x1, y1] = this.px(u), [x2, y2] = this.px(post[e]);
      g.moveTo(x1, y1); g.lineTo(x2, y2);
    }
    g.stroke(); g.globalAlpha = 1;
    const names = this.c.meta.superclass_names, sc = this.c.meta.superclass;
    for (let i = 0; i < N; i++) { const [x, y] = this.px(i); g.fillStyle = SUPERCLASS_COLOR[names[sc[i]]] || t.ink3; g.globalAlpha = .55; g.fillRect(x - .75, y - .75, 1.5, 1.5); }
    g.globalAlpha = 1;
  }
  draw(sim) {
    const t = this.colors(); if (!this.theme || this.theme.paper !== t.paper) this.drawBase();
    const ctx = this.ctx; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(this.base, 0, 0); ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    const act = sim.brain.activity; ctx.fillStyle = t.accent;
    for (let i = 0; i < act.length; i++) {
      const a = act[i]; if (a < .03) continue; const [x, y] = this.px(i); const r = 1.2 + 2.2 * a;
      ctx.globalAlpha = Math.min(1, a * 1.1); ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
}

export class RasterView {
  constructor(canvas, { width = 420, rows = RASTER_ROWS, rowH = 11 } = {}) {
    this.cv = canvas; this.rows = rows; this.rowH = rowH; this.w = width; this.h = rows.length * rowH + 16;
    const dpr = Math.min(2, window.devicePixelRatio || 1); this.dpr = dpr;
    canvas.width = width * dpr; canvas.height = this.h * dpr; this.ctx = canvas.getContext('2d');
  }
  draw(sim) {
    const b = sim.brain, ctx = this.ctx, cs = getComputedStyle(document.documentElement);
    const paper = cs.getPropertyValue('--paper').trim(), ink3 = cs.getPropertyValue('--ink-3').trim(), accent = cs.getPropertyValue('--accent').trim(), line = cs.getPropertyValue('--line').trim();
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0); ctx.fillStyle = paper; ctx.fillRect(0, 0, this.w, this.h);
    const x0 = 64, cw = (this.w - x0 - 8) / b.R; ctx.font = '10px ui-monospace, Menlo, monospace'; ctx.textBaseline = 'middle';
    this.rows.forEach((name, r) => {
      const y = 8 + r * this.rowH; const g = b.index[name]; if (g === undefined) return;
      ctx.fillStyle = ink3; ctx.fillText(name, 6, y + this.rowH / 2);
      ctx.fillStyle = line; ctx.fillRect(x0, y + this.rowH - 1, this.w - x0 - 8, .5);
      const size = b.sizes[g]; ctx.fillStyle = accent;
      for (let k = 0; k < b.R; k++) {
        const col = (b.ptr - b.R + k + b.R) % b.R; const c = b.ring[g * b.R + col]; if (c <= 0) continue;
        ctx.globalAlpha = Math.min(1, .35 + c / Math.max(1, size * .25)); ctx.fillRect(x0 + k * cw, y + 1, Math.max(1, cw), this.rowH - 3);
      }
      ctx.globalAlpha = 1;
    });
    ctx.fillStyle = ink3; ctx.fillText('last 200 ms', x0, this.h - 5);
  }
}

export function drawArena(canvas, sim) {
  const ctx = canvas.getContext('2d'), cs = getComputedStyle(document.documentElement), dpr = Math.min(2, window.devicePixelRatio || 1);
  const S = 150; if (canvas.width !== S * dpr) { canvas.width = S * dpr; canvas.height = S * dpr; }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = cs.getPropertyValue('--paper').trim(); ctx.fillRect(0, 0, S, S);
  ctx.strokeStyle = cs.getPropertyValue('--line').trim(); ctx.lineWidth = 1;
  for (let k = 1; k < 4; k++) { ctx.beginPath(); ctx.moveTo(k * S / 4, 0); ctx.lineTo(k * S / 4, S); ctx.moveTo(0, k * S / 4); ctx.lineTo(S, k * S / 4); ctx.stroke(); }
  const f = sim.fly, x = S / 2 + f.x * (S / 9), y = S / 2 - f.y * (S / 9);
  ctx.save(); ctx.translate(x, y); ctx.rotate(-f.h);
  ctx.fillStyle = sim.cmd.label === 'jump' ? cs.getPropertyValue('--amber').trim() : cs.getPropertyValue('--accent').trim();
  ctx.beginPath(); ctx.moveTo(9, 0); ctx.lineTo(-6, 5); ctx.lineTo(-3, 0); ctx.lineTo(-6, -5); ctx.closePath(); ctx.fill();
  ctx.restore();
}

export const PANEL_GROUPS = OUT_PANEL;
export const RASTER = RASTER_ROWS;
export const fmtHz = v => (v >= 100 ? v.toFixed(0) : v.toFixed(1)) + ' Hz';
