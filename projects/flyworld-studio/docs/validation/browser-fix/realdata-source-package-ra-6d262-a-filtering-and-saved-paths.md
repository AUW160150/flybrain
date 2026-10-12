# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: realdata.spec.ts >> source package, raw body metadata, filtering and saved paths
- Location: tests/e2e/realdata.spec.ts:10:1

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: expect(locator).toHaveText(expected) failed

Locator: getByTestId('real-scientific-label')
Expected: "RAW_STRUCTURAL"
Error: element(s) not found

Call log:
  - Expect "toHaveText" with timeout 30000ms
  - waiting for getByTestId('real-scientific-label')

```

```yaml
- main:
  - link "FlyWorld.":
    - /url: "#"
  - navigation "Main navigation":
    - button "Explore"
    - button "MaleCNS data"
    - button "Circuit packages"
    - button "Experiments LATER"
  - text: LOCAL WORKSPACE
  - button "Controls and help": "?"
  - text: EXPLORATION STUDIO / DATA INTEGRATION 03
  - heading "A small world. A closer look." [level=1]
  - button "EDUCATIONAL + STRUCTURAL Explicit sources · no neural dynamics ↗"
  - button "USER CONTROL" [pressed]
  - button "EDUCATIONAL RULE"
  - button "DATA REPLAY"
  - text: SIMULATION UNAVAILABLE
  - checkbox "Reduced motion"
  - text: Reduced motion
  - button "Performance"
  - region "MaleCNS data workspace":
    - text: MALECNS / LOCAL VERIFIED SOURCE FILES
    - heading "Inspect the records. Keep the limits visible." [level=2]
    - button "← World & educational brain"
    - text: Scientific package
    - combobox "Scientific package":
      - option "Loading catalog…" [disabled] [selected]
    - text: Import small local package
    - button "Import real circuit package"
    - alert: "Rejected: [ { \"origin\": \"string\", \"code\": \"invalid_format\", \"format\": \"regex\", \"pattern\": \"/^malecns-[a-z-]+\\\\.json$/\", \"path\": [ \"packages\", 3, \"file\" ], \"message\": \"Invalid string: must match pattern /^malecns-[a-z-]+\\\\.json$/\" }, { \"origin\": \"string\", \"code\": \"invalid_format\", \"format\": \"regex\", \"pattern\": \"/^malecns-[a-z-]+\\\\.json$/\", \"path\": [ \"packages\", 4, \"file\" ], \"message\": \"Invalid string: must match pattern /^malecns-[a-z-]+\\\\.json$/\" } ]"
  - region "Activity and behavior controls":
    - text: BEHAVIORS
    - button "Take offSPACE"
    - button "FeedF"
    - button "GroomG"
    - button "Escape animationE"
    - button "CourtshipC"
    - button "StopX"
    - text: Explicit gesture commands
    - button "Pause activity timeline": Ⅱ
    - text: SESSION RECORDING
    - strong: 25.5 / 25.5 s
    - slider "Activity timeline position": "25460"
    - text: Scrub to review this session; physical controls pause during review. Speed
    - combobox "Playback speed":
      - option "0.25×"
      - option "0.5×"
      - option "1×" [selected]
      - option "1.5×"
      - option "2×"
    - button "Reset"
    - button "Clear"
    - text: V
    - meter "Visual system intensity"
    - text: T
    - meter "Gustatory / taste system intensity"
    - text: M
    - meter "Motor / descending system intensity"
    - text: C
    - meter "Mating / courtship system intensity"
    - text: I
    - meter "Central integration / other intensity"
    - text: Normalized display intensity [0, 1] · never a firing rate CAMERA:WORLD_FOLLOW / PRESS · USER_DRIVEN_ILLUSTRATION 0 / 120 events · original provenance retained
  - text: FLYWORLD / v0.3.0 Explore the interface. Keep the evidence visible.
  - button "Scientific boundaries ↗"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { mkdir, readFile } from 'node:fs/promises';
  3  | 
  4  | test.beforeEach(async ({ page }) => {
  5  |   await page.goto('/');
  6  |   await page.getByRole('button', { name: 'MaleCNS data', exact: true }).click();
> 7  |   await expect(page.getByTestId('real-scientific-label')).toHaveText('RAW_STRUCTURAL', { timeout: 30000 });
     |                                                           ^ Error: expect(locator).toHaveText(expected) failed
  8  | });
  9  | 
  10 | test('source package, raw body metadata, filtering and saved paths', async ({ page }) => {
  11 |   await expect(page.getByTestId('dataset-panel')).toContainText('4b2087c0fbe046bfaf0d60bc970e3e5d');
  12 |   await page.getByLabel('Inspect real body').selectOption('957530');
  13 |   await expect(page.getByTestId('real-inspector')).toContainText('M003');
  14 |   await expect(page.getByTestId('real-inspector')).toContainText('ANATOMY UNAVAILABLE FOR THIS BODY');
  15 |   await page.getByRole('button', { name: 'One hop', exact: true }).click();
  16 |   await expect(page.locator('.path-controls')).toContainText('ONE_HOP');
  17 |   await page.getByLabel('Body side filter').selectOption('L');
  18 |   await page.getByRole('button', { name: 'Reset filters', exact: true }).click();
  19 |   await page.getByLabel('Scientific package').selectOption('malecns-paper');
  20 |   await expect(page.getByTestId('real-scientific-label')).toHaveText('PAPER_ASSOCIATED');
  21 |   await page.getByLabel('Saved package path number').fill('1');
  22 |   await page.getByRole('button', { name: 'Isolate saved path', exact: true }).click();
  23 |   await expect(page.locator('.path-controls')).toContainText('PATH');
  24 |   await page.getByRole('button', { name: 'Raw edges', exact: true }).click();
  25 |   await expect(page.locator('.raw-table tbody tr')).toHaveCount(3);
  26 |   await mkdir('docs/previews', { recursive: true });
  27 |   await page.screenshot({ path: 'docs/previews/realdata-package.png', fullPage: true });
  28 | });
  29 | 
  30 | test('candidate independence, blocked selection, local loader guards and educational mapping', async ({ page }) => {
  31 |   await page.getByLabel('Scientific package').selectOption('malecns-candidates');
  32 |   await expect(page.getByTestId('real-scientific-label')).toHaveText('CANDIDATE');
  33 |   await expect(page.locator('.population-grid')).toContainText('GNG232');
  34 |   await expect(page.getByTestId('dataset-panel')).toContainText('12 / 0');
  35 |   await page.getByLabel('Scientific package').selectOption('malecns-sugar-selected');
  36 |   await expect(page.getByText('VALIDATED SUGAR SELECTION UNAVAILABLE', { exact: true })).toBeVisible();
  37 |   const bad = JSON.parse(await readFile('public/data/malecns/malecns-motors.json', 'utf8'));
  38 |   bad.dataset.uuid = '0'.repeat(32);
  39 |   await page.getByLabel('Import real circuit package').setInputFiles({ name: 'wrong-dataset.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(bad)) });
  40 |   await expect(page.getByRole('alert').filter({ hasText: 'Rejected:' })).toContainText('Incompatible dataset');
  41 |   await page.getByLabel('Import real circuit package').setInputFiles('public/data/malecns/malecns-motors.json');
  42 |   await expect(page.getByTestId('dataset-panel')).toContainText('Custom file: schema valid');
  43 |   await page.getByRole('button', { name: 'Illustrate feeding', exact: true }).click();
  44 |   await expect(page.getByTestId('real-highlight-source')).toContainText('USER_DRIVEN_ILLUSTRATION');
  45 |   await expect(page.getByTestId('real-highlight-source')).toContainText('10 mapped bodies');
  46 |   await page.getByRole('button', { name: 'EDUCATIONAL RULE', exact: true }).click();
  47 |   await expect(page.getByTestId('real-highlight-source')).toHaveCount(0);
  48 | });
  49 | 
  50 | test('geometry provenance, absent anatomy, region context and narrow layout', async ({ page }) => {
  51 |   await expect(page.getByRole('button', { name: 'Morphology', exact: true })).toBeDisabled();
  52 |   await page.getByRole('button', { name: 'Region context', exact: true }).click();
  53 |   await expect(page.locator('.region-context')).toContainText('No verified body-to-region assignment');
  54 |   await page.getByLabel('Scientific package').selectOption('malecns-anatomy');
  55 |   await expect(page.getByTestId('real-scientific-label')).toHaveText('ANATOMY_ONLY');
  56 |   await expect(page.getByRole('button', { name: 'Morphology', exact: true })).toBeEnabled();
  57 |   await expect(page.locator('.morphology-view')).toContainText('SOURCE-BACKED NATIVE SWC', { timeout: 30000 });
  58 |   await expect(page.locator('.morphology-view')).toContainText('orientation UNVERIFIED');
  59 |   await page.setViewportSize({ width: 390, height: 844 });
  60 |   expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  61 |   await mkdir('docs/previews', { recursive: true });
  62 |   await page.screenshot({ path: 'docs/previews/realdata-anatomy.png', fullPage: true });
  63 | });
  64 | 
```