# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: controls.spec.ts >> 13-step controls acceptance sequence with captured movement evidence
- Location: tests/e2e/controls.spec.ts:22:1

# Error details

```
Test timeout of 75000ms exceeded.
```

```
Error: keyboard.up: Target page, context or browser has been closed
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
      - button "Performance" [pressed] [ref=e39] [cursor=pointer]
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
          - generic: /
          - generic: Brain
          - generic: BRAIN_INSPECTION
        - generic: "CONTROL MODE: USER"
      - generic:
        - text: LAYERED EDUCATIONAL BRAIN
        - paragraph: Five teaching categories · 13 generic demo nodes
        - generic: "COLLISION HANDLING: GAME PHYSICS"
      - generic "Performance overlay" [ref=e46]:
        - strong [ref=e47]: MOVEMENT · GAME UNITS
        - generic [ref=e48]:
          - term [ref=e49]: Pressed keys
          - definition [ref=e50]: None
          - term [ref=e51]: Movement pad
          - definition [ref=e52]: None
          - term [ref=e53]: Position X / Y / Z
          - definition [ref=e54]: "-1.32 / 0.00 / 3.96"
          - term [ref=e55]: Heading / yaw
          - definition [ref=e56]: 374.3°
          - term [ref=e57]: Forward speed
          - definition [ref=e58]: 0.000 units/s
          - term [ref=e59]: Turn speed
          - definition [ref=e60]: 0.000 rad/s
          - term [ref=e61]: Movement state
          - definition [ref=e62]: BRAIN_INSPECTION_PAUSED
          - term [ref=e63]: Avatar gesture
          - definition [ref=e64]: IDLE
          - term [ref=e65]: Collision
          - definition [ref=e66]: CLEAR
          - term [ref=e67]: Controls
          - definition [ref=e68]: INACTIVE
          - term [ref=e69]: Focus target
          - definition [ref=e70]: button
          - term [ref=e71]: Camera
          - definition [ref=e72]: BRAIN_INSPECTION
          - term [ref=e73]: Brain target
          - definition [ref=e74]: Whole brain
          - term [ref=e75]: Control mode
          - definition [ref=e76]: USER_CONTROL
        - strong [ref=e77]: LIVE RENDER METRICS
        - generic [ref=e78]:
          - term [ref=e79]: FPS
          - definition [ref=e80]: "20"
          - term [ref=e81]: Visible meshes
          - definition [ref=e82]: "19"
          - term [ref=e83]: Draw calls
          - definition [ref=e84]: "19"
          - term [ref=e85]: Active highlights
          - definition [ref=e86]: "0"
        - generic [ref=e87]:
          - text: "Motion: 100 ms sample, measured after collision."
          - text: "Render: 1 s sample · instances count as one mesh."
          - text: Controls badge describes viewport keyboard focus; the movement pad works separately.
      - generic:
        - generic:
          - generic "Hold to move" [ref=e88]:
            - button "Move forward" [disabled] [ref=e89]: W
            - button "Turn left" [disabled] [ref=e90]: A
            - button "Move backward" [disabled] [ref=e91]: S
            - button "Turn right" [disabled] [ref=e92]: D
          - generic:
            - text: Orbit to look closer
            - generic: Drag to orbit · scroll to zoom
        - generic "Camera controls" [ref=e93]:
          - button "Follow" [ref=e94] [cursor=pointer]
          - button "Orbit" [ref=e95] [cursor=pointer]
          - button "Fly" [ref=e96] [cursor=pointer]
          - button "Brain" [active] [pressed] [ref=e97] [cursor=pointer]
      - generic [ref=e98]:
        - button "← Back to world ESC" [ref=e99] [cursor=pointer]
        - button "Whole brain" [ref=e100] [cursor=pointer]
      - generic [ref=e101]:
        - generic [ref=e102]: PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA
        - generic [ref=e103]: WEBGL · READY
      - generic [ref=e104]:
        - generic [ref=e105]: X -1.32 · Z 3.96
        - generic [ref=e106]: 374°
        - generic [ref=e107]: BRAIN_INSPECTION_PAUSED
        - generic [ref=e108]: CLEAR
    - complementary "Inspector" [ref=e109]:
      - generic [ref=e110]:
        - generic [ref=e111]: INSPECTOR / EDUCATIONAL
        - img [ref=e112]
      - generic [ref=e115]:
        - generic [ref=e116]: "02"
        - generic [ref=e117]:
          - heading "Drosophila avatar" [level=2] [ref=e118]
          - paragraph [ref=e119]: PROCEDURAL PLACEHOLDER AVATAR
      - generic [ref=e122]:
        - strong [ref=e123]: No anatomical data loaded
        - paragraph [ref=e124]: Systems and nodes are teaching categories. Shapes, placement, and relations are arbitrary.
      - generic [ref=e125]:
        - generic [ref=e126] [cursor=pointer]:
          - generic [ref=e127]:
            - text: Transparent head
            - generic [ref=e128]: Reveal the educational brain
          - switch "Transparent head" [ref=e129]
        - generic [ref=e130]:
          - button "Inspect fly" [ref=e131] [cursor=pointer]
          - button "Reset brain view" [ref=e132] [cursor=pointer]
      - generic [ref=e133]:
        - generic [ref=e134]:
          - heading "Brain layers" [level=3] [ref=e135]
          - generic [ref=e136]: 5 SYSTEMS
        - paragraph [ref=e137]: Select a system or node. Use the checkbox to hide a layer.
        - generic [ref=e138]:
          - generic [ref=e139]:
            - generic [ref=e140]:
              - checkbox "Show Visual system" [checked] [ref=e141]
              - button "V Visual system" [ref=e142] [cursor=pointer]:
                - generic [ref=e143]: V
                - text: Visual system
            - generic [ref=e144]:
              - text: Opacity
              - slider "Visual system opacity" [ref=e145]: "26"
              - generic [ref=e146]: 26%
            - group [ref=e147]:
              - generic "2 generic demo nodes" [ref=e148] [cursor=pointer]
          - generic [ref=e149]:
            - generic [ref=e150]:
              - checkbox "Show Gustatory / taste system" [checked] [ref=e151]
              - button "T Gustatory / taste system" [ref=e152] [cursor=pointer]:
                - generic [ref=e153]: T
                - text: Gustatory / taste system
            - generic [ref=e154]:
              - text: Opacity
              - slider "Gustatory / taste system opacity" [ref=e155]: "26"
              - generic [ref=e156]: 26%
            - group [ref=e157]:
              - generic "2 generic demo nodes" [ref=e158] [cursor=pointer]
          - generic [ref=e159]:
            - generic [ref=e160]:
              - checkbox "Show Motor / descending system" [checked] [ref=e161]
              - button "M Motor / descending system" [ref=e162] [cursor=pointer]:
                - generic [ref=e163]: M
                - text: Motor / descending system
            - generic [ref=e164]:
              - text: Opacity
              - slider "Motor / descending system opacity" [ref=e165]: "26"
              - generic [ref=e166]: 26%
            - group [ref=e167]:
              - generic "4 generic demo nodes" [ref=e168] [cursor=pointer]
          - generic [ref=e169]:
            - generic [ref=e170]:
              - checkbox "Show Mating / courtship system" [checked] [ref=e171]
              - button "C Mating / courtship system" [ref=e172] [cursor=pointer]:
                - generic [ref=e173]: C
                - text: Mating / courtship system
            - generic [ref=e174]:
              - text: Opacity
              - slider "Mating / courtship system opacity" [ref=e175]: "26"
              - generic [ref=e176]: 26%
            - group [ref=e177]:
              - generic "2 generic demo nodes" [ref=e178] [cursor=pointer]
          - generic [ref=e179]:
            - generic [ref=e180]:
              - checkbox "Show Central integration / other" [checked] [ref=e181]
              - button "I Central integration / other" [ref=e182] [cursor=pointer]:
                - generic [ref=e183]: I
                - text: Central integration / other
            - generic [ref=e184]:
              - text: Opacity
              - slider "Central integration / other opacity" [ref=e185]: "26"
              - generic [ref=e186]: 26%
            - group [ref=e187]:
              - generic "3 generic demo nodes" [ref=e188] [cursor=pointer]
      - generic [ref=e189]:
        - generic [ref=e190]:
          - heading "Latest display event" [level=3] [ref=e191]
          - generic [ref=e192]: PROVENANCE
        - generic [ref=e193]: USER_DRIVEN_ILLUSTRATION
        - paragraph [ref=e194]: TURN LEFT
      - generic [ref=e197]:
        - text: 13 generic nodes · 0 biological records
        - generic [ref=e198]: PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA
  - region "Activity and behavior controls" [ref=e199]:
    - generic [ref=e200]:
      - generic [ref=e201]: BEHAVIORS
      - generic [ref=e202]:
        - button "Take offSPACE" [disabled] [ref=e203]
        - button "FeedF" [disabled] [ref=e204]
        - button "GroomG" [disabled] [ref=e205]
        - button "Escape animationE" [disabled] [ref=e206]
        - button "CourtshipC" [disabled] [ref=e207]
        - button "StopX" [disabled] [ref=e208]
      - generic [ref=e209]: Explicit gesture commands
    - generic [ref=e210]:
      - button "Pause activity timeline" [ref=e211] [cursor=pointer]: Ⅱ
      - generic [ref=e212]:
        - generic [ref=e213]: SESSION RECORDING
        - strong [ref=e214]:
          - text: "48.1"
          - generic [ref=e215]: / 48.1 s
      - generic [ref=e216]:
        - slider "Activity timeline position" [ref=e229]: "48080"
        - generic [ref=e230]: Scrub to review this session; physical controls pause during review.
      - generic [ref=e231]:
        - text: Speed
        - combobox "Playback speed" [ref=e232]:
          - option "0.25×"
          - option "0.5×"
          - option "1×" [selected]
          - option "1.5×"
          - option "2×"
      - generic [ref=e233]:
        - button "Reset" [ref=e234] [cursor=pointer]
        - button "Clear" [ref=e235] [cursor=pointer]
    - generic [ref=e236]:
      - generic [ref=e237]:
        - 'generic "Visual system: illustrative intensity" [ref=e238]':
          - generic [ref=e239]: V
          - meter "Visual system intensity" [ref=e240]
        - 'generic "Gustatory / taste system: illustrative intensity" [ref=e241]':
          - generic [ref=e242]: T
          - meter "Gustatory / taste system intensity" [ref=e243]
        - 'generic "Motor / descending system: illustrative intensity" [ref=e244]':
          - generic [ref=e245]: M
          - meter "Motor / descending system intensity" [ref=e246]
        - 'generic "Mating / courtship system: illustrative intensity" [ref=e247]':
          - generic [ref=e248]: C
          - meter "Mating / courtship system intensity" [ref=e249]
        - 'generic "Central integration / other: illustrative intensity" [ref=e250]':
          - generic [ref=e251]: I
          - meter "Central integration / other intensity" [ref=e252]
      - generic [ref=e253]: Normalized display intensity [0, 1] · never a firing rate
    - generic [ref=e254]:
      - generic [ref=e255]: CAMERA:BRAIN_INSPECTION / PRESS · USER_DRIVEN_ILLUSTRATION
      - generic [ref=e256]: 11 / 120 events · original provenance retained
  - generic [ref=e257]:
    - generic [ref=e258]: FLYWORLD / v0.3.0
    - generic [ref=e259]: Explore the interface. Keep the evidence visible.
    - button "Scientific boundaries ↗" [ref=e260] [cursor=pointer]
```

# Test source

```ts
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
  112 |       expect(distance(await pose(page), before)).toBeGreaterThan(0.3);
  113 |       await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS ACTIVE');
  114 |       await page.screenshot({ path: 'docs/previews/controls-return.png', fullPage: true });
  115 |     });
  116 |     expect(errors).toEqual([]);
  117 |   } finally {
> 118 |     await page.keyboard.up('w'); await page.keyboard.up('a');
      |                         ^ Error: keyboard.up: Target page, context or browser has been closed
  119 |     await page.keyboard.up('ArrowUp'); await page.keyboard.up('ArrowRight');
  120 |     await writeFile('docs/validation/prompt03a/browser-acceptance.json', JSON.stringify({
  121 |       kind: 'AUTOMATED_BROWSER_SEQUENCE', humanVisualReview: 'PENDING', results, pageErrors: errors,
  122 |     }, null, 2) + '\n');
  123 |   }
  124 | });
  125 | 
  126 | test('focus, typing, pointer movement, and all camera modes', async ({ page }) => {
  127 |   await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
  128 |   const before = await pose(page);
  129 |   await hold(page, 'w', 250); expect(await pose(page)).toEqual(before);
  130 |   await activate(page); await page.keyboard.down('w');
  131 |   await expect.poll(async () => (await pose(page)).z).toBeGreaterThan(before.z + 0.1);
  132 |   // Exercise a real editable DOM target without adding a product form for this test.
  133 |   await page.evaluate(() => {
  134 |     const field = document.createElement('input');
  135 |     field.setAttribute('aria-label', 'Focus test input'); document.body.append(field); field.focus();
  136 |   });
  137 |   await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
  138 |   await page.keyboard.up('w'); await page.waitForTimeout(150);
  139 |   const typing = await pose(page);
  140 |   await page.getByLabel('Focus test input').pressSequentially('wasd');
  141 |   expect(await page.getByLabel('Focus test input').inputValue()).toBe('wasd');
  142 |   await hold(page, 'ArrowUp', 250); expect(await pose(page)).toEqual(typing);
  143 |   await page.getByLabel('Focus test input').evaluate(field => field.remove());
  144 |   await activate(page);
  145 |   const forward = page.getByRole('button', { name: 'Move forward', exact: true });
  146 |   const rect = (await forward.boundingBox())!;
  147 |   await page.mouse.move(rect.x + rect.width / 2, rect.y + rect.height / 2);
  148 |   await page.mouse.down(); await page.waitForTimeout(400); await page.mouse.up();
  149 |   await expect.poll(async () => (await pose(page)).z).toBeGreaterThan(typing.z + 0.1);
  150 |   for (const [name, mode, paused] of [
  151 |     ['Orbit', 'WORLD_ORBIT', false], ['Fly', 'FLY_INSPECTION', true],
  152 |     ['Brain', 'BRAIN_INSPECTION', true], ['Follow', 'WORLD_FOLLOW', false],
  153 |   ] as const) {
  154 |     await page.getByRole('button', { name, exact: true }).click();
  155 |     await expect(page.getByTestId('camera-mode')).toHaveText(mode);
  156 |     await activate(page); await page.waitForTimeout(150); const start = await pose(page);
  157 |     await hold(page, 'w', 300); const end = await pose(page);
  158 |     if (paused) expect(end).toEqual(start); else expect(distance(end, start)).toBeGreaterThan(0.1);
  159 |   }
  160 |   await activate(page); await page.keyboard.down('w');
  161 |   await page.getByRole('button', { name: 'MaleCNS data', exact: true }).click();
  162 |   await page.keyboard.up('w'); await hold(page, 'w', 300);
  163 |   await page.getByRole('button', { name: 'Explore', exact: true }).click();
  164 |   await expect(page.getByTestId('controls-active')).toHaveText('CONTROLS INACTIVE');
  165 |   const back = await pose(page); await hold(page, 'w', 300); expect(await pose(page)).toEqual(back);
  166 | });
  167 | 
```