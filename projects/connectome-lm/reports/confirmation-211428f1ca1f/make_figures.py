"""Render presentation figures from immutable experiment artifacts; no model execution.

PYTHONPATH=fly_connectome_lm/src .venv/bin/python fly_connectome_lm/reports/confirmation-211428f1ca1f/make_figures.py
"""
from __future__ import annotations
import html
import json
import os
from pathlib import Path
import zipfile
os.environ.setdefault('MPLCONFIGDIR', '/tmp/fly-lm-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
import networkx as nx
import numpy as np
from fly_connectome_lm.util import ROOT, read_json, sha256, code_hash, atomic_json, now
from fly_connectome_lm.graph_extract import Graph

HERE = Path(__file__).resolve().parent
OUT = HERE / 'figures'
OUT.mkdir(exist_ok=True)
CONDITIONS = ['FLY-TOPOLOGY', 'DEGREE-REWIRED', 'RANDOM-DENSITY', 'PARAMETER-MATCHED-GRU', 'NO-CROSS-NODE-RECURRENCE']
LABELS = dict(zip(CONDITIONS, ['Fly topology', 'Degree-rewired', 'Random-density', 'Conventional GRU', 'Independent memory']))
COLORS = dict(zip(CONDITIONS, ['#16816A', '#D77C44', '#4285B4', '#7561AD', '#83939E']))
BG, INK, MUTED, GRID = '#F7F8FC', '#1E3443', '#627786', '#DDE5EB'
SEEDS = [11, 22, 33, 44, 55]
font = Path('/System/Library/Fonts/Avenir Next.ttc')
if font.exists():
    font_manager.fontManager.addfont(str(font))
    family = font_manager.FontProperties(fname=str(font)).get_name()
else:
    family = 'DejaVu Sans'
plt.rcParams.update({'font.family': [family, 'DejaVu Sans'], 'font.size': 11, 'text.color': INK,
    'axes.labelcolor': MUTED, 'axes.edgecolor': GRID, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.titleweight': 'bold', 'axes.titlesize': 15, 'axes.titlepad': 18,
    'axes.labelsize': 11, 'axes.labelpad': 12, 'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': BG, 'axes.facecolor': 'white', 'savefig.facecolor': BG,
    'pdf.fonttype': 42, 'svg.fonttype': 'none', 'axes.unicode_minus': True})

test_path = ROOT / 'reports/final-evaluation-ffb133aefbbd.json'
test = read_json(test_path)['records']
training = {r['run_id']: r for r in read_json(HERE / 'run-values.json')}
effects = read_json(HERE / 'final-test-effects.json')['best']
audit = read_json(HERE / 'final-audit.json')
assert len(test) == 35 and audit['status'] == 'passed'
assert code_hash() == audit['code_hash']
frozen = ROOT / 'configs/confirmation-frozen.json'
assert sha256(frozen) == audit['freeze_sha256']
for row in test:
    assert sha256(ROOT / 'runs' / row['run_id'] / 'test.json') == audit['test_artifact_sha256'][row['run_id']]
protected = [frozen, ROOT / 'docs/analysis_plan.md', test_path]
protected += [ROOT / 'runs' / r['run_id'] / name for r in test for name in ['test.json', 'result.json', 'history.json']]
before = {str(p.relative_to(ROOT)): sha256(p) for p in protected}
diagnostics = read_json(HERE / 'validation-diagnostics-review.json')['records']
histories = {}
for row in test:
    vals = [v for v in read_json(ROOT / 'runs' / row['run_id'] / 'history.json') if 'validation' in v]
    assert [v['step'] for v in vals] == list(range(1000, 20001, 1000))
    histories[row['run_id']] = vals
curves = {}
for condition in CONDITIONS:
    seed_curves, seed_times = [], []
    for seed in SEEDS:
        rs = [r for r in test if r['condition'] == condition and r['training_seed'] == seed]
        assert len(rs) == (3 if condition == 'DEGREE-REWIRED' else 1)
        seed_curves.append(np.mean([[v['validation']['bpb'] for v in histories[r['run_id']]] for r in rs], axis=0))
        seed_times.append(np.mean([[v['training_seconds'] for v in histories[r['run_id']]] for r in rs], axis=0))
    curves[condition] = {'seed_bpb': np.array(seed_curves), 'seed_seconds': np.array(seed_times)}

def canvas(number, title, subtitle, height=8.5):
    fig = plt.figure(figsize=(15, height))
    fig.text(.05, .952, f'MALECNS / LANGUAGE EXPERIMENT                                      {number:02d}   •   CONFIRMATION',
             fontsize=10, color=MUTED, weight='medium')
    fig.text(.05, .887, title, fontsize=28, weight='bold')
    fig.text(.05, .841, subtitle, fontsize=12, color=MUTED)
    return fig

def footer(fig, text):
    fig.text(.05, .035, text, fontsize=9.5, color=MUTED, va='bottom', linespacing=1.6)

def style(ax, axis='x'):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color=GRID, lw=.8, alpha=.8)
    ax.tick_params(length=0, pad=8)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(GRID)

def legend(fig, y=.76):
    handles = [Line2D([0], [0], color=COLORS[c], lw=3, label=LABELS[c]) for c in CONDITIONS]
    fig.legend(handles=handles, loc='center', bbox_to_anchor=(.52, y), ncol=5,
               frameon=False, fontsize=10.5, handlelength=1.7, columnspacing=1.8)

FIGURES = []
pdf = PdfPages(OUT / 'experiment-figures.pdf')

def save(fig, name, caption):
    fig.savefig(OUT / f'{name}.png', dpi=220)
    fig.savefig(OUT / f'{name}.svg')
    fig.savefig(OUT / f'{name}.pdf')
    pdf.savefig(fig)
    FIGURES.append({'name': name, 'caption': caption})
    plt.close(fig)
    print(f'Rendered {name}', flush=True)


# 01: individual runs and means, paired uncertainty, with no invented error bars.
fig = canvas(1, 'Does fly wiring help predict text?', 'Held-out test • 35 completed runs • 512 neurons / 3,061 directed connections')
ax = fig.add_axes([.18, .23, .38, .49])
style(ax)
ax.axhspan(-.44, .44, color=COLORS[CONDITIONS[0]], alpha=.045, zorder=0)
for i, c in enumerate(CONDITIONS):
    rs = sorted([r for r in test if r['condition'] == c], key=lambda r: (r['training_seed'], r['null_index']))
    values = np.array([r['best']['bpb'] for r in rs])
    offset = np.linspace(-.18, .18, len(rs))
    ax.scatter(values, i + offset, s=37, facecolors='white', edgecolors=COLORS[c], lw=1.3, zorder=3)
    ax.scatter(values.mean(), i, marker='D', s=94, color=COLORS[c], edgecolors='white', linewidths=1, zorder=4)
    ax.text(2.733, i, f'{values.mean():.4f}', fontsize=12, weight='bold', va='center', ha='right', color=COLORS[c])
ax.set(yticks=range(5), yticklabels=[LABELS[c] for c in CONDITIONS], ylim=(4.6, -.6), xlim=(2.52, 2.742),
       xlabel='Test bits per byte  ·  lower is better')
ax.xaxis.set_major_locator(MultipleLocator(.05))
ax.set_title('A   Final prediction performance', loc='left')
ax2 = fig.add_axes([.68, .40, .27, .25]); style(ax2)
p = effects['per_graph']['101']; lo, hi = p['ci95']; mean = p['mean_delta']
ax2.axvline(0, color=INK, lw=1)
ax2.axvline(.02, color=COLORS[CONDITIONS[0]], linestyle=(0, (3, 3)), lw=1.3)
ax2.errorbar(mean, 0, xerr=[[mean-lo], [hi-mean]], fmt='D', color=INK, ms=9, lw=3, capsize=6, zorder=5)
for i, pair in enumerate(effects['pairs']):
    ax2.scatter(pair['delta'], .38 + .04 * (i % 2), color=MUTED, alpha=.75, s=32)
ax2.set(xlim=(-.033, .029), ylim=(-.55, .85), yticks=[], xlabel='Rewired BPB − fly BPB')
ax2.xaxis.set_major_locator(MultipleLocator(.02))
ax2.set_title('B   The primary comparison', loc='left', y=1.18)
fig.text(.68, .265, f'Mean {mean:+.4f} BPB', fontsize=18, weight='bold')
fig.text(.68, .217, f'95% paired interval [{lo:+.4f}, {hi:+.4f}]', fontsize=11, color=MUTED)
fig.text(.68, .16, 'No fly-wiring advantage established.', fontsize=13, color=COLORS[CONDITIONS[0]], weight='bold')
footer(fig, 'A: hollow circles = individual runs; diamonds = means. Rewired has 15 runs; each other arm has 5.\n'
       'B: dots = five paired seed effects; interval = 10,000 seed-level bootstrap resamples. Dashed line = chosen +0.02 practical threshold. One graph, one specimen.')
save(fig, '01-results-overview', 'Final test performance and the predeclared paired effect. The interval crosses zero; five seeds offer limited uncertainty.')

# 02: show every paired result; independent observations remain the five seeds.
fig = canvas(2, 'The controlled comparison, seed by seed', 'Same nodes, degrees, trainable count, interfaces, data order and training budget; different connection partners.')
left = fig.add_axes([.1, .20, .37, .51]); style(left, 'y')
left.set_title('A   Fly and its three rewired controls', loc='left')
for i, pair in enumerate(effects['pairs']):
    fly, vals = pair['fly_bpb'], pair['rewired_bpbs']
    null = float(np.mean(vals))
    left.plot([i-.16, i+.16], [fly, null], color=MUTED, alpha=.5, lw=1.4)
    left.scatter(i-.16, fly, s=70, color=COLORS[CONDITIONS[0]], zorder=4)
    left.scatter([i+.12, i+.16, i+.20], vals, s=32, facecolors='white', edgecolors=COLORS[CONDITIONS[1]], zorder=3)
    left.scatter(i+.16, null, s=72, marker='D', color=COLORS[CONDITIONS[1]], edgecolors='white', zorder=4)
left.set(xticks=range(5), xticklabels=SEEDS, xlabel='Training seed', ylabel='Test bits per byte  ·  lower is better', xlim=(-.55, 4.55), ylim=(2.604, 2.658))
left.legend(handles=[Line2D([], [], color=COLORS[CONDITIONS[0]], marker='o', ls='', label='Fly'),
    Line2D([], [], color=COLORS[CONDITIONS[1]], marker='D', ls='', label='Rewired mean'),
    Line2D([], [], color=COLORS[CONDITIONS[1]], marker='o', mfc='white', ls='', label='Individual control')],
    frameon=False, fontsize=9, ncol=3, loc='upper center', bbox_to_anchor=(.5, 1.03))
right = fig.add_axes([.63, .20, .31, .51]); style(right)
right.axvspan(-.035, 0, color=COLORS[CONDITIONS[1]], alpha=.055)
right.axvspan(0, .03, color=COLORS[CONDITIONS[0]], alpha=.045)
right.axvline(0, color=INK, lw=1)
right.axvline(.02, color=COLORS[CONDITIONS[0]], linestyle=(0, (3, 3)))
for i, pair in enumerate(effects['pairs']):
    right.plot([0, pair['delta']], [i, i], color=MUTED, lw=1.2, alpha=.6)
    right.scatter(pair['delta'], i, s=66, color=COLORS[CONDITIONS[1] if pair['delta'] < 0 else CONDITIONS[0]], zorder=4)
right.axhline(4.55, color=GRID)
right.errorbar(mean, 5.3, xerr=[[mean-lo], [hi-mean]], fmt='D', color=INK, ms=9, lw=2.8, capsize=5)
right.set(xlim=(-.035, .03), ylim=(6.05, -.6), yticks=[0, 1, 2, 3, 4, 5.3],
          yticklabels=[f'Seed {s}' for s in SEEDS] + ['Mean / 95% CI'], xlabel='Mean rewired BPB − fly BPB')
right.xaxis.set_major_locator(MultipleLocator(.02))
right.set_title('B   Paired differences', loc='left')
fig.text(.645, .09, '← favors rewiring', color=COLORS[CONDITIONS[1]], fontsize=11)
fig.text(.805, .09, 'favors fly →', color=COLORS[CONDITIONS[0]], fontsize=11)
footer(fig, 'The three controls are averaged before pairing with their fly model. The five seed-level effects are the bootstrap units.\n'
       'Dashed line = the predeclared +0.02 BPB practical-effect threshold. A reused fly model is never counted as three independent observations.')
save(fig, '02-paired-comparison', 'All five matched comparisons and all 15 rewired test scores, with the primary seed-level bootstrap interval.')

# 03: no smoothing or extra test evaluations; validation curves from saved logs.
fig = canvas(3, 'How the models learned', 'Validation loss across the full training budget • the held-out test was evaluated separately after training.')
legend(fig)
xs = np.arange(1, 21) * 1.024
for rect, title, zoom in [([.09, .20, .38, .49], 'A   Full learning trajectory', False),
                          ([.58, .20, .36, .49], 'B   Later training, expanded', True)]:
    ax = fig.add_axes(rect); style(ax, 'both')
    for c in CONDITIONS:
        y = curves[c]['seed_bpb']
        ax.fill_between(xs, y.min(0), y.max(0), color=COLORS[c], alpha=.10, linewidth=0)
        ax.plot(xs, y.mean(0), color=COLORS[c], lw=2.5, marker='o', ms=2.7)
    ax.set(xlabel='Cumulative training targets (millions)', ylabel='Validation bits per byte', xlim=(10, 20.6) if zoom else (0, 20.6))
    if zoom: ax.set_ylim(2.31, 2.83)
    ax.set_title(title, loc='left')
footer(fig, 'Lines = means across five training seeds. For rewired models, the three controls are averaged within each seed first.\n'
       'Bands = minimum–maximum across those five seed values, not confidence intervals. Each point is a logged validation evaluation; no smoothing.')
save(fig, '03-learning-curves', 'Validation curves versus training-byte exposures. Shaded ranges show seed variability, with a separate late-training view.')

# 04: record actual time, without passing this off as the unrun fixed-time protocol.
fig = canvas(4, 'Training time changes the picture', 'Measured CPU time from the completed fixed-byte experiment • validation time is excluded.')
legend(fig)
ax = fig.add_axes([.1, .21, .83, .48]); style(ax, 'both')
for c in CONDITIONS:
    times, ys = curves[c]['seed_seconds'], curves[c]['seed_bpb']
    ax.plot(times.mean(0) / 60, ys.mean(0), color=COLORS[c], lw=2.7, marker='o', ms=3.2)
    ax.scatter(times[:, -1] / 60, ys[:, -1], color=COLORS[c], s=25, alpha=.5)
ax.set(xlabel='Elapsed training time (minutes)', ylabel='Validation bits per byte', xlim=(0, 9))
footer(fig, 'Means are taken at matched update checkpoints; rewired controls are averaged within seed before averaging seeds. Dots at the right ends show seed endpoints.\n'
       'Same device / precision / threads. These are timing traces from fixed-byte runs, not a separate equal-time experiment or a universal hardware benchmark.')
save(fig, '04-learning-versus-time', 'Measured validation trajectories against CPU training time. This is not the separately planned fixed-time protocol.')

# 05: all active parameters included; core includes graph bias and GRU gates/biases.
fig = canvas(5, 'What was matched — and what was different', 'Equal training data and near-equal total parameters do not imply equal allocation or compute.')
axs = [fig.add_axes([.18, .23, .33, .48]), fig.add_axes([.64, .23, .29, .48])]
for a in axs: style(a)
for i, c in enumerate(CONDITIONS):
    rs = [r for r in training.values() if r['condition'] == c]
    a = rs[0]['accounting']; interfaces = a['interface_parameters']; core = a['active_trainable_parameters'] - interfaces
    assert interfaces + core == a['active_trainable_parameters']
    axs[0].barh(i, interfaces / 1000, height=.53, color='#CED9E2')
    axs[0].barh(i, core / 1000, left=interfaces / 1000, height=.53, color=COLORS[c])
    axs[0].text(a['active_trainable_parameters']/1000+1, i, f'{a["active_trainable_parameters"]:,}', va='center', fontsize=10)
    ts = np.array([r['training_seconds'] / 60 for r in rs])
    axs[1].barh(i, ts.mean(), height=.53, color=COLORS[c], alpha=.85)
    axs[1].scatter(ts, i+np.linspace(-.15, .15, len(ts)), s=20, facecolors='white', edgecolors=COLORS[c], lw=.8)
    axs[1].text(ts.mean()+.16, i, f'{ts.mean():.2f} min', va='center', fontsize=10)
axs[0].set(yticks=range(5), yticklabels=[LABELS[c] for c in CONDITIONS], ylim=(4.6, -.6), xlim=(0, 64), xlabel='Active trainable parameters (thousands)')
axs[1].set(yticks=[], ylim=(4.6, -.6), xlim=(0, 10.8), xlabel='Mean training time (minutes)')
axs[0].set_title('A   Parameter allocation', loc='left'); axs[1].set_title('B   Observed training time', loc='left')
fig.legend(handles=[Patch(color='#CED9E2', label='Text input / output interfaces'), Patch(color=INK, label='Recurrent core, including biases')],
    frameon=False, fontsize=10, ncol=2, loc='center', bbox_to_anchor=(.52, .775))
footer(fig, 'All runs: 20,000 updates × 8 windows × 128 targets = 20.48 million training-byte exposures. CPU float32, two threads.\n'
       'The GRU uses gates and a different state width. Independent memory is an ablation with fewer parameters; it is not parameter matched.')
save(fig, '05-parameters-and-runtime', 'Complete active parameter accounting and observed training time, with all individual run timings visible.')

# 06: validation-only dependence heatmap, one common quantitative color scale.
fig = canvas(6, 'The models use their recurrent memory', 'Predeclared interventions on trained models • validation only • larger increases mean more damage to prediction.')
matrix = np.full((5, 3), np.nan)
baselines = []
for i, c in enumerate(CONDITIONS):
    ds = [r['diagnostics'] for r in diagnostics if r['condition'] == c]
    baselines.append(float(np.mean([r['baseline_validation']['bpb'] for r in ds])))
    for j, key in enumerate(['perturb_10_percent', 'reset_each_byte', 'zero_core']):
        values = [r[key]['bpb'] - r['baseline_validation']['bpb'] for r in ds if key in r]
        if values: matrix[i, j] = np.mean(values)
heat = LinearSegmentedColormap.from_list('dependence', ['#F0F4F7', '#C1DDD5', '#62A78F', '#176B59'])
heat.set_bad('#EEF0F3')
ax = fig.add_axes([.26, .22, .59, .48])
im = ax.imshow(matrix, cmap=heat, vmin=0, vmax=2.5, aspect='auto')
ax.set(yticks=range(5), yticklabels=[LABELS[c] for c in CONDITIONS], xticks=range(3),
       xticklabels=['Zero 10% of coefficients', 'Reset state every byte', 'Zero recurrent core'])
ax.tick_params(axis='both', length=0, pad=12)
ax.xaxis.tick_top()
for spine in ax.spines.values(): spine.set_visible(False)
for i in range(5):
    for j in range(3):
        v = matrix[i, j]
        ax.text(j, i, f'+{v:.3f}' if np.isfinite(v) else 'Not applied', ha='center', va='center',
                fontsize=17 if np.isfinite(v) else 11, color='white' if v > 1.55 else INK, weight='medium')
ax.set_xticks(np.arange(-.5, 3, 1), minor=True); ax.set_yticks(np.arange(-.5, 5, 1), minor=True)
ax.grid(which='minor', color=BG, linewidth=5); ax.tick_params(which='minor', length=0)
cax = fig.add_axes([.89, .22, .013, .48]); cb=fig.colorbar(im, cax=cax); cb.outline.set_visible(False)
cb.set_label('Increase in validation bits per byte', labelpad=12)
footer(fig, 'Values are intervention BPB minus the unmodified model’s validation BPB, averaged over all runs in that condition. Test scores and saved checkpoints are unchanged.\n'
       'Interventions differ by architecture. Parameter damage demonstrates dependence on recurrence; it does not establish a benefit from the fly’s particular wiring.')
save(fig, '06-recurrence-diagnostics', 'Validation-only changes after disrupting recurrence. Positive values show worse prediction; they do not establish a special fly-wiring benefit.')

# 07: actual labelled graphs, one fixed null chosen by seed/index, never by result.
base_path = ROOT / 'data/processed/fly-n512-sample101.npz'
base = Graph.load(base_path)
null_row = next(r for r in test if r['condition'] == 'DEGREE-REWIRED' and r['training_seed'] == 11 and r['null_index'] == 1)
meta = read_json(ROOT / 'runs' / null_row['run_id'] / 'manifest.json')['metadata']
null_path = ROOT / 'data/processed/controls' / f'degree-rewired-{base.hash[:12]}-seed{meta["null_seed"]}.npz'
null = Graph.load(null_path)
assert len(base.ids) == len(null.ids) == 512 and len(base.source) == len(null.source) == 3061
assert np.array_equal(base.ids, null.ids)
for attr in ['source', 'target']:
    assert np.array_equal(np.bincount(getattr(base, attr), minlength=512), np.bincount(getattr(null, attr), minlength=512))
layout_graph = nx.Graph()
layout_graph.add_nodes_from(range(512)); layout_graph.add_edges_from(zip(base.source.tolist(), base.target.tolist()))
layout = nx.spring_layout(layout_graph, seed=101, iterations=100)
xy = np.array([layout[i] for i in range(512)])
degree = np.bincount(base.source, minlength=512) + np.bincount(base.target, minlength=512)
sizes = 5 + 2 * np.sqrt(degree)
overlap = len(set(zip(base.source, base.target)) & set(zip(null.source, null.target))) / 3061
fig = canvas(7, 'Same neurons. Different connection partners.', 'Real MaleCNS adjacency and one degree-preserving control • identical node positions and identical per-node degree counts.', height=10)
for graph, x, c, title in [(base, .10, CONDITIONS[0], 'Original fly wiring'), (null, .57, CONDITIONS[1], 'Rewired control')]:
    ax = fig.add_axes([x, .44, .35, .33])
    segments = np.stack([xy[graph.source], xy[graph.target]], axis=1)
    ax.add_collection(LineCollection(segments, colors=COLORS[c], alpha=.12, linewidths=.40, rasterized=False))
    ax.scatter(xy[:, 0], xy[:, 1], s=sizes, color=COLORS[c], alpha=.87, edgecolors='white', linewidths=.13, zorder=3)
    ax.set(xlim=(-1.12, 1.12), ylim=(-1.12, 1.12), aspect='equal'); ax.axis('off')
    ax.set_title(title, fontsize=17, color=COLORS[c], loc='center', pad=8)
    adj = fig.add_axes([x+.082, .17, .19, .25])
    adj.scatter(graph.source, graph.target, marker='s', s=.9, color=COLORS[c], linewidths=0)
    adj.set(xlim=(-1, 512), ylim=(512, -1), aspect='equal', xlabel='Source node index', ylabel='Target node index',
            xticks=[0, 256, 511], yticks=[0, 256, 511])
    adj.tick_params(labelsize=8, length=0, pad=3); adj.xaxis.label.set_size(9); adj.yaxis.label.set_size(9)
fig.text(.51, .355, f'{overlap:.1%}\nof directed\nedges shared', ha='center', va='center', fontsize=11, color=MUTED)
footer(fig, 'Top: a shared abstract spring layout, not anatomical coordinates; arrowheads are omitted for clarity. Bottom: directed adjacency (source → target).\n'
       'Control = training seed 11, null 1, chosen by identifier. 512 real neuron IDs / 3,061 directed pairs; each node’s incoming and outgoing counts match exactly.')
save(fig, '07-wiring-and-control', 'Actual 512-node fly and rewired graphs, a common abstract layout, and directed adjacency matrices. Layout is not anatomy.')
pdf.close()

for rel, h in before.items():
    assert sha256(ROOT / rel) == h, f'Protected artifact changed: {rel}'
assert code_hash() == audit['code_hash']
plot_data = {'test_records': test, 'primary_effects': effects, 'validation_curves': {
    c: {'steps': list(range(1000, 20001, 1000)), 'training_targets_millions': xs.tolist(),
        'seeds': SEEDS, **{k: v.tolist() for k, v in values.items()}} for c, values in curves.items()},
    'intervention_bpb_increase': {'rows': CONDITIONS, 'columns': ['perturb_10_percent', 'reset_each_byte', 'zero_core'],
        'values': [[float(v) if np.isfinite(v) else None for v in row] for row in matrix]},
    'graph_comparison': {'base_hash': base.hash, 'null_hash': null.hash, 'null_run_id': null_row['run_id'],
        'layout': 'Undirected fly adjacency used for visualization-only spring layout; seed101; 100 iterations; same positions in both panels.',
        'node_xy': xy.tolist(), 'ids': [str(v) for v in base.ids], 'source': base.source.tolist(), 'target': base.target.tolist(),
        'null_source': null.source.tolist(), 'null_target': null.target.tolist(), 'directed_edge_overlap': overlap}}
atomic_json(OUT / 'plot-data.json', plot_data)
receipt = {'generated_utc': now(), 'source_code_hash': code_hash(), 'freeze_sha256': sha256(frozen),
           'input_artifact_sha256': before, 'renderer_sha256': sha256(Path(__file__)), 'font': family,
           'figures': FIGURES, 'no_training_or_model_inference': True, 'protected_artifacts_unchanged': True,
           'uncertainty': 'Only primary comparison uses a CI: fixed 10,000 paired-seed bootstrap from audited results. Learning bands are seed min/max.',
           'checks': ['35 complete test records match final audit hashes', '20 logged validation evaluations per run',
                      'five seed curves per condition, averaging three rewired controls within each seed',
                      'exact labelled node IDs/in/out degrees and counts in graph comparison',
                      'all source data, test results, histories, freeze, analysis plan and experiment code unchanged'],
           'outputs_sha256': {p.name: sha256(p) for p in sorted(OUT.iterdir()) if p.suffix in ('.png', '.svg', '.pdf')}}
atomic_json(OUT / 'provenance.json', receipt)
cards = []
for entry in FIGURES:
    name, caption = entry['name'], entry['caption']
    cards.append(f'<article><a href="{name}.png"><img loading="lazy" src="{name}.png" alt="{html.escape(caption)}"></a>'
                 f'<div class="caption"><p>{html.escape(caption)}</p><nav><a href="{name}.png">PNG</a>'
                 f'<a href="{name}.svg">SVG</a><a href="{name}.pdf">PDF</a></nav></div></article>')
page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MaleCNS experiment — figures</title><style>
*{box-sizing:border-box}body{margin:0;background:#f0f3f8;color:#1e3443;font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1240px;margin:70px auto;padding:0 28px}header{margin-bottom:36px}.eyebrow{font-size:12px;letter-spacing:2px;color:#627786;font-weight:600}
h1{font-size:clamp(30px,5vw,52px);line-height:1.15;letter-spacing:-1.4px;margin:18px 0}header p{max-width:810px;color:#627786}
a{color:#16816a;text-decoration:none}a:hover{text-decoration:underline}.downloads{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}
.downloads a{padding:10px 18px;background:white;border:1px solid #dce5e9;border-radius:9px;font-weight:600;font-size:14px}
article{margin:0 0 34px;background:white;border:1px solid #dce5e9;border-radius:14px;overflow:hidden;box-shadow:0 8px 28px #1e344305}
img{width:100%;display:block}.caption{padding:8px 25px 20px;display:flex;justify-content:space-between;gap:20px;align-items:center}
.caption p{font-size:14px;color:#627786;max-width:880px}.caption nav{white-space:nowrap;display:flex;gap:15px;font-size:13px;font-weight:600}
footer{font-size:13px;color:#627786;margin:35px 0}@media(max-width:650px){main{margin:30px auto;padding:0 12px}.caption{display:block}}
</style><main><header><div class="eyebrow">REAL MALECNS CONNECTIVITY / FROZEN CONFIRMATION</div><h1>What the experiment shows.</h1>
<p>Seven figures from the completed 35-run comparison. The fly wiring showed no established advantage on this text task.
The primary paired interval crosses zero; five seeds and one graph limit what we can infer.</p>
<div class="downloads"><a href="experiment-figures.pdf">All figures · PDF</a><a href="experiment-figures.zip">Download complete collection</a>
<a href="../final-review.md">Full research report</a><a href="plot-data.json">Plot data</a></div></header>'''
page += '\n'.join(cards)
page += '<footer>Figures use saved logs and audited test artifacts. No training or model inference was run to make them. '
page += 'Test results, validation diagnostics, and graph illustrations are labelled separately. '
page += '<a href="provenance.json">Data and rendering provenance</a>.</footer></main></html>'
(OUT / 'index.html').write_text(page)
(OUT / 'CAPTIONS.txt').write_text('MaleCNS confirmation: scientific figure collection\n\n' + '\n\n'.join(f'{v["name"]}: {v["caption"]}' for v in FIGURES)
    + '\n\nReproduce from workspace root:\nPYTHONPATH=fly_connectome_lm/src .venv/bin/python fly_connectome_lm/reports/confirmation-211428f1ca1f/make_figures.py\n')
with zipfile.ZipFile(OUT / 'experiment-figures.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.suffix != '.zip': archive.write(p, p.name)
    archive.write(Path(__file__), 'make_figures.py')
print(f'Saved {len(FIGURES)} figures, PDF collection, local gallery and ZIP in {OUT}', flush=True)
