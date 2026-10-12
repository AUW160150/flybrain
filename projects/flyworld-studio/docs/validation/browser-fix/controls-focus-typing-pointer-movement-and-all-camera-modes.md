# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: controls.spec.ts >> focus, typing, pointer movement, and all camera modes
- Location: tests/e2e/controls.spec.ts:126:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('[data-world-viewport]')
    - locator resolved to <div tabindex="0" class="viewport" data-world-viewport="true" aria-label="3D viewport. Click to focus keyboard controls. Tab inspects the brain. Escape returns to the world.">…</div>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <button>…</button> from <div class="brain-navigation">…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <button>…</button> from <div class="brain-navigation">…</div> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    43 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <button>…</button> from <div class="brain-navigation">…</div> subtree intercepts pointer events
     - retrying click action
       - waiting 500ms

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
      - button "Experiments LATER" [ref=e16] [cursor=pointer]
    - generic [ref=e17]:
      - generic [ref=e18]: LOCAL WORKSPACE
      - button "Controls and help" [ref=e20] [cursor=pointer]: "?"
  - generic [ref=e21]:
    - generic [ref=e22]:
      - generic [ref=e23]: EXPLORATION STUDIO / DATA INTEGRATION 03
      - heading "A small world. A closer look." [level=1] [ref=e24]
    - button "EDUCATIONAL + STRUCTURAL Explicit sources · no neural dynamics ↗" [ref=e25] [cursor=pointer]:
      - generic [ref=e27]:
        - text: EDUCATIONAL + STRUCTURAL
        - generic [ref=e28]: Explicit sources · no neural dynamics
      - generic [ref=e29]: ↗
  - generic [ref=e30]:
    - generic "Exploration modes" [ref=e31]:
      - button "USER CONTROL" [pressed] [ref=e32] [cursor=pointer]
      - button "EDUCATIONAL RULE" [ref=e33] [cursor=pointer]
      - button "DATA REPLAY" [ref=e34] [cursor=pointer]
    - generic [ref=e35]: SIMULATION UNAVAILABLE
    - generic [ref=e36]:
      - generic [ref=e37] [cursor=pointer]:
        - checkbox "Reduced motion" [ref=e38]
        - text: Reduced motion
      - button "Performance" [ref=e39] [cursor=pointer]
  - generic [ref=e40]:
    - region "World workspace" [ref=e41]:
      - generic "3D viewport. Click to focus keyboard controls. Tab inspects the brain. Escape returns to the world." [ref=e42]:
        - generic "Procedural placeholder fly in a 3D world" [ref=e43]
      - generic:
        - strong: CONTROLS INACTIVE
        - generic: Inspection pauses locomotion
        - generic: USER_DRIVEN_ILLUSTRATION
      - generic:
        - generic "Current camera mode":
          - generic: World
          - generic: /
          - generic: Fly
          - generic: FLY_INSPECTION
        - generic: "CONTROL MODE: USER"
      - generic:
        - text: GARDEN / 001
        - paragraph: Tree obstacle · flower / food marker · neutral landmark
        - generic: "COLLISION HANDLING: GAME PHYSICS"
      - generic:
        - generic:
          - generic "Hold to move" [ref=e46]:
            - button "Move forward" [disabled] [ref=e47]: W
            - button "Turn left" [disabled] [ref=e48]: A
            - button "Move backward" [disabled] [ref=e49]: S
            - button "Turn right" [disabled] [ref=e50]: D
          - generic:
            - text: Orbit to look closer
            - generic: Drag to orbit · scroll to zoom
        - generic "Camera controls" [ref=e51]:
          - button "Follow" [ref=e52] [cursor=pointer]
          - button "Orbit" [ref=e53] [cursor=pointer]
          - button "Fly" [active] [pressed] [ref=e54] [cursor=pointer]
          - button "Brain" [ref=e55] [cursor=pointer]
      - button "← Back to world ESC" [ref=e57] [cursor=pointer]
      - generic [ref=e58]:
        - generic [ref=e59]: PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA
        - generic [ref=e60]: WEBGL · READY
      - generic [ref=e61]:
        - generic [ref=e62]: X 0.00 · Z 1.64
        - generic [ref=e63]: 0°
        - generic [ref=e64]: FLY_INSPECTION_PAUSED
        - generic [ref=e65]: CLEAR
    - complementary "Inspector" [ref=e66]:
      - generic [ref=e67]:
        - generic [ref=e68]: INSPECTOR / EDUCATIONAL
        - img [ref=e69]
      - generic [ref=e72]:
        - generic [ref=e73]: "02"
        - generic [ref=e74]:
          - heading "Drosophila avatar" [level=2] [ref=e75]
          - paragraph [ref=e76]: PROCEDURAL PLACEHOLDER AVATAR
      - generic [ref=e79]:
        - strong [ref=e80]: No anatomical data loaded
        - paragraph [ref=e81]: Systems and nodes are teaching categories. Shapes, placement, and relations are arbitrary.
      - generic [ref=e82]:
        - generic [ref=e83] [cursor=pointer]:
          - generic [ref=e84]:
            - text: Transparent head
            - generic [ref=e85]: Reveal the educational brain
          - switch "Transparent head" [ref=e86]
        - generic [ref=e87]:
          - button "Inspect brain" [ref=e88] [cursor=pointer]
          - button "Reset brain view" [ref=e89] [cursor=pointer]
      - generic [ref=e90]:
        - generic [ref=e91]:
          - heading "Brain layers" [level=3] [ref=e92]
          - generic [ref=e93]: 5 SYSTEMS
        - paragraph [ref=e94]: Select a system or node. Use the checkbox to hide a layer.
        - generic [ref=e95]:
          - generic [ref=e96]:
            - generic [ref=e97]:
              - checkbox "Show Visual system" [checked] [ref=e98]
              - button "V Visual system" [ref=e99] [cursor=pointer]:
                - generic [ref=e100]: V
                - text: Visual system
            - generic [ref=e101]:
              - text: Opacity
              - slider "Visual system opacity" [ref=e102]: "26"
              - generic [ref=e103]: 26%
            - group [ref=e104]:
              - generic "2 generic demo nodes" [ref=e105] [cursor=pointer]
          - generic [ref=e106]:
            - generic [ref=e107]:
              - checkbox "Show Gustatory / taste system" [checked] [ref=e108]
              - button "T Gustatory / taste system" [ref=e109] [cursor=pointer]:
                - generic [ref=e110]: T
                - text: Gustatory / taste system
            - generic [ref=e111]:
              - text: Opacity
              - slider "Gustatory / taste system opacity" [ref=e112]: "26"
              - generic [ref=e113]: 26%
            - group [ref=e114]:
              - generic "2 generic demo nodes" [ref=e115] [cursor=pointer]
          - generic [ref=e116]:
            - generic [ref=e117]:
              - checkbox "Show Motor / descending system" [checked] [ref=e118]
              - button "M Motor / descending system" [ref=e119] [cursor=pointer]:
                - generic [ref=e120]: M
                - text: Motor / descending system
            - generic [ref=e121]:
              - text: Opacity
              - slider "Motor / descending system opacity" [ref=e122]: "26"
              - generic [ref=e123]: 26%
            - group [ref=e124]:
              - generic "4 generic demo nodes" [ref=e125] [cursor=pointer]
          - generic [ref=e126]:
            - generic [ref=e127]:
              - checkbox "Show Mating / courtship system" [checked] [ref=e128]
              - button "C Mating / courtship system" [ref=e129] [cursor=pointer]:
                - generic [ref=e130]: C
                - text: Mating / courtship system
            - generic [ref=e131]:
              - text: Opacity
              - slider "Mating / courtship system opacity" [ref=e132]: "26"
              - generic [ref=e133]: 26%
            - group [ref=e134]:
              - generic "2 generic demo nodes" [ref=e135] [cursor=pointer]
          - generic [ref=e136]:
            - generic [ref=e137]:
              - checkbox "Show Central integration / other" [checked] [ref=e138]
              - button "I Central integration / other" [ref=e139] [cursor=pointer]:
                - generic [ref=e140]: I
                - text: Central integration / other
            - generic [ref=e141]:
              - text: Opacity
              - slider "Central integration / other opacity" [ref=e142]: "26"
              - generic [ref=e143]: 26%
            - group [ref=e144]:
              - generic "3 generic demo nodes" [ref=e145] [cursor=pointer]
      - generic [ref=e146]:
        - generic [ref=e147]:
          - heading "Latest display event" [level=3] [ref=e148]
          - generic [ref=e149]: PROVENANCE
        - generic [ref=e150]: USER_DRIVEN_ILLUSTRATION
        - paragraph [ref=e151]: WALK
      - generic [ref=e154]:
        - text: 13 generic nodes · 0 biological records
        - generic [ref=e155]: PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA
  - region "Activity and behavior controls" [ref=e156]:
    - generic [ref=e157]:
      - generic [ref=e158]: BEHAVIORS
      - generic [ref=e159]:
        - button "Take offSPACE" [disabled] [ref=e160]
        - button "FeedF" [disabled] [ref=e161]
        - button "GroomG" [disabled] [ref=e162]
        - button "Escape animationE" [disabled] [ref=e163]
        - button "CourtshipC" [disabled] [ref=e164]
        - button "StopX" [disabled] [ref=e165]
      - generic [ref=e166]: Explicit gesture commands
    - generic [ref=e167]:
      - button "Pause activity timeline" [ref=e168] [cursor=pointer]: Ⅱ
      - generic [ref=e169]:
        - generic [ref=e170]: SESSION RECORDING
        - strong [ref=e171]:
          - text: "26.1"
          - generic [ref=e172]: / 26.1 s
      - generic [ref=e173]:
        - slider "Activity timeline position" [ref=e178]: "26060"
        - generic [ref=e179]: Scrub to review this session; physical controls pause during review.
      - generic [ref=e180]:
        - text: Speed
        - combobox "Playback speed" [ref=e181]:
          - option "0.25×"
          - option "0.5×"
          - option "1×" [selected]
          - option "1.5×"
          - option "2×"
      - generic [ref=e182]:
        - button "Reset" [ref=e183] [cursor=pointer]
        - button "Clear" [ref=e184] [cursor=pointer]
    - generic [ref=e185]:
      - generic [ref=e186]:
        - 'generic "Visual system: illustrative intensity" [ref=e187]':
          - generic [ref=e188]: V
          - meter "Visual system intensity" [ref=e189]
        - 'generic "Gustatory / taste system: illustrative intensity" [ref=e190]':
          - generic [ref=e191]: T
          - meter "Gustatory / taste system intensity" [ref=e192]
        - 'generic "Motor / descending system: illustrative intensity" [ref=e193]':
          - generic [ref=e194]: M
          - meter "Motor / descending system intensity" [ref=e195]
        - 'generic "Mating / courtship system: illustrative intensity" [ref=e196]':
          - generic [ref=e197]: C
          - meter "Mating / courtship system intensity" [ref=e198]
        - 'generic "Central integration / other: illustrative intensity" [ref=e199]':
          - generic [ref=e200]: I
          - meter "Central integration / other intensity" [ref=e201]
      - generic [ref=e202]: Normalized display intensity [0, 1] · never a firing rate
    - generic [ref=e203]:
      - generic [ref=e204]: CAMERA:FLY_INSPECTION / PRESS · USER_DRIVEN_ILLUSTRATION
      - generic [ref=e205]: 3 / 120 events · original provenance retained
  - generic [ref=e206]:
    - generic [ref=e207]: FLYWORLD / v0.3.0
    - generic [ref=e208]: Explore the interface. Keep the evidence visible.
    - button "Scientific boundaries ↗" [ref=e209] [cursor=pointer]
```

# Test source

```ts
  1   | import { test, expect, type Page } from '@playwright/test';
  2   | import { mkdir, writeFile } from 'node:fs/promises';
  3   | import { obstacles, FLY_RADIUS } from '../../src/world/collision';
  4   | 
  5   | async function pose(page: Page) {
  6   |   const p = page.getByTestId('fly-position');
  7   |   return { x: Number(await p.getAttribute('data-x')), y: Number(await p.getAttribute('data-y')), z: Number(await p.getAttribute('data-z')), yaw: Number(await page.getByTestId('fly-heading').getAttribute('data-yaw')) };
  8   | }
  9   | const distance = (a: { x: number; z: number }, b: { x: number; z: number }) => Math.hypot(a.x - b.x, a.z - b.z);
  10  | async function activate(page: Page) {
> 11  |   await page.locator('[data-world-viewport]').click({ position: { x: 35, y: 200 } });
      |                                               ^ Error: locator.click: Test timeout of 30000ms exceeded.
  12  | }
  13  | async function hold(page: Page, code: string, ms: number) {
  14  |   await page.keyboard.down(code); await page.waitForTimeout(ms); await page.keyboard.up(code); await page.waitForTimeout(150);
  15  | }
  16  | 
  17  | test.beforeEach(async ({ page }) => {
  18  |   await page.goto('/');
  19  |   await expect(page.getByTestId('renderer-status')).toHaveText('WEBGL · READY', { timeout: 30000 });
  20  | });
  21  | 
  22  | test('13-step controls acceptance sequence with captured movement evidence', async ({ page }) => {
  23  |   test.setTimeout(75000);
  24  |   const results: object[] = [];
  25  |   const errors: string[] = [];
  26  |   page.on('pageerror', error => errors.push(error.message));
  27  |   await mkdir('docs/validation/prompt03a', { recursive: true });
  28  |   await mkdir('docs/previews', { recursive: true });
  29  |   const step = async (name: string, run: () => Promise<void>) => {
  30  |     await test.step(name, async () => {
  31  |       try { await run(); results.push({ name, status: 'PASS', pose: await pose(page) }); }
  32  |       catch (error) { results.push({ name, status: 'FAIL', error: String(error) }); throw error; }
  33  |     });
  34  |   };
  35  |   const tree = obstacles.find(o => o.id === 'tree')!;
  36  |   let start = await pose(page), leftStart = start, rightStart = start, blocked = start, paused = start;
  37  |   try {
  38  |     await step('1. Start in Follow mode', async () => {
  39  |       await page.getByRole('button', { name: 'Follow', exact: true }).click();
  40  |       await expect(page.getByTestId('camera-mode')).toHaveText('WORLD_FOLLOW');
  41  |       await page.getByRole('button', { name: 'Performance', exact: true }).click();
  42  |     });
  43  |     await step('2. Click the 3D viewport', async () => {
  44  |       await activate(page); await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS ACTIVE');
  45  |       await expect(page.locator('[data-world-viewport]')).toBeFocused(); start = await pose(page);
  46  |     });
  47  |     await step('3. Hold W for 2 seconds', async () => {
  48  |       await page.keyboard.down('w'); await page.waitForTimeout(2000);
  49  |     });
  50  |     await step('4. Confirm advancing position; capture rendered scene', async () => {
  51  |       expect((await pose(page)).z - start.z).toBeGreaterThan(1);
  52  |       await expect(page.getByTestId('fly-state')).toHaveText('WALK_FORWARD');
  53  |       await page.screenshot({ path: 'docs/previews/controls-forward.png', fullPage: true });
  54  |     });
  55  |     await step('5. Hold A while still holding W', async () => {
  56  |       leftStart = await pose(page); await page.keyboard.down('a'); await page.waitForTimeout(600);
  57  |     });
  58  |     await step('6. Confirm curved left path', async () => {
  59  |       const end = await pose(page); expect(end.yaw - leftStart.yaw).toBeGreaterThan(0.2); expect(distance(end, leftStart)).toBeGreaterThan(0.2);
  60  |       expect(end.x - leftStart.x).toBeGreaterThan(0.1);
  61  |       await expect(page.getByTestId('fly-state')).toHaveText('WALK_TURN');
  62  |       await page.screenshot({ path: 'docs/previews/controls-left.png', fullPage: true });
  63  |       await page.keyboard.up('a'); await page.keyboard.up('w'); await page.waitForTimeout(150);
  64  |     });
  65  |     await step('7. Repeat with ArrowUp + ArrowRight', async () => {
  66  |       rightStart = await pose(page);
  67  |       const scroll = await page.evaluate(() => window.scrollY);
  68  |       await page.keyboard.down('ArrowUp'); await page.keyboard.down('ArrowRight'); await page.waitForTimeout(600);
  69  |       const end = await pose(page); expect(end.yaw).toBeGreaterThan(rightStart.yaw + 0.2); expect(distance(end, rightStart)).toBeGreaterThan(0.2);
  70  |       expect(await page.evaluate(() => window.scrollY)).toBe(scroll);
  71  |       await page.keyboard.up('ArrowRight'); await page.keyboard.up('ArrowUp'); await page.waitForTimeout(150);
  72  |     });
  73  |     await step('8. Walk into the tree', async () => {
  74  |       // Steer through public key events using observed telemetry; no pose injection.
  75  |       for (let i = 0; i < 8; i++) {
  76  |         const p = await pose(page); const angle = Math.atan2(tree.x - p.x, tree.z - p.z);
  77  |         const delta = Math.atan2(Math.sin(angle - p.yaw), Math.cos(angle - p.yaw));
  78  |         if (Math.abs(delta) < 0.08) break;
  79  |         await hold(page, delta > 0 ? 'a' : 'd', Math.min(500, Math.abs(delta) * 500));
  80  |       }
  81  |       await page.keyboard.down('w');
  82  |       await expect(page.getByTestId('fly-state')).toHaveText('COLLISION_BLOCKED', { timeout: 12000 });
  83  |     });
  84  |     await step('9. Confirm collision prevents penetration', async () => {
  85  |       blocked = await pose(page);
  86  |       expect(distance(blocked, tree)).toBeGreaterThanOrEqual(tree.radius + FLY_RADIUS - 0.001);
  87  |       expect(distance(blocked, tree)).toBeLessThan(tree.radius + FLY_RADIUS + 0.1);
  88  |       await expect(page.getByTestId('forward-speed')).toContainText('0.000');
  89  |       await page.screenshot({ path: 'docs/previews/controls-tree.png', fullPage: true });
  90  |     });
  91  |     await step('10. Turn away and move again', async () => {
  92  |       await hold(page, 'a', 1600); await page.waitForTimeout(400);
  93  |       expect(distance(await pose(page), blocked)).toBeGreaterThan(0.5);
  94  |       await expect(page.getByTestId('collision-state')).toHaveText('CLEAR');
  95  |       await page.keyboard.up('w');
  96  |     });
  97  |     await step('11. Enter Brain mode', async () => {
  98  |       await page.getByRole('button', { name: 'Brain', exact: true }).click();
  99  |       await expect(page.getByTestId('camera-mode')).toHaveText('BRAIN_INSPECTION');
  100 |       await page.waitForTimeout(200); paused = await pose(page);
  101 |     });
  102 |     await step('12. Confirm locomotion pauses', async () => {
  103 |       await activate(page); await hold(page, 'w', 500);
  104 |       expect(await pose(page)).toEqual(paused);
  105 |       await expect(page.getByTestId('fly-state')).toHaveText('BRAIN_INSPECTION_PAUSED');
  106 |       await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
  107 |       await page.screenshot({ path: 'docs/previews/controls-brain.png', fullPage: true });
  108 |     });
  109 |     await step('13. Return to Follow mode and move again', async () => {
  110 |       await page.getByRole('button', { name: 'Follow', exact: true }).click(); await activate(page);
  111 |       const before = await pose(page); await hold(page, 'w', 600);
```