/* Game page: the full brain panel of the Python game — group LEDs, stimulate/silence, raster, decoded body. */
import { loadCircuit, Sim, GraphView, RasterView, drawArena, PANEL_GROUPS, fmtHz } from './brain.js';

const root = document.querySelector('[data-brain-panel]');
if (root) boot(root).catch(err => { const l = root.querySelector('.loading'); if (l) l.textContent = 'Could not load the circuit: ' + err.message; });

async function boot(root) {
  const circuit = await loadCircuit(root.dataset.base || '/assets/circuit/');
  root.querySelector('.loading')?.remove();
  const sim = new Sim(circuit, { speed: 1 });
  const graph = new GraphView(root.querySelector('[data-graph]'), circuit, { width: 700, height: 380 });
  const raster = new RasterView(root.querySelector('[data-raster]'), { width: 460 });
  const arena = root.querySelector('[data-arena]');
  const list = root.querySelector('[data-groups]');
  const b = sim.brain;
  const rows = PANEL_GROUPS.filter(n => b.index[n] !== undefined).map(name => {
    const li = document.createElement('li');
    li.innerHTML = `<i class="led"></i><span class="gname">${name}</span><span class="gn">n=${b.sizes[b.index[name]]}</span><span class="ghz">0.0 Hz</span>
      <span class="gbtn"><button class="stim" aria-pressed="false" title="Inject current into every ${name} cell (S in the game)">stim</button><button class="sil" aria-pressed="false" title="Clamp ${name} to rest (X in the game)">silence</button></span>`;
    const [stim, sil] = li.querySelectorAll('button');
    stim.addEventListener('click', () => { sim.toggleStim(name); sync(); });
    sil.addEventListener('click', () => { sim.toggleSilence(name); sync(); });
    list.appendChild(li);
    return { name, li, led: li.querySelector('.led'), hz: li.querySelector('.ghz'), stim, sil };
  });
  const sync = () => rows.forEach(r => { r.stim.setAttribute('aria-pressed', sim.stim.has(r.name)); r.sil.setAttribute('aria-pressed', sim.silence.has(r.name)); });
  root.querySelectorAll('[data-scenario]').forEach(el => el.addEventListener('click', () => sim.play(el.dataset.scenario)));
  root.querySelector('[data-clear]')?.addEventListener('click', () => { sim.clearPanel(); sim.scenario = null; sync(); });
  root.querySelector('[data-reset]')?.addEventListener('click', () => { sim.clearPanel(); sim.scenario = null; sim.brain.reset(); sync(); });
  const amp = root.querySelector('[data-amp]'), ampOut = root.querySelector('[data-amp-out]');
  amp?.addEventListener('input', () => { sim.panelAmp = +amp.value; ampOut.textContent = (+amp.value).toFixed(2); });
  const speed = root.querySelector('[data-speed-select]'); speed?.addEventListener('change', () => { sim.speed = +speed.value; });
  const body = root.querySelector('[data-body]'), cmd = root.querySelector('[data-cmd]'), perf = root.querySelector('[data-perf]');
  const accent = () => getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
  let visible = true, last = performance.now(), frame = 0;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; }, { threshold: .02 }).observe(root);
  const loop = now => {
    const dt = Math.min(.05, (now - last) / 1000); last = now;
    if (visible && !document.hidden) {
      sim.advance(dt); graph.draw(sim); raster.draw(sim); drawArena(arena, sim);
      if ((frame++ & 1) === 0) {
        const ac = accent();
        for (const r of rows) {
          const hz = b.rate(r.name); r.hz.textContent = fmtHz(hz);
          const k = Math.min(1, hz / 60); r.led.style.background = k > .02 ? `color-mix(in srgb, ${ac} ${Math.round(k * 100)}%, var(--paper))` : '';
          r.led.style.boxShadow = k > .3 ? `0 0 ${Math.round(6 * k)}px ${ac}` : '';
        }
        body.textContent = sim.cmd.label;
        cmd.innerHTML = `v ${sim.cmd.v.toFixed(2)} u/s · ω ${(sim.cmd.omega * 180 / Math.PI).toFixed(0)}°/s${sim.onFood ? ' · on food' : ''}${sim.scenario ? ' · ' + sim.scenario : ''}`;
        perf.textContent = `${(sim.lastStepsPerS / 1000).toFixed(1)}k steps/s · ${(b.lastFrac * 100).toFixed(2)}% of cells spiking · t = ${(b.t / 1000).toFixed(1)} s bio`;
      }
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}
