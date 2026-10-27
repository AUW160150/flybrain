"""Write reports/figure_data_manifest.json: for every planned figure, the exact source files, the exact
fields or tables it reads, and each file's SHA-256 at read time.

    python3 scripts/write_manifest.py [--workspace ..]

Selector grammar (resolved by scripts/build_figures.py, and independently by check_results_site.py):

  json:<file>#<JSON pointer>      one value; a `*` segment matches every key or index
  md:<file>#<caption>|<row>|<col> one cell of the first table after the line containing <caption>;
                                  <row> is the first cell's text, or col=value pairs joined by commas
  csv:<file>#<k=v,...>|<column>   that column for every matching row, in file order
  mdtext:<file>#<regex>           group 1 of the first match of <regex> in the file's prose

<file> is relative to the Flybrain workspace and to site/src/results/sources/. A figure may only read
selectors its own entry lists; build_figures.py refuses anything else.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENDORED = REPO / "site" / "src" / "results" / "sources"
OUT = REPO / "reports" / "figure_data_manifest.json"

T, TB = "fly_track/reports/stage1_headroom.md", "fly_track/reports/stage1b_occlusion.md"
G1, G1B = "fly_track/reports/exp1c/g1.json", "fly_track/reports/exp1c/g1b.json"
POWER, ACT = "fly_track/reports/exp1c/power.json", "fly_track/reports/exp1c/activity.json"
PREREG = "fly_track/docs/exp1_continuation_preregistration.md"
PILOT = "fly_track/raw_results/exp2/conditional_seed_pilot/pilot_analysis.json"
P2, R2 = "fly_track/reports/exp2_conditional_power.json", "fly_track/reports/exp2_conditional_report.md"
A_MD, A_JS = "fly_retrieval/reports/exp3_trackA_novelty.md", "fly_retrieval/reports/trackA_summary.json"
B_MD, EXPORT = "fly_retrieval/reports/exp3_trackB_connectome.md", "fly_retrieval/b2/export.csv"
B2S, TOUCH = "fly_retrieval/reports/trackB2_summary.json", "fly_retrieval/b2/flyhash_candidates_touched.csv"
C_MD, C_JS = "fly_retrieval/reports/exp3_trackC_skew.md", "fly_retrieval/reports/trackC_summary.json"
SYN, PRE3 = "fly_retrieval/docs/exp3_analysis.md", "fly_retrieval/docs/exp3_preregistration.md"

ARMS = ["bio", "bypass", "rew1001", "rew1002", "rew1003", "two_unit"]
STEPS = ["1000", "2000", "4000", "8000", "12000", "16000"]
CURVE = "Mean validation tracked fraction by step"
B2_ALGOS = ["flyhash", "densefly", "hnswlib", "scann", "faiss-ivfpq", "faiss-ivfpqfs"]
B2_SETS = ["sift-128-euclidean", "glove-100-angular"]
ODOUR = "Odours: BIO against each null"

FIGURES = [
    {
        "id": "exp1-memory-dissociation",
        "title": "The memory dissociation: post and wall collisions, circuit against direct connection",
        "page": "/projects/steering-circuit/", "lead": True,
        "sources": [G1, G1B, T, TB],
        "fields": [f"json:{g}#/descriptives/{a}/{e}" for g in (G1, G1B) for a in ("bio", "bypass")
                   for e in ("post_collision", "wall_collision")]
                  + [f"json:{g}#/secondary/{e}/{k}" for g in (G1, G1B)
                     for e in ("post_collision", "wall_collision") for k in ("diff", "ci95")],
        "rendered_tables": [f"{T}: 'Every arm (descriptive)' and 'Bio minus bypass, secondary endpoints'",
                            f"{TB}: the same two tables"],
        "notes": "Reliable = 95% interval excludes zero (ci95 field). Rates drawn as % of evaluation episodes.",
    },
    {
        "id": "exp1-loops-not-wiring",
        "title": "Post-collision rate for all six arms under occlusion",
        "page": "/projects/steering-circuit/",
        "sources": [G1B, TB],
        "fields": [f"json:{G1B}#/descriptives/{a}/post_collision" for a in ARMS]
                  + [f"json:{G1B}#/seeds_per_arm/{a}" for a in ARMS],
        "rendered_tables": [f"{TB}: 'Every arm (descriptive)', column 'Post-collision episodes'"],
    },
    {
        "id": "exp1-why-stopped",
        "title": "The planned Stage 2 test's smallest detectable difference against the whole gap it would search",
        "page": "/projects/steering-circuit/",
        "sources": [POWER, G1B, PREREG, TB],
        "fields": [f"json:{POWER}#/stage2_table/{i}/{k}" for i in range(12)
                   for k in ("graphs", "seeds_per_graph", "sd_graph", "mde80_two_sided")]
                  + [f"json:{G1B}#/tracked_frac/diff", f"json:{G1B}#/tracked_frac/ci95"],
        "rendered_tables": [f"{PREREG}: section 4.4 Stage 2 power table (20 x 5 rows)",
                            f"{TB}: Verdict table, tracked fraction row"],
        "notes": "Planned design 20 null graphs x 5 seeds (the 5-seed remedy in prereg 4.4). 0.020 is its "
                 "graph-SD 0 row, the most favourable; graph SD 0.03 gives 0.028.",
    },
    {
        "id": "exp1-not-inert",
        "title": "Circuit minus crude two-unit summary, against circuit minus direct connection",
        "page": "/projects/steering-circuit/",
        "sources": [G1, G1B, T, TB],
        "fields": [f"json:{g}#/bio_minus_other_arms_tracked_frac/two_unit/{k}" for g in (G1, G1B)
                   for k in ("diff", "ci95")]
                  + [f"json:{g}#/tracked_frac/{k}" for g in (G1, G1B) for k in ("diff", "ci95")],
        "rendered_tables": [f"{T} and {TB}: 'Bio minus each other arm' (bio - two_unit) and the Verdict table"],
    },
    {
        "id": "exp1-learning-curves",
        "title": "Mean validation tracked fraction by training step, every arm, both conditions",
        "page": "/projects/steering-circuit/",
        "sources": [T, TB, G1, G1B],
        "fields": [f"md:{f}#{CURVE}|{a}|{s}" for f in (T, TB) for a in ARMS for s in STEPS]
                  + [f"json:{g}#/convergence/*/stop_reason" for g in (G1, G1B)],
        "rendered_tables": [f"{T} and {TB}: 'Convergence' and 'Mean validation tracked fraction by step'"],
        "notes": "Each point carries the number of runs still training (n=...). Only the six tabulated steps "
                 "exist in the reports; nothing between them is drawn as data.",
    },
    {
        "id": "exp1-activity",
        "title": "Pre-training output-rate offset of every null graph against the real circuit",
        "page": "/projects/steering-circuit/",
        "sources": [ACT, PREREG],
        "fields": [f"json:{ACT}#/graphs/*/rel_offset_unnormalized", f"json:{ACT}#/bio/rate_output",
                   f"json:{ACT}#/n_flagged"],
        "rendered_tables": [f"{PREREG}: section 6 activity table"],
        "notes": "64 null graphs: L0-L4 (60) plus the parent's four rewired graphs. The bypass entry (no graph) "
                 "is excluded from the plot and mentioned in the page's detail block.",
    },
    {
        "id": "exp2-variability-stop",
        "title": "Measured seed-to-seed variability against the planning value and the stop threshold",
        "page": "/projects/forward-only-training/",
        "sources": [PILOT, P2, R2],
        "fields": [f"json:{PILOT}#/gate/{k}" for k in
                   ("tracking_seed_sd", "collision_seed_sd", "effective_stop_threshold_inclusive",
                    "effective_recompute_threshold_inclusive", "nominal_boundaries", "decision")]
                  + [f"json:{PILOT}#/per_seed_rows/*/{k}" for k in ("metric", "train_seed", "paired_CL_minus_OL")]
                  + [f"json:{P2}#/condition1_exact_model/tracking_seed_sd"]
                  + [f"json:{P2}#/scenario_rows/*/{k}" for k in
                     ("scientific_seed_pairs", "episodes", "tracking_shared_episode_sd", "tracking_seed_sd",
                      "tracking_guardrail_power_true_difference_zero")],
        "rendered_tables": [f"{R2}: Condition 2 gate block"],
        "notes": "Power curve = scenario rows at the planned design (20 seed pairs, 2000 episodes, episode SD "
                 "0.2). The rows stop at seed SD 0.1, so the measured 0.1348 is marked on the axis with no "
                 "power value attached.",
    },
    {
        "id": "exp3-frontier",
        "title": "Recall@10 against queries per second, six methods, SIFT and GloVe",
        "page": "/projects/fly-retrieval/",
        "sources": [EXPORT, B2S, B_MD],
        "fields": [f"csv:{EXPORT}#dataset={d},algorithm={a}|{c}" for d in B2_SETS for a in B2_ALGOS
                   for c in ("k-nn", "qps", "parameters")]
                  + [f"json:{B2S}#/{d}/algorithms/*/max_recall" for d in B2_SETS]
                  + [f"json:{B2S}#/{d}/algorithms/*/front" for d in B2_SETS]
                  + [f"json:{B2S}#/{d}/readout/0.9/{k}" for d in B2_SETS for k in ("best_baseline_qps", "fly")],
        "rendered_tables": [f"{B_MD}: generated B2 tables"],
        "notes": "Each method's line joins only its exported Pareto points (computed from export.csv and "
                 "asserted equal to the analysis' own 'front'). DenseFly's line ends at its last point.",
    },
    {
        "id": "exp3-candidates-touched",
        "title": "FlyHash candidates touched per query against the database size",
        "page": "/projects/fly-retrieval/",
        "sources": [TOUCH, EXPORT, PRE3, B_MD],
        "fields": [f"csv:{TOUCH}#dataset={d}|{c}" for d in B2_SETS for c in ("name", "candidates_touched_per_query")]
                  + [f"csv:{EXPORT}#dataset={d},algorithm=flyhash|{c}" for d in B2_SETS for c in ("parameters", "k-nn")]
                  + [f"md:{PRE3}#**Benchmark data:**|Dataset=`{d}`|Train × dim" for d in B2_SETS],
        "rendered_tables": [f"{B_MD}: 'Why the fly methods are slow'", f"{PRE3}: dataset table (train sizes)"],
        "notes": f"{TOUCH} is copied verbatim from the HDF5 attributes of the 108 FlyHash result files by "
                 "scripts/extract_b2_touched.py; each row carries its result file's SHA-256.",
    },
    {
        "id": "exp3-novelty-filter",
        "title": "Fly Bloom filter minus best production baseline, and misses at a 1% false-alarm rate",
        "page": "/projects/fly-retrieval/",
        "sources": [A_JS, A_MD],
        "fields": [f"json:{A_JS}#/cells/*/{k}" for k in ("dataset", "B", "delta", "delta_ci", "best_production_on_val")]
                  + [f"json:{A_JS}#/cells/*/methods/*/fnr_at_fpr_1pct"],
        "rendered_tables": [f"{A_MD}: Δ table and 'Every method, every cell' (FNR @FPR 1%)"],
    },
    {
        "id": "exp3-null-ladder-imputation",
        "title": "Real wiring against each scrambled control, zero-filled and mean-imputed, both hemispheres",
        "page": "/projects/fly-retrieval/",
        "sources": [B_MD],
        "fields": [f"md:{B_MD}#{ODOUR}|matrix={m},level={lv}|{c}" for m in ("w5_L", "w5_R")
                   for lv in ("N0", "N1", "N3", "NQ") for c in ("Δ zero-filled [95% CI]", "Δ mean-imputed [95% CI]")],
        "rendered_tables": [f"{B_MD}: '{ODOUR}' (generated B1 table), rows w5_L and w5_R"],
        "notes": "Primary threshold w >= 5. Rows are matched on (matrix, level), since the matrix column repeats.",
    },
    {
        "id": "exp3-skew",
        "title": "Real wiring's advantage over its degree-preserving null as queries concentrate",
        "page": "/projects/fly-retrieval/",
        "sources": [C_JS, C_MD],
        "fields": [f"json:{C_JS}#/hemispheres/{h}/cells/{b}|{o}|N1/{k}" for h in ("L", "R")
                   for b in ("0.0", "0.5", "1.0", "1.5", "2.0") for o in ("matched", "mismatched")
                   for k in ("delta", "ci")] + [f"json:{C_JS}#/sesoi"],
        "rendered_tables": [f"{C_MD}: generated table, 'Δ vs N1 [95% CI]' column"],
    },
    {
        "id": "verdicts",
        "title": "The four verdicts",
        "page": "/results/",
        "sources": [G1, G1B, PILOT, A_JS, B2S, C_JS, SYN],
        "fields": [f"json:{G1}#/verdict", f"json:{G1B}#/verdict", f"json:{PILOT}#/gate/decision",
                   f"json:{A_JS}#/verdict/verdict", f"json:{B2S}#/sift-128-euclidean/verdict",
                   f"json:{B2S}#/glove-100-angular/verdict", f"json:{C_JS}#/overall"],
        "rendered_tables": [f"{SYN}: 'Verdicts, as predeclared'"],
        "notes": "Text only; no numbers are drawn.",
    },
]

REPORT = "fly_track/reports/report.md"
CF = "Cost and frontier"
# Numbers quoted in page text that no figure on that page already reads. Every decimal or percentage in a
# new page's visible text must match one of these, a field of a figure shown on that page, or a constant.
PAGES = {
    "/projects/steering-circuit/": [
        f"md:{REPORT}#{CF}|group=classical,impl=np|success [95% CI]",
        f"md:{REPORT}#{CF}|group=fly_bio,impl=dense|success [95% CI]",
        f"json:{G1}#/tracked_frac/mean_a", f"json:{G1}#/tracked_frac/mean_b",
        f"json:{G1B}#/tracked_frac/mean_a", f"json:{G1B}#/tracked_frac/mean_b",
        f"json:{G1}#/success/diff", f"json:{G1}#/success/ci95", f"json:{G1B}#/success/diff", f"json:{G1B}#/success/ci95",
        f"md:{TB}#Realized precision|Endpoint=success,Arm=bio|Ratio",
        f"json:{G1}#/bio_minus_other_arms_tracked_frac/rew1003/diff",
    ],
    "/projects/forward-only-training/": [],
    "/projects/fly-retrieval/": [
        f"json:{B2S}#/{d}/readout/0.9/fly/flyhash/ratio_to_best_baseline" for d in B2_SETS
    ] + [
        f"mdtext:{B_MD}#with his filter reproduced exactly: 35 glomeruli, 172 odorants, ([0-9.]+)% unmeasured",
        f"mdtext:{B_MD}#His odour primary is \\*\\*([^*]+)%\\*\\*",
        f"md:{B_MD}#{ODOUR}|matrix=w1_R,level=N1|Δ zero-filled [95% CI]",
        f"md:{B_MD}#{ODOUR}|matrix=w5_L,level=N1|Δ zero-filled [95% CI]",
    ],
    "/results/": [],
    "/": [],
}
# Method constants that appear in page text: thresholds and levels, not results.
CONSTANTS = [
    {"value": 0.95, "why": "the confidence level of every interval ('95% confident', '95% range')",
     "source": f"md:{T}#**G1: NO-GO**|Tracked fraction (primary)|Estimate [95% CI]"},
    {"value": 0.9, "why": "the 90% accuracy (recall@10 0.9) readout level",
     "source": f"json:{B2S}#/sift-128-euclidean/readout/0.9/best_baseline_qps"},
    {"value": 0.95, "why": "the 95% accuracy readout level FlyHash never reaches on GloVe",
     "source": f"json:{B2S}#/glove-100-angular/readout/0.95/best_baseline_qps"},
    {"value": 0.01, "why": "the 1% false-alarm rate of the miss-rate comparison",
     "source": f"json:{A_JS}#/cells/0/methods/FBF/fnr_at_fpr_1pct"},
    {"value": 0.025, "why": "the +2.5% benefit margin set in advance (EXP3 B1 and C)",
     "source": f"json:{C_JS}#/sesoi"},
]

# Read during the inventory, not plotted. Recorded so the read is auditable.
INVENTORY_ONLY = [
    ("fly_track/reports/stage0_diagnostics.md", "context for the activity confound (finding 6) and post/wall split"),
    ("fly_track/reports/exp1c/ladder.json", "null-ladder rung properties; rung labels only"),
    ("fly_track/reports/exp1c/evalsets.json", "fresh evaluation-set definitions"),
    ("fly_track/reports/report.md", "parent experiment results; cited in page text only"),
    ("fly_track/analysis.md", "parent analysis (the brief's docs/analysis.md does not exist; this is the file)"),
    ("fly_retrieval/reports/trackB2_costs.json", "insertion and encoding costs; cited in page details only"),
]
NOT_FOUND = {
    "fly_track/docs/analysis.md": "does not exist; the parent analysis is fly_track/analysis.md",
    "fly_retrieval/reports/exp3_analysis.md": "does not exist; the synthesis is fly_retrieval/docs/exp3_analysis.md",
}
NOT_PLOTTED_DIRS = {
    "fly_track/raw_results_exp1c/stage1/": "per-episode data; every plotted EXP1 number is the frozen analysis' "
                                            "aggregate in g1.json, so nothing is re-derived from episodes",
    "fly_track/raw_results_exp1c/stage1b/": "as above, for g1b.json",
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=str(REPO.parent))
    ws = Path(ap.parse_args().workspace).resolve()
    files = {}
    for fig in FIGURES:
        for rel in fig["sources"] + [REPORT]:
            if rel in files:
                continue
            v = sha256(VENDORED / rel)
            orig = ws / rel if rel != TOUCH else None
            o = sha256(orig) if orig else None
            if o is not None and o != v:
                raise SystemExit(f"vendored copy differs from workspace original: {rel}")
            files[rel] = {"sha256": v, "served_at": f"/results/sources/{rel}",
                          "origin": "workspace file, copied byte for byte" if orig else
                          "derived verbatim from HDF5 attributes by scripts/extract_b2_touched.py"}
    manifest = {
        "about": "Every figure on the EXP1-EXP3 result pages, the exact fields it reads and the SHA-256 of each "
                 "source file at read time. Paths are relative to the Flybrain workspace; copies are served "
                 "from /results/sources/. See scripts/write_manifest.py for the selector grammar.",
        "files": dict(sorted(files.items())),
        "figures": FIGURES,
        "pages": PAGES,
        "constants": CONSTANTS,
        "inventory_only": [{"file": f, "sha256": sha256(ws / f), "use": u} for f, u in INVENTORY_ONLY],
        "expected_but_not_found": NOT_FOUND,
        "not_plotted": NOT_PLOTTED_DIRS,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(FIGURES)} figures, {len(files)} source files -> {OUT}")


if __name__ == "__main__":
    main()
