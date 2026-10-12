# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: foundation.spec.ts >> rule tour, synthetic replay, pause, scrub, speed, clear and reset
- Location: tests/e2e/foundation.spec.ts:62:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByTestId('timeline-time')
Expected substring: "6.0"
Received string:    "0.1 / 24.3 s"
Timeout: 5000ms

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for getByTestId('timeline-time')
    2 × locator resolved to <strong data-testid="timeline-time">…</strong>
      - unexpected value "0.1 / 19.6 s"
    12 × locator resolved to <strong data-testid="timeline-time">…</strong>
       - unexpected value "0.1 / 24.3 s"

```

```yaml
- strong: 0.1 / 24.3 s
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { mkdir } from 'node:fs/promises';
  3  | 
  4  | test.beforeEach(async ({ page }) => {
  5  |   await page.goto('/');
  6  |   await expect(page.getByTestId('renderer-status')).toHaveText('WEBGL · READY', { timeout: 30000 });
  7  | });
  8  | 
  9  | test('world controls, collisions, and explicit educational provenance', async ({ page }) => {
  10 |   const errors: string[] = [];
  11 |   page.on('pageerror', error => errors.push(error.message));
  12 |   await expect(page.getByText('PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA', { exact: true }).first()).toBeVisible();
  13 |   await expect(page.getByText('COLLISION HANDLING: GAME PHYSICS', { exact: true })).toBeVisible();
  14 |   await expect(page.getByText('SIMULATION UNAVAILABLE', { exact: true })).toBeVisible();
  15 |   await page.locator('[data-world-viewport]').click({ position: { x: 35, y: 200 } });
  16 |   await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS ACTIVE');
  17 |   await page.keyboard.down('a'); await page.waitForTimeout(365); await page.keyboard.up('a');
  18 |   await page.keyboard.down('w');
  19 |   await expect(page.getByTestId('collision-state')).toHaveText('CONTACT', { timeout: 12000 });
  20 |   await page.keyboard.up('w');
  21 |   await page.keyboard.press('b');
  22 |   await expect(page.getByRole('switch', { name: 'Transparent head' })).toBeChecked();
  23 |   await page.keyboard.press('f');
  24 |   await expect(page.getByTestId('activation-source')).toHaveText('USER_DRIVEN_ILLUSTRATION');
  25 |   await expect(page.getByTestId('last-control')).toContainText('FEED');
  26 |   await page.getByRole('button', { name: 'Performance', exact: true }).click();
  27 |   await expect(page.getByLabel('Performance overlay')).toContainText('FPS');
  28 |   await mkdir('docs/previews', { recursive: true });
  29 |   await page.screenshot({ path: 'docs/previews/mvp-world.png', fullPage: true });
  30 |   expect(errors).toEqual([]);
  31 | });
  32 | 
  33 | test('brain click, region and neuron metadata, layers, focus and return', async ({ page }) => {
  34 |   await page.getByLabel('Reduced motion', { exact: true }).check();
  35 |   await page.getByRole('button', { name: 'Brain', exact: true }).click();
  36 |   await expect(page.getByTestId('camera-mode')).toHaveText('BRAIN_INSPECTION');
  37 |   const canvas = page.locator('canvas');
  38 |   const box = await canvas.boundingBox();
  39 |   await page.waitForTimeout(250);
  40 |   await canvas.click({ position: { x: box!.width / 2, y: box!.height / 2 } });
  41 |   await expect(page.getByTestId('entity-record')).toBeVisible();
  42 |   await page.locator('.region-layer-heading button').filter({ hasText: 'Gustatory / taste system' }).click();
  43 |   await expect(page.getByTestId('entity-record')).toContainText('demo-taste-system');
  44 |   await page.getByRole('button', { name: 'Isolate system' }).click();
  45 |   await expect(page.getByLabel('Show Visual system', { exact: true })).not.toBeChecked();
  46 |   await page.getByLabel('Gustatory / taste system opacity').fill('60');
  47 |   await page.getByRole('button', { name: 'Focus selection' }).click();
  48 |   const tasteLayer = page.locator('.region-layer').filter({ has: page.getByLabel('Show Gustatory / taste system', { exact: true }) });
  49 |   await tasteLayer.locator('summary').click();
  50 |   await page.getByRole('button', { name: 'Taste demo 01', exact: true }).click();
  51 |   await expect(page.getByTestId('entity-record')).toContainText('demo-taste-01');
  52 |   await expect(page.getByTestId('entity-record')).toContainText('Downstream demo relations');
  53 |   await expect(page.getByTestId('entity-record')).toContainText('UNVERIFIED');
  54 |   await mkdir('docs/previews', { recursive: true });
  55 |   await page.screenshot({ path: 'docs/previews/mvp-brain.png', fullPage: true });
  56 |   await page.getByRole('button', { name: 'Reset brain view' }).click();
  57 |   await expect(page.getByLabel('Show Visual system', { exact: true })).toBeChecked();
  58 |   await page.getByRole('button', { name: /Back to world/ }).click();
  59 |   await expect(page.getByTestId('camera-mode')).toHaveText('WORLD_FOLLOW');
  60 | });
  61 | 
  62 | test('rule tour, synthetic replay, pause, scrub, speed, clear and reset', async ({ page }) => {
  63 |   await page.getByRole('button', { name: 'EDUCATIONAL RULE', exact: true }).click();
  64 |   await expect(page.getByTestId('control-mode')).toContainText('EDUCATIONAL RULE');
  65 |   await expect(page.getByTestId('activation-source')).toHaveText('RULE_DRIVEN_EDUCATIONAL');
  66 |   await page.getByRole('button', { name: 'DATA REPLAY', exact: true }).click();
  67 |   await page.getByLabel('Activity timeline position').fill('6000');
> 68 |   await expect(page.getByTestId('timeline-time')).toContainText('6.0');
     |                                                   ^ Error: expect(locator).toContainText(expected) failed
  69 |   await page.getByLabel('Playback speed').selectOption('2');
  70 |   await page.getByRole('button', { name: 'Play activity timeline' }).click();
  71 |   await expect(page.getByTestId('timeline-time')).not.toContainText('6.0');
  72 |   await page.getByRole('button', { name: 'Pause activity timeline' }).click();
  73 |   await page.getByRole('button', { name: 'Clear', exact: true }).click();
  74 |   await expect(page.locator('.timeline-events span')).toHaveCount(0);
  75 |   await page.getByRole('button', { name: 'Reset', exact: true }).click();
  76 |   await expect(page.locator('.timeline-events span')).toHaveCount(9);
  77 | });
  78 | 
  79 | test('package validation, disabled experiment controls, shortcuts and narrow layout', async ({ page }) => {
  80 |   await page.getByRole('button', { name: 'Circuit packages' }).click();
  81 |   await page.getByLabel('Validate a JSON package').setInputFiles({ name: 'invalid.json', mimeType: 'application/json', buffer: Buffer.from('{"schemaVersion":99}') });
  82 |   await expect(page.getByRole('status')).toContainText('Rejected');
  83 |   await page.getByLabel('Validate a JSON package').setInputFiles('public/data/demo/educational-circuits.json');
  84 |   await expect(page.getByRole('status')).toContainText('13 generic nodes');
  85 |   await page.keyboard.press('Escape');
  86 |   await page.getByRole('button', { name: /Experiments/ }).click();
  87 |   await expect(page.getByText('NOT CONNECTED TO A VALIDATED SIMULATOR', { exact: true })).toBeVisible();
  88 |   for (const action of ['Stimulate', 'Silence', 'Lesion', 'Restore', 'Load brain', 'Compare brains']) await expect(page.getByRole('button', { name: new RegExp(`^${action}\\s*Unavailable$`) })).toBeDisabled();
  89 |   await page.keyboard.press('Escape');
  90 |   await page.getByRole('button', { name: 'Controls and help' }).click();
  91 |   await expect(page.getByRole('dialog')).toContainText('courtship');
  92 |   await page.keyboard.press('Escape');
  93 |   await page.setViewportSize({ width: 390, height: 844 });
  94 |   await expect(page.getByRole('heading', { name: 'A small world. A closer look.' })).toBeVisible();
  95 |   expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  96 |   await mkdir('docs/previews', { recursive: true });
  97 |   await page.screenshot({ path: 'docs/previews/mvp-mobile.png', fullPage: true });
  98 | });
  99 | 
```