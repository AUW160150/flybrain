import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { catalogSchema } from '../src/realdata/catalog';

const manifest = JSON.parse(readFileSync('public/data/malecns/manifest.json', 'utf8'));
describe('the actual browser package catalog', () => {
  it('accepts all eight published entries, including LB3b and LB3c filenames', () => {
    const catalog = catalogSchema.parse(manifest);
    expect(catalog.packages).toHaveLength(8);
    expect(catalog.packages.map(entry => entry.file)).toEqual(expect.arrayContaining(['malecns-lb3b.json', 'malecns-lb3c.json']));
  });
  it.each(['../malecns-focused.json', 'https://example.com/malecns-focused.json', 'malecns-focused.json?x=1', 'malecns-%2e%2e.json'])('still refuses nonlocal filename %s', file => {
    expect(() => catalogSchema.parse({ ...manifest, packages: [{ ...manifest.packages[0], file }] })).toThrow();
  });
});
