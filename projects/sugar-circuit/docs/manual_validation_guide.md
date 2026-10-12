# Manual validation guide — initial checkpoint

Use the sources and saved outputs below to check each claim. Raw responses and hashes are retained, including unsuccessful earlier requests. Select `male-cns:v1.0` in neuPrint before submitting a query.

## Active dataset — C029

In neuPrint's custom query view:

```cypher
MATCH (m:Meta)
RETURN m.dataset AS family, m.tag AS release, m.uuid AS uuid
```

Expected: family `male-cns`, release `v1.0`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`. A different family/tag/UUID is a stop condition. `Meta.dataset` alone does not contain the release suffix. Compare [the saved full Meta response](../data/raw/neuprint_meta_authenticated.json) and [public dataset listing](../data/raw/neuprint_datasets.json).

## Body IDs and sides — C006–C009

```cypher
MATCH (n:Neuron)
WHERE n.type IN ['LB3a','LB3b','LB3c','LB3d',
                 'GNG042','ANXXX462a','GNG015','GNG021',
                 'MN4','MN4a','MN6','MN8','MN9']
RETURN n.bodyId, n.type, n.instance, n.rootSide, n.somaSide,
       n.class, n.superclass, n.entryNerve, n.exitNerve, n.synonyms
ORDER BY n.type, n.bodyId
```

Expected counts: LB3a 17, LB3b 11, LB3c 23, LB3d 26; GNG042/ANXXX462a/GNG015/GNG021 two each; MN4 zero, MN4a four, MN6/MN8/MN9 two each. Total: 95.

Compare every ID with [resolved_bodies.csv](../results/validation/20261006T171922Z/resolved_bodies.csv). All individual LB3b/LB3c IDs are listed there. Check sensory sides against `rootSide`; motor/interneuron `somaSide` is preserved separately. Do not interpret missing class/nerve/soma fields as inferred biology.

For paper corroboration open [Table S1](../paper/supplement/table_s1.xlsx). Filter `Connectome=maleCNS`, then `Subtype` for GRNs or `Type` for MNs. The [comparison CSV](../results/validation/20261006T171922Z/table_s1_comparison.csv) gives exact Excel row references. A body missing on either side or a changed type is a mismatch.

## Aliases and predicted NT — C008–C010, C026

```cypher
MATCH (n:Neuron)
WHERE n.type IN ['GNG042','ANXXX462a','GNG015','GNG021']
RETURN n.bodyId, n.type, n.somaSide, n.synonyms,
       n.predictedNt, n.predictedNtConfidence,
       n.celltypePredictedNt, n.celltypePredictedNtConfidence,
       n.consensusNt
ORDER BY n.type, n.bodyId
```

Expected IDs: GNG042 15321/15734; ANXXX462a 19480/514625; GNG015 28181/523590; GNG021 27203/521222. The first two types' synonyms contain Quasimodo and Clavicle. GNG042/GNG015 are predicted GABA; ANXXX462a/GNG021 acetylcholine in both body and consensus fields. Compare exact confidence values with the raw NT table and [neuPrint comparison CSV](../results/validation/20261006T171922Z/neuprint_annotation_comparison.csv); small float32 rounding differences are expected and logged.

For all sensory/motor targets inspect both body and consensus fields. They differ in 33 records; treating consensus as the original body prediction would be an error. No physiological sign is inferred solely from this check.

## Known nerve mismatch — C025

```cypher
MATCH (n:Neuron {bodyId: 957530})
RETURN n.type, n.rootSide, n.entryNerve
```

Expected v1.0: LB3c, R, null. Table S1 `GRNs!I250` says MxLbN. This is an unresolved missing annotation; do not silently fill it.

## Paper method and hypotheses — C011–C024, C028

| Check | Where | Expected / error condition |
|---|---|---|
| Sugar associations and low-salt overlap | Figure 2D–E | LB3b/c under Gr64f; LB3b additionally low salt/Ir56b. Exclusive sugar claims exceed this evidence |
| Paper input/output populations | Figure 6G; S16 pp.17,26–27 | LB3a–d and MN4a/MN6/MN8/MN9; b/c-only is an extension |
| Motor naming | S12C legend p.25 | MN4a corresponds to earlier MN4; MN4b distinct |
| Quasimodo/GNG015 route | Figure 6I; S17 pp.18,27 | Predicted disinhibition to MN9/MN4a; check the separate Puddle branch for MN8 |
| Initial percentile | S16 legend pp.26–27 | Greater than 99th percentile for initial top partners; full percentile universe/pruning still missing |
| Hop and bootstrap references | S13 p.14 and legend pp.25–26 | Maximum seven-hop heatmap; two upper 95% CI references; do not confuse these criteria |
| Simulation conditions | S17 p.18 and legend p.27 | 200 Hz LB3, selected 100 Hz GNG015 conditions, 30 runs/condition in the paper; none executed here |
| Exact equation and later pruning | Full STAR Methods and official code | **BLOCKED — SOURCE REQUIRED**; no validated formula/config exists |
| Raw edge weights | Targeted neuPrint edge queries plus official weights table | **UNVERIFIED in this checkpoint**; compare body pairs and identical filters before accepting values |
| Replication, sugar-restricted paths, GNG021 selection | Future validated experiment outputs | **NOT RUN**; no selection or whole-path dominance verdict is available |

Rerunning `.venv/bin/python scripts/04_resolve_neuron_ids.py` reads the saved records, verifies source hashes, and writes a new timestamped comparison directory. It performs identity/metadata validation only and does not refresh the server or run an experiment.

## Structural checkpoint review

Open `results/structural/20261006T180116Z/named_neuron_edge_validation.csv` to inspect individual body IDs, tested absences and raw weights. Each record names a complete outgoing query; the same basename in `queries/` gives exact Cypher and `raw/` gives the saved response. Cross-check `raw_edges.csv` using both integer body IDs, not type-level pooled sums. Use `paper_motif_comparison.csv` only as a descriptive figure/current comparison. Review `motor_origin_edges_in_circuit_A.csv` anatomically before inferring motor feedback; use skeleton/synapse coordinates before claiming anatomical midline crossing. Load `circuit_graph.graphml` with `visualization_views.json`; keep unknown annotation and prediction fields explicit. Do not treat capped `simple_paths.csv` examples as an exhaustive route listing; use exact membership/count files. Puddle needs an authoritative identity mapping before labeling a body.
