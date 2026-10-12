import argparse
import json
from pathlib import Path
from .common import ROOT

def main():
    parser=argparse.ArgumentParser(description='Flycodes: fixed-connectome coding experiments')
    sub=parser.add_subparsers(dest='command',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('--raw',type=Path,default=ROOT.parents[1]/'data/flat-connectome')
    train=sub.add_parser('train');train.add_argument('--seed',type=int,default=7);train.add_argument('--steps',type=int,default=200);train.add_argument('--max-bytes',type=int,default=384)
    serve=sub.add_parser('serve');serve.add_argument('--port',type=int,default=8765)
    baseline=sub.add_parser('baseline');baseline.add_argument('--prepare-only',action='store_true');baseline.add_argument('--collect',action='store_true')
    sub.add_parser('status')
    sub.add_parser('prepare-curriculum')
    sub.add_parser('train-curriculum')
    args=parser.parse_args()
    if args.command=='prepare-curriculum':
        from .curriculum_data import prepare
        print(json.dumps(prepare(),indent=2))
    elif args.command=='train-curriculum':
        from .curriculum_experiment import run_v2
        from .curriculum_audit import audit_run
        run=run_v2();audit_run(run)
        print(run)
    elif args.command=='prepare':
        from .connectome import prepare
        print(json.dumps(prepare(args.raw),indent=2))
    elif args.command=='train':
        if not 1<=args.steps<=10000 or not 16<=args.max_bytes<=2048:parser.error('steps 1..10000; max-bytes 16..2048')
        from .experiment import pilot
        print(pilot(args.seed,args.steps,args.max_bytes))
    elif args.command=='serve':
        from .server import serve
        serve(args.port)
    elif args.command=='baseline':
        from .hosted import requests,collect,run_baseline
        result=requests() if args.prepare_only else collect() if args.collect else run_baseline()
        print(result if isinstance(result,Path) else json.dumps(result['summary'],indent=2))
        if not isinstance(result,Path) and not result['completed']:
            raise SystemExit(1)
    elif args.command=='status':
        from .server import dashboard
        print(json.dumps(dashboard(),indent=2))

if __name__=='__main__':main()
