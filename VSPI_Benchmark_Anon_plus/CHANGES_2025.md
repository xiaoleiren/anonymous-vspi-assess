# 2025-oriented completion pass

This bundle extends the earlier repaired scaffold toward a closer-to-complete late-2025 style evaluation artifact, while remaining de-weaponized.

## Added in this pass

- Optional OpenAI Responses API wrapper.
- Optional Gemini Google GenAI wrapper.
- Defense modules (`ocr_gating`, `inst_data_sep`).
- Richer run-record fields (timestamps, hashes, decoding config, render metadata).
- Task-prompt presets including `no_benign_framing`.
- Manifest-driven tables for main results, robustness, and ablations.
- Render manifests.
- Safe end-to-end matrix script.
- Dummy backend updated to create stable trend-like behavior for pipeline testing.

## Still not included

- Raw harmful prompt suite.
- Publication-grade judge or human audit labels.
- Exact closed-model paper numbers.
- White-box/open-checkpoint jailbreak optimization.
- Any weaponizable payload content.

## Practical status

This repo is now suitable for:

- artifact sanity checking
- safe pipeline validation
- internal approved redacted experiments
- reproducing table-generation logic and run-record structure

It is still not equivalent to a full release of the final paper artifact.
