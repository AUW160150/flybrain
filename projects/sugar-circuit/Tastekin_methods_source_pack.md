# Tastekin methods source pack for Astra/Codex

## Purpose

Use this pack to unblock the methodology reconstruction for the Tastekin et al. gustatory-connectome project when the Cell PDF/STAR Methods endpoint returns 401/403.

**Important:** the bioRxiv manuscript is a preprint version of the same study, not automatically identical to the final Cell version. Treat any method detail found only in the preprint as `PREPRINT_ONLY` until it is cross-checked against the final Cell article, supplement, source data, or official code.

## Final published article

- Final Cell DOI: https://doi.org/10.1016/j.cell.2026.08.016
- ScienceDirect landing page: https://www.sciencedirect.com/science/article/abs/pii/S0092867426009438
- PubMed record: https://pubmed.ncbi.nlm.nih.gov/42691996/
- Janelia publication page: https://www.janelia.org/publication/the-complete-gustatory-connectome-of-adult-drosophila-reveals-how-taste-guides-feeding

The indexed final Cell page exposes relevant method/result text even when direct PDF rendering is blocked, including the Figure 6 significant-path description and the 80th-percentile selection/pruning description.

## Open preprint version of the same study

- bioRxiv v2 landing page:
  https://www.biorxiv.org/content/10.1101/2025.08.25.671814v2

- Direct PDF pattern:
  https://www.biorxiv.org/content/10.1101/2025.08.25.671814v2.full.pdf

The bioRxiv page also exposes a **Supplementary Material** download. If direct automated access fails, download the PDF and supplement manually from the landing page and place them in:

- `paper/preprint/`
- `paper/supplement/`

Suggested filenames:

- `tastekin_biorxiv_v2.pdf`
- `tastekin_biorxiv_v2_supplement.*`

## How to use these sources

1. Use the **final Cell article** as highest authority wherever its text is accessible.
2. Use the **bioRxiv v2 full text + supplement** to fill method details that are inaccessible in the final publisher PDF.
3. For every recovered method parameter, label its source:
   - `FINAL_CELL_CONFIRMED`
   - `FINAL_SUPPLEMENT_CONFIRMED`
   - `PREPRINT_ONLY`
   - `SOURCE_CONFLICT`
   - `UNVERIFIED`
4. Do not silently assume the preprint and final paper are identical.
5. If a parameter differs, preserve both values and stop before strict replication until the conflict is resolved.
6. Do not tune thresholds to make MaleCNS v1.0 resemble the published figure.

## Known final-paper method information that can be cross-checked

From the indexed final Cell article:

- Figure 6G links LB3a-d to proboscis-positioning motor neurons using cell types with high effective connectivity to both the GRNs and motor neurons.
- Significant-path construction is iterative across synaptic layers.
- Candidate neurons are retained when normalized effective-connectivity scores to the selected outputs exceed an 80th-percentile threshold.
- A second pruning step evaluates strong effective connectivity from the original input population, again using an 80th-percentile criterion.
- Quasimodo/GNG042 and Clavicle/ANXXX462a are highlighted as major downstream partners in the LB3 feeding-motor circuit.

Use these only as final-paper-confirmed anchors; reconstruct all remaining equations, normalizations, bootstrap settings, pooling, and implementation details from the primary materials.

## Suggested message to Astra

> The Cell PDF/STAR Methods endpoint is blocked, but an open bioRxiv v2 manuscript of the same study is available. Use the final Cell indexed text wherever accessible as the highest authority, and use the bioRxiv v2 full text/supplement as a provisional method source. Mark every parameter found only in the preprint as PREPRINT_ONLY. Do not assume the versions are identical. Build a final-vs-preprint method-diff table before freezing the replication implementation.
