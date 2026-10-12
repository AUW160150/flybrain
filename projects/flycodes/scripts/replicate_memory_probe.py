"""Repeat the fixed delayed-bit protocol on two new streams, without tuning it."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from backtrace_model import delayed_bit_probe
from flycodes.common import ROOT,read_json,write_json,sha256,now
from flycodes.curriculum_dashboard import latest_v2
from flycodes.curriculum_experiment import setup,reservoir
from flycodes.curriculum_model import Tokenizer
from flycodes.connectome import load_graph

setup(7);run=latest_v2();config=read_json(run/'config.json');tok=Tokenizer.load(run/'tokenizer.json')
base=ROOT/'diagnostics'/read_json(ROOT/'diagnostics/latest-backtrace.json')['directory']
output=base/'memory-replication';output.mkdir(exist_ok=False)
plan=dict(time=now(),seeds=[91010,91011],reservoir_seed=7,selection='same six ridge values; validation only',
          protocol='Same as original probe, no model/hyperparameter changes. Independent synthetic streams, same fixed reservoir/input mapping.',
          probe_source_sha256=sha256(ROOT/'scripts/backtrace_model.py'),driver_sha256=sha256(Path(__file__)))
write_json(output/'plan.json',plan);W,ids,graph=load_graph();results={};delayed_bit_probe.zero_token=ord('0')
for seed in plan['seeds']:
    sequence=np.random.default_rng(seed).integers(0,2,size=2416)+ord('0');np.save(output/f'tokens-{seed}.npy',sequence)
    results[str(seed)]={}
    for label,recurrence,setting in [
        ('selected',True,config['selected_setting']),
        ('no_recurrence',False,config['selected_setting']),
        ('gain_only_radius_0.9',True,{**config['selected_setting'],'target_radius':.9})]:
        print(seed,label,flush=True)
        res=reservoir(W,tok,config,setting,recurrence)
        results[str(seed)][label]=delayed_bit_probe(res,sequence)
        write_json(output/'results.json',results);del res
write_json(output/'manifest.json',{p.name:sha256(p) for p in output.iterdir() if p.is_file()})
print(output)
