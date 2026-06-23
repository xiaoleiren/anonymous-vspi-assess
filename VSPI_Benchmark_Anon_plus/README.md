# VSPI Supplemental Material (Artifact Overview)

This supplemental package accompanies the manuscript:

**“Visual-Structural Prompt Injection: Measuring Cross-Modal Policy Gaps in Multimodal LLMs on Text-Rich Inputs.”**

It provides a **redacted, de-weaponized scaffold** of the evaluation pipeline used in the paper, aimed at:

- validating the end-to-end rendering → inference → judging → table-generation flow on safe data,
- documenting the artifact structure,
- enabling internal reproduction on non-weaponizable inputs.

It is **not** a full public release of all private evaluation assets. Raw harmful prompts, weaponizable payload strings, non-redacted benchmark data, and private judge configurations are intentionally omitted.

---

## Directory structure

```
VSPI_Benchmark_Anon_plus/
├── README.md                  # This document
├── LICENSE                    # MIT license for the scaffold
├── requirements.txt           # Python dependencies
├── AUDIT_REPORT.md            # Safety and redaction audit notes
├── CHANGES_2025.md            # Change log for the artifact
├── configs/
│   ├── experiment_common.json # Global experiment settings
│   └── model_registry.json    # Model identifiers and metadata
├── data/
│   ├── experiment_dataset_50_redacted.csv # Redacted example prompts (safe subset)
│   └── README_DATA.md         # Data card and selection notes
├── analysis/
│   └── compute_tables.py      # Manifest-driven table generation from judged runs
├── defenses/
│   └── policies.py            # Lightweight defenses (e.g., OCR-gating, inst_data_sep)
├── evaluation/
│   ├── judge.py               # Safe public scaffold judge implementation
│   └── run_inference.py       # Inference harness entry point
├── generators/
│   ├── _common.py             # Shared rendering helpers
│   ├── render_typography_only.py # Typography-only control templates
│   ├── render_vspi_diagram.py # VSPI diagram/document templates
│   └── render_vspi_terminal.py# VSPI terminal/log templates
├── manifests/
│   ├── table1_main.csv        # Manifest for main results table
│   ├── table2_robust.csv      # Manifest for robustness table
│   └── table3_ablation.csv    # Manifest for attribution/ablation table
├── models/
│   ├── dummy.py               # Deterministic dummy backend for smoke tests
│   ├── gemini_client.py       # Optional Gemini wrapper (non-essential)
│   └── openai_client.py       # Optional OpenAI wrapper (non-essential)
├── sample_outputs/
│   └── images/                # De-weaponized illustrative images
│       ├── typography_only/
│       ├── vspi_diagram/
│       └── vspi_terminal/
├── scripts/
│   ├── check_repo.sh          # Repository health-check and smoke test
│   ├── run_all_dummy.sh       # Example end-to-end dummy run
│   └── run_safe_matrix.sh     # Safe matrix: generate, run dummy, judge, build tables
├── utils/
│   ├── bootstrap.py           # Bootstrap and summary utilities
│   ├── io.py                  # JSONL / CSV IO helpers
│   └── transforms.py          # Transform sweep and Min-rASR support
└── paper/
    └── tables/                # Generated LaTeX/JSON tables from judged runs

```
Quick start (safe smoke test)
We recommend running a local smoke test on the redacted subset to validate the pipeline:
```
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 1) Repository health-check and dummy end-to-end run
bash scripts/check_repo.sh

# 2) Generate de-weaponized images, run dummy inference, judge outputs, and build tables
bash scripts/run_safe_matrix.sh
```

After a successful run, you should see:
```
results/images/ – generated example VSPI / typography-only / control images,

results/logs/ – dummy inference logs and judged JSONL files,

paper/tables/ – LaTeX/JSON tables corresponding to the manifests in manifests/.
```
The dummy backend in models/dummy.py suffices for all public smoke tests. Optional OpenAI / Gemini wrappers are provided only for approved, non-weaponizable internal evaluations and are not required to reproduce the supplemental results.

Paper-to-code mapping (mini)
The following mapping links key paper components to this scaffold:

VSPI terminal/log template family → generators/render_vspi_terminal.py

VSPI diagram/document template family → generators/render_vspi_diagram.py

Typography-only control templates → generators/render_typography_only.py

Transform sweep and Min-rASR utilities → utils/transforms.py

Lightweight defenses (e.g., ocr_gating, inst_data_sep) → defenses/policies.py

Inference harness → evaluation/run_inference.py

Public scaffold judge → evaluation/judge.py

Table generation from judged JSONL → analysis/compute_tables.py

Table manifests (main, robustness, attribution) → manifests/table1_main.csv, table2_robust.csv, table3_ablation.csv

Scope and safety

This artifact is designed for artifact transparency and safe pipeline validation:

It reproduces the structure of the evaluation pipeline and the behavior of de-weaponized smoke tests.

It does not release raw harmful prompts, weaponizable payloads, private human audit labels, or exact closed-model outputs used in the full paper benchmark.

Users should restrict experiments on this scaffold to non-weaponizable content and adhere to local safety and compliance policies.
