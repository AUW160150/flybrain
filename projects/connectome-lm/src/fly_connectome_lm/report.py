from __future__ import annotations
import os
import shlex
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/fly-lm-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .util import ROOT,read_json,atomic_json,sha256,now
from .statistics import paired_effects
from .graph_extract import Graph
from .experiment import graph_path

COLORS={'FLY-TOPOLOGY':'#1b7f3a','DEGREE-REWIRED':'#ad5520','RANDOM-DENSITY':'#3059b1',
        'PARAMETER-MATCHED-GRU':'#8241a0','NO-CROSS-NODE-RECURRENCE':'#697477',
        'TRANSFORMER':'#c4436f','FROZEN-FLY':'#5ca091','COUNT-INIT':'#9d8540','SHUFFLED-COUNT-INIT':'#393939'}

def report(bundle_path:Path,output:Path|None=None) -> Path:
    bundle=read_json(bundle_path); out=output or ROOT/'reports'/bundle_path.stem; out.mkdir(parents=True,exist_ok=True)
    records=[]; manifests=[]; failures=[]; missing=[]
    for name in bundle['run_ids']:
        path=ROOT/'runs'/name
        if not (path/'manifest.json').exists(): missing.append(name); continue
        manifest=read_json(path/'manifest.json'); manifests.append(manifest)
        if manifest['status']!='complete': failures.append({'run_id':name,'status':manifest['status'],'failure':manifest.get('failure')}); continue
        result=read_json(path/'result.json'); result['run_id']=name; records.append(result)
    profile=bundle['profile'].upper(); sealed=[]
    for r in records:
        path=ROOT/'runs'/r['run_id']/'test.json'
        if path.exists():
            value=read_json(path); sealed.append({**value,'bpb':value['best']['bpb']})
    complete=len(records)==len(bundle['run_ids'])
    heading=f'# {profile} — small connectome-constrained language model\n'
    if bundle.get('synthetic'): heading+='\nSYNTHETIC SOFTWARE SMOKE. Not MaleCNS scientific evidence.\n'
    if profile=='SMOKE': conclusion='Software smoke only. These results are not evidence that fly wiring helps. No pilot, confirmation or test-set result is implied.'
    elif not sealed: conclusion='Validation-only comparison. The sealed test set has not been evaluated. No confirmatory topology conclusion is available.'
    elif len(sealed)<len(bundle['run_ids']): conclusion='Incomplete final test matrix. No complete primary conclusion available.'
    else: conclusion='Final test results available for the frozen matrix; inspect paired effects and limitations below.'
    lines=[heading,conclusion,'',f'Report generated {now()}. Completed {len(records)}/{len(bundle["run_ids"])} runs. Failed/incomplete {len(failures)}, missing {len(missing)}.',
           '',f'Code SHA-256: `{bundle["code_hash"]}`. Git revision: `{manifests[0]["git_revision"] if manifests else None}` (null means unavailable).',
           f'Corpus manifest SHA-256: `{bundle["corpus_manifest_sha256"]}`.',
           f'Analysis plan SHA-256: `{bundle["analysis_plan"]["sha256"]}`. Freeze: `{bundle.get("freeze_hash")}`.',
           '',f'Command argv: `{bundle["command"]}`.',
           '', '| Condition | Sample / seed / null | Best validation BPB | Final validation BPB | Byte exposures | Selected step | Train seconds |',
           '|---|---|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f'| {r["condition"]} | {r["sampling_seed"]}/{r["training_seed"]}/{r["null_index"]} | {r["validation_best"]["bpb"]:.6f} | {r["validation_final"]["bpb"]:.6f} | {r["training_byte_exposures"]} | {r["selected_checkpoint_step"]} | {r["training_seconds"]:.3f} |')
    lines+=['', 'Reproduce from project directory: `./fly-lm '+shlex.join(bundle['command'][1:])+'`.']
    source_archive=ROOT/'reports'/f'smoke-source-{bundle["code_hash"][:12]}.zip'
    if source_archive.exists(): lines+=['',f'Exact executed source archive: [{source_archive.name}](../{source_archive.name}).']
    reference_path=ROOT/'reports'/f'{bundle_path.stem}-validation-ngram.json'
    references=read_json(reference_path) if reference_path.exists() else None
    if references:
        lines+=['','Train-only additive-smoothed sanity references (not parameter matched):',
                f'- Unigram validation BPB: {references["unigram"]["bpb"]:.6f}.',
                f'- Bigram validation BPB: {references["bigram"]["bpb"]:.6f}.']
    if records:
        for axis,filename,label in [('training_bytes','bpb-versus-bytes.png','Cumulative training prediction bytes'),('training_seconds','bpb-versus-training-time.png','Training seconds (validation excluded)')]:
            fig,ax=plt.subplots(figsize=(8,5)); used=set()
            for r in records:
                history=read_json(ROOT/'runs'/r['run_id']/'history.json'); vals=[v for v in history if 'validation' in v]
                c=r['condition']; ax.plot([v[axis] for v in vals],[v['validation']['bpb'] for v in vals],marker='.',color=COLORS.get(c),alpha=.75,label=c if c not in used else None); used.add(c)
            ax.set(xlabel=label,ylabel='Validation bits per byte',title=f'{profile}: full deterministic validation')
            ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(out/filename,dpi=150); plt.close(fig)
            lines+=['',f'![{label}]({filename})']
        fig,axs=plt.subplots(1,3,figsize=(13,5)); labels=[f'{r["condition"]}\ng{r["sampling_seed"]} s{r["training_seed"]} k{r["null_index"]}' for r in records]
        metrics=[([r['accounting']['active_trainable_parameters'] for r in records],'Active trainable parameters'),
                 ([r['training_seconds'] for r in records],'Training seconds'),
                 ([r['peak_rss_bytes']/2**20 for r in records],'Process lifetime peak RSS (MiB)')]
        for ax,(values,title) in zip(axs,metrics):
            ax.bar(range(len(records)),values,color=[COLORS.get(r['condition'],'gray') for r in records]); ax.set_title(title); ax.set_xticks(range(len(records)),labels,rotation=90,fontsize=5)
        fig.suptitle(f'{profile}: resource accounting; RSS includes earlier runs in process'); fig.tight_layout(); fig.savefig(out/'accounting.png',dpi=150); plt.close(fig)
        lines+=['','![Parameter, time and memory accounting](accounting.png)']
        fig,axes=plt.subplots(1,2,figsize=(9,4))
        for sample in bundle['config']['sampling_seeds']:
            p=graph_path(bundle['config']['n'],sample,bundle.get('synthetic',False)); g=Graph.load(p)
            for ax,values,title in zip(axes,[g.target,g.source],['Incoming degree','Outgoing degree']):
                degree=np.bincount(values,minlength=len(g.ids)); ax.hist(degree,bins=20,histtype='step',label=f'sample {sample}'); ax.set(xlabel=title,ylabel='Nodes'); ax.legend()
        fig.suptitle(f'{profile}: extracted graph degrees'); fig.tight_layout(); fig.savefig(out/'graph-degrees.png',dpi=150); plt.close(fig)
        lines+=['','![Graph degree distributions](graph-degrees.png)']
    stats=None
    if sealed:
        lines+=['','| Condition | Sample / seed / null | Best test BPB | Final test BPB | Byte perplexity | Accuracy |','|---|---|---:|---:|---:|---:|']
        for r in sealed:
            lines.append(f'| {r["condition"]} | {r["sampling_seed"]}/{r["training_seed"]}/{r["null_index"]} | {r["best"]["bpb"]:.6f} | {r["final"]["bpb"]:.6f} | {r["best"]["byte_perplexity"]:.4f} | {r["best"]["accuracy"]:.6f} |')
        stats=paired_effects(sealed,bundle['config']['nulls_per_seed'])
    elif profile=='PILOT':
        stats=paired_effects([{**r,'bpb':r['validation_best']['bpb']} for r in records],bundle['config']['nulls_per_seed'])
    if stats:
        atomic_json(out/'paired-effects.json',stats)
        pairs=stats['pairs']
        if pairs:
            fig,ax=plt.subplots(figsize=(8,4)); ax.scatter(range(len(pairs)),[r['delta'] for r in pairs]); ax.axhline(.02,color='gray',ls='--',label='Chosen practical threshold .02'); ax.axhline(0,color='black',lw=.5)
            ax.set_xticks(range(len(pairs)),[f'g{r["sampling_seed"]}/s{r["training_seed"]}' for r in pairs],rotation=45)
            ax.set(ylabel='Mean rewired BPB − fly BPB',title=f'{profile}: paired seed effects ({"test" if sealed else "validation only"})'); ax.legend(); fig.tight_layout(); fig.savefig(out/'paired-effects.png',dpi=150); plt.close(fig)
            lines+=['','![Paired seed effects](paired-effects.png)', '',str(stats['per_graph'])]
        lines+=['',stats['warning'],'Samples can overlap and come from one specimen; not independent flies.']
    if failures or missing:
        lines+=['','Failures/incomplete runs are retained:',f'```json\n{__import__("json").dumps({"failures":failures,"missing":missing},indent=2)}\n```']
    lines+=['','Every run-level metric, seed, graph/config hash, accounting field and timing is preserved in [evidence.json](evidence.json).',
            '', 'Limitations: local BFS sampling biases circuit selection; degree-preserving swaps do not prove uniform null sampling; no strong-connectivity matching; one specimen; narrow Shakespeare benchmark and repeated material; engineered dense interfaces and artificial learned signs; equal parameter count does not equal compute; CPU RSS is process lifetime high-water. Smoke cannot answer the scientific hypothesis. No biological language or whole-brain claims.']
    atomic_json(out/'evidence.json',{'bundle':bundle,'records':records,'manifests':manifests,'test_records':sealed,'failures':failures,'missing':missing,'statistics':stats,'train_only_validation_ngram':references})
    (out/'report.md').write_text('\n'.join(lines)+'\n'); return out/'report.md'
