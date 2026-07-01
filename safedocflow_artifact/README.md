# SafeDocFlow Artifact

This repository contains the anonymized software scaffold and redacted validation artifacts for the manuscript:

**SafeDocFlow: Knowledge-Represented Guardrail Evaluation and Routing Blueprint for Trustworthy Engineering Document AI Workflows**

The artifact is designed for double-anonymized review. It provides safe, de-weaponized code and redacted aggregate/per-item metadata needed to audit the paper's computation path without releasing harmful prompts, private model outputs, or identifying metadata.

## What this package includes

- A runnable SafeDocFlow Python package for:
  - risk-score computation,
  - workflow predicate evaluation,
  - Algorithm 1 routing with boundary-band audit flags,
  - P0--P5 pipeline definitions,
  - D1/D2/D3 component metadata,
  - exact statistical checks for the paper tables.
- A reference text-safety classifier card for **SafeDocFlow-D3-reference-v1**, the P3 classifier used by this public reproducibility scaffold.
- Redacted, non-weaponizable per-item/aggregate metadata for:
  - diagnostic four-model gap results,
  - the defense pair,
  - LLaVA supplemental defense evaluation,
  - D2-only ablation,
  - P1/P2 paired McNemar table,
  - RiskScore features and perturbation stability,
  - policy-loss and break-even calculations.
- Legacy-compatible renderers and dummy inference scripts for safe local smoke tests.

## Safety and scope

This package does **not** include raw harmful prompts, actionable payload text, private API outputs, or non-redacted human-audit labels. The files under `data/paper_metrics/` are redacted audit tables and metadata, not a weaponizable benchmark release. All prompt-like fields are synthetic or redacted.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run syntax checks, smoke tests, routing checks, and paper-number validation.
bash scripts/check_repo.sh
```

A successful check writes generated validation outputs under `paper/tables/generated/` and exits with `Repository check passed.`

## Core files

```text
safedocflow/
  risk.py                 RiskScore, workflow predicates, Algorithm 1 routing
  stats.py                Clopper-Pearson, Fisher, McNemar, break-even, policy loss
  classifier.py           SafeDocFlow-D3-reference-v1 classifier scaffold
  pipelines.py            P0--P5 component definitions and cost/latency proxies
  schemas.py              Run-record validation helpers
analysis/
  validate_paper_numbers.py  Validates manuscript table numbers from redacted data
  compute_tables.py          Legacy manifest-driven table generator
data/paper_metrics/
  *.csv / *.json             Redacted audit data and table inputs
data/run_records/
  redacted_example_run_records.jsonl
configs/
  experiment_common.json
  model_registry.json
  workflow_predicates.json
  p3_classifier_card.json
docs/
  P3_CLASSIFIER_CARD.md
  PAPER_TO_ARTIFACT_MAP.md
```

## Paper-to-artifact map

| Paper component | Artifact file(s) |
|---|---|
| RiskScore and workflow predicates | `safedocflow/risk.py`, `configs/workflow_predicates.json`, `data/run_records/redacted_example_run_records.jsonl` |
| Algorithm 1 routing | `safedocflow/risk.py`, `analysis/validate_paper_numbers.py` |
| P3 classifier | `safedocflow/classifier.py`, `configs/p3_classifier_card.json`, `docs/P3_CLASSIFIER_CARD.md` |
| Main diagnostic results | `data/paper_metrics/main_results.csv` |
| Defense pair and P1/P2 McNemar | `data/paper_metrics/defense_pair.csv`, `data/paper_metrics/mcnemar_pairing.csv` |
| LLaVA supplemental defense | `data/paper_metrics/llava_defense.csv` |
| D2-only ablation | `data/paper_metrics/ablation_results.csv`, `data/paper_metrics/ablation_per_model.csv`, `data/paper_metrics/ablation_frr_category.csv` |
| Cost, loss, and break-even checks | `data/paper_metrics/pipeline_summary.csv`, `data/paper_metrics/policy_loss.csv`, `data/paper_metrics/prevalence_sensitivity.csv` |
| RiskScore stability | `data/paper_metrics/risk_score_features_redacted.csv`, `data/paper_metrics/risk_score_stability.csv` |

## Reproducibility note

Closed-model API wrappers are included only as optional adapters. The default dummy backend and all validation scripts run offline. Exact private API responses and raw harmful prompt text are intentionally omitted; the public artifact verifies the computation, routing, and table-generation logic on redacted metadata.
