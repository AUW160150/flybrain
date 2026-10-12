"""Generate measured diagnosis and a standalone scientific figure."""
import os
import sys
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/flycodes-matplotlib')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flycodes.common import ROOT,read_json,write_json,sha256,now
from flycodes.curriculum_dashboard import latest_v2

run=latest_v2();base=ROOT/'diagnostics'/read_json(ROOT/'diagnostics/latest-backtrace.json')['directory']
d=read_json(base/'results.json');reps=read_json(base/'memory-replication/results.json')
traces=read_json(base/'validation-token-traces.json');probes=read_json(base/'prompt-information-probes.json')
streams=[d['memory_probe'],*reps.values()]
labels={'selected':'Current fly model','no_recurrence':'No recurrence','gain_only_radius_0.9':'Stronger recurrence (.9)'}
delays=[0,1,2,4,8,16,32]
memory={key:np.array([[s[key]['delayed_bit_r2'][str(lag)] for lag in delays] for s in streams]) for key in labels}
fig,axes=plt.subplots(1,3,figsize=(14,4.5),layout='constrained')
colors=['#cc542e','#7c8b98','#287766']
for (key,label),color in zip(labels.items(),colors):
    m=memory[key];axes[0].plot(range(len(delays)),m.mean(0),marker='o',label=label,color=color)
    axes[0].fill_between(range(len(delays)),m.min(0),m.max(0),alpha=.13,color=color)
axes[0].set(xticks=range(len(delays)),xticklabels=delays,xlabel='Input delay (tokens)',ylabel='Held-out delayed-bit R²',title='Memory can improve without rewiring')
axes[0].axhline(0,color='#999999',lw=.8);axes[0].legend(fontsize=8)
v=d['validation_ablations']['fly-s7']
names=['Original','Recurrence\nremoved','Prompt context\nshuffled']
values=[v[k]['token_accuracy']*100 for k in ['baseline','recurrence_removed_same_head','prompt_context_shuffled']]
axes[1].bar(names,values,color=['#cc542e','#7c8b98','#527d99'])
axes[1].set(ylabel='Next-token accuracy (%)',ylim=(0,65),title='Decoder barely uses the fly connections')
for i,value in enumerate(values):axes[1].text(i,value+1,f'{value:.2f}%',ha='center',fontsize=9)
h=read_json(run/'fly-s7-training.json')['history']
axes[2].plot([x['step'] for x in h],[x['train_loss'] for x in h],label='Training',color='#287766')
axes[2].plot([x['step'] for x in h],[x['validation_loss'] for x in h],label='Validation',color='#cc542e')
axes[2].axvline(100,color='#999999',ls='--',lw=1,label='Selected checkpoint')
axes[2].set(xlabel='Training updates',ylabel='Cross-entropy loss',title='Continued fitting overfits the corpus');axes[2].legend(fontsize=8)
fig.suptitle('Flycodes: measured model diagnosis, not a coding-performance improvement',fontsize=13)
fig.text(.01,-.035,'Memory: three random streams, same reservoir/input seed; bands show min–max. Ablations: validation, fixed seed-7 decoder, correct prefixes. Coding benchmarks unchanged.',fontsize=8)
fig.savefig(ROOT/'docs/BACKTRACE_FIGURE.png',dpi=160,bbox_inches='tight')
fig.savefig(ROOT/'docs/BACKTRACE_FIGURE.svg',bbox_inches='tight');plt.close(fig)
lines=['# Flycodes model backtrace', '', f'Diagnostic directory: `{base.name}`; source coding run: `{run.name}`.', '',
       'The current failure is a property of our frozen-reservoir coding system. It does not establish a limit on biological flies or on every connectome-constrained architecture. No coding checkpoint or recorded connection was changed. The only fitted additions are separate diagnostic readers, which never generate benchmark solutions.', '',
       '![Measured diagnosis](BACKTRACE_FIGURE.png)', '',
       '## 1. The recurrent wiring has very weak influence on the coding decoder', '',
       '| Saved fly head | Original validation accuracy | Same head, recurrence removed | Next-token choices changed | Shuffled prompt context accuracy |',
       '|---|---:|---:|---:|---:|']
for name,v in d['validation_ablations'].items():
    lines.append(f'| {name} | {v["baseline"]["token_accuracy"]:.3%} | {v["recurrence_removed_same_head"]["token_accuracy"]:.3%} | {v["recurrence_removed_same_head"]["top1_changed_fraction"]:.3%} | {v["prompt_context_shuffled"]["token_accuracy"]:.3%} |')
delta=d['cached_features']['validation']['current_state']['relative_frobenius_difference']
lines+=['',f'Across cached validation states, removing recurrence changes the pooled current-state feature matrix by {delta:.3%} in relative Frobenius norm. This is a specific norm comparison, not a percentage of biological brain activity. With separately trained matched controls, {sum(v["identical"] for v in d["same_generated_code"].values())}/{sum(v["total"] for v in d["same_generated_code"].values())} previously recorded generated programs are byte-identical.', '',
        'Inference: the current input/decoder system can perform almost all of its observed code prediction without the fly connections. Prompt-context shuffling does hurt, so the decoder is using information about the question. The weak contribution is specifically recurrent graph processing. Ablations hold the coding head fixed; they measure sensitivity, not the best possible retrained system.', '',
        '## 2. There is a reproducible memory improvement available', '',
        'A new probe feeds independent random 0/1 tokens through the complete frozen network and trains only a linear diagnostic reader to reconstruct previous bits from the current pooled state. It excludes the separate persistent prompt-context buffer. Each stream uses 1,200 fitting, 320 validation and 640 held-out test states, with 64-token gaps. Ridge strength is selected on validation only. Three independent input streams share the same reservoir/input seed. These are selected-delay memory probes, not a complete information-processing-capacity measurement.', '',
        '| Configuration | R² at delay 4 | R² at delay 8 | R² at delay 16 | R² at delay 32 |',
        '|---|---:|---:|---:|---:|']
for key,label in labels.items():
    values=memory[key]
    lines.append('| '+label+' | '+' | '.join(f'{values[:,delays.index(lag)].mean():.3f} [{values[:,delays.index(lag)].min():.3f}, {values[:,delays.index(lag)].max():.3f}]' for lag in [4,8,16,32])+' |')
lines+=['', 'Values are means with min–max across streams. R² = 1 is perfect reconstruction; 0 is the test-set mean baseline; negative values are worse. The stronger configuration changes only the global gain (target radius 0.0453 → 0.9); input scale .35 and leak .5 are held fixed. No edges are added, removed or overwritten.', '',
        'This is a measured improvement in a narrow memory task. It has not improved a coding score: no new coding head was trained on this setting. The earlier v2 .9-radius calibration also changed input scale to .1 and did not win validation selection; that result remains intact. This new gain-only comparison answers a different question.', '',
        '## 3. The decoder makes logical choices incorrectly, before syntax breaks', '',
        'Under correct reference prefixes, validation token accuracy is only about 51–52%. The first divergence from a reference appears at median token 8 for seed 7 and token 6 for seed 19. Until the first divergence, this is also the free-running greedy path. Subsequent teacher-forced accuracy assumes the correct previous tokens and is not free-running accuracy. A different valid algorithm could diverge, so a divergence alone is not classified as a logic error.', '']
for id in ['curr-add-each--4','curr-contains-number-4','curr-offset-sum-4']:
    r=next(r for r in traces['rows'] if r['seed']==7 and r['problem']==id)
    lines += [f'### {id}', '', r['statement'], '', 'Exact correct prefix before first divergence:', '',
              '```python',r['prefix'],'```', '',f'Expected token: `{r["expected"]}`. Chosen token: `{r["chosen"]}`. Probability assigned to the expected token: {r["expected_probability"]:.6%}.', '']
lines+=['These particular choices change the requested operation or literal. A parser cannot repair that without supplying computational content. Training loss falls from 6.619 to 0.029 for seed 7 while validation loss reaches 10.367; the evaluated checkpoint was the earlier validation minimum at step 100. This supports overfitting as a diagnosed issue, not a claim that the last overfit checkpoint was used in the benchmark.', '',
        '## 4. Some required prompt information remains accessible', '',
        '| Diagnostic probe | Fly features | No-recurrence features | Held-out split |',
        '|---|---:|---:|---|']
for key,title,split in [
    ('operation_with_unseen_constants','Identify operation family','20 examples; unseen constants'),
    ('constant_in_heldout_operation_families','Identify requested constant','24 examples; two unseen operation families')]:
    a=probes['results']['fly'][key];b=probes['results']['no-recurrence'][key]
    lines.append(f'| {title} | {a["test_accuracy"]:.0%} | {b["test_accuracy"]:.0%} | {split} |')
lines += ['', 'These are newly fitted linear readers of mean/final prompt state. They are not the coding decoder. In particular, the constant probe sees every constant during its own fitting and is tested across held-out operation families; it does not establish extrapolation to unseen constants. These small probes show that useful information can remain in the representation while the code decoder fails to use it. They justify testing explicit supervised operation/literal objectives and input–output alignment, rather than assuming every failure is lost memory.', '',
          '## 5. The simulator omits relevant biology', '',
          f'The local transmitter file matches {d["neurotransmitter_inventory"]["matched_neurons"]:,} of 165,122 selected neurons; 502 have no matching row and 3,100 matched labels are unclear. Matched labels include 22,055 GABA and 29,296 glutamate neurons. The current simulator never reads these labels and uses only nonnegative recurrent coefficients. A transmitter identity is not itself a measured efficacy or a universal synaptic sign: receptor information and uncertainty policies matter.', '',
          'The present input mapping broadcasts only 256 random channels, and all neuron activity is pooled into 768 signed buckets. On 2,048 sampled validation states, the current-state feature participation ratio is 17.23 and 82 principal directions cover 99% of variance. This describes correlated measured features, not a claim that the brain has only 17 neurons or a proof of its computational capacity.', '',
          '## Evidence, scope and reproduction', '',
          'The original graph and 66 run artifacts passed hash checks. Original coding scores, model weights and localhost server are unchanged. No hosted model calls or new final coding-test attempts were made. The measured primitive-memory gain and probe accuracies must remain separate from LeetCode/MBPP claims.', '',
          'The directory contains the diagnostic plan, script snapshot, raw metrics, synthetic sequences, validation token distributions, prompt-probe predictions and verification hashes. Reproduce from the flycodes directory:', '',
          '```sh','../../.venv/bin/python scripts/backtrace_model.py','../../.venv/bin/python scripts/replicate_memory_probe.py','../../.venv/bin/python scripts/trace_validation_tokens.py','../../.venv/bin/python scripts/probe_prompt_information.py','../../.venv/bin/python scripts/report_backtrace.py','```', '',
          'See [the redesign plan and primary scientific sources](REDESIGN_PLAN.md).']
(ROOT/'docs/BACKTRACE_RESULTS.md').write_text('\n'.join(lines)+'\n')
write_json(base/'report-artifacts.json',dict(created_at=now(),files={name:sha256(ROOT/name) for name in ['docs/BACKTRACE_RESULTS.md','docs/BACKTRACE_FIGURE.png','docs/BACKTRACE_FIGURE.svg']}))
print(ROOT/'docs/BACKTRACE_RESULTS.md')
