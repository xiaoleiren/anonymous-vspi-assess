# SafeDocFlow artifact audit summary

## Scope of this artifact

This repository is a de-weaponized, anonymized artifact for the SafeDocFlow manuscript. It is intended to let reviewers inspect and execute the computation, routing, run-record, and table-validation logic while avoiding release of raw harmful prompts or private model outputs.

## Key repairs relative to the older VSPI scaffold

1. Rebranded and reorganized the package around SafeDocFlow rather than the earlier VSPI-only benchmark scaffold.
2. Added executable RiskScore, workflow-predicate, boundary-band, and routing logic matching Algorithm 1.
3. Added run-record schema checks and redacted example run records with `boundary_band` and `workflow_predicates` fields.
4. Added a versioned P3 classifier scaffold (`SafeDocFlow-D3-reference-v1`) and classifier card.
5. Added redacted paper-metric tables for the main diagnostic gap, defense pair, LLaVA supplement, D2-only ablation, policy loss, break-even analysis, and RiskScore stability.
6. Added `analysis/validate_paper_numbers.py`, which recomputes core paper statistics from the redacted metric files.
7. Removed stale bytecode and generated-cache files from the release package.
8. Kept legacy renderers and dummy inference scripts for safe local smoke testing.

## What is verifiable here

- Exact Clopper-Pearson interval calculations used in the public tables.
- McNemar and Fisher exact p-values reported in the manuscript.
- P1/P2/P2_D2/P3/P0 pooled fractions used by the policy-loss and break-even demonstrations.
- RiskScore worked examples and routing predicates.
- P3 classifier metadata and run-record fields.
- LLaVA supplemental and D2-only ablation aggregate arithmetic.

## What is intentionally not included

- Raw harmful or actionable prompts.
- Private closed-model responses.
- Non-redacted human-audit notes.
- Any operational payload text.

## Bottom line

The package is suitable for reviewer-facing artifact inspection, smoke testing, and verification of the manuscript's public arithmetic and routing claims. It is not a public release of unsafe benchmark contents.
