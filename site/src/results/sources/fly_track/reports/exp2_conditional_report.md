# EXP2 conditional sign-off follow-through

Generated UTC: 2026-10-25T07:04:11.485388+00:00. Campaign: **pilot_complete_analyzed**.

Condition 1 is satisfied prospectively; condition 3 is logged. Condition 2: **NOT_POWERED_STOP**. No full Registration 1 fit has been launched by this pilot supervisor. Registration 2 remains deferred.

## Authorization and prospective decisions

The user explicitly supplied `../SIGNOFF_EXP2_v2_conditional.md`. It authorizes ten full forward-only pilot fits immediately and full Registration 1 after the three conditions pass, without another review cycle. The graph-SD prerequisite was withdrawn from Registration 1. No EXP1 training, old test evaluation or cloud spending is part of this work.

The methodological primary change to final nominal tracked fraction at update4,000 is approved and logged in `docs/exp2/amendments_v2.md`, with its date, reason and absence of any EXP2 outcomes. AUC remains exploratory on the same200-scene panel at every full-study checkpoint. Original v2 bytes and manifests are retained in `docs/exp2/archive/v2_before_conditional/`.

## Condition 1: own power model and revised workload

| Quantity | Prospective value |
|---|---:|
| Scientific paired seeds, OL and CL hybrid BIO A3/B1/C1 |20|
| Tracking noninferiority power, true difference0 |89.0213%|
| Directional collision-superiority power, true difference−.05 |96.5348%|
| Detection + tracking-guardrail joint power, dependence-free bounds |85.5561–89.0213%|
| Methodological power, ten paired seeds, worst Holm cutoff |91.9730%|
| Tracking marginal97.5% CI half-width |.0196190|
| Collision marginal97.5% CI half-width |.0279316|
| Methodological CI half-width at first Holm threshold |.0326278|
| Revised full-study final fits / tuning fits |260 /182|
| Revised full-study evaluation episodes |2,264,800|
| Additional pilot fits / planned endpoint episodes |10 /20,000|
| Maximum additional descriptive failure-recovery episodes |20,000|

These are conditional noncentral-t calculations, retaining shared-episode uncertainty and the registered two-sided97.5% interval convention. The reviewer’s approximate back-solve is not substituted. Both scientific groups use at least20 pairs; the methodological contrasts use the first matched10 hybrid OL seeds and the corresponding comparator seeds. At an effect exactly equal to a practical point-label threshold, meeting that point threshold has roughly50% probability under the symmetric working model. The ≥80% statements apply to detection/guardrail tests, not that full label. The13-rule width/reachable-verdict audit and all150 sensitivity rows are in `reports/exp2_conditional_power.json` and its CSV companions.

## Condition 2: frozen pilot and current execution

Pilot protocol hash: `a034f027cbc62cf7b25e44de74a020ecef22a610d58f6222c756208ae876c9c0`.

Five paired labels27001–27005; full4,000 updates per fit; T300/K4; P256 split32/32/64/64/32/32 plus64 local fields and one clean trajectory. DefaultsLR.003, momentum.9, global clip1, all sigmas.1, internal gamma.98 are fixed without extra tuning. Endpoint scenes81,000,000–81,001,999 are fresh; CL training is in82million. The initially proposed27/28million ranges were withdrawn unused after discovering concurrent EXP1 reservations. OL reuses only the permitted600 training demonstrations. The pilot is excluded from confirmatory fits.

The pre-outcome gate uses the larger corrected paired seed SD for tracking and post collision: below.025 retains nominal planning; [.025,.045) recomputes/increases counts; at least.045 stops. This assigns the.005 neighborhood below each sign-off boundary to the worse branch. Raw signed variance, raw seed-mean SD and conservative Gaussian crossed-ANOVA intervals are retained. Five pairs provide noisy SD estimates. CL–OL SD does not directly identify hybrid–classic or hybrid–BPTT SD; transfer is an explicit assumption. No incomplete or untrained pilot can pass; infrastructure interruptions resume the same seeds, while scientific failures retain flagged penalty endpoints and separate descriptive last-finite recovery.

| Mode | Seed | Status | Updates /4000 | Last update compute seconds |
|---|---:|---|---:|---:|
|OL|27001|complete|4000|6.950|
|CL|27001|complete|4000|8.465|
|OL|27002|complete|4000|6.816|
|CL|27002|complete|4000|9.078|
|OL|27003|complete|4000|4.413|
|CL|27003|complete|4000|5.187|
|OL|27004|complete|4000|3.067|
|CL|27004|complete|4000|4.501|
|OL|27005|complete|4000|2.361|
|CL|27005|complete|4000|4.156|

The completed pilot analysis is `raw_results/exp2/conditional_seed_pilot/pilot_analysis.json`; its companion CSVs retain paired seed means and episode effects.

```json
{
  "gate": {
    "collision_seed_sd": 0.05981002106093639,
    "decision": "NOT_POWERED_STOP",
    "effective_recompute_threshold_inclusive": 0.025,
    "effective_stop_threshold_inclusive": 0.045,
    "gate_sd": 0.13479470508499508,
    "nominal_boundaries": [
      0.03,
      0.05
    ],
    "note": "Statistical component only. Parent launch gate must verify all signoff conditions; uncertainty interval is reported separately.",
    "tracking_seed_sd": 0.13479470508499508,
    "training_authorized": false,
    "worse_branch_radius": 0.005
  },
  "revised_design": null
}
```

## Verification, provenance and retained data

Estimator tests cover independent finite-difference/analytic gradients, per-trajectory recurrent eligibility, internal discount timing, one-hop local replacement, mask/freeze/sign constraints, and actual443-neuron forward parity with the prior Torch model. Simulator tests verify full300-action state/render equivalence and separate post/wall events. Runner tests cover exact RNG/optimizer replay, atomic commits, failure finalization and fresh-scene restrictions. Power validation checks independent quadrature, MDE inversions, gate boundaries, missing/duplicate episodes and failed-run inclusion. The launch validation artifact records the executed commands and counts.

DUST original source and MIT license are archived at upstream commit `b20f7c03eac630b6441ba6f254128c1761dc45ad` with verified Git blob hashes and SHA256. Whitespace-normalized source matches the earlier audit. Historical64v1 and52v2 artifacts were verified before the intentional amendment. Four Stage0/EXP1 ledger/tool changes already present on entry are recorded explicitly; no old scientific artifact was overwritten.

Per-fit raw directories retain initial state, every update’s `restart.npz`, `record.json` and `draws.npz`, exact final4,000 checkpoint, full endpoint CSV and any separate recovery CSV. The data dictionary is `docs/exp2/conditional_data_dictionary.json`. Global power/decision CSVs, paired seed/episode CSVs, raw estimator timing and source/configuration hashes support later visualization without reconstruction from prose.

Synthetic full-estimator checks measured3.5724 and3.3495seconds, peak RSS about690MB, with constant synthetic observations and no environment or optimizer update. These are implementation checks, not training-time predictions. Actual per-update and cumulative training timings are stored separately. The prior.22sec/episode evaluation cost remains an assumption; the.600sec synthetic kernel is not extrapolated into a training promise.

## Execution and remaining work

Run `scripts/report_exp2_conditional.py` with the project Python to refresh this report. `scripts/run_exp2_conditional_pilot.py --run --workers 4` supervises/resumes the ten fits, validates hashes, and automatically analyzes the complete pilot. A failed SD gate stops expansion. A passing SD and power result permits full Registration1 once its complete implementation and source/configuration manifest are frozen. No further review cycle is required by the conditional sign-off. Registration2 retains its separate EXP1 headroom, R1 usefulness, trained-null SD, and approval/budget gates.
