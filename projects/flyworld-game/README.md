# Flybrain / flyworld

A small 3D arena where six fruit flies are driven by the MaleCNS v1.0 connectome and you drive a
bigger fly with the keyboard. Each small fly runs a real sub-circuit of the fly nervous system
(looming detectors, odour and taste neurons, and every neuron on short paths from them to the
descending neurons that walk, turn, back up, jump, groom and extend the proboscis). The fly you
select can be switched to the whole central nervous system (165,122 traced neurons).

Background reading: `DATASET_ANALYSIS.md` (the dataset), `NEURON_CHOICES.md` (what 25 other
connectome games stimulate and read out), `GATES.md` (the verified completion ledger).

## Setup (already done on this machine)

```
uv pip install --python .venv/bin/python panda3d==1.10.16 pygame-ce pytest
.venv/bin/python scripts/extract_circuits.py --verify   # builds processed/circuit_npc.npz
.venv/bin/python scripts/calibrate.py                   # writes processed/calibration.json
```

## The flies

| Fly | Role | Sex | Colour |
|---|---|---|---|
| Nick | the big fly you drive | male | white |
| Kathy | brain-driven | female | pink |
| Isshan | brain-driven | male | red |
| Parth | brain-driven | male | dark blue |
| Leyla | brain-driven | female | baby blue |
| Jack | brain-driven | male | orange |
| Rodela | brain-driven | female | yellow |

The arena is a garden: blue sky with sun, clouds and haze, a mottled lawn with flowers, trees,
bushes and rocks (the obstacles), a picket fence, and four fruit patches to eat: grapes,
watermelon, cherries and kiwi. Fruit shrinks as it is eaten. Garden dressing lives in
`flyworld/garden.py`.

Female flies are drawn larger with a pointed abdomen, males smaller with a dark rounded tip. Kathy
is drawn Jigglypuff-style: round, big eyes, ears, a curl and flapping wings. Wings flap fast
while a fly walks or jumps. Each fly carries its name above it. Profiles live in `flyworld/profiles.py`.

## Watching the neurons

The right-hand panel is live. Each fly has a row of LEDs, one per neuron group (looming cells
LC4/LPLC2/LC16/LC6/LC11, odour DM1/DA1, taste LB3c, descending neurons DNp01/DNp09/MDN/DNa02 L
and R/DNg11, motor MN9, mushroom body KC/MBON, punishment PPL1, and all descending neurons).
An LED lights in the fly's colour as that group fires, and the word beside the name says what
the body is doing (walk, back, jump, groom, eat, wander, still). "Still" is a quiet brain for
under 2 s; "wander" is the one scripted behaviour: after 2 s of brain silence the fly drifts
slowly so it does not look dead. Everything else comes from the connectome readout. Below the LEDs is a spike raster
of the selected fly: one row per group, the last 200 ms of biological time scrolling left to
right. The left column lists every group of the selected fly with its firing rate in Hz.

## Play: Shepherd mode

```
.venv/bin/python -m flyworld.game                    # 3D chase camera (panda3d)
.venv/bin/python -m flyworld.game --renderer pygame  # top-down view of the whole arena
.venv/bin/python -m flyworld.game --time-limit 300   # more time; --mode sandbox removes the goal
```

Goal: get the six flies to eat all four fruit patches (20 units of food) before the timer
(default 3 minutes) runs out. You win when the food is gone; you lose when time is up. R restarts.

You have two tools, both of which go through the flies' real connectome circuits:

1. **Loom at them.** Walk the big fly at a small fly. Its looming detectors (LC4, LPLC2, LC16)
   fire the giant fiber DNp01 and it jumps away from you. Approach from the side opposite the
   food to push it there.
2. **Drive their brains.** Select a fly (Tab), put the cursor on DNp09 and press S: it walks
   forward. DNa02 left or right makes it turn. MDN backs it up. Press S again to release.

Once a fly is within about 2 units of food, the odour (ORN_DM1 to the feeding circuit) shuts
down walking and drives the proboscis motor neuron MN9, so it stops on the patch and eats. That
"stop when you smell food" behaviour is the circuit's own, measured in calibration, not scripted.

| Key | Action |
|---|---|
| arrow keys | drive the big fly (up/down walk, left/right turn) |
| Tab / Shift-Tab | select the next / previous small fly (cyan marker) |
| [ and ] | move the cursor through the neuron groups |
| S | stimulate the group under the cursor on the selected fly (inject current) |
| X | silence that group (clamp it to rest) |
| + / - | change the stimulation amplitude |
| W | switch the selected fly to the whole-CNS brain (all 165,122 neurons) and back |
| R | restart the round |
| H | hide or show the key help |
| Esc | quit |

What to try: walk the big fly at a small fly and watch it jump away (looming cells LC4/LPLC2/LC16
fire the giant fiber DNp01). Select a fly, put the cursor on DNp09 and press S: it walks. Silence
DNa02 and it can no longer turn. Stimulate MDN: it backs up. Park a fly on food: taste (LB3c) and
odour (ORN_DM1) drive MN9 and it eats.

## Headless and scripted runs

Headless and script runs start in sandbox mode; use `mode shepherd` inside a script.

```
.venv/bin/python -m flyworld.game --headless --frames 600 --seed 0 --out runs/traj.json --assert-complete
.venv/bin/python -m flyworld.game --headless --script "focus 2; isolate; stim DNp09; run 150; assert rate DNp09 >= 50; report"
.venv/bin/python -m flyworld.game --headless --focus-whole --frames 300
.venv/bin/python scripts/behaviour_tests.py
.venv/bin/python scripts/check_render.py       # headless render check (SDL dummy driver)
.venv/bin/python -m pytest -q tests
```

Script commands: `focus N|Name`, `isolate`, `mark`, `stim G`, `unstim G`, `silence G`, `unsilence G`,
`amp X`, `whole on|off`, `mode sandbox|shepherd`, `time_limit S`, `food X`, `onfood K`,
`foodahead D`, `restart`, `run FRAMES`, `assert rate G <op> X`, `assert speed <op> X`,
`assert moved <op> X`, `assert eaten <op> X`, `assert eaten_total <op> X`,
`assert round == playing|won|lost`, `report`.

## How it works

- `flyworld/circuits.py` extracts the sub-circuit: edges with at least 5 synapses, neurons on a
  path of at most 3 hops from looming cells (or 4 from odour/taste cells) to the target descending
  neurons, optic-lobe columnar cells excluded. Result: 10,203 neurons, 401,680 edges.
- `flyworld/brain.py` is a batched leaky integrate-and-fire model (1 ms steps, tau 20 ms, 2 ms
  refractory, synapse count times transmitter sign as weight, gain 0.005). Propagation is
  event-driven: only neurons that spiked scatter their outgoing synapses each step, so cost scales
  with activity (1 to 3% of cells). Six sub-circuit brains step together at about 2,500 steps/s
  on Apple MPS at rest and about 1,500 under stimulation; the whole CNS at about 600 steps/s in
  the game loop. Both run at the same clock: 10 biological ms per 30 Hz game tick.
- `flyworld/encoders.py` turns the geometry around a fly into currents: angular expansion of an
  approaching object drives LC4/LC6, its angular size drives LPLC2/LC16, food odour decays with
  distance onto ORN_DM1/DM4/DC1, standing on food drives LB3c.
- `flyworld/decoder.py` reads DNp09 (forward), MDN (backward), DNa02/DNa01 left minus right
  (turning), DNp01 (jump), DNg11 (groom), MN9 (eat) with hysteresis and a calibrated correction
  for the walk-coupled DNa02 asymmetry the circuit produces.
- `scripts/calibrate.py` sweeps gain and amplitude and picks a point where rest is silent, DNp09
  stimulation walks without recruiting more than 50 descending neurons, and looming reaches DNp01
  within 20 ms.

Known limits: odour does not steer the flies toward food through this circuit (it drives MN9 and
suppresses walking instead), which is why the player has to bring them there. The brains run at 0.3x
biological speed relative to the wall clock (10 ms of brain per 33 ms frame). No plasticity yet.
