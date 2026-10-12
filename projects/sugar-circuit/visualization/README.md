# Gustatory visualization system

Open [the local circuit explorer](interactive/index.html), [the anatomy viewer](anatomy/index.html), or [the figure index](docs/VISUALIZATION_INDEX.md). The HTML files are self-contained and open directly from disk; no server or external JavaScript service is required.

The current figures are **PAPER-ASSOCIATED**, **RAW STRUCTURAL**, or **CANDIDATE** display derivatives of the frozen structural checkpoint. The four **SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY** panels are explicitly blocked/empty until validated analysis results exist. No scientific results or experiment configuration are changed by the builder. Puddle remains **UNRESOLVED**.

## Rebuild

Use Python 3.12+ with [requirements.txt](requirements.txt). Installation can be performed in a dedicated environment when package-network access is available. This session used the already installed compatible interpreter at `/Users/Rodela1/Code/Flybrain/.venv/bin/python`, without modifying that environment.

From the project root:

```sh
MPLCONFIGDIR=/tmp/sugar-matplotlib python visualization/scripts/build.py --fetch-skeletons
python visualization/scripts/validate.py
python -m unittest discover -s visualization/scripts -p 'test_*.py'
node --check visualization/interactive/explorer.js
node --check visualization/anatomy/viewer.js
node visualization/scripts/test_explorer.cjs
```

Every build creates timestamped subdirectories under `data/`, `static/`, `interactive/`, `anatomy/` and `graph/`. Existing runs cannot be overwritten. The two entry HTML files and documentation point to the latest build. The source structural run is read from `config/current_structural_run.txt`, or an explicit `--source-run` can be supplied. The builder verifies the saved authenticated dataset family/tag/UUID and matching start/end metadata; it does not describe this cached check as a new live dataset query.

Outputs include SVG, PDF, 320-DPI PNG, self-contained HTML, body/edge CSV and JSON, GraphML and GEXF. The manifest hashes all inputs, implementation files and generated artifacts. Figure 1 has same-side and opposite-side sheets to reduce clutter. Its sensory cards list every member body ID; all remaining nodes are individual bodies. The explorer and graph files preserve all individual sensory bodies too.

## Interactive use

Choose raw, paper-associated, selected sugar, or candidate comparison views. Select LB3b/LB3c/other LB3, requested candidates, additional mapped paper counterparts, motor types, evidence and sides. Click or keyboard-activate a node to inspect raw weights, separate NT fields, side provenance and evidence status.

Raw edge width is `0.7 + 4.3 * sqrt(count / visible_maximum)`. A minimum-count control is a **display-only** filter. Above 260 visible edges the explorer withholds arrows and asks for narrower controls, while retaining the full matching records table. Click a body and enable the focus control to inspect a small neighborhood. Reciprocal/recurrent arrows curve. A raw edge never receives an inhibitory/excitatory sign.

Effective-score mode never falls back to raw counts. With no validated scores it displays an explicit unavailable message. The D panel compares independently provided A/B/C memberships, including any combined-only membership, and never assumes that validated effective selection has the raw source-union property. D shows raw widths only because multiple condition-specific scores cannot be silently pooled.

Candidate cards are six independent comparisons. Their fixed boundary-count tables pool all verified sensory/motor partners across sides; side/evidence filters choose candidate rows. Graph-only controls do not change those fixed summaries. No D badge is inferred from a `Shiu 2022` annotation synonym, and no E or X badge is invented.

Supplementary-paper P badges for GNG232, Fudog and Rounddown use the later verified C061 audit: S16A and/or S19 labels. These are type/alias support, not recovered selected body membership. They do not add those candidates to Figure 1's mapped motif inventory. GNG021 paper presence remains unverified.

## Anatomy and future results

See [ANATOMY.md](docs/ANATOMY.md) for the authoritative SWC interface, allowlist, blocked retrieval, orientation requirements, retry command and native-coordinate renderer. Actual anatomy requires actual skeletons. A status PNG/SVG/PDF is clearly named `anatomy_BLOCKED`, not presented as a morphology render.

See [SELECTED_RESULTS.md](docs/SELECTED_RESULTS.md) for the future input contract. The adapter validates provenance, dataset and raw-weight joins. It does not implement or certify the Tastekin selection algorithm. This task stops at constructing the framework and currently valid views.
