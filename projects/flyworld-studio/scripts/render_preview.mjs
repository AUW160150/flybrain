import { build } from 'esbuild';
import { pathToFileURL } from 'node:url';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { readFile, writeFile, mkdir } from 'node:fs/promises';

// Use Vite's locked esbuild dependency without creating a dev server or socket.
await mkdir('.cache', { recursive: true });
await build({ stdin: { contents: "export * from './src/realdata/RawGraph'; export * from './src/realdata/RealInspector'; export * from './src/realdata/graph'; export * from './src/realdata/schema';", resolveDir: process.cwd(), loader: 'ts' }, bundle: true, packages: 'external', platform: 'node', format: 'esm', jsx: 'automatic', outfile: '.cache/preview-renderer.mjs' });
const { RawGraph, RealInspector, DatasetPanel, filterGraph, initialFilters, parseRealPackageText } = await import(pathToFileURL(process.cwd() + '/.cache/preview-renderer.mjs').href);
{
  const input = await readFile('public/data/malecns/malecns-paper.json', 'utf8');
  const pkg = parseRealPackageText(input), selected = '15321';
  const graph = filterGraph(pkg, { ...initialFilters, selected, isolation: 'ONE_HOP' });
  const node = pkg.neurons.find(n => n.bodyId === selected);
  const noop = () => {};
  const markup = renderToStaticMarkup(createElement('section', { className: 'real-workspace' },
    createElement('h1', null, 'FlyWorld — local source preview'),
    createElement('p', { className: 'real-notice' }, 'STATIC SERVER RENDER — not a browser screenshot or interactive acceptance test. Paper-associated, one-hop package view around body 15321. Layout is abstract.'),
    createElement('div', { className: 'real-badges' }, createElement('strong', null, 'PAPER_ASSOCIATED'), createElement('span', null, 'SIMULATION UNAVAILABLE')),
    createElement('div', { className: 'real-content' },
      createElement('div', { className: 'real-visualization' }, createElement(RawGraph, { pkg, ...graph, selected, highlights: new Set(), select: noop })),
      createElement(RealInspector, { pkg, node, select: noop, isolate: noop })),
    createElement(DatasetPanel, { pkg, bytes: Buffer.byteLength(input), origin: 'Generated locally from the checked package; static preview' })));
  const css = await readFile('src/ui/styles.css', 'utf8');
  await mkdir('docs/previews', { recursive: true });
  await writeFile('docs/previews/realdata-static.html', '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FlyWorld source preview</title><style>' + css + '</style></head><body>' + markup + '</body></html>');
  console.log('Created docs/previews/realdata-static.html without starting a server.');
}
