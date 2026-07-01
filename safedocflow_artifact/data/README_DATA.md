# Data directory

This directory contains only redacted or synthetic public artifact data.

## Files

- `experiment_dataset_50_redacted.csv`: tiny safe smoke-test dataset for rendering and dummy inference.
- `paper_metrics/*.csv`: redacted aggregate and per-item metadata used to validate paper tables and calculations.
- `run_records/redacted_example_run_records.jsonl`: redacted run-record examples with RiskScore, workflow predicates, boundary-band flags, selected pipeline, model/classifier metadata, and final labels.

## Safety restrictions

Do not add raw harmful strings, actionable payloads, private user records, or non-redacted closed-model outputs. The manuscript's private evaluation data should remain in an approved secure archive.
