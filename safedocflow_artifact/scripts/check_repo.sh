#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"
python -m compileall -q safedocflow analysis defenses evaluation generators models utils scripts
python analysis/validate_paper_numbers.py
bash scripts/run_safe_matrix.sh >/tmp/safedocflow_smoke.log 2>&1 || { cat /tmp/safedocflow_smoke.log; exit 1; }
echo "Repository check passed."
