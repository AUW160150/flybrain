# Discrepancy report — initial checkpoint

6 October 2026. All records remain in [the mismatch ledger](../logs/mismatch_ledger.csv). No experiment result exists to compare with the published circuit.

| Finding | Status | Evidence / action |
|---|---|---|
| LB3c body 957530: entry nerve MxLbN in Table S1; missing in both v1.0 representations | SOURCE CONFLICT; unresolved annotation gap | M003 / C025; retain missing value and paper value separately; tracing/curator clarification needed |
| 22 unclear body NT predictions with assigned consensus | UNVERIFIED at body prediction level | M010–M042 contain these and the following 11 records; no consensus overwrite |
| 11 named body NT predictions disagree with consensus | Distinct prediction/consensus fields; interpretation unresolved | Full records and confidence in the NT difference CSV; determine documented policy before signed modeling |
| 190 NT confidence precision differences, flat files versus neuPrint | EXPLAINED_DIFFERENCE | M100–M289; each neuPrint value matches the corresponding float32 conversion within 1e-14 |
| 95 target identities and 1,615 compared fields | EXACT_MATCH | No unexplained neuPrint/flat-file annotation mismatch; not a connectivity validation |
| Paper target IDs/types | EXACT_MATCH for all 87 requested sensory/motor bodies | Table S1 comparison; motor side-label semantics remain explicitly distinguished |
| MN4 generic naming | Resolved for checkpoint | M002: use MN4a; MN4b is distinct |
| Dataset Meta family/tag format | Resolved validation expectation | M004: validate male-cns + v1.0 + UUID |
| Crossref omits group authors | Resolved citation | M005: use the publisher supplement and PubMed complete author list |
| Scaffold ledger schemas and protocol status | Resolved documentation | M001/M006: original schemas archived; canonical ledgers initialized; README updated |

Detailed machine-readable evidence: [Table S1 comparisons](../results/validation/20261006T171922Z/table_s1_comparison.csv), [NT field differences](../results/validation/20261006T171922Z/nt_field_differences.csv), [neuPrint comparisons](../results/validation/20261006T171922Z/neuprint_annotation_comparison.csv).

The unresolved blockers are source coverage, algorithm definition/code, and the paper's dataset snapshot. Authenticated access is now working. Raw edge comparisons have not been performed in this checkpoint, and no v1.0 pathway conclusion is established.

## Gates 2 and 3 follow-up

All 746,910 exported edge weights agree across current neuPrint/flat representations. Eight paper Figure 6 labels differ from all-body current sums; causes remain unresolved (M290–M297). Puddle mapping is missing (M298). An additional 976 NT field distinctions are preserved (M299–M1274), not treated as edge-source conflicts. See [structural checkpoint](structural_connectivity_checkpoint.md) and [per-motif comparison](../results/structural/20261006T180116Z/paper_motif_comparison.csv). No paper-method uncertainty was filled with a guessed default.
