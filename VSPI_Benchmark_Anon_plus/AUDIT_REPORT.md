# Code audit summary

## What was broken in the original draft

1. The repository tree shown in the paper was not actually present in the uploaded files. All Python files were flat, so imports like `from generators._common import ...` and `from utils.io import ...` failed immediately.
2. `generators/_common.py` was missing, which made all three renderers unrunnable.
3. `__init__.py` files were missing, so package-style imports were fragile.
4. `scripts/run_all_dummy.sh` assumed the missing repo layout and called files as plain paths, which broke module resolution.
5. `analysis/compute_tables.py` only supported a single sanity table, but the README claimed it could produce the main paper tables from manifests.
6. `analysis/compute_tables.py` emitted malformed LaTeX row endings before repair.
7. `models/openai_client.py` and `models/gemini_client.py` were stubs, so the code did not actually reproduce the paper's reported API experiments.
8. `evaluation/judge.py` was a placeholder judge, not the conservative publication-grade judging pipeline described in the paper.
9. The paper describes controls and metrics such as explicit untrusted-content control, human audit, category-balanced aggregation, paired testing, and exact model snapshots, but those assets and annotations were not included.
10. The dataset file required by the scripts was absent.

## What this repaired package now does

- Runs end to end with a redacted CSV and the dummy backend.
- Generates terminal, diagram, and typography-only images.
- Runs multi-resolution and transform sweeps.
- Produces judged JSONL logs.
- Computes ASR, rASR, Min-rASR, and an OCR-hit proxy.
- Writes LaTeX tables and JSON summaries.

## What is still not verifiable from the draft alone

- The headline numeric claims in the paper.
- Real commercial-model behavior.
- Human-audit agreement and Cohen's kappa.
- Publication-grade judge behavior.
- Final table manifests and exact category-balanced aggregation.

## Bottom line

The original upload was a scaffold, not a complete reproducibility artifact. The repaired package is runnable for safe, de-weaponized pipeline validation, but it does not prove the paper's empirical claims by itself.
