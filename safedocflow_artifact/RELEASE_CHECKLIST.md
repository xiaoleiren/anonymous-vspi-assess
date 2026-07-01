# Release checklist

This package was checked before zipping with:

```bash
bash scripts/check_repo.sh
```

The check performs:

1. Python compilation for the SafeDocFlow package and legacy scaffold modules.
2. Exact validation of public paper-number metadata, including Clopper-Pearson intervals, Fisher and McNemar exact tests, policy loss, break-even values, LLaVA supplemental counts, D2-only ablation counts, and RiskScore examples.
3. Run-record schema validation, including `boundary_band`, `workflow_predicates`, and guard/final-label consistency.
4. P3 classifier-card/version consistency check.
5. Safe dummy end-to-end rendering, inference, judging, and table-generation smoke test.

Known intentional omissions:

- Raw harmful prompts and actionable payloads.
- Private closed-model outputs.
- Non-redacted human audit notes.
- Institution-identifying metadata.

Before public posting, confirm that any private/DOI-linked archive referenced by the manuscript contains the corresponding private run records and that the public package contains only approved redacted material.
