# SafeDocFlow artifact update log

## 2026 AEI submission refresh

- Updated artifact title and documentation to SafeDocFlow.
- Added `safedocflow/` package with routing, statistics, P3 classifier, pipeline definitions, and schemas.
- Added `data/paper_metrics/` redacted aggregate/per-item metadata.
- Added `data/run_records/redacted_example_run_records.jsonl`.
- Added `configs/workflow_predicates.json` and `configs/p3_classifier_card.json`.
- Added `docs/P3_CLASSIFIER_CARD.md` and `docs/PAPER_TO_ARTIFACT_MAP.md`.
- Added validation script for manuscript statistics and routing invariants.
- Updated smoke-test script to run both artifact validation and safe dummy pipeline checks.

## Safety stance

The artifact remains de-weaponized. It validates code paths and numerical claims without distributing unsafe prompts or private model outputs.
