import { test, expect, type Page } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { obstacles, FLY_RADIUS } from '../../src/world/collision';
import { activateViewport as activate } from './viewport';

async function pose(page: Page) {
  const p = page.getByTestId('fly-position');
  return { x: Number(await p.getAttribute('data-x')), y: Number(await p.getAttribute('data-y')), z: Number(await p.getAttribute('data-z')), yaw: Number(await page.getByTestId('fly-heading').getAttribute('data-yaw')) };
}
const distance = (a: { x: number; z: number }, b: { x: number; z: number }) => Math.hypot(a.x - b.x, a.z - b.z);
async function hold(page: Page, code: string, ms: number) {
  await page.keyboard.down(code); await page.waitForTimeout(ms); await page.keyboard.up(code); await page.waitForTimeout(150);
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('renderer-status')).toHaveText('WEBGL · READY', { timeout: 30000 });
});

test('13-step controls acceptance sequence with captured movement evidence', async ({ page }) => {
  test.setTimeout(75000);
  const results: object[] = [];
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await mkdir('docs/validation/prompt03a', { recursive: true });
  await mkdir('docs/previews', { recursive: true });
  const step = async (name: string, run: () => Promise<void>) => {
    await test.step(name, async () => {
      try { await run(); results.push({ name, status: 'PASS', pose: await pose(page) }); }
      catch (error) { results.push({ name, status: 'FAIL', error: String(error) }); throw error; }
    });
  };
  const tree = obstacles.find(o => o.id === 'tree')!;
  let start = await pose(page), leftStart = start, rightStart = start, blocked = start, paused = start;
  try {
    await step('1. Start in Follow mode', async () => {
      await page.getByRole('button', { name: 'Follow', exact: true }).click();
      await expect(page.getByTestId('camera-mode')).toHaveText('WORLD_FOLLOW');
      await page.getByRole('button', { name: 'Performance', exact: true }).click();
    });
    await step('2. Click the 3D viewport', async () => {
      await activate(page); await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS ACTIVE');
      await expect(page.locator('[data-world-viewport]')).toBeFocused(); start = await pose(page);
    });
    await step('3. Hold W for 2 seconds', async () => {
      await page.keyboard.down('w'); await page.waitForTimeout(2000);
    });
    await step('4. Confirm advancing position; capture rendered scene', async () => {
      expect((await pose(page)).z - start.z).toBeGreaterThan(1);
      await expect(page.getByTestId('fly-state')).toHaveText('WALK_FORWARD');
      await page.screenshot({ path: 'docs/previews/controls-forward.png', fullPage: true });
    });
    await step('5. Hold A while still holding W', async () => {
      leftStart = await pose(page); await page.keyboard.down('a'); await page.waitForTimeout(600);
    });
    await step('6. Confirm curved left path', async () => {
      const end = await pose(page); expect(end.yaw - leftStart.yaw).toBeGreaterThan(0.2); expect(distance(end, leftStart)).toBeGreaterThan(0.2);
      expect(end.x - leftStart.x).toBeGreaterThan(0.1);
      await expect(page.getByTestId('fly-state')).toHaveText('WALK_TURN');
      await page.screenshot({ path: 'docs/previews/controls-left.png', fullPage: true });
      await page.keyboard.up('a'); await page.keyboard.up('w'); await page.waitForTimeout(150);
    });
    await step('7. Repeat with ArrowUp + ArrowRight', async () => {
      rightStart = await pose(page);
      const scroll = await page.evaluate(() => window.scrollY);
      await page.keyboard.down('ArrowUp'); await page.keyboard.down('ArrowRight'); await page.waitForTimeout(600);
      const end = await pose(page); expect(end.yaw).toBeLessThan(rightStart.yaw - 0.2); expect(distance(end, rightStart)).toBeGreaterThan(0.2);
      expect(await page.evaluate(() => window.scrollY)).toBe(scroll);
      await page.keyboard.up('ArrowRight'); await page.keyboard.up('ArrowUp'); await page.waitForTimeout(150);
    });
    await step('8. Walk into the tree', async () => {
      // Steer through public key events using observed telemetry; no pose injection.
      for (let i = 0; i < 8; i++) {
        const p = await pose(page); const angle = Math.atan2(tree.x - p.x, tree.z - p.z);
        const delta = Math.atan2(Math.sin(angle - p.yaw), Math.cos(angle - p.yaw));
        if (Math.abs(delta) < 0.08) break;
        await hold(page, delta > 0 ? 'a' : 'd', Math.min(500, Math.abs(delta) * 500));
      }
      await page.keyboard.down('w');
      await expect(page.getByTestId('fly-state')).toHaveText('COLLISION_BLOCKED', { timeout: 12000 });
    });
    await step('9. Confirm collision prevents penetration', async () => {
      blocked = await pose(page);
      expect(distance(blocked, tree)).toBeGreaterThanOrEqual(tree.radius + FLY_RADIUS - 0.001);
      expect(distance(blocked, tree)).toBeLessThan(tree.radius + FLY_RADIUS + 0.1);
      await expect(page.getByTestId('forward-speed')).toContainText('0.000');
      await page.screenshot({ path: 'docs/previews/controls-tree.png', fullPage: true });
    });
    await step('10. Turn away and move again', async () => {
      await hold(page, 'a', 1600); await page.waitForTimeout(400);
      expect(distance(await pose(page), blocked)).toBeGreaterThan(0.5);
      await expect(page.getByTestId('collision-state')).toHaveText('CLEAR');
      await page.keyboard.up('w');
    });
    await step('11. Enter Brain mode', async () => {
      await page.getByRole('button', { name: 'Brain', exact: true }).click();
      await expect(page.getByTestId('camera-mode')).toHaveText('BRAIN_INSPECTION');
      await page.waitForTimeout(200); paused = await pose(page);
    });
    await step('12. Confirm locomotion pauses', async () => {
      await activate(page); await hold(page, 'w', 500);
      expect(await pose(page)).toEqual(paused);
      await expect(page.getByTestId('fly-state')).toHaveText('BRAIN_INSPECTION_PAUSED');
      await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
      await page.screenshot({ path: 'docs/previews/controls-brain.png', fullPage: true });
    });
    await step('13. Return to Follow mode and move again', async () => {
      await page.getByRole('button', { name: 'Follow', exact: true }).click(); await activate(page);
      const before = await pose(page); await hold(page, 'w', 600);
      expect(distance(await pose(page), before)).toBeGreaterThan(0.3);
      await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS ACTIVE');
      await page.screenshot({ path: 'docs/previews/controls-return.png', fullPage: true });
    });
    expect(errors).toEqual([]);
  } finally {
    // Save outcomes before cleanup: a timed-out page may already be closed.
    await writeFile('docs/validation/prompt03a/browser-acceptance.json', JSON.stringify({
      kind: 'AUTOMATED_BROWSER_SEQUENCE', humanVisualReview: 'PENDING', results, pageErrors: errors,
    }, null, 2) + '\n');
    await Promise.allSettled(['w', 'a', 'ArrowUp', 'ArrowRight'].map(code => page.keyboard.up(code)));
  }
});

test('focus, typing, pointer movement, and all camera modes', async ({ page }) => {
  await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
  const before = await pose(page);
  await hold(page, 'w', 250); expect(await pose(page)).toEqual(before);
  await activate(page); await page.keyboard.down('w');
  await expect.poll(async () => (await pose(page)).z).toBeGreaterThan(before.z + 0.1);
  // Exercise a real editable DOM target without adding a product form for this test.
  await page.evaluate(() => {
    const field = document.createElement('input');
    field.setAttribute('aria-label', 'Focus test input'); document.body.append(field); field.focus();
  });
  await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
  await page.keyboard.up('w'); await page.waitForTimeout(150);
  const typing = await pose(page);
  await page.getByLabel('Focus test input').pressSequentially('wasd');
  expect(await page.getByLabel('Focus test input').inputValue()).toBe('wasd');
  await hold(page, 'ArrowUp', 250); expect(await pose(page)).toEqual(typing);
  await page.getByLabel('Focus test input').evaluate(field => field.remove());
  await activate(page);
  const forward = page.getByRole('button', { name: 'Move forward', exact: true });
  const rect = (await forward.boundingBox())!;
  await page.mouse.move(rect.x + rect.width / 2, rect.y + rect.height / 2);
  await page.mouse.down(); await page.waitForTimeout(400); await page.mouse.up();
  await expect.poll(async () => (await pose(page)).z).toBeGreaterThan(typing.z + 0.1);
  for (const [name, mode, paused] of [
    ['Orbit', 'WORLD_ORBIT', false], ['Fly', 'FLY_INSPECTION', true],
    ['Brain', 'BRAIN_INSPECTION', true], ['Follow', 'WORLD_FOLLOW', false],
  ] as const) {
    await page.getByRole('button', { name, exact: true }).click();
    await expect(page.getByTestId('camera-mode')).toHaveText(mode);
    await activate(page); await page.waitForTimeout(150); const start = await pose(page);
    await hold(page, 'w', 300); const end = await pose(page);
    if (paused) expect(end).toEqual(start); else expect(distance(end, start)).toBeGreaterThan(0.1);
  }
  await activate(page); await page.keyboard.down('w');
  await page.getByRole('button', { name: 'MaleCNS data', exact: true }).click();
  await page.keyboard.up('w'); await hold(page, 'w', 300);
  await page.getByRole('button', { name: 'Explore', exact: true }).click();
  await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
  const back = await pose(page); await hold(page, 'w', 300); expect(await pose(page)).toEqual(back);
});
