# Final Cell versus bioRxiv v2 method audit

Run: `results/method_recovery/20261006T220302Z`. This updates the earlier source-access failure. The user-supplied [source pack](../Tastekin_methods_source_pack.md) explicitly permits indexed final text as primary evidence. We independently recovered contiguous relevant Methods sections, not just the pack's assertions. The complete final PDF remains unavailable.

The [final Cell article](https://www.sciencedirect.com/science/article/abs/pii/S0092867426009438) governs. Its saved passages are in [search 2](../results/method_recovery/20261006T220302Z/sources/indexed_final_methods_search2.txt), [search 4](../results/method_recovery/20261006T220302Z/sources/indexed_search4.txt), and [search 5](../results/method_recovery/20261006T220302Z/sources/indexed_search5.txt); other search hits in those files are not evidence for Tastekin. HTML pagination is unavailable; section names identify locations. We obtained the complete [bioRxiv v2 XML](https://www.biorxiv.org/content/early/2025/12/13/2025.08.25.671814.source.xml), verified its DOI, version identifier and 13 December 2025 version date, and saved it [locally](../paper/preprint/tastekin_biorxiv_v2.xml). Its PDF/supplement requests returned 429; those response files are not PDFs. The existing final supplement remains the authority for supplemental claims.

| Detail | Final Cell | bioRxiv v2 | Resolution |
| --- | --- | --- | --- |
| Raw graph | Directed, neuron-pair synapse counts | Agrees | FINAL_CELL_CONFIRMED |
| Edge normalization | Postsynaptic total-input fractions | Agrees | FINAL_CELL_CONFIRMED |
| Propagation | Successive matrix products | Agrees | FINAL_CELL_CONFIRMED |
| Layer scaling | Divide by nonzero-score mean | Agrees | FINAL_CELL_CONFIRMED; grouping axis unresolved |
| Sign | Explicitly excluded in Limitations | Unsigned matrix description | FINAL_CELL_CONFIRMED |
| First candidates | Top partners; S16A reference | Downstream partners, no equivalent explicit reference in this paragraph | Final clarification governs; final S16A specifies >99th percentile |
| Output criterion | >80th percentile | “80th quantile” | Final wording governs |
| Original-input pruning | 80th percentile explicit | Numeric value absent in Methods; Figure 8G supplies >80th for both directions | Agreement after checking preprint caption; not a conflicting threshold |
| Iteration | Survivors seed next iteration | Agrees | FINAL_CELL_CONFIRMED; exact candidate expansion/horizons unresolved |
| Graph export | Induced all-by-all connectivity | Agrees | FINAL_CELL_CONFIRMED |
| Bootstrap | 10,000 resamples of 75, replacement | Dedicated Methods section absent | FINAL_CELL_CONFIRMED; added final detail |
| Random control | 1,446 brain neurons, then same bootstrap | Dedicated Methods section absent | FINAL_CELL_CONFIRMED; initial sampling details unresolved |
| CI cutoff | Upper endpoint of 95% interval | Dedicated Methods section absent | FINAL_CELL_CONFIRMED; estimator unresolved |
| Synapse filter | Cleft threshold 50 | Agrees | FINAL_CELL_CONFIRMED; dataset-specific translation unresolved |
| Circuit panel | Figure 6G | Figure 8G | Renumbering; both depict types |
| Clavicle label in Results | ANXXX462a | ANXXX462 | SOURCE_CONFLICT at annotation granularity; final specificity governs |
| Identity table | Table S1 | Supplemental Table 2 | Final table already validated locally |
| Simulation | Separate proofread graph and signed model | No corresponding model Methods section | Final addition; excluded from this task |
| Implementation | No paper-specific code recovered | Additional analysis information available on request | UNVERIFIED; no author contact sent |

The machine-readable [diff](../results/method_recovery/20261006T220302Z/final_vs_preprint_method_diff.csv) and [parameter inventory](../results/method_recovery/20261006T220302Z/method_parameters.csv) distinguish source confirmation from implementation readiness. No preprint-only detail has been promoted to a final-paper fact. No numeric threshold conflict remains after using final wording and the preprint caption; the Clavicle granularity difference is resolved to the final label, without guessing an alias equivalence for the broader preprint label.

## Implementation and remaining source requirements

With pre-by-post adjacency W and supplied postsynaptic totals T, the verified algebra is P[i,j] = W[i,j]/T[j], E(1) = P[source,:], E(h+1) = E(h)P. This is an exact-hop walk sum. Recurrence follows mathematically from unrestricted matrix products; an explicit publication-specific self-loop exclusion was not recovered. Mean scaling is applied to reported scores, not fed back into propagation. The paper does not provide a reproducible choice of score grouping when multiple source/target populations are involved.

[src/effective_connectivity.py](../src/effective_connectivity.py) implements that algebra, explicitly supplied nonzero-mean scaling, strict percentile comparisons, two-stage filtering of supplied scores, and induced raw graph extraction. It preserves body identities, zero-degree bodies, laterality distinctions, multiple routes and recurrence. It does not implement the unresolved significant-path iterator, bootstrap CI selection, or signed motif classification. Percentile reference vectors, estimator and hop counts have no biological defaults. Test choices are labeled synthetic.

The publication cited for the adapted method is [Stürner et al.](https://www.nature.com/articles/s41586-025-08925-z). We inspected its public repository tree and all five Rmd scripts plus README under `code/`, pinned at `94637d7d82920234ef0bfdbf383c000e74a8b45a`. Those files do not supply Tastekin's significant-path implementation. Cited-paper partner thresholds must not be imported as Tastekin rules.

The smallest useful missing artifact is the function and call/config used to generate Figure 6G/S16, with its input adjacency definition. It must settle:

1. Which neurons/segments and synapses enter the graph and the input denominators; how cleft 50 applies to MaleCNS. The released minconf-0.5 file contains segment endpoints as well as neurons, so using every row silently would change the stated graph.
2. Whether scores are pooled over bodies, left/right pairs, subtypes or target motor types, and when that pooling occurs relative to normalization and thresholding.
3. The comparison populations, treatment of zeros and percentile estimator for initial 99th and both 80th-percentile steps.
4. Candidate expansion, hop horizon for each direction and iteration, total Figure 6G depth, and handling of revisited/previously selected nodes. A reachability plateau or seven-hop heatmap does not specify these settings.

Historical snapshot and figure source tables are separately needed to explain the eight raw-weight differences and measure complete published-node recall. Bootstrap seed, CI estimator and initial random-neuron sampling remain necessary for the GRN–MN control analysis; that separate uncertainty is not the sole reason Figure 6G selection is gated. Puddle and Tentacular identities remain unresolved.

## Why this gate changes the scientific result

[Reproducible synthetic examples](../results/method_recovery/20261006T220302Z/selection_ambiguity_examples.json) hold the percentile at 80 and use an explicitly chosen linear estimator:

| Unresolved choice | One interpretation | Another interpretation |
| --- | --- | --- |
| Reference population for scores 1–5 | Five candidates: threshold 4.2, selects E | Add twenty zero-score bodies: threshold 0.2, selects A–E |
| Pool motor scores A=(0.6,0), B=(0.4,0.4) | Sum: selects B | Maximum: selects A |
| Candidate-to-motor horizon | One hop: selects direct candidate A | Two hops: selects candidate B through a relay |

These examples demonstrate material non-uniqueness, not biological sensitivity results and not permission to choose the best-looking circuit. All 21 new tests and six existing raw-weight tests pass. No current-v1 effective circuit, failed-neuron selection, sugar dominance or functional effect is asserted.
