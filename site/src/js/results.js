// Result figures: swap each <img> for its inline SVG so the figure's colours follow the theme toggle.
// Without JavaScript the <img> stays and follows the operating system's light/dark setting instead.
for (const img of document.querySelectorAll('.rfig-art img[src$=".svg"]')) {
  fetch(img.getAttribute('src'))
    .then(r => (r.ok ? r.text() : Promise.reject(r.status)))
    .then(text => {
      const svg = new DOMParser().parseFromString(text, 'image/svg+xml').documentElement;
      if (svg.nodeName !== 'svg') return;
      svg.removeAttribute('width'); svg.removeAttribute('height');
      svg.classList.add(...img.classList);
      img.replaceWith(document.importNode(svg, true));
    })
    .catch(() => {});
}
