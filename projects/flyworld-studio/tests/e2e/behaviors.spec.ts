import { expect, test } from '@playwright/test';
import { activateViewport } from './viewport';

test('takeoff, landing and courtship respond to buttons and shortcuts', async ({ page }) => {
  test.setTimeout(60000);
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByTestId('renderer-status')).toHaveText('WEBGL · READY', { timeout: 30000 });
  const height = async () => Number(await page.getByTestId('fly-position').getAttribute('data-y'));
  const status = page.getByTestId('behavior-status');

  await page.getByRole('button', { name: /^Take off/ }).click();
  await expect(page.getByRole('button', { name: /^Land/ })).toBeEnabled();
  await expect.poll(height).toBeGreaterThan(1.5);
  await expect(status).toContainText('Hovering');
  await expect(status).toContainText('USER_DRIVEN_ILLUSTRATION');
  await page.locator('[data-world-viewport]').screenshot({ path: test.info().outputPath('airborne.png') });
  await page.getByRole('button', { name: /^Land/ }).click();
  await expect.poll(height).toBeLessThan(0.01);
  await expect(status).toContainText('Ready');

  await page.getByRole('button', { name: /^Courtship/ }).click();
  await expect(status).toContainText('Courtship wing display');
  await page.waitForTimeout(500);
  await page.locator('[data-world-viewport]').screenshot({ path: test.info().outputPath('courtship.png') });
  await expect(status).toContainText('Ready');
  await activateViewport(page);
  await page.keyboard.press('Space');
  await expect.poll(height).toBeGreaterThan(1.5);
  await page.keyboard.press('Space');
  await expect.poll(height).toBeLessThan(0.01);
  await page.keyboard.press('c');
  await expect(status).toContainText('Courtship wing display');

  await page.getByLabel('Reduced motion', { exact: true }).check();
  await page.getByRole('button', { name: /^Courtship/ }).click();
  await expect(status).toContainText('Reduced motion: static wing poses');
  await page.getByRole('button', { name: 'Brain', exact: true }).click();
  await expect(page.getByRole('button', { name: /^Take off/ })).toBeDisabled();
  await expect(page.locator('#behavior-guidance')).toContainText('Inspection pauses');
  await page.getByRole('button', { name: 'Enable behavior controls' }).click();
  await expect(page.getByTestId('camera-mode')).toHaveText('WORLD_FOLLOW');
  await page.getByRole('button', { name: 'DATA REPLAY', exact: true }).click();
  await expect(page.getByRole('button', { name: /^Courtship/ })).toBeDisabled();
  await page.getByRole('button', { name: 'Enable behavior controls' }).click();
  await expect(page.getByRole('button', { name: 'USER CONTROL', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'MaleCNS data', exact: true }).click();
  await expect(page.getByRole('button', { name: /^Courtship/ })).toBeDisabled();
  await expect(page.locator('#behavior-guidance')).toContainText('Open the world');
  await page.getByRole('button', { name: 'Enable behavior controls' }).click();
  await expect(page.locator('[data-world-viewport]')).toBeVisible();
  await expect(page.getByRole('button', { name: /^Take off/ })).toBeEnabled();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});
