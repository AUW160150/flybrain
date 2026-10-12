#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ -x .venv/bin/python ]; then
  exec .venv/bin/python -m flycodes.cli "$@"
elif [ -x ../../.venv/bin/python ]; then
  exec ../../.venv/bin/python -m flycodes.cli "$@"
else
  exec python3 -m flycodes.cli "$@"
fi
