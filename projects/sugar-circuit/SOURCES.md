# Primary sources for the initial checkpoint

Accessed 6 October 2026. File hashes, URLs and retrieval completion times are in [the source manifest](config/source_manifest.yaml); failed requests remain in [the fetch log](logs/source_fetch_log.jsonl). Source IDs below are used in the claim ledger.

| ID | Source | Local record |
|---|---|---|
| P01 | [Publisher metadata](https://api.elsevier.com/content/article/pii/S0092867426009438?httpAccept=text/xml) | [XML](paper/primary/elsevier_article.xml) |
| P02 | [Final supplemental information](https://ars.els-cdn.com/content/image/1-s2.0-S0092867426009438-mmc1.pdf) | [28-page PDF](paper/supplement/supplemental_information.pdf) |
| P03 | [Table S1](https://ars.els-cdn.com/content/image/1-s2.0-S0092867426009438-mmc2.xlsx) | [Workbook](paper/supplement/table_s1.xlsx) |
| P04 | [Published Figure 2](https://ars.els-cdn.com/content/image/1-s2.0-S0092867426009438-gr2_lrg.jpg) | [Image](paper/primary/figure2.jpg) |
| P05 | [Published Figure 6](https://ars.els-cdn.com/content/image/1-s2.0-S0092867426009438-gr6_lrg.jpg) | [Image](paper/primary/figure6.jpg) |
| P06 | [Crossref record](https://api.crossref.org/works/10.1016/j.cell.2026.08.016) | [JSON](paper/primary/crossref.json) |
| P07 | [Janelia download documentation](https://male-cns.janelia.org/download/) | [HTML](paper/primary/malecns_download.html) |
| P08 | [neuPrint dataset inventory](https://neuprint.janelia.org/api/dbmeta/datasets) | [JSON](data/raw/neuprint_datasets.json) |
| P09 | Official v1.0 body annotations, linked by P07 | [Feather](data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather) |
| P10 | Official v1.0 neurotransmitter table, linked by P07 | [Feather](data/raw/body-neurotransmitters-male-cns-v1.0.feather) |
| P11 | Authenticated neuPrint Meta query | [Request](data/raw/query_meta.json), [response](data/raw/neuprint_meta_authenticated.json) |
| P12 | Authenticated neuPrint target-neuron query | [Request](data/raw/query_neurons_full_properties.json), [response](data/raw/neuprint_neurons_authenticated.json) |

Citation: Ibrahim Tastekin; Inês de Haan Vicente; Rory J. Beresford; Billy J. Morris; Isabella Beckett; Philipp Schlegel; Marina Gkantia; FlyEM Project Team; Cambridge Connectomics Group; Elizabeth C. Marin; Marta Costa; Gregory S. X. E. Jefferis; Carlos Ribeiro. *The complete gustatory connectome of adult Drosophila reveals how taste guides feeding, foraging, and social behavior.* Cell 189(18), 5527–5551.e5, 3 September 2026. [DOI](https://doi.org/10.1016/j.cell.2026.08.016). C001, C031.

The title and author list on the supplement cover agree with the [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42691996/). Crossref omits the two group authors; it was not used alone for authorship. No correction was located in the retrieved relation/update fields, PubMed record, or targeted title/DOI correction searches; this is a bounded search, not a guarantee of absence (C002).

**Full final paper/STAR Methods: BLOCKED — SOURCE REQUIRED.** Publisher HTML/PDF requests returned 403; the full API request returned 401; the basic API returned metadata only. The public preprint PDF request returned 429. Files named `*_response.bin`, `publisher.html`, and `elsevier_full_response.xml` are failed-access responses, not article content. Indexed text was used to discover sources, never to validate equations or numerical implementation choices.

Read: the complete project protocol; all existing logs and scaffold method/audit documents; all supplemental figure legends; the relevant S2/S12/S13/S16/S17 figures; Figure 2 and Figure 6; Table S1 target rows; official metadata and target records. The final main Results and STAR Methods have **not** been read in full.

No paper-specific effective-connectivity repository or paper-used commit was found in the public [Ribeiro lab](https://api.github.com/orgs/ribeiro-lab/repos?per_page=100) and [author](https://api.github.com/users/ibrahimtastekin/repos?per_page=100) inventories or targeted searches. The JSON inventories are preserved under `paper/code/`. General libraries or a referenced simulation framework cannot establish the exact implementation used by this paper (C032). Additional source datasets and a complete source-data inventory remain unverified.


## Structural checkpoint sources

- P13: [Complete official released segment connection graph](data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather); [official endpoint](https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather).
- P14: [Authenticated structural run meta_start; exact query saved alongside](results/structural/20261006T180116Z/raw/meta_start.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P15: [Authenticated structural run meta_end; exact query saved alongside](results/structural/20261006T180116Z/raw/meta_end.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P16: [Authenticated structural run sensory_out; exact query saved alongside](results/structural/20261006T180116Z/raw/sensory_out.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P17: [Authenticated structural run motor_in; exact query saved alongside](results/structural/20261006T180116Z/raw/motor_in.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P18: [Authenticated structural run named_out; exact query saved alongside](results/structural/20261006T180116Z/raw/named_out.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P19: [Authenticated structural run gng021_in; exact query saved alongside](results/structural/20261006T180116Z/raw/gng021_in.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P20: [Authenticated structural run additional_named_out; exact query saved alongside](results/structural/20261006T180116Z/raw/additional_named_out.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P21: [Authenticated structural run additional_named_metadata; exact query saved alongside](results/structural/20261006T180116Z/raw/additional_named_metadata.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).
- P22: [Authenticated structural run puddle_alias; exact query saved alongside](results/structural/20261006T180116Z/raw/puddle_alias.json); [official endpoint](https://neuprint.janelia.org/api/custom/custom).

The 126 additional edge-query responses are individually recorded in logs/query_log.jsonl and `results/structural/20261006T180116Z/queries/graph_validation_plan.json`; the run manifest hashes all requests/responses. Derived tables are evidence transformations, not independent biological measurements.


## Method-recovery recheck — 2026-10-06T21:56:23.667556+00:00

New responses and hashes: `results/method_recovery/20261006T214639Z/sources/`, `logs/source_fetch_log.jsonl`; live dataset query: `results/method_recovery/20261006T214639Z/meta_retry.json` and `logs/query_log.jsonl`. The re-fetched final supplement/Table S1 are byte-identical to P02/P03. Crossref has no update-to or correction relation in this response; Europe PMC has no PMC full-text link and labels the DOI route subscription-required. This is bounded correction/access coverage. Public Ribeiro-lab and ibrahimtastekin repository inventories were rechecked; none is identified as this paper's analysis implementation. The [lab publications page](https://ribeirolab.org/publications/) links the final [extended PDF](https://www.cell.com/cell/pdfExtended/S0092-8674(26)00943-8), which returned 403. Final complete Methods remain unavailable. Search-index excerpts are discovery leads only; no equations were validated from them.

## Source-pack continuation — 2026-10-06T22:16:22.713335+00:00

Sources P30–P47 document user recovery guidance, independently indexed final Methods, verified preprint v2 XML, metadata, and pinned cited-method code. The latter is not a Tastekin implementation. See `config/source_manifest.yaml` for paths/hashes and [method diff](docs/final_vs_preprint_method_diff.md). Failed 429 responses remain labeled failures.
