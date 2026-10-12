# Future validated selected-result contract

No effective-connectivity results have been created for this visualization task. `data/<run>/selected_results.json` records a blocked state with empty conditions, intermediate membership and effective edges. The example below is a schema description, not a scientific result, and must not be loaded as a validated analysis.

Run the independently validated Tastekin implementation later, under separate authorization. Then provide an explicit JSON result to:

```sh
python visualization/scripts/build.py --selected-results PATH_TO_VALIDATED_JSON
```

Required top-level fields:

| Field | Requirement |
|---|---|
| `schema_version` | Integer `1` |
| `dataset` | Exactly `male-cns:v1.0` |
| `dataset_uuid` | Exactly `4b2087c0fbe046bfaf0d60bc970e3e5d` |
| `status` | Exactly `VALIDATED` |
| `scientific_label` | Exactly `SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY` |
| `algorithm_source`, `algorithm_version`, `method_source` | Nonempty source/version references |
| `selection_definition` | The actual definition, including whether restriction affects starting inputs only or other sensory intermediates |
| `artifacts` | Mapping of local artifact paths (relative to the JSON) to SHA256; all must resolve within this project |
| `validation_artifact` | Path to an actual JSON validation report, included in `artifacts`; `status: PASS`, same `dataset`, `dataset_uuid`, and `algorithm_version` |
| `conditions` | Exactly `lb3b_only`, `lb3c_only`, `lb3b_lb3c_combined` |

Each condition requires `status: VALIDATED`, a nonempty `provenance` reference, `input_body_ids` matching the verified input population, `node_ids` listing every retained body including those inputs, and an `edges` list. IDs are decimal **strings** to avoid JavaScript integer precision loss. Duplicate or unknown body IDs and duplicate ordered edges are rejected.

Each edge requires:

```text
source:                  decimal body ID string
target:                  decimal body ID string
raw_synapse_count:       exact integer from the audited body-edge table
effective_connectivity_score: distinct finite, nonnegative numeric score
provenance:              exact analysis output / row / method reference
```

The adapter checks both endpoints against explicit selected membership and joins the raw count to the source structural record. It never overwrites a raw count with a score. This contract currently supports nonnegative scores; a signed metric requires an explicit documented extension instead of silently applying absolute values. Selected nodes outside the current audited node/edge source require that source to be extended and verified first. The visualization layer cannot assign their identities itself.

A/B/C contain only the independently supplied selections. The D panel compares A∩B, A-only, B-only and C-only body membership, preserving whether each body also occurs in C. Raw edge hover retains per-condition scores for difference-view records. It does not assume effective selection obeys the raw path-union property. Scores are never averaged across conditions without a separately validated rule.

The explorer supports toggling raw-count versus effective-score width in A/B/C. D refuses the ambiguous score-width mode and asks the viewer to choose a condition. Graph exports include the two fields separately and identify standard graph `weight` as the raw count.

The builder verifies hashes and structural joins, not the scientific validity of an algorithm implementation. A successful visualization import does **not** certify the method or constitute strict paper replication. The paper replication method, Puddle mapping, snapshot discrepancies and all existing experiment gates remain governed by the original protocol and checkpoints.

Evidence badges E are added only to bodies explicitly retained in a supplied validated condition, with a pointer to that result. P and R remain independent. D/X remain unverified until a separate body-mapped, provenance-bearing evidence adapter is implemented; adding a candidate name or alias is insufficient.
