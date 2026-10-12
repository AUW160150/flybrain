# Initial validation checkpoint — 6 October 2026

**PARTIAL VALIDATION; METHOD RECONSTRUCTION BLOCKED.** Dataset access and the requested body identities are verified. The final paper's main text and STAR Methods remain inaccessible, so the algorithm is not validated. No experiments, effective-connectivity calculations, edge-weight hypothesis tests, or physiological simulations were run.

## Confirmed

The final publication is Tastekin et al., *The complete gustatory connectome of adult Drosophila reveals how taste guides feeding, foraging, and social behavior*, Cell 189(18):5527–5551.e5, 3 September 2026, DOI [10.1016/j.cell.2026.08.016](https://doi.org/10.1016/j.cell.2026.08.016). Its supplemental PDF, Table S1 and Figures 2/6 are saved and checked. No correction was found in the sources searched; correction coverage remains bounded. C001–C003, C031.

Authenticated neuPrint confirms `male-cns:v1.0` on `https://neuprint.janelia.org`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`. Meta stores the family as `dataset=male-cns` and release as `tag=v1.0`. The token is excluded from scientific logs. C004, C029.

| Population | Left | Right | Total |
|---|---:|---:|---:|
| LB3a | 9 | 8 | 17 |
| LB3b | 5 | 6 | 11 |
| LB3c | 12 | 11 | 23 |
| LB3d | 11 | 15 | 26 |
| MN4a | 2 | 2 | 4 |
| MN6 | 1 | 1 | 2 |
| MN8 | 1 | 1 | 2 |
| MN9 | 1 | 1 | 2 |

All 87 sensory/motor IDs and types match Table S1, with no missing or extra IDs in the requested types. Sensory sides use `rootSide`; motor labels use `somaSide` and agree with the paper's `Root_Side` labels without assuming these fields are biologically equivalent. C006–C007.

| Type | Left body ID | Right body ID | Supplied body prediction and consensus |
|---|---:|---:|---|
| GNG042 / Quasimodo | 15321 | 15734 | GABA |
| ANXXX462a / Clavicle | 514625 | 19480 | Acetylcholine |
| GNG015 | 523590 | 28181 | GABA |
| GNG021 | 27203 | 521222 | Acetylcholine |

These eight interneurons bring the total to 95. Aliases come from raw annotation synonyms. Predicted neurotransmitters are not physiological validation. C008–C010.

Figure 2 supports sugar-associated LB3b/LB3c; LB3b also carries the low-salt association. Figure 6G/S16 use LB3a–d and the four motor types above. Figure 6I/S17 place GNG015 in the Quasimodo disinhibitory route to MN9/MN4a; the illustrated MN8 route uses Puddle. The supplement establishes several stage-specific parameters, documented in [the partial reconstruction](paper_method_reconstruction.md). C011–C022.

## Corrections and discrepancies

- **Motor naming:** use MN4a for the illustrated target. MN4b is distinct; exact `MN4` has no returned v1.0 bodies. C014 / M002.
- **Missing nerve:** Table S1 `GRNs!row 250` assigns `MxLbN` to LB3c body **957530**; the flat annotation and neuPrint omit `entryNerve`. The missing field was not filled or used to exclude the body. C025 / M003.
- **NT fields:** 22 target bodies have an unclear body prediction but assigned consensus; another 11 have a named prediction different from consensus. Each record is preserved. A policy for interpreting these fields remains unresolved. C026 / M010–M042.
- **Cross-representation precision:** 1,615 field comparisons match exactly. The other 190 confidence values match a float32 conversion of the flat-file values within 1e-14; all are recorded as explained differences. No unexplained neuPrint/flat-file annotation mismatch remains. C030 / M100–M289.
- **Project scaffolding:** ledger columns were outdated and the README incorrectly said the protocol was missing. Original header-only ledgers were archived, the required schemas created, and current documents updated. M001, M006.
- **Metadata guard:** checking `Meta.dataset` alone against the combined release string was an incorrect validation expectation; the correct check uses `dataset + ":" + tag` and UUID. M004.

## Still blocked or unverified

| Item | Reason | Required next source/access |
|---|---|---|
| Full paper-method reconstruction | Main paper and STAR Methods not retrievable; no indexed excerpts promoted to verified methods | A local legally obtained final PDF/HTML or accessible publisher/author copy, including STAR Methods |
| Exact equation, normalization, bootstrap and pruning | Supplement gives only parts of the method | Full Methods and paper-associated implementation or author clarification |
| Analysis repository and paper-used commit | Not located in sources searched | Official repository/archive link and version |
| Paper's MaleCNS snapshot | Table S1 labels the dataset only as MaleCNS | Explicit paper/code data provenance; matching IDs alone is insufficient |
| Raw synaptic edge agreement | Outside the completed ID check; no connectivity table comparison yet | Targeted v1.0 edge queries and official connection table, with filtering agreed from Methods |
| Whole-path H1 and GNG021 selection | Requires the validated analysis and experiments, which were not authorized for this checkpoint | Complete method validation first; later experiment work only when requested |

C023–C028, C032. The GNG021 name was not found in the extracted supplement or named in the inspected relevant panels; this does **not** prove absence from unnamed nodes or the inaccessible main text.

## Audit records

- [Claim ledger: 33 claims](../logs/claim_ledger.csv)
- [Mismatch ledger: 229 records](../logs/mismatch_ledger.csv), including individually retained precision differences
- [All 95 bodies, sides, nerves and NT fields](../results/validation/20261006T171922Z/resolved_bodies.csv)
- [Table S1 comparison](../results/validation/20261006T171922Z/table_s1_comparison.csv)
- [neuPrint/flat-file comparison](../results/validation/20261006T171922Z/neuprint_annotation_comparison.csv)
- [Run provenance and hashes](../results/validation/20261006T171922Z/manifest.json)
- [Source manifest](../config/source_manifest.yaml) and [query log](../logs/query_log.jsonl)

The project is an isolated Git repository in the existing workspace. The run manifest records that it has no commit yet. The earlier flat-file-only validation run remains intact; this report uses the later authenticated run.

