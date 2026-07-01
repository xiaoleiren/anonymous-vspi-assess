from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from safedocflow.classifier import classify_text
from safedocflow.io import read_jsonl, write_jsonl


def main() -> None:
    ap = argparse.ArgumentParser(description="Run SafeDocFlow-D3-reference-v1 on OCR/text rows.")
    ap.add_argument("--in_jsonl", required=True, help="Input JSONL containing ocr_text or text fields")
    ap.add_argument("--out_jsonl", required=True)
    args = ap.parse_args()

    rows = read_jsonl(args.in_jsonl)
    out: List[Dict[str, Any]] = []
    for r in rows:
        text = str(r.get("ocr_text", r.get("text", r.get("response_text", ""))))
        dec = classify_text(text)
        r2 = dict(r)
        r2["classifier_version"] = dec.classifier_version
        r2["classifier_name"] = dec.classifier_name
        r2["classifier_threshold"] = dec.threshold
        r2["classifier_score"] = dec.score
        r2["classifier_label"] = dec.label
        r2["classifier_matched_rules"] = dec.matched_rules
        out.append(r2)
    write_jsonl(args.out_jsonl, out)
    print(f"Wrote classified rows to {args.out_jsonl}")


if __name__ == "__main__":
    main()
