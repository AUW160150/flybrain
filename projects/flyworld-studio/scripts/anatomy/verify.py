"""Check recorded evidence, preserved source bytes and audit referential integrity."""
import csv
import json
from pathlib import Path
from contracts import sha256, verify_snapshot, validate_mappings
from discover import paths_in

project = Path(__file__).resolve().parents[2]
cache = project/'data/anatomy/manifests'
manifest = json.loads((project/'docs/anatomy/ANATOMY_SOURCE_MANIFEST.json').read_text())
baseline = json.loads((cache/'source-baseline.json').read_text())
verify_snapshot(baseline)
roots = list(map(Path, manifest['discovery']['roots']))
if {str(p) for p in paths_in(roots)} != set(baseline):
    raise ValueError('Protected source file set changed')
for sid, record in manifest['sources'].items():
    if sha256(record['path']) != record['sha256']:
        raise ValueError('Manifest source checksum changed: '+sid)
annotation = json.loads((cache/'authoritative-bodies.json').read_text())
mappings = json.loads((cache/'geometry-mappings.json').read_text())
validate_mappings(mappings, annotation['bodies'])
for mapping in mappings:
    for prefix in ['source','receipt']:
        if sha256(mapping[prefix+'_cache_path']) != mapping[prefix+'_sha256']:
            raise ValueError('Recovered raw copy differs from original')
for c in json.loads((cache/'conversions.json').read_text()):
    if sha256(c['output_path']) != c['output_sha256']:
        raise ValueError('Conversion checksum changed')
for name, key in [('ANATOMY_CLAIM_LEDGER.csv','claim_id'),('ANATOMY_MISMATCH_LEDGER.csv','mismatch_id')]:
    with (project/'docs/anatomy'/name).open() as f:
        rows = list(csv.DictReader(f))
    if len(rows) != len({r[key] for r in rows}):
        raise ValueError('Duplicate ledger IDs')
    for row in rows:
        for ref in row['source_ids'].split(';'):
            if ref.endswith('*'):
                if not any(s.startswith(ref[:-1]) for s in manifest['sources']):
                    raise ValueError('Unresolved source prefix '+ref)
            elif ref not in manifest['sources']:
                raise ValueError('Unresolved source '+ref)
report = {'status':'PASS','protected_files_unchanged':len(baseline),
          'public_assets_unchanged':sum(str(project/'public')+'/' in p for p in baseline),
          'source_manifest_entries_checked':len(manifest['sources']),
          'verified_body_mappings':len(mappings),'raw_copy_checks':len(mappings)*2,
          'source_scope':'All nonexcluded files in the six recorded roots; no claim about excluded/private/dependency paths.',
          'research_files_unchanged':sum('/Sugar/malecns_sugar_circuit_v1/' in p for p in baseline)}
(project/'docs/validation/prompt04a/integrity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
