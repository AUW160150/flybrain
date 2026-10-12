# Assumptions at the initial checkpoint

6 October 2026. No prior assumptions file existed. This document distinguishes protocol hypotheses from verified observations. See [the full audit](docs/prompt_vs_paper_audit.md) and claim IDs below.

| Item | Current disposition | Evidence / claim |
|---|---|---|
| Target new analysis is `male-cns:v1.0` | VERIFIED as the active queried release | Authenticated Meta family + tag + UUID; C029 |
| Published analysis used this exact release | UNVERIFIED | The retrieved paper sources say MaleCNS; identical IDs are insufficient; C027 |
| Paper LB3 inputs include LB3a–d | CONFIRMED BY PAPER | Figure 6G and S16; C013 |
| LB3b/LB3c are sugar-associated | CONFIRMED BY PAPER at morphological/receptor-matching level | Figure 2D–E; C011 |
| LB3b is exclusively sugar-specific | CONTRADICTED | Low-salt association is also shown; C011 |
| All LB3 inputs are sugar-specific | CONTRADICTED | LB3a water and LB3d high salt/heavy metal labels; C012 |
| MN4, MN4a and MN4b are interchangeable | CONTRADICTED | S12C distinguishes MN4a and MN4b; C014 |
| GNG042 and ANXXX462a aliases | VERIFIED | Direct annotation synonyms and neuPrint; C008 |
| GNG021 is selected by the paper method | UNVERIFIED hypothesis | Existence and predicted NT are established; path selection is not; C009–C010, C024 |
| H1: stronger LB3c input implies whole-path dominance | UNSUPPORTED inference | S16A supports a qualitative first-edge comparison only; C023 |
| One confidence/synapse threshold serves all stages | UNSUPPORTED | Classification, bootstrapped thresholds and S16 selection have different roles; C015–C019 |
| Body-level NT prediction equals consensus | CONTRADICTED for some records | 33 target records differ, including 22 unclear predictions; C026 |
| Structural edges imply physiological influence | UNVERIFIED without further evidence | No raw edges, path experiments or simulations performed here |

Operational choices: preserve the existing workspace project; use exact type membership for the ID check; keep root-side and soma-side fields distinct; retain missing values; keep both NT prediction and consensus; treat the annotation filename's `minconf-0.5` as source provenance, not a paper-method parameter. These choices are recorded in the decision log.


## Structural checkpoint update

[Gate 2/3 report](docs/structural_connectivity_checkpoint.md) supersedes earlier “no raw edges assessed” statuses. Input-only B/C restrictions retain other sensory intermediates. GNG021 is indirectly reachable and overlaps Quasimodo/GNG015; structural presence does not establish paper selection or function. Raw motors are not assumed to be absorbing sinks. Opposite-side body labels are not synapse locations. NT fields remain distinct. Exact source/filter/bound choices: `results/structural/20261006T180116Z/search_config.json`.
