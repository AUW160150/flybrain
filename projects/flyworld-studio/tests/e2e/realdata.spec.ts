import { test, expect } from '@playwright/test';
import { mkdir, readFile } from 'node:fs/promises';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'MaleCNS data', exact: true }).click();
  // Surface a load rejection immediately instead of timing out on a missing badge.
  const label = page.getByTestId('real-scientific-label');
  const rejection = page.locator('.real-workspace [role="alert"]');
  await expect(label.or(rejection)).toBeVisible({ timeout: 15000 });
  expect(await rejection.allTextContents(), 'The bundled catalog/package must load without a rejection').toEqual([]);
  await expect(label).toHaveText('RAW_STRUCTURAL');
});

test('source package, raw body metadata, filtering and saved paths', async ({ page }) => {
  await expect(page.getByTestId('dataset-panel')).toContainText('4b2087c0fbe046bfaf0d60bc970e3e5d');
  await page.getByLabel('Inspect real body').selectOption('957530');
  await expect(page.getByTestId('real-inspector')).toContainText('M003');
  await expect(page.getByTestId('real-inspector')).toContainText('ANATOMY UNAVAILABLE FOR THIS BODY');
  await page.getByRole('button', { name: 'One hop', exact: true }).click();
  await expect(page.locator('.path-controls')).toContainText('ONE_HOP');
  await page.getByLabel('Body side filter').selectOption('L');
  await page.getByRole('button', { name: 'Reset filters', exact: true }).click();
  await page.getByLabel('Scientific package').selectOption('malecns-paper');
  await expect(page.getByTestId('real-scientific-label')).toHaveText('PAPER_ASSOCIATED');
  await page.getByLabel('Saved package path number').fill('1');
  await page.getByRole('button', { name: 'Isolate saved path', exact: true }).click();
  await expect(page.locator('.path-controls')).toContainText('PATH');
  await page.getByRole('button', { name: 'Raw edges', exact: true }).click();
  await expect(page.locator('.raw-table tbody tr')).toHaveCount(3);
  await mkdir('docs/previews', { recursive: true });
  await page.screenshot({ path: 'docs/previews/realdata-package.png', fullPage: true });
});

test('candidate independence, blocked selection, local loader guards and educational mapping', async ({ page }) => {
  await page.getByLabel('Scientific package').selectOption('malecns-candidates');
  await expect(page.getByTestId('real-scientific-label')).toHaveText('CANDIDATE');
  await expect(page.locator('.population-grid')).toContainText('GNG232');
  await expect(page.getByTestId('dataset-panel')).toContainText('12 / 0');
  await page.getByLabel('Scientific package').selectOption('malecns-sugar-selected');
  await expect(page.getByText('VALIDATED SUGAR SELECTION UNAVAILABLE', { exact: true })).toBeVisible();
  const bad = JSON.parse(await readFile('public/data/malecns/malecns-motors.json', 'utf8'));
  bad.dataset.uuid = '0'.repeat(32);
  await page.getByLabel('Import real circuit package').setInputFiles({ name: 'wrong-dataset.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(bad)) });
  await expect(page.getByRole('alert').filter({ hasText: 'Rejected:' })).toContainText('Incompatible dataset');
  await page.getByLabel('Import real circuit package').setInputFiles('public/data/malecns/malecns-motors.json');
  await expect(page.getByTestId('dataset-panel')).toContainText('Custom file: schema valid');
  await page.getByRole('button', { name: 'Illustrate feeding', exact: true }).click();
  await expect(page.getByTestId('real-highlight-source')).toContainText('USER_DRIVEN_ILLUSTRATION');
  await expect(page.getByTestId('real-highlight-source')).toContainText('10 mapped bodies');
  await page.getByRole('button', { name: 'EDUCATIONAL RULE', exact: true }).click();
  await expect(page.getByTestId('real-highlight-source')).toHaveCount(0);
});

test('geometry provenance, absent anatomy, region context and narrow layout', async ({ page }, testInfo) => {
  await expect(page.getByRole('button', { name: 'Morphology', exact: true })).toBeDisabled();
  await page.getByRole('button', { name: 'Region context', exact: true }).click();
  await expect(page.locator('.region-context')).toContainText('No verified body-to-region assignment');
  await page.getByLabel('Scientific package').selectOption('malecns-anatomy');
  await expect(page.getByTestId('real-scientific-label')).toHaveText('ANATOMY_ONLY');
  await expect(page.getByRole('button', { name: 'Morphology', exact: true })).toBeEnabled();
  await expect(page.locator('.morphology-view')).toContainText('SOURCE-BACKED NATIVE SWC', { timeout: 30000 });
  await expect(page.locator('.morphology-view')).toContainText('orientation UNVERIFIED');
  await page.setViewportSize({ width: 390, height: 844 });
  try {
    // ResizeObserver/canvas layout may settle asynchronously; permanent overflow
    // still fails. Never hide page overflow to satisfy this assertion.
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth), { message: 'Anatomy page must fit the 390px viewport' }).toBeLessThanOrEqual(390);
    for (const name of ['Scientific package', 'Import real circuit package', 'Body side filter', 'Body evidence filter', 'Body type filter', 'Inspect real body']) {
      const control = page.getByLabel(name, { exact: true });
      const size = await control.evaluate(element => {
        const rect = element.getBoundingClientRect(), label = element.closest('label')!.getBoundingClientRect();
        return { left: rect.left, right: rect.right, labelLeft: label.left, labelRight: label.right };
      });
      expect(size.left, name + ' left edge').toBeGreaterThanOrEqual(size.labelLeft);
      expect(size.right, name + ' right edge').toBeLessThanOrEqual(size.labelRight);
    }
  } finally {
    const layout = await page.evaluate(() => ({
      viewport: window.innerWidth, documentWidth: document.documentElement.scrollWidth,
      elements: [...document.querySelectorAll<HTMLElement>('body *')].flatMap(element => {
        const rect = element.getBoundingClientRect();
        if (!rect.width || (rect.left >= 0 && rect.right <= window.innerWidth)) return [];
        const style = getComputedStyle(element);
        return [{ tag: element.tagName, class: element.className, label: element.getAttribute('aria-label'),
          left: rect.left, right: rect.right, width: rect.width, minWidth: style.minWidth, display: style.display,
          overflowX: style.overflowX, clientWidth: element.clientWidth, scrollWidth: element.scrollWidth }];
      }).slice(0, 40),
    }));
    await testInfo.attach('mobile-layout', { body: JSON.stringify(layout, null, 2), contentType: 'application/json' });
  }
  await mkdir('docs/previews', { recursive: true });
  await page.screenshot({ path: 'docs/previews/realdata-anatomy.png', fullPage: true });
});
