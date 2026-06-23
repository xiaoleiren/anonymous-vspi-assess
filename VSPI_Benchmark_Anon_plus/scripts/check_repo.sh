#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"
python -m compileall -q .
bash scripts/run_safe_matrix.sh >/tmp/vspi_smoke.log 2>&1 || { cat /tmp/vspi_smoke.log; exit 1; }
echo "Repository check passed."
