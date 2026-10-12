# Gates: flyworld v1

OWNS: flyworld/**, scripts/extract_circuits.py, scripts/calibrate.py, scripts/behaviour_tests.py, tests/**, runs/**, processed/circuit_npc.npz, processed/circuit_npc_groups.json, processed/groups_whole.json, processed/calibration.json, GATES.md

Scope: a panda3d arena with one keyboard-driven big fly and six connectome-driven small flies, where the focus fly runs the whole CNS and the others a batched sub-circuit, driven by looming, odour and taste, with a stimulate/silence key panel.

- [x] G0: panda3d opens an offscreen window in the venv and torch sees MPS
  CHECK: .venv/bin/python -c "from panda3d.core import loadPrcFileData; loadPrcFileData('', 'window-type offscreen'); from direct.showbase.ShowBase import ShowBase; b=ShowBase(); import torch; print('ENV OK mps', torch.backends.mps.is_available())"
  EXPECT: ENV OK mps True
  EVIDENCE: automatic-evidence=v1; definition-sha256=957b056492fff6cf20c12845f8d3511f0c03f4c92b7dbf855515f54ef6d5a07c; exit=0; EXPECT=matched; output-sha256=e4841bd119ba71b90694e21e65f88eb755d29fafe4d4d2b07da42bc7e8d995e5; output-bytes=391; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G1: the NPC sub-circuit is extracted within the planned size band and every named group is present at its expected count
  CHECK: .venv/bin/python scripts/extract_circuits.py --verify
  EXPECT: CIRCUIT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=d7a5a72eeffc85c8a34e62b7cd020127f43bf06bbeffe714dcb17bebe708e24c; exit=0; EXPECT=matched; output-sha256=a58d34690a4c5c9b5f73c04b0954f683365520f76bf5dc04a6bcfa6ae9c0978b; output-bytes=380; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G1b: the unit tests for groups, brain, encoders, decoder and world pass on CPU
  CHECK: .venv/bin/python -m pytest -q tests
  EXPECT: /^\d+ passed in/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=6cefc3a646c57bd411f92a74d445108e11bf05ec2293ee317a0cffd8b77ba159; exit=0; EXPECT=matched; output-sha256=8a172545199d60658b51895fbdbeae88d963398daceba8e03f3b7b88ecd83a66; output-bytes=99; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G2: six batched sub-circuit brains run at or above 600 steps/s and are silent at rest
  CHECK: .venv/bin/python -m flyworld.brain --bench --B 6 --steps 1000 --min-steps-per-s 600 --max-rest-dn-hz 1 --max-activity 0.01
  EXPECT: BENCH OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=c28e797ac6a796c0aaa458df0955bfe08def33ebe6abb50077a76b0711b93250; exit=0; EXPECT=matched; output-sha256=d6bdbe4df2b77c1a60ca66d3cabf0f823cd85aa1eeefddff5cc6bf5b2a48ad5d; output-bytes=285; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G3: calibration finds a gain and amplitude where rest is quiet, DNp09 stimulation walks, looming reaches DNp01 within 20 ms, and right-only looming is lateralized
  CHECK: .venv/bin/python scripts/calibrate.py
  EXPECT: CALIBRATION OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=a0d0c90af04870fbc3eadba1c67dffdcaea9de03a52c3eeb7e3575861d87517d; exit=0; EXPECT=matched; output-sha256=bfa9ee84917ef99f31ef46e581d92df2e2ce7775f1cbb7fcaa3d26dd4d4c6649; output-bytes=2945; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G4: the headless game runs 600 frames with seven flies and writes a complete trajectory
  CHECK: .venv/bin/python -m flyworld.game --headless --frames 600 --seed 0 --out runs/traj.json --assert-complete
  EXPECT: GAME OK 600 frames
  EVIDENCE: automatic-evidence=v1; definition-sha256=2418c053d2e0d1cae28f756f0817c77e179042b4af2c648f418a1de4c21227ad; exit=0; EXPECT=matched; output-sha256=c70c25489d2883e86810f2c837c41d9eb1e7f3b89a852b2bbc5f2155d865c67a; output-bytes=174; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G5: scripted behaviours hold: DNp09 stimulation moves a fly forward, a resting fly stays put, a big-fly approach fires DNp01 and triggers a jump
  CHECK: .venv/bin/python scripts/behaviour_tests.py
  EXPECT: BEHAVIOUR OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=c27c2369c6498ce961ddfd294ce0cc4ba984b137f2b428aa1c55f453b6ee8fb1; exit=0; EXPECT=matched; output-sha256=7c0abe4869ee623745a4c871234c6be56f5140cafb3955e9da81d5737cd693da; output-bytes=544; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G6: the rendered game reaches 25 fps and saves a non-empty screenshot
  CHECK: .venv/bin/python -m flyworld.game --frames 120 --screenshot runs/shot.png --min-fps 25
  EXPECT: RENDER OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=658e2c8abce40d80fc8c160d477b48c18d742b492e66242fb6a6ee9378bc0b32; exit=0; EXPECT=matched; output-sha256=644cb905b81c8a22b17a6447b8fe8e999b45b92c95577cb429148f027ff32006; output-bytes=240; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G7: the panel script can stimulate and silence groups on a chosen fly and the body responds
  CHECK: .venv/bin/python -m flyworld.game --headless --script "focus 2; isolate; mark; stim DNp09; run 150; assert rate DNp09 >= 50; assert speed > 1; assert moved > 1; silence DNa02; run 150; assert rate DNa02 == 0; assert rate DNp09 >= 50; unstim DNp09; run 150; assert rate DNp09 == 0; assert speed < 0.5; report"
  EXPECT: SCRIPT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=378789ffe1fa1f2c74476ef9ba02b47a1823632492faa23badd93ef04fd9d815; exit=0; EXPECT=matched; output-sha256=06e04f1aed761e4caa845467170a87b06fc0235064594a2f52dfdf87104ed4a2; output-bytes=474; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G8: whole-CNS focus mode runs at or above 300 steps/s with ticks under 40 ms for 300 frames
  CHECK: .venv/bin/python -m flyworld.game --headless --focus-whole --frames 300 --seed 0 --min-whole-steps-per-s 300 --max-tick-ms 40
  EXPECT: FOCUS OK 300 frames
  EVIDENCE: automatic-evidence=v1; definition-sha256=2712cb3a962ec2a9ea139db12d91f9b19b6404f0423ca1f530afb15e054aed5c; exit=0; EXPECT=matched; output-sha256=632deb89dc6e207e9e8ddc4ef9889907b2110b3d0445eebe5dff0ebd6497aaba; output-bytes=247; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G9: the ledger itself lints clean
  CHECK: node /Users/Rodela1/.claude/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=00b2a107de75024ee1d12c9f57f352402d71c327ef96682042b78a1f0e330c8c; exit=0; EXPECT=matched; output-sha256=5143c1258a9df6b9ef4e5513e93ec0122f63bb28b9081fae1e4d229522fb401d; output-bytes=151; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [ ] G10: playing the game by hand, the six flies escape the big fly, approach food, and the panel poke on the focus fly visibly changes its movement
  EVIDENCE: pending

- [x] G11: shepherd mode declares a win once every food spot has been eaten by flies standing on it
  CHECK: .venv/bin/python -m flyworld.game --headless --script "mode shepherd; food 1.5; focus 1; onfood 0; focus 2; onfood 1; focus 3; onfood 2; focus 4; onfood 3; run 15; assert round == playing; run 180; assert round == won; assert eaten_total >= 6; report"
  EXPECT: SCRIPT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=4df23174b57f29e0ec8d9865c558469a359182f29ca08e9f27d09785fd0ff732; exit=0; EXPECT=matched; output-sha256=28a56b0c89ddef42e11df9caecde934bd635dce41aa0af2538c3d5657ae5122b; output-bytes=502; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G12: shepherd mode declares a loss when the timer runs out with food left, and the world freezes afterwards
  CHECK: .venv/bin/python -m flyworld.game --headless --script "mode shepherd; time_limit 2; run 30; assert round == playing; run 60; assert round == lost; mark; focus 1; stim DNp09; run 60; assert moved < 0.01"
  EXPECT: SCRIPT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=fc960b7a59e9ce5c9b2614b3f3168ff530503e94eddade6651ca2f3c27d1458a; exit=0; EXPECT=matched; output-sha256=7d17e050948b5d4891f8fc2b63ea47decd11fe440344cd1792a3394c5ee5d993; output-bytes=270; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G13: a fly driven from the panel walks to food ahead of it, stops on the patch because food odour suppresses walking, and eats
  CHECK: .venv/bin/python -m flyworld.game --headless --script "mode shepherd; focus 1; isolate; foodahead 3.0; stim DNp09; run 150; assert eaten > 0.3; assert rate MN9 >= 20; assert speed < 0.5; report"
  EXPECT: SCRIPT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=13955d7a70f8ad957b95b8f37767af282fad6ef20af5e3877a316a681449ff3d; exit=0; EXPECT=matched; output-sha256=2a8cd01a735bb29843cedd2b506494f6ec180faefe37500df89bac32ffa307d5; output-bytes=543; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G14: the live readout reports activity for every named group, so stimulating a sensory group shows that group and its downstream descending neuron firing
  CHECK: .venv/bin/python -m flyworld.game --headless --script "focus Kathy; isolate; stim LC4; run 30; assert rate LC4 >= 50; assert rate DNp01 > 0; assert rate ORN_DM1 == 0; unstim LC4; stim ORN_DM1; run 60; assert rate ORN_DM1 >= 50; assert rate MN9 >= 20; report"
  EXPECT: SCRIPT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=d500a09499125adeab8cf2b2ad5219480d2bfe3d850ac7bc4d7f29789902bfbf; exit=0; EXPECT=matched; output-sha256=ba84d5ab4599d70f30331a9ff982f28608b15771d1e67b86926cfe2ccaf33788; output-bytes=581; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries

- [x] G15: every named fly is drawn in its own colour with the activity panel, and that panel changes when a fly's neurons are stimulated
  CHECK: .venv/bin/python scripts/check_render.py
  EXPECT: RENDER CHECK OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=b6fca9b70ddb3c0d1a22f792ca7807ca4b33606ffe34bc0a96010a1680f0e282; exit=0; EXPECT=matched; output-sha256=a7a3cce89a5ae480cb6e7a321c39a52c517ba71ff3777d17adfe264699796859; output-bytes=683; shell=/bin/sh; cwd=/Users/Rodela1/Code/Flybrain; path=f36abe55b9e5/33 entries
