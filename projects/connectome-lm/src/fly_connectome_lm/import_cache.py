"""Import HTTP evidence retrieved separately when network sandbox blocks child curl.

All URLs must occur in the fetched catalogue. Both official size and MD5 must
match existing files. Original retrieval times remain unknown for existing data.
"""
from pathlib import Path
import hashlib
import json
from .data_download import NAMES,CATALOGUE,Links,md5_base64,schema,CEILING
from .util import sha256,atomic_json,now,environment

def import_cache(raw:Path,cache:Path) -> None:
    html=(raw/'catalogue.html').read_text(); parser=Links(); parser.feed(html); files=[]
    env=environment()
    total=sum((cache/name).stat().st_size for name in NAMES)
    if total>CEILING: raise RuntimeError('Raw download ceiling exceeded')
    if env['disk_free_bytes']<5_000_000_000: raise RuntimeError('Insufficient preprocessing disk')
    for name,hfile in zip(NAMES,['annotations-headers.txt','weights-headers.txt']):
        urls={u for u in parser.links if u.split('/')[-1]==name}
        if len(urls)!=1: raise ValueError('Catalogue link mismatch')
        url=urls.pop(); head={}
        for line in (raw/hfile).read_text().splitlines():
            if ':' in line:
                key,value=line.split(':',1); head.setdefault(key.lower(),[]).append(value.strip())
        p=cache/name; size=p.stat().st_size
        if size!=int(head['content-length'][-1]): raise ValueError('Size mismatch')
        md5=md5_base64(p)
        if f'md5={md5}' not in ','.join(head.get('x-goog-hash',[])): raise ValueError('Official MD5 mismatch')
        files.append({'name':name,'path':str(p.resolve()),'source_url':url,'size_bytes':size,'sha256':sha256(p),
                      'official_md5_base64':md5,'http_headers':head,'retrieved_utc':None,'verified_utc':now(),
                      'origin':'existing local cache; original retrieval time unknown; official HTTP headers verified',
                      'schema':schema(p)})
    atomic_json(raw/'malecns-manifest.json',{'release':'male-cns:v1.0','catalogue':CATALOGUE,
        'catalogue_sha256':sha256(raw/'catalogue.html'),'verified_utc':now(),'license':'CC-BY-4.0',
        'license_url':'https://creativecommons.org/licenses/by/4.0/',
        'attribution':'FlyEM (HHMI Janelia), University of Cambridge, MRC LMB, Google Research',
        'resource_check':env,'files':files,'acquisition_note':'Top-level curl allowed; Python child network DNS restricted'})
    revision=json.loads((raw/'shakespeare-revision-response.json').read_text())['sha']
    p=raw/'shakespeare.txt'
    atomic_json(raw/'shakespeare-source.json',{'repository':'https://github.com/karpathy/char-rnn','revision':revision,
        'source_url':f'https://raw.githubusercontent.com/karpathy/char-rnn/{revision}/data/tinyshakespeare/input.txt',
        'sha256':sha256(p),'size_bytes':p.stat().st_size,'retrieved_utc':now(),
        'attribution':'William Shakespeare; Tiny Shakespeare benchmark prepared by Andrej Karpathy',
        'license_note':'Public-domain literary source; repository code MIT; no byte transformations'})
