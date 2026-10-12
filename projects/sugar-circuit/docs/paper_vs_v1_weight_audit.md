# Figure 6 versus current v1.0: weight audit

6 October 2026. **RAW_WEIGHT_AUDIT; not Experiment 1R.** Run:
`results/method_recovery/20261006T214639Z/weight_audit/`.

The 12 mapped Figure 6I/J labels were visually rechecked against the saved final
[publisher figure](https://ars.els-cdn.com/content/image/1-s2.0-S0092867426009438-gr6_lrg.jpg).
The current weights were recomputed from the previous run's complete named-body
queries, with input hashes checked against its frozen manifest. Live metadata
again confirms `male-cns:v1.0`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`, and the
same mutation/edit metadata. No raw file was changed.

| Source | Target | Figure 6 | Current all-body raw | Current minus paper | Current weightHP | Current weightHR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| GNG042 | GNG015 | 329 | 329 | 0 | 302 | 329 |
| GNG015 | MN9 | 473 | 478 | 5 | 446 | 478 |
| GNG015 | MN4a | 188 | 188 | 0 | 172 | 188 |
| ANXXX462a | GNG585 | 179 | 178 | -1 | 155 | 178 |
| GNG585 | GNG108 | 835 | 835 | 0 | 741 | 835 |
| GNG585 | GNG120 | 359 | 350 | -9 | 292 | 350 |
| GNG108 | MN9 | 376 | 381 | 5 | 356 | 381 |
| GNG108 | MN4a | 98 | 135 | 37 | 111 | 135 |
| GNG120 | MN9 | 441 | 443 | 2 | 390 | 443 |
| GNG120 | MN4a | 89 | 98 | 9 | 78 | 98 |
| GNG585 | GNG472 | 244 | 244 | 0 | 196 | 244 |
| GNG472 | MN8 | 205 | 221 | 16 | 201 | 221 |

Four of twelve raw totals match exactly; eight remain different. These are
descriptive motif-weight agreements, not selected-edge recall or circuit
replication metrics. No post hoc near-match tolerance was introduced.

## Exhaustive arithmetic test of selection/pooling explanations

For each mapped motif, enumerate (1) every nonempty subset of its current source
bodies crossed with every nonempty subset of its current target bodies, and
(2) every sum obtainable by retaining any subset of its positive raw body-pair
edges. The second test permits more choices than any whole-body restriction,
whole-edge path pruning, hemisphere restriction, or partner filter that keeps
unchanged weights and adds each retained edge once.

**None of the eight discrepant paper labels is an attainable raw-edge subset
sum.** Thus no choice of current mapped bodies or deletion of whole current
raw edges, followed by simple summation, can exactly explain any of these eight
differences. This is a falsification of a specific explanation, not recovery
of the paper's selection procedure. Do not use the enumeration to choose a
nearby sum or tune a threshold.

For ANXXX462a→GNG585 and GNG585→GNG120, the paper values even exceed the current
all-body raw totals. Under the same mappings, deletion of individual synapses
also cannot increase those totals. For the six paper values below the current
raw sums, filtering individual synapses can in principle change body-pair
weights; that mechanism has not been tested or verified.

The all-body `weightHR` totals equal the raw totals for these motifs. Substituting
all-body `weightHP` produces **zero of twelve** exact matches. Neither wholesale
field substitution explains the discrepancies. These fields are not equated to
an unverified paper cleft-score rule.

| Proposed explanation | Result / limit |
| --- | --- |
| A: selected bodies | Excluded as sole explanation under unchanged mapped raw counts and additive pooling, for all eight differences |
| B: pathway pruning | Whole-edge deletion alone excluded under the same conditions; any recomputation of edge weights remains untested |
| C: 99th-percentile partner filtering | Whole-edge retention alone cannot explain the eight differences; the paper's exact percentile population is still unknown |
| D: type pooling | Ordinary summation over a subset is excluded; alternate mappings, multiplicity, averaging, or transformed values remain unverified |
| E: different snapshot | Plausible but unverified; paper-used adjacency/version required |
| F: proofreading/version changes | Plausible but unverified; historical body/edge records required |
| G: other rule | Synapse-level filtering, other weight transformations, figure transcription or source-data differences remain possible; no cause assigned |

The column `probable_explanation` in the machine-readable table records these
constraints, not an unsupported most-likely cause. `paper_selected_body_ids_if_recoverable`,
`v1_selected_body_ids`, and `selected_v1_weight` are blank because no method-selected
body set exists. Separate columns list the current **all-body** sets actually audited.

## Reproduction and evidence

- [All required comparison fields](../results/method_recovery/20261006T214639Z/weight_audit/paper_weight_comparison.csv)
- [Every body pair, sides, counts and source](../results/method_recovery/20261006T214639Z/weight_audit/body_pairs.csv)
- [All attainable sums and body-subset witnesses](../results/method_recovery/20261006T214639Z/weight_audit/subset_enumeration.json)
- [Left/right raw totals](../results/method_recovery/20261006T214639Z/weight_audit/left_right_raw_weights.csv)
- [Input integrity checks](../results/method_recovery/20261006T214639Z/weight_audit/input_integrity.json)
- [Audit program](../scripts/17_paper_weight_audit.py), [six hand-calculated tests](../tests/test_weight_audit.py)

Run from the project root:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/17_paper_weight_audit.py --output /tmp/flybrain-weight-audit-new
```

The output directory must be new. These tests validate the arithmetic audit,
not effective-connectivity mathematics. Historical discrepancies M290–M297
remain unresolved; follow-up ledger rows retain the new exclusions.
