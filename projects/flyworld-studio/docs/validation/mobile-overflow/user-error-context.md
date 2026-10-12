# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: realdata.spec.ts >> geometry provenance, absent anatomy, region context and narrow layout
- Location: tests/e2e/realdata.spec.ts:55:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e4]:
    - link "FlyWorld." [ref=e5] [cursor=pointer]:
      - /url: "#"
      - img [ref=e6]
      - generic [ref=e11]: FlyWorld.
    - navigation "Main navigation" [ref=e12]:
      - button "Explore" [ref=e13] [cursor=pointer]
      - button "MaleCNS data" [ref=e14] [cursor=pointer]
      - button "Circuit packages" [ref=e15] [cursor=pointer]
      - button "Experiments" [ref=e16] [cursor=pointer]
    - button "Controls and help" [ref=e18] [cursor=pointer]: "?"
  - generic [ref=e19]:
    - generic [ref=e20]:
      - generic [ref=e21]: EXPLORATION STUDIO / DATA INTEGRATION 03
      - heading "A small world. A closer look." [level=1] [ref=e22]
    - button "EDUCATIONAL + STRUCTURAL Explicit sources · no neural dynamics" [ref=e23] [cursor=pointer]:
      - generic [ref=e25]:
        - text: EDUCATIONAL + STRUCTURAL
        - generic [ref=e26]: Explicit sources · no neural dynamics
  - generic [ref=e27]:
    - generic "Exploration modes" [ref=e28]:
      - button "USER CONTROL" [pressed] [ref=e29] [cursor=pointer]
      - button "EDUCATIONAL RULE" [ref=e30] [cursor=pointer]
      - button "DATA REPLAY" [ref=e31] [cursor=pointer]
    - generic [ref=e32]: SIMULATION UNAVAILABLE
    - generic [ref=e33]:
      - generic [ref=e34] [cursor=pointer]:
        - checkbox "Reduced motion" [ref=e35]
        - text: Reduced motion
      - button "Performance" [ref=e36] [cursor=pointer]
  - region "MaleCNS data workspace" [ref=e37]:
    - generic [ref=e38]:
      - generic [ref=e39]:
        - generic [ref=e40]: MALECNS / LOCAL VERIFIED SOURCE FILES
        - heading "Inspect the records. Keep the limits visible." [level=2] [ref=e41]
      - button "← World & educational brain" [ref=e42] [cursor=pointer]
    - generic [ref=e43]:
      - generic [ref=e44]:
        - text: Scientific package
        - combobox "Scientific package" [ref=e45]:
          - option "Custom local package" [disabled]
          - option "Focused verified bodies · 110 bodies"
          - option "Paper-associated structural motif · 102 bodies"
          - option "Independent candidate comparison · 12 bodies"
          - option "LB3b population · 11 bodies"
          - option "LB3c population · 23 bodies"
          - option "Requested motor neurons · 10 bodies"
          - option "Sugar-selected circuit — unavailable · 0 bodies"
          - option "Locally cached anatomy subset · 3 bodies" [selected]
      - generic [ref=e46]:
        - text: Import small local package
        - button "Import real circuit package" [ref=e47]
    - generic [ref=e48]:
      - strong [ref=e49]: ANATOMY_ONLY
      - generic [ref=e50]: male-cns:v1.0
      - generic [ref=e51]: IN-PACKAGE ONLY
      - generic [ref=e52]: SIMULATION UNAVAILABLE
    - generic [ref=e53]:
      - generic [ref=e54]: Raw counts describe saved structure. No connectome activity or autonomous behavior is calculated.
      - button "Illustrate feeding" [ref=e55] [cursor=pointer]
    - paragraph [ref=e56]: Feeding can illustrate source-labelled motor records where they are package members. Other behavior keys have no real-body mapping. No highlight is inferred from raw edge counts.
    - generic [ref=e57]:
      - generic [ref=e58]:
        - text: Side
        - combobox "Body side filter" [ref=e59]:
          - option "ALL" [selected]
          - option "L"
          - option "R"
          - option "M"
          - option "UNKNOWN"
      - generic [ref=e60]:
        - text: Evidence
        - combobox "Body evidence filter" [ref=e61]:
          - option "ALL" [selected]
          - option "RAW_STRUCTURAL"
          - option "LITERATURE_ASSOCIATED"
          - option "SOURCE_BACKED_ANATOMY"
      - generic [ref=e62]:
        - text: Type
        - combobox "Body type filter" [ref=e63]:
          - option "ALL" [selected]
          - option "Am1"
          - option "DNc01"
          - option "Pm11"
      - generic [ref=e64]:
        - text: Body
        - combobox "Inspect real body" [ref=e65]:
          - option "Select body" [disabled]
          - option "Am1 · 10093 · R" [selected]
          - option "Pm11 · 10807 · R"
          - option "DNc01 · 11369 · L"
      - button "Reset filters" [ref=e66] [cursor=pointer]
    - generic "Scientific data views" [ref=e67]:
      - button "Body diagram" [ref=e68] [cursor=pointer]
      - button "Populations" [ref=e69] [cursor=pointer]
      - button "Region context" [active] [ref=e70] [cursor=pointer]
      - button "Raw edges" [ref=e71] [cursor=pointer]
      - button "Morphology" [pressed] [ref=e72] [cursor=pointer]
    - generic [ref=e73]:
      - generic [ref=e74]: "Isolation: ALL · 3/3 visible bodies"
      - button "Full package membership" [ref=e75] [cursor=pointer]
      - generic [ref=e76]:
        - text: Saved paper path (0)
        - spinbutton "Saved package path number" [disabled] [ref=e77]: "1"
      - button "Isolate saved path" [disabled] [ref=e78]
    - generic [ref=e79]:
      - generic [ref=e81]:
        - generic [ref=e82]:
          - strong [ref=e83]: SOURCE-BACKED NATIVE SWC · 10093
          - generic [ref=e84]: 54,204 original points · 8 nm coordinate units · orientation UNVERIFIED
        - paragraph [ref=e89]: Native XYZ axes; no anatomical camera names, mirroring, branch repair, or inferred neurites. Lines are skeleton cables, not synaptic edges. This view is centered for display only.
        - group [ref=e90]:
          - generic "Original SWC headers and geometry provenance" [ref=e91] [cursor=pointer]
      - complementary "Real neuron inspector" [ref=e92]:
        - generic [ref=e93]: SOURCE RECORD / BODY
        - heading "Am1 10093" [level=2] [ref=e94]:
          - text: Am1
          - generic [ref=e95]: "10093"
        - generic [ref=e96]:
          - generic [ref=e97]: RAW_STRUCTURAL
          - generic [ref=e98]: SOURCE_BACKED_ANATOMY
        - paragraph [ref=e99]: SOURCE-BACKED SWC · native orientation UNVERIFIED
        - generic [ref=e100]:
          - generic [ref=e101]:
            - term [ref=e102]: Body ID
            - definition [ref=e103]: "10093"
          - generic [ref=e104]:
            - term [ref=e105]: Type
            - definition [ref=e106]: Am1
          - generic [ref=e107]:
            - term [ref=e108]: Aliases (source)
            - definition [ref=e109]: UNRESOLVED / not supplied
          - generic [ref=e110]:
            - term [ref=e111]: Display alias
            - definition [ref=e112]: UNRESOLVED / not supplied
          - generic [ref=e113]:
            - term [ref=e114]: Side
            - definition [ref=e115]: R
          - generic [ref=e116]:
            - term [ref=e117]: Side source
            - definition [ref=e118]: somaSide
          - generic [ref=e119]:
            - term [ref=e120]: Root side
            - definition [ref=e121]: UNRESOLVED / not supplied
          - generic [ref=e122]:
            - term [ref=e123]: Soma side
            - definition [ref=e124]: R
          - generic [ref=e125]:
            - term [ref=e126]: Class
            - definition [ref=e127]: UNRESOLVED / not supplied
          - generic [ref=e128]:
            - term [ref=e129]: Superclass
            - definition [ref=e130]: ol_intrinsic
          - generic [ref=e131]:
            - term [ref=e132]: Source classification
            - definition [ref=e133]: interneuron_or_projection_neuron
          - generic [ref=e134]:
            - term [ref=e135]: Entry nerve
            - definition [ref=e136]: UNRESOLVED / not supplied
          - generic [ref=e137]:
            - term [ref=e138]: Exit nerve
            - definition [ref=e139]: UNRESOLVED / not supplied
          - generic [ref=e140]:
            - term [ref=e141]: NT body prediction
            - definition [ref=e142]: gaba
          - generic [ref=e143]:
            - term [ref=e144]: Prediction confidence
            - definition [ref=e145]: "0.886853987401077"
          - generic [ref=e146]:
            - term [ref=e147]: Transmitter consensus
            - definition [ref=e148]: gaba
          - generic [ref=e149]:
            - term [ref=e150]: Cell-type prediction
            - definition [ref=e151]: gaba
          - generic [ref=e152]:
            - term [ref=e153]: Cell-type confidence
            - definition [ref=e154]: "0.883054076455254"
        - paragraph [ref=e155]: PREDICTED TRANSMITTER — NOT DIRECT PHYSIOLOGICAL VALIDATION
        - heading "Package membership" [level=3] [ref=e156]
        - list [ref=e157]:
          - listitem [ref=e158]: malecns-anatomy
        - paragraph [ref=e159]: "Source search memberships: E. These are bounded raw-search sets, not effective selection."
        - heading "Inspect raw partners IN-PACKAGE ONLY" [level=3] [ref=e160]:
          - text: Inspect raw partners
          - generic [ref=e161]: IN-PACKAGE ONLY
        - generic [ref=e162]:
          - button "Incoming" [ref=e163] [cursor=pointer]
          - button "Outgoing" [ref=e164] [cursor=pointer]
          - button "One hop" [ref=e165] [cursor=pointer]
          - button "Full package" [ref=e166] [cursor=pointer]
        - group [ref=e167]:
          - 'generic "Incoming: 0 partners · 0 raw synapses" [ref=e168] [cursor=pointer]'
          - paragraph [ref=e170]: No records in this package. This does not establish absence from the connectome.
        - group [ref=e171]:
          - 'generic "Outgoing: 0 partners · 0 raw synapses" [ref=e172] [cursor=pointer]'
          - paragraph [ref=e174]: No records in this package. This does not establish absence from the connectome.
        - heading "Mismatch warnings" [level=3] [ref=e175]
        - paragraph [ref=e176]: No body-specific ledger warning supplied. Package-wide limitations still apply.
        - heading "Unresolved fields" [level=3] [ref=e177]
        - paragraph [ref=e178]: root_side, cell_class, entry_nerve
        - heading "Evidence and sources" [level=3] [ref=e179]
        - paragraph [ref=e180]: NOT ASSESSED
        - list [ref=e181]:
          - listitem [ref=e182]: results/structural/20261006T180116Z/nodes.csv
        - group [ref=e183]:
          - generic "Original evidence and annotation references" [ref=e184] [cursor=pointer]
    - group [ref=e185]:
      - generic "Dataset and package provenance" [ref=e186] [cursor=pointer]
      - generic [ref=e187]:
        - generic [ref=e188]:
          - term [ref=e189]: Loaded package
          - definition [ref=e190]: Locally cached anatomy subset
        - generic [ref=e191]:
          - term [ref=e192]: Scientific label
          - definition [ref=e193]: ANATOMY_ONLY
        - generic [ref=e194]:
          - term [ref=e195]: Dataset / version
          - definition [ref=e196]: male-cns:v1.0 / v1.0
        - generic [ref=e197]:
          - term [ref=e198]: UUID
          - definition [ref=e199]: 4b2087c0fbe046bfaf0d60bc970e3e5d
        - generic [ref=e200]:
          - term [ref=e201]: Bodies / edges
          - definition [ref=e202]: 3 / 0
        - generic [ref=e203]:
          - term [ref=e204]: Package size
          - definition [ref=e205]: 19,749 bytes
        - generic [ref=e206]:
          - term [ref=e207]: Source run
          - definition [ref=e208]: results/structural/20261006T180116Z
        - generic [ref=e209]:
          - term [ref=e210]: Visualization run
          - definition [ref=e211]: visualization/data/20261006T221533490089Z
        - generic [ref=e212]:
          - term [ref=e213]: Anatomy
          - definition [ref=e214]: 3/3 source-backed local SWCs
        - generic [ref=e215]:
          - term [ref=e216]: Effective selection
          - definition [ref=e217]: UNAVAILABLE — no validated result
        - generic [ref=e218]:
          - term [ref=e219]: Simulation
          - definition [ref=e220]: UNAVAILABLE
        - generic [ref=e221]:
          - term [ref=e222]: Import assurance
          - definition [ref=e223]: Bundled package checksum verified; source hashes checked offline
      - paragraph [ref=e224]: Receipt-verified local native morphology; no connectivity graph claimed.
      - paragraph [ref=e225]:
        - text: "Generated 2026-10-08T00:24:31.828775+00:00. Partner scope:"
        - strong [ref=e226]: IN-PACKAGE ONLY
        - text: .
      - group [ref=e227]:
        - generic "Source hashes and preprocessing scripts" [ref=e228] [cursor=pointer]
      - group [ref=e229]:
        - generic "Unresolved warnings and scientific limits (19)" [ref=e230] [cursor=pointer]
    - paragraph [ref=e231]: "Safety limits: 500 bodies · 5000 edges · 16 geometry objects · 4 MiB/package. Anatomy loads one selected body at a time. No full raw graph enters this browser."
    - generic [ref=e232]:
      - link "Download package checksums" [ref=e233] [cursor=pointer]:
        - /url: /data/malecns/SHA256SUMS
      - link "Download a generated two-body custom example" [ref=e234] [cursor=pointer]:
        - /url: /data/custom-example/malecns-custom.json
  - region "Activity and behavior controls" [ref=e235]:
    - generic [ref=e236]:
      - generic [ref=e237]: BEHAVIORS
      - generic [ref=e238]:
        - button "Take offSPACE" [ref=e239] [cursor=pointer]
        - button "FeedF" [ref=e240] [cursor=pointer]
        - button "GroomG" [ref=e241] [cursor=pointer]
        - button "Escape animationE" [ref=e242] [cursor=pointer]
        - button "CourtshipC" [ref=e243] [cursor=pointer]
        - button "StopX" [ref=e244] [cursor=pointer]
    - generic [ref=e245]:
      - button "Pause activity timeline" [ref=e246] [cursor=pointer]: Ⅱ
      - generic [ref=e247]:
        - generic [ref=e248]: SESSION RECORDING
        - strong [ref=e249]:
          - text: "1.0"
          - generic [ref=e250]: / 10.0 s
      - generic [ref=e251]:
        - slider "Activity timeline position" [ref=e253]: "980"
        - generic [ref=e254]: Scrub to review this session; physical controls pause during review.
      - generic [ref=e255]:
        - text: Speed
        - combobox "Playback speed" [ref=e256]:
          - option "0.25×"
          - option "0.5×"
          - option "1×" [selected]
          - option "1.5×"
          - option "2×"
      - generic [ref=e257]:
        - button "Reset" [ref=e258] [cursor=pointer]
        - button "Clear" [ref=e259] [cursor=pointer]
    - generic [ref=e260]:
      - generic [ref=e261]:
        - 'generic "Visual system: illustrative intensity" [ref=e262]':
          - generic [ref=e263]: V
          - meter "Visual system intensity" [ref=e264]
        - 'generic "Gustatory / taste system: illustrative intensity" [ref=e265]':
          - generic [ref=e266]: T
          - meter "Gustatory / taste system intensity" [ref=e267]
        - 'generic "Motor / descending system: illustrative intensity" [ref=e268]':
          - generic [ref=e269]: M
          - meter "Motor / descending system intensity" [ref=e270]
        - 'generic "Mating / courtship system: illustrative intensity" [ref=e271]':
          - generic [ref=e272]: C
          - meter "Mating / courtship system intensity" [ref=e273]
        - 'generic "Central integration / other: illustrative intensity" [ref=e274]':
          - generic [ref=e275]: I
          - meter "Central integration / other intensity" [ref=e276]
      - generic [ref=e277]: Normalized display intensity [0, 1] · never a firing rate
    - generic [ref=e279]: CAMERA:WORLD_FOLLOW / PRESS · USER_DRIVEN_ILLUSTRATION
  - generic [ref=e280]:
    - generic [ref=e281]: FLYWORLD / v0.3.0
    - button "Scientific boundaries ↗" [ref=e282] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { mkdir, readFile } from 'node:fs/promises';
  3  | 
  4  | test.beforeEach(async ({ page }) => {
  5  |   await page.goto('/');
  6  |   await page.getByRole('button', { name: 'MaleCNS data', exact: true }).click();
  7  |   // Surface a load rejection immediately instead of timing out on a missing badge.
  8  |   const label = page.getByTestId('real-scientific-label');
  9  |   const rejection = page.locator('.real-workspace [role="alert"]');
  10 |   await expect(label.or(rejection)).toBeVisible({ timeout: 15000 });
  11 |   expect(await rejection.allTextContents(), 'The bundled catalog/package must load without a rejection').toEqual([]);
  12 |   await expect(label).toHaveText('RAW_STRUCTURAL');
  13 | });
  14 | 
  15 | test('source package, raw body metadata, filtering and saved paths', async ({ page }) => {
  16 |   await expect(page.getByTestId('dataset-panel')).toContainText('4b2087c0fbe046bfaf0d60bc970e3e5d');
  17 |   await page.getByLabel('Inspect real body').selectOption('957530');
  18 |   await expect(page.getByTestId('real-inspector')).toContainText('M003');
  19 |   await expect(page.getByTestId('real-inspector')).toContainText('ANATOMY UNAVAILABLE FOR THIS BODY');
  20 |   await page.getByRole('button', { name: 'One hop', exact: true }).click();
  21 |   await expect(page.locator('.path-controls')).toContainText('ONE_HOP');
  22 |   await page.getByLabel('Body side filter').selectOption('L');
  23 |   await page.getByRole('button', { name: 'Reset filters', exact: true }).click();
  24 |   await page.getByLabel('Scientific package').selectOption('malecns-paper');
  25 |   await expect(page.getByTestId('real-scientific-label')).toHaveText('PAPER_ASSOCIATED');
  26 |   await page.getByLabel('Saved package path number').fill('1');
  27 |   await page.getByRole('button', { name: 'Isolate saved path', exact: true }).click();
  28 |   await expect(page.locator('.path-controls')).toContainText('PATH');
  29 |   await page.getByRole('button', { name: 'Raw edges', exact: true }).click();
  30 |   await expect(page.locator('.raw-table tbody tr')).toHaveCount(3);
  31 |   await mkdir('docs/previews', { recursive: true });
  32 |   await page.screenshot({ path: 'docs/previews/realdata-package.png', fullPage: true });
  33 | });
  34 | 
  35 | test('candidate independence, blocked selection, local loader guards and educational mapping', async ({ page }) => {
  36 |   await page.getByLabel('Scientific package').selectOption('malecns-candidates');
  37 |   await expect(page.getByTestId('real-scientific-label')).toHaveText('CANDIDATE');
  38 |   await expect(page.locator('.population-grid')).toContainText('GNG232');
  39 |   await expect(page.getByTestId('dataset-panel')).toContainText('12 / 0');
  40 |   await page.getByLabel('Scientific package').selectOption('malecns-sugar-selected');
  41 |   await expect(page.getByText('VALIDATED SUGAR SELECTION UNAVAILABLE', { exact: true })).toBeVisible();
  42 |   const bad = JSON.parse(await readFile('public/data/malecns/malecns-motors.json', 'utf8'));
  43 |   bad.dataset.uuid = '0'.repeat(32);
  44 |   await page.getByLabel('Import real circuit package').setInputFiles({ name: 'wrong-dataset.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(bad)) });
  45 |   await expect(page.getByRole('alert').filter({ hasText: 'Rejected:' })).toContainText('Incompatible dataset');
  46 |   await page.getByLabel('Import real circuit package').setInputFiles('public/data/malecns/malecns-motors.json');
  47 |   await expect(page.getByTestId('dataset-panel')).toContainText('Custom file: schema valid');
  48 |   await page.getByRole('button', { name: 'Illustrate feeding', exact: true }).click();
  49 |   await expect(page.getByTestId('real-highlight-source')).toContainText('USER_DRIVEN_ILLUSTRATION');
  50 |   await expect(page.getByTestId('real-highlight-source')).toContainText('10 mapped bodies');
  51 |   await page.getByRole('button', { name: 'EDUCATIONAL RULE', exact: true }).click();
  52 |   await expect(page.getByTestId('real-highlight-source')).toHaveCount(0);
  53 | });
  54 | 
  55 | test('geometry provenance, absent anatomy, region context and narrow layout', async ({ page }) => {
  56 |   await expect(page.getByRole('button', { name: 'Morphology', exact: true })).toBeDisabled();
  57 |   await page.getByRole('button', { name: 'Region context', exact: true }).click();
  58 |   await expect(page.locator('.region-context')).toContainText('No verified body-to-region assignment');
  59 |   await page.getByLabel('Scientific package').selectOption('malecns-anatomy');
  60 |   await expect(page.getByTestId('real-scientific-label')).toHaveText('ANATOMY_ONLY');
  61 |   await expect(page.getByRole('button', { name: 'Morphology', exact: true })).toBeEnabled();
  62 |   await expect(page.locator('.morphology-view')).toContainText('SOURCE-BACKED NATIVE SWC', { timeout: 30000 });
  63 |   await expect(page.locator('.morphology-view')).toContainText('orientation UNVERIFIED');
  64 |   await page.setViewportSize({ width: 390, height: 844 });
> 65 |   expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
     |                                                                                                ^ Error: expect(received).toBe(expected) // Object.is equality
  66 |   await mkdir('docs/previews', { recursive: true });
  67 |   await page.screenshot({ path: 'docs/previews/realdata-anatomy.png', fullPage: true });
  68 | });
  69 | 
```