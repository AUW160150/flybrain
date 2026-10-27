// Browser check for the EXP1-EXP3 result pages: serves site/src locally and loads every new page (and the
// landing page) in headless Chromium at phone and desktop width, light and dark.
//
//   node scripts/check_results_render.mjs [--shots DIR]
//
// Fails unless, for every page and setting: no horizontal page overflow; every figure image was replaced by
// its inline SVG; the visible figure's text renders at >= 11 px and stays inside the figure without
// overlapping other text; and flipping the theme toggle changes a figure's series colour.
// Uses the Playwright install in projects/flyworld-studio (no new dependency).
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const root = path.join(repo, 'site', 'src');
const { chromium } = await import(pathToFileURL(path.join(repo, 'projects/flyworld-studio/node_modules/playwright/index.mjs')).href);
const shotArg = process.argv.indexOf('--shots');
const shots = shotArg > 0 ? process.argv[shotArg + 1] : fs.mkdtempSync(path.join(os.tmpdir(), 'flybrain-render-'));
fs.mkdirSync(shots, { recursive: true });

const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.json': 'application/json', '.md': 'text/markdown', '.csv': 'text/csv', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p.endsWith('/')) p += 'index.html';
  const f = path.join(root, p);
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;

function chromePath() {
  const cache = path.join(os.homedir(), 'Library/Caches/ms-playwright');
  if (!fs.existsSync(cache)) return undefined;
  for (const d of fs.readdirSync(cache).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse()) {
    for (const sub of fs.readdirSync(path.join(cache, d))) {
      const exe = path.join(cache, d, sub, 'chrome-headless-shell');
      if (fs.existsSync(exe)) return exe;
    }
  }
}
let browser;
try { browser = await chromium.launch(); } catch { browser = await chromium.launch({ executablePath: chromePath() }); }

const pages = ['/', '/results/', '/projects/steering-circuit/', '/projects/forward-only-training/', '/projects/fly-retrieval/'];
const problems = [];
let figuresSeen = 0, textsMeasured = 0;
for (const url of pages) {
  for (const width of [375, 1280]) {
    for (const theme of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme });
      await ctx.addInitScript(t => { try { localStorage.setItem('flybrain-theme', t); } catch {} }, theme);
      const page = await ctx.newPage();
      await page.goto(base + url, { waitUntil: 'networkidle' });
      await page.waitForFunction(() => document.querySelectorAll('.rfig-art img').length === 0, null, { timeout: 10000 }).catch(() => {});
      await page.evaluate(() => document.fonts.ready);
      const r = await page.evaluate(() => {
        const out = { problems: [], figures: 0, texts: 0 };
        const doc = document.documentElement;
        if (doc.scrollWidth > window.innerWidth + 1) out.problems.push(`page is ${doc.scrollWidth}px wide in a ${window.innerWidth}px viewport`);
        if (document.querySelectorAll('.rfig-art img').length) out.problems.push(`${document.querySelectorAll('.rfig-art img').length} figure images were not inlined`);
        for (const fig of document.querySelectorAll('.rfig-art')) {
          const svgs = [...fig.querySelectorAll('svg.rf')];
          if (svgs.length !== 2) { out.problems.push(`figure has ${svgs.length} inline SVGs`); continue; }
          const vis = svgs.filter(s => s.getBoundingClientRect().width > 0);
          if (vis.length !== 1) { out.problems.push(`${vis.length} visible layouts in one figure`); continue; }
          const s = vis[0]; out.figures++;
          const id = [...s.classList].find(c => c.startsWith('rf-') && c !== 'rf-lg' && c !== 'rf-sm');
          const W = s.viewBox.baseVal.width, H = s.viewBox.baseVal.height, scale = s.getBoundingClientRect().width / W;
          const boxes = [];
          for (const t of s.querySelectorAll('text')) {
            if (!t.textContent.trim()) continue;
            out.texts++;
            const px = parseFloat(t.getAttribute('font-size')) * scale;
            if (px < 10.95) out.problems.push(`${id}: "${t.textContent}" renders at ${px.toFixed(1)}px`);
            const b = t.getBBox(); boxes.push([t.textContent, b]);
            if (b.x < -0.5 || b.x + b.width > W + 0.5 || b.y < -0.5 || b.y + b.height > H + 0.5) out.problems.push(`${id}: "${t.textContent}" is clipped`);
          }
          for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
            const a = boxes[i][1], c = boxes[j][1];
            const ox = Math.min(a.x + a.width, c.x + c.width) - Math.max(a.x, c.x), oy = Math.min(a.y + a.height, c.y + c.height) - Math.max(a.y, c.y);
            if (ox > 1 && oy > 2) out.problems.push(`${id}: "${boxes[i][0]}" overlaps "${boxes[j][0]}"`);
          }
        }
        const mark = document.querySelector('.rfig-art svg.rf .f1');
        out.fill = mark ? getComputedStyle(mark).fill : null;
        out.bg = getComputedStyle(document.body).backgroundColor;
        return out;
      });
      figuresSeen += r.figures; textsMeasured += r.texts;
      for (const p of r.problems) problems.push(`${url} @${width} ${theme}: ${p}`);
      if (r.figures === 0) problems.push(`${url} @${width} ${theme}: no figure rendered`);
      // the toggle must repaint inline figures: click it and the series colour must change
      if (r.fill) {
        await page.click('[data-theme-toggle]');
        const after = await page.evaluate(() => getComputedStyle(document.querySelector('.rfig-art svg.rf .f1')).fill);
        if (after === r.fill) problems.push(`${url} @${width} ${theme}: theme toggle did not change figure colours (${after})`);
        await page.click('[data-theme-toggle]');
      }
      const name = (url === '/' ? 'home' : url.replace(/^\/|\/$/g, '').replace(/\//g, '_')) + `-${width}-${theme}.png`;
      await page.screenshot({ path: path.join(shots, name), fullPage: true });
      await ctx.close();
    }
  }
}
await browser.close(); server.close();
console.log(`${pages.length} pages x 2 widths x 2 themes; ${figuresSeen} visible figures, ${textsMeasured} text elements measured; screenshots in ${shots}`);
if (problems.length) { console.log(problems.slice(0, 60).join('\n')); console.log(`${problems.length} problem(s)`); process.exit(1); }
console.log('RENDER OK');
