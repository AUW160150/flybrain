from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import pyarrow as pa
from .util import atomic_json,read_json,sha256,now,environment

CATALOGUE='https://male-cns.janelia.org/download/'
NAMES=['body-annotations-male-cns-v1.0-minconf-0.5.feather','connectome-weights-male-cns-v1.0-minconf-0.5.feather']
CEILING=2_000_000_000

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            href=dict(attrs).get('href')
            if href: self.links.append(href)

def curl(url:str,*args:str) -> bytes:
    p=subprocess.run(['curl','--fail','--location','--silent','--show-error','--retry','2','--connect-timeout','20',*args,url],capture_output=True)
    if p.returncode: raise RuntimeError(f'HTTP acquisition failed for {url}: {p.stderr.decode(errors="replace")}')
    return p.stdout

def headers(url:str) -> dict:
    result={}
    for line in curl(url,'--head').decode().splitlines():
        if ':' in line:
            k,v=line.split(':',1); result.setdefault(k.lower(),[]).append(v.strip())
    return result

def schema(path:Path) -> dict:
    with pa.memory_map(str(path),'r') as f:
        reader=pa.ipc.open_file(f)
        return {'fields':{field.name:str(field.type) for field in reader.schema},
                'record_batches':reader.num_record_batches,
                'rows':sum(reader.get_batch(i).num_rows for i in range(reader.num_record_batches))}

def md5_base64(path:Path) -> str:
    h=hashlib.md5(usedforsecurity=False)
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8<<20),b''): h.update(chunk)
    return base64.b64encode(h.digest()).decode()

def atomic_download(url:str,path:Path,size:int,head:dict) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    partial=path.with_suffix(path.suffix+'.part'); state=partial.with_suffix(partial.suffix+'.json')
    signature={'url':url,'size':size,'etag':head.get('etag')}
    if partial.exists() and (not state.exists() or read_json(state)!=signature):
        raise RuntimeError(f'Stale partial file {partial}; inspect/remove it explicitly before retrying')
    atomic_json(state,signature)
    args=['--output',str(partial),'--max-filesize',str(CEILING)]
    if partial.exists() and partial.stat().st_size: args+=['--continue-at','-']
    curl(url,*args)
    if partial.stat().st_size!=size: raise RuntimeError('Incomplete download; retained .part for resume')
    os.replace(partial,path); state.unlink()

def acquire_malecns(out:Path,cached:Path|None=None,ceiling:int=CEILING) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    receipt_path=out/'malecns-manifest.json'
    if receipt_path.exists():
        receipt=read_json(receipt_path)
        for item in receipt['files']:
            if sha256(Path(item['path']))!=item['sha256']: raise ValueError('Cached dataset changed')
        return receipt
    html=curl(CATALOGUE).decode(); parser=Links(); parser.feed(html)
    resolved=[]
    for name in NAMES:
        matches={urljoin(CATALOGUE,h) for h in parser.links if h.split('/')[-1]==name}
        if len(matches)!=1: raise RuntimeError(f'Catalogue link ambiguous or missing: {name}')
        url=matches.pop()
        if not url.startswith('https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/'):
            raise RuntimeError('Catalogue release/path changed; review before acquisition')
        head=headers(url); size=int(head.get('x-goog-stored-content-length',head.get('content-length',['0']))[-1])
        if size<=0: raise RuntimeError('Missing size; cannot enforce acquisition ceiling')
        resolved.append((name,url,head,size))
    total=sum(v[3] for v in resolved)
    if total>ceiling: raise RuntimeError(f'Raw files require {total} bytes > ceiling {ceiling}; review new scope explicitly')
    env=environment()
    if shutil.disk_usage(out).free<total*2+2_000_000_000: raise RuntimeError('Insufficient disk headroom')
    if env['ram_bytes'] is not None and env['ram_bytes']<2_000_000_000: raise RuntimeError('Need 2 GB RAM headroom for batched extraction')
    files=[]
    for name,url,head,size in resolved:
        existing=cached/name if cached else None
        p=existing if existing and existing.exists() else out/name
        downloaded=False
        if not p.exists(): atomic_download(url,p,size,head); downloaded=True
        if p.stat().st_size!=size: raise RuntimeError(f'Official size differs: {p}')
        md5=md5_base64(p)
        hashes=','.join(head.get('x-goog-hash',[]))
        if f'md5={md5}' not in hashes: raise RuntimeError(f'Official MD5 mismatch/missing for {p}; provenance not verified')
        files.append({'name':name,'path':str(p.resolve()),'source_url':url,'size_bytes':size,
                      'sha256':sha256(p),'official_md5_base64':md5,'http_headers':head,
                      'retrieved_utc':now() if downloaded else None,'verified_utc':now(),
                      'origin':'downloaded' if downloaded else 'existing local cache; original retrieval time unknown',
                      'schema':schema(p)})
    receipt={'release':'male-cns:v1.0','catalogue':CATALOGUE,'catalogue_sha256':hashlib.sha256(html.encode()).hexdigest(),
             'verified_utc':now(),'license':'CC-BY-4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
             'attribution':'FlyEM (HHMI Janelia), University of Cambridge, MRC LMB, Google Research',
             'resource_check':env,'files':files}
    (out/'catalogue.html').write_text(html); atomic_json(receipt_path,receipt)
    return receipt

def acquire_shakespeare(out:Path) -> tuple[Path,dict]:
    out.mkdir(parents=True,exist_ok=True); manifest_path=out/'shakespeare-source.json'
    if manifest_path.exists():
        manifest=read_json(manifest_path); p=out/'shakespeare.txt'
        if sha256(p)!=manifest['sha256']: raise ValueError('Corpus cache hash mismatch')
        return p,manifest
    commit=json.loads(curl('https://api.github.com/repos/karpathy/char-rnn/commits/master'))['sha']
    if not re.fullmatch('[0-9a-f]{40}',commit): raise RuntimeError('Invalid repository revision')
    url=f'https://raw.githubusercontent.com/karpathy/char-rnn/{commit}/data/tinyshakespeare/input.txt'
    p=out/'shakespeare.txt'; data=curl(url)
    if len(data)>10_000_000: raise RuntimeError('Unexpected corpus size')
    tmp=p.with_suffix('.tmp'); tmp.write_bytes(data); os.replace(tmp,p)
    manifest={'repository':'https://github.com/karpathy/char-rnn','revision':commit,'source_url':url,
              'sha256':sha256(p),'size_bytes':len(data),'retrieved_utc':now(),
              'attribution':'William Shakespeare; Tiny Shakespeare benchmark prepared by Andrej Karpathy',
              'license_note':'Public-domain literary source; repository code is MIT; exact benchmark bytes preserved'}
    atomic_json(manifest_path,manifest); return p,manifest
