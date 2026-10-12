/* small things: current-page nav marking, theme toggle memory */
for (const a of document.querySelectorAll('.nav li a')) {
  const here = location.pathname.replace(/index\.html$/, '');
  if (a.getAttribute('href') === here || (a.dataset.match && here.startsWith(a.dataset.match))) a.setAttribute('aria-current', 'page');
}
const toggle = document.querySelector('[data-theme-toggle]');
if (toggle) {
  try { const t = localStorage.getItem('flybrain-theme'); if (t) document.documentElement.dataset.theme = t; } catch {}
  toggle.addEventListener('click', () => {
    const cur = document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const next = cur === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = next;
    try { localStorage.setItem('flybrain-theme', next); } catch {}
  });
}
