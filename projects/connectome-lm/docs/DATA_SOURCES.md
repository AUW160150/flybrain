# Data sources and provenance

Verified/retrieved 2026-10-05 UTC. Raw MaleCNS files already existed in the workspace; their original acquisition times are unknown. Official catalogue links and object HTTP headers were retrieved on this date. Local content matched the official size and MD5 headers; SHA-256 below identifies the bytes used. Content hashing alone does not prove provenance.

## MaleCNS

[Official catalogue](https://male-cns.janelia.org/download/) selects release `male-cns:v1.0`, directory `gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/`. The catalogue describes neuron annotations and segment-to-segment connection strengths. Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution: FlyEM (HHMI Janelia), University of Cambridge, MRC Laboratory of Molecular Biology, and Google Research. This project thresholds and extracts a neuron-level subnetwork; it does not reproduce a whole CNS.

| Product | Exact bytes | SHA-256 |
|---|---:|---|
| [body-annotations-male-cns-v1.0-minconf-0.5.feather](https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather) | 14483314 | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |
| [connectome-weights-male-cns-v1.0-minconf-0.5.feather](https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather) | 1051241946 | `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1` |

Both URLs were resolved from the catalogue, not guessed. Total required raw data: 1,065,725,260 bytes, below the default 2,000,000,000-byte ceiling. No additional anatomy/NT products were acquired. Cache files remain at the original workspace paths; this project stores manifests and derived arrays.

Actual weight schema: `body_pre:int64`, `body_post:int64`, `weight:int64`; canonical direction is pre/source to post/target. Annotation key is `bodyId:int64`; status/statusLabel/type/superclass/class drive transparent inventory bookkeeping. ID values never pass through floats. Complete actual schemas, HTTP headers, cache locations, MD5 checks and retrieval/verification details are in `data/raw/malecns-manifest.json`.

All 151,856,684 source rows were audited for duplicate ordered pairs; none occurred. The table contains no regional-breakdown fields, and no aggregation/summing was applied. Filtering leaves 165,122 curated neurons (including 2,605 with missing type) and 6,235,649 loop-free directed pairs at >=5 contacts. There are 126,293,487 excluded endpoint pairs, 19,327,515 curated pairs below threshold and 33 self-edges removed after thresholding. `canonical-manifest.json` retains all status exclusions and unresolved classifications.

## Text

[Original Tiny Shakespeare repository](https://github.com/karpathy/char-rnn/blob/master/data/tinyshakespeare/input.txt), pinned commit `6f9487a6fe5b420b7ca9afb0d7c078e37c1d1b4e`. [Exact immutable raw file](https://raw.githubusercontent.com/karpathy/char-rnn/6f9487a6fe5b420b7ca9afb0d7c078e37c1d1b4e/data/tinyshakespeare/input.txt). Source SHA-256: `86c4e6aa9db7c042ec79f339dcb96d42b0075e16b8fc2e86bf0ca57e2dc565ed`; 1,115,394 exact UTF-8 bytes, no normalization. Public-domain Shakespeare text, benchmark prepared by Andrej Karpathy; repository code is MIT. This is narrow benchmark coverage, not general language.

| Split | Half-open byte offsets | Bytes | SHA-256 |
|---|---|---:|---|
| test | [1059624, 1115394) | 55770 | `8b5a8c8af45905547ad03b7aae6980a277a5dd78924a6e6ac64b75d63d7d40bd` |
| train | [0, 1003854) | 1003854 | `a9e24e23a1ec77744dad26844bfd5a09b6e041954e1eef0000e7f24cba6db735` |
| validation | [1003854, 1059624) | 55770 | `c64e90c160750d91a9d2d9b1ace5eab1a440f5a1701d32a8e97a179b7839f1c8` |

Exact cross-split spans of at least 256 bytes: 0 for train/validation, 0 for train/test, 0 for validation/test. This preprocessing audit is not model evaluation on test text. Every validation or eventual test evaluation scores 55,769 targets; the first byte of its split supplies context only.

## Software and research context

- [NetworkX directed_edge_swap documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.swap.directed_edge_swap.html), and its [source](https://networkx.org/documentation/stable/_modules/networkx/algorithms/swap.html), retrieved 2026-10-05. Our instrumented directed three-edge implementation adds explicit loop rejection and saves every proposal/accepted count; it does not call the undirected swap routine.
- [PyTorch sparse matrix multiplication documentation](https://docs.pytorch.org/docs/stable/generated/torch.sparse.mm.html), accessed 2026-10-05 (web reader returned a redirect). Installed torch 2.14.0 behavior was checked locally with CPU float64 forward/backward equivalence; documentation alone was not taken as proof of backend support.
- [Lappalainen et al., Connectome-constrained networks predict neural activity across the fly visual system](https://www.nature.com/articles/s41586-024-07939-3), Nature 2024, retrieved 2026-10-05. Methodological precedent for fitting parameters under connectome constraints in visual computation; it is not evidence that fly wiring benefits language prediction.
- [Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md/), accessed 2026-10-05, resolved to [ChatGPT Learn guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md). Local AGENTS.md records brief invariants and points back to the full specification.
- Optional [Project Gutenberg Alice ebook 11](https://www.gutenberg.org/ebooks/11) is a protocol reference only; it was not fetched, processed or used. No independent-corpus replication is claimed.

Installed versions are pinned in requirements.lock. Original cache-header/catalogue evidence remains under data/raw, and a compact provenance receipt is persisted alongside this document.
