import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flycodes.curriculum_dashboard import latest_v2
from flycodes.curriculum_audit import audit_run
run = latest_v2()
if run is None: raise SystemExit('No completed curriculum run')
receipt = audit_run(run)
for row in receipt['scores']:
    print(row['arm'], row['split'], row['original']['solved'], '->', row['audited']['solved'], '/', row['audited']['total'])
