/* Landing-page hero: the real sub-circuit firing, with four things to do to it. */
import { loadCircuit, Sim, GraphView, fmtHz } from './brain.js';

const root = document.querySelector('[data-hero-brain]');
if (root) boot(root).catch(err => { root.querySelector('.loading').textContent = 'Could not load the circuit: ' + err.message; });

async function boot(root) {
  const canvas = root.querySelector('canvas');
  const circuit = await loadCircuit(root.dataset.base || '/assets/circuit/');
  root.querySelector('.loading')?.remove();
  const sim = new Sim(circuit, { speed: 1 });
  const view = new GraphView(canvas, circuit, { width: 760, height: 400 });
  const body = root.querySelector('[data-body]'), rates = root.querySelector('[data-rates]'), speedEl = root.querySelector('[data-speed]');
  root.querySelectorAll('[data-scenario]').forEach(b => b.addEventListener('click', () => { sim.clearPanel(); sim.play(b.dataset.scenario); }));
  root.querySelectorAll('[data-stim]').forEach(b => b.addEventListener('click', () => {
    sim.scenario = null; sim.toggleStim(b.dataset.stim); b.setAttribute('aria-pressed', sim.stim.has(b.dataset.stim));
  }));
  root.querySelector('[data-reset]')?.addEventListener('click', () => { sim.clearPanel(); sim.scenario = null; sim.brain.reset(); root.querySelectorAll('[data-stim]').forEach(b => b.setAttribute('aria-pressed', 'false')); });
  let visible = true, last = performance.now(), frame = 0;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; }, { threshold: .05 }).observe(root);
  const loop = now => {
    const dt = Math.min(.05, (now - last) / 1000); last = now;
    if (visible && !document.hidden) {
      sim.advance(dt); view.draw(sim);
      if ((frame++ & 3) === 0) {
        const b = sim.brain;
        body.textContent = sim.cmd.label;
        rates.innerHTML = ['DNp01', 'DNp09', 'MDN', 'DNa02_L', 'DNa02_R', 'MN9'].map(n => `${n} <b>${fmtHz(b.rate(n))}</b>`).join('<br>');
        if (speedEl) speedEl.textContent = `${(sim.lastStepsPerS / 1000).toFixed(1)}k steps/s · ${(b.lastFrac * 100).toFixed(2)}% active`;
      }
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}
