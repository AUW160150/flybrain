#!/usr/bin/env bash
# Assemble the static site into site/public. Runs on Render and locally.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=site/public
rm -rf "$OUT"; mkdir -p "$OUT"

echo "== pages, styles, scripts, images"
cp -R site/src/. "$OUT"/

echo "== FlyWorld studio (React / Vite) -> /flyworld/"
pushd projects/flyworld-studio >/dev/null
if [ ! -d node_modules ]; then npm ci --include=dev --no-audit --no-fund; fi
FLYWORLD_BASE=/flyworld/ npm run build
popd >/dev/null
mkdir -p "$OUT/flyworld" && cp -R projects/flyworld-studio/dist/. "$OUT/flyworld/"

echo "== Flycodes results platform -> /flycodes/"
mkdir -p "$OUT/flycodes/docs"
cp projects/flycodes/flycodes.html "$OUT/flycodes/index.html"
cp projects/flycodes/docs/*.md "$OUT/flycodes/docs/"
cp projects/flycodes/docs/BACKTRACE_FIGURE.png projects/flycodes/docs/BACKTRACE_FIGURE.svg "$OUT/flycodes/docs/"

echo "== MaleCNS atlas report -> /atlas/"
mkdir -p "$OUT/atlas" && cp -R projects/connectome-atlas/reports/current/. "$OUT/atlas/"

echo "== Sugar circuit explorer -> /sugar/"
mkdir -p "$OUT/sugar" && cp -R projects/sugar-circuit/visualization/. "$OUT/sugar/"
rm -rf "$OUT/sugar/scripts"

echo "== done: $(du -sh "$OUT" | cut -f1) in $OUT"
