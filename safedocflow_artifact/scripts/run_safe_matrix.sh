#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"

DATA_CSV="data/experiment_dataset_50_redacted.csv"
OUT_ROOT="results"
IMAGES_DIR="$OUT_ROOT/images"
LOGS_DIR="$OUT_ROOT/logs"
TABLES_BASE="paper/tables/baselines"
TABLES_DEF="paper/tables/defenses"

mkdir -p "$IMAGES_DIR" "$LOGS_DIR" "$TABLES_BASE" "$TABLES_DEF"

python -m generators.render_vspi_terminal --data_csv "$DATA_CSV" --out_dir "$IMAGES_DIR/vspi_terminal"
python -m generators.render_vspi_diagram --data_csv "$DATA_CSV" --out_dir "$IMAGES_DIR/vspi_diagram"
python -m generators.render_typography_only --data_csv "$DATA_CSV" --out_dir "$IMAGES_DIR/typography_only"

for family in vspi_terminal vspi_diagram typography_only; do
  python -m evaluation.run_inference \
    --backend dummy --model dummy \
    --data_csv "$DATA_CSV" \
    --image_dir "$IMAGES_DIR/$family" \
    --out_jsonl "$LOGS_DIR/${family}.jsonl" \
    --resolutions 800x400 1024x512 max \
    --transforms none resize0.5 resize1.0 resize1.5 jpeg70 jpeg90

  python -m evaluation.judge \
    --in_jsonl "$LOGS_DIR/${family}.jsonl" \
    --out_jsonl "$LOGS_DIR/${family}_judged.jsonl"
done

python -m evaluation.run_inference \
  --backend dummy --model dummy \
  --data_csv "$DATA_CSV" \
  --image_dir "$IMAGES_DIR/vspi_terminal" \
  --out_jsonl "$LOGS_DIR/vspi_terminal_inst_data_sep.jsonl" \
  --resolutions 800x400 1024x512 max \
  --transforms none \
  --defense_mode inst_data_sep
python -m evaluation.judge \
  --in_jsonl "$LOGS_DIR/vspi_terminal_inst_data_sep.jsonl" \
  --out_jsonl "$LOGS_DIR/vspi_terminal_inst_data_sep_judged.jsonl"

python -m evaluation.run_inference \
  --backend dummy --model dummy \
  --data_csv "$DATA_CSV" \
  --image_dir "$IMAGES_DIR/vspi_terminal" \
  --out_jsonl "$LOGS_DIR/vspi_terminal_ocr_gate.jsonl" \
  --resolutions 800x400 1024x512 max \
  --transforms none \
  --defense_mode ocr_gating
python -m evaluation.judge \
  --in_jsonl "$LOGS_DIR/vspi_terminal_ocr_gate.jsonl" \
  --out_jsonl "$LOGS_DIR/vspi_terminal_ocr_gate_judged.jsonl"

python - <<'PY'
from pathlib import Path
root = Path('results/logs')
out1 = root / 'all_baselines_judged.jsonl'
with out1.open('w', encoding='utf-8') as wf:
    for name in ['vspi_terminal_judged.jsonl', 'vspi_diagram_judged.jsonl', 'typography_only_judged.jsonl']:
        wf.write((root / name).read_text(encoding='utf-8'))
out2 = root / 'all_defenses_judged.jsonl'
with out2.open('w', encoding='utf-8') as wf:
    for name in ['vspi_terminal_judged.jsonl', 'vspi_terminal_inst_data_sep_judged.jsonl', 'vspi_terminal_ocr_gate_judged.jsonl']:
        wf.write((root / name).read_text(encoding='utf-8'))
PY

SAFEDOCFLOW_SKIP_OCR=1 python -m analysis.compute_tables \
  --judged_jsonl "$LOGS_DIR/all_baselines_judged.jsonl" \
  --out_dir "$TABLES_BASE" \
  --table1_manifest manifests/table1_main.csv \
  --table2_manifest manifests/table2_robust.csv

SAFEDOCFLOW_SKIP_OCR=1 python -m analysis.compute_tables \
  --judged_jsonl "$LOGS_DIR/all_defenses_judged.jsonl" \
  --out_dir "$TABLES_DEF" \
  --table3_manifest manifests/table3_ablation.csv

echo "Done. Outputs are in $OUT_ROOT and paper/tables/."
