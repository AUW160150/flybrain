"""A self-contained measured-results view, usable without a local server."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from flycodes.server import dashboard
html=(root/'web/index.html').read_text()
css=(root/'web/style.css').read_text()
# Make the portable artifact network independent, including fonts.
css='\n'.join(line for line in css.splitlines() if not line.startswith('@import'))
js=(root/'web/app.js').read_text()
payload=json.dumps(dashboard(),ensure_ascii=True).replace('<','\\u003c')
html=html.replace('<link rel="stylesheet" href="/style.css">','<style>'+css+'</style>')
html=html.replace('<script src="/app.js"></script>','<script>window.FLYCODES_SNAPSHOT='+payload+';</script><script>'+js+'</script>')
html=html.replace('href="/docs/','href="docs/')
(root/'flycodes.html').write_text(html)
print(root/'flycodes.html')
