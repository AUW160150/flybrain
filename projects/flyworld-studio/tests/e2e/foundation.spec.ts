import { test, expect } from '@playwright/test';
import { mkdir } from 'node:fs/promises';
import { activateViewport } from './viewport';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('renderer-status')).toHaveText('WEBGL · READY', { timeout: 30000 });
});

test('world controls, collisions, and explicit educational provenance', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await expect(page.getByText('PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('COLLISION HANDLING: GAME PHYSICS', { exact: true })).toBeVisible();
  await expect(page.getByText('SIMULATION UNAVAILABLE', { exact: true })).toBeVisible();
  await activateViewport(page);
  await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS ACTIVE');
  await page.keyboard.down('a'); await page.waitForTimeout(365); await page.keyboard.up('a');
  await page.keyboard.down('w');
  await expect(page.getByTestId('collision-state')).toHaveText('CONTACT', { timeout: 12000 });
  await page.keyboard.up('w');
  await page.keyboard.press('b');
  await expect(page.getByRole('switch', { name: 'Transparent head' })).toBeChecked();
  await page.keyboard.press('f');
  await expect(page.getByTestId('activation-source')).toHaveText('USER_DRIVEN_ILLUSTRATION');
  await expect(page.getByTestId('last-control')).toContainText('FEED');
  await page.getByRole('button', { name: 'Performance', exact: true }).click();
  await expect(page.getByLabel('Performance overlay')).toContainText('FPS');
  await mkdir('docs/previews', { recursive: true });
  await page.screenshot({ path: 'docs/previews/mvp-world.png', fullPage: true });
  expect(errors).toEqual([]);
});

test('brain click, region and neuron metadata, layers, focus and return', async ({ page }) => {
  await page.getByLabel('Reduced motion', { exact: true }).check();
  await page.getByRole('button', { name: 'Brain', exact: true }).click();
  await expect(page.getByTestId('camera-mode')).toHaveText('BRAIN_INSPECTION');
  const canvas = page.locator('canvas');
  const box = await canvas.boundingBox();
  await page.waitForTimeout(250);
  await canvas.click({ position: { x: box!.width / 2, y: box!.height / 2 } });
  await expect(page.getByTestId('entity-record')).toBeVisible();
  await page.locator('.region-layer-heading button').filter({ hasText: 'Gustatory / taste system' }).click();
  await expect(page.getByTestId('entity-record')).toContainText('demo-taste-system');
  await page.getByRole('button', { name: 'Isolate system' }).click();
  await expect(page.getByLabel('Show Visual system', { exact: true })).not.toBeChecked();
  await page.getByLabel('Gustatory / taste system opacity').fill('60');
  await page.getByRole('button', { name: 'Focus selection' }).click();
  const tasteLayer = page.locator('.region-layer').filter({ has: page.getByLabel('Show Gustatory / taste system', { exact: true }) });
  await tasteLayer.locator('summary').click();
  await page.getByRole('button', { name: 'Taste demo 01', exact: true }).click();
  await expect(page.getByTestId('entity-record')).toContainText('demo-taste-01');
  await expect(page.getByTestId('entity-record')).toContainText('Downstream demo relations');
  await expect(page.getByTestId('entity-record')).toContainText('UNVERIFIED');
  await mkdir('docs/previews', { recursive: true });
  await page.screenshot({ path: 'docs/previews/mvp-brain.png', fullPage: true });
  await page.getByRole('button', { name: 'Reset brain view' }).click();
  await expect(page.getByLabel('Show Visual system', { exact: true })).toBeChecked();
  await page.getByRole('button', { name: /Back to world/ }).click();
  await expect(page.getByTestId('camera-mode')).toHaveText('WORLD_FOLLOW');
});

test('rule tour, synthetic replay, pause, scrub, speed, clear and reset', async ({ page }) => {
  await page.getByRole('button', { name: 'EDUCATIONAL RULE', exact: true }).click();
  await expect(page.getByTestId('control-mode')).toContainText('EDUCATIONAL RULE');
  await expect(page.getByTestId('activation-source')).toHaveText('RULE_DRIVEN_EDUCATIONAL');
  await page.getByRole('button', { name: 'DATA REPLAY', exact: true }).click();
  const timeline = page.getByLabel('Activity timeline position');
  await expect(timeline).toHaveAttribute('max', '24300');
  // Exercise native keyboard input as well as an exact seek, then wait across
  // two telemetry samples to catch the stale controlled-value regression.
  await timeline.press('Home'); await timeline.press('ArrowRight');
  await expect(timeline).toHaveValue('20');
  await timeline.fill('6000');
  await expect(timeline).toHaveValue('6000');
  await page.waitForTimeout(250);
  await expect(timeline).toHaveValue('6000');
  await expect(page.getByTestId('timeline-time')).toContainText('6.0');
  await page.getByLabel('Playback speed').selectOption('2');
  await page.getByRole('button', { name: 'Play activity timeline' }).click();
  await expect(page.getByTestId('timeline-time')).not.toContainText('6.0');
  await page.getByRole('button', { name: 'Pause activity timeline' }).click();
  await page.getByRole('button', { name: 'Clear', exact: true }).click();
  await expect(page.locator('.timeline-events span')).toHaveCount(0);
  await page.getByRole('button', { name: 'Reset', exact: true }).click();
  await expect(page.locator('.timeline-events span')).toHaveCount(9);
});

test('package validation, disabled experiment controls, shortcuts and narrow layout', async ({ page }) => {
  await page.getByRole('button', { name: 'Circuit packages' }).click();
  await page.getByLabel('Validate a JSON package').setInputFiles({ name: 'invalid.json', mimeType: 'application/json', buffer: Buffer.from('{"schemaVersion":99}') });
  await expect(page.getByRole('status')).toContainText('Rejected');
  await page.getByLabel('Validate a JSON package').setInputFiles('public/data/demo/educational-circuits.json');
  await expect(page.getByRole('status')).toContainText('13 generic nodes');
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: /Experiments/ }).click();
  await expect(page.getByText('NOT CONNECTED TO A VALIDATED SIMULATOR', { exact: true })).toBeVisible();
  for (const action of ['Stimulate', 'Silence', 'Lesion', 'Restore', 'Load brain', 'Compare brains']) await expect(page.getByRole('button', { name: new RegExp(`^${action}\\s*Unavailable$`) })).toBeDisabled();
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: 'Controls and help' }).click();
  await expect(page.getByRole('dialog')).toContainText('courtship');
  await page.keyboard.press('Escape');
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole('heading', { name: 'A small world. A closer look.' })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await mkdir('docs/previews', { recursive: true });
  await page.screenshot({ path: 'docs/previews/mvp-mobile.png', fullPage: true });
});
