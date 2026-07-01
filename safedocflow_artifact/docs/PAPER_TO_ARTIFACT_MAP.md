# Paper-to-artifact map

This map records where each paper claim can be audited in the public package.

- Main diagnostic ASR/GI values: `data/paper_metrics/main_results.csv`
- P1/P2 paired McNemar table: `data/paper_metrics/mcnemar_pairing.csv`
- Defense pair P0/P1/P2/P3 values: `data/paper_metrics/defense_pair.csv`
- LLaVA supplemental defense values: `data/paper_metrics/llava_defense.csv`
- D2-only ablation: `data/paper_metrics/ablation_results.csv`, `data/paper_metrics/ablation_per_model.csv`, `data/paper_metrics/ablation_frr_category.csv`
- Policy-loss and break-even calculations: `data/paper_metrics/pipeline_summary.csv`, `data/paper_metrics/policy_loss.csv`, `data/paper_metrics/prevalence_sensitivity.csv`, `safedocflow/stats.py`
- RiskScore, workflow predicates, and routing: `safedocflow/risk.py`, `configs/workflow_predicates.json`
- Example run records: `data/run_records/redacted_example_run_records.jsonl`
- P3 classifier card: `docs/P3_CLASSIFIER_CARD.md`, `configs/p3_classifier_card.json`

The public rows are redacted and non-weaponizable. They are intended to verify computation and metadata consistency, not to reproduce unsafe inputs.
