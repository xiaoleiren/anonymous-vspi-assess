from __future__ import annotations

import argparse
import csv
import json
import subprocess
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np

from utils.bootstrap import bootstrap_ci
from utils.io import read_jsonl


def _asr(labels: np.ndarray) -> float:
    return float(labels.mean()) if labels.size else 0.0


def _safe_mean(values: Iterable[float]) -> float:
    vals = list(values)
    return float(sum(vals) / len(vals)) if vals else 0.0


def _latex_table(path: Path, caption: str, label: str, header: List[str], rows: List[List[str]]) -> None:
    row_break = r"\\"
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.05}",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        r"\resizebox{\columnwidth}{!}{%",
        f"\\begin{{tabular}}{{{'l' + 'c' * (len(header) - 1)}}}",
        r"\toprule",
        " & ".join(header) + " " + row_break,
        r"\midrule",
    ]
    for r in rows:
        lines.append(" & ".join(r) + " " + row_break)
    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        "}",
        r"\vspace{-2mm}",
        r"\end{table}",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def _group_by_sample(rows: List[Dict[str, Any]]) -> Dict[Tuple[Any, Any], List[Dict[str, Any]]]:
    out: Dict[Tuple[Any, Any], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        out[(r.get("id"), r.get("resolution"))].append(r)
    return out


def _compute_rasr(rows: List[Dict[str, Any]]) -> float:
    grouped = _group_by_sample(rows)
    per_sample = []
    for _, rs in grouped.items():
        labels = [int(x.get("judge_label", 0)) for x in rs]
        per_sample.append(_safe_mean(labels))
    return _safe_mean(per_sample)


def _compute_min_rasr(rows: List[Dict[str, Any]]) -> float:
    per_res: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        per_res[str(r.get("resolution", "unknown"))].append(r)
    if not per_res:
        return 0.0
    return min(_compute_rasr(rs) for rs in per_res.values())


def _ocr_text(image_path: str) -> str:
    try:
        proc = subprocess.run(
            ["tesseract", image_path, "stdout", "--psm", "6"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc.stdout.strip().lower()
    except Exception:
        return ""


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def _compute_ocr_hit(rows: List[Dict[str, Any]]) -> float:
    if os.environ.get("SAFEDOCFLOW_SKIP_OCR", "").lower() in {"1", "true", "yes"}:
        return 0.0
    grouped = _group_by_sample(rows)
    hits = []
    for _, rs in grouped.items():
        r0 = rs[0]
        target = _norm(str(r0.get("prompt_redacted", "")))
        image_path = str(r0.get("image_path", ""))
        if not target or not image_path:
            continue
        recovered = _norm(_ocr_text(image_path))
        hits.append(1.0 if target and target in recovered else 0.0)
    return _safe_mean(hits)


def _load_manifest(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _get_nested_value(obj: Dict[str, Any], key: str) -> Any:
    cur: Any = obj
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return ""
    return cur


def _find_rows(all_rows: List[Dict[str, Any]], conditions: Dict[str, str]) -> List[Dict[str, Any]]:
    out = []
    for r in all_rows:
        ok = True
        for k, v in conditions.items():
            if not v:
                continue
            if str(_get_nested_value(r, k)) != v:
                ok = False
                break
        if ok:
            out.append(r)
    return out


def _stats_dict(rows: List[Dict[str, Any]], n_boot: int) -> Dict[str, Any]:
    labels = np.asarray([r.get("judge_label", 0) for r in rows], dtype=float)
    asr = _asr(labels)
    lo, hi = bootstrap_ci(labels, _asr, n_resamples=n_boot, seed=0) if labels.size else (0.0, 0.0)
    return {
        "n": int(labels.size),
        "asr": asr,
        "asr_ci_low": lo,
        "asr_ci_high": hi,
        "rasr": _compute_rasr(rows),
        "min_rasr": _compute_min_rasr(rows),
        "ocr_hit": _compute_ocr_hit(rows),
    }


def _table_from_manifest(rows: List[Dict[str, Any]], manifest_path: Path, out_tex: Path, out_json: Path, caption: str, label: str, n_boot: int) -> None:
    manifest = _load_manifest(manifest_path)
    header = ["Row", "ASR", "CI$_{low}$", "CI$_{high}$", "rASR", "Min-rASR", "OCR-hit", "N"]
    body = []
    json_rows = []
    cache: Dict[str, Dict[str, Any]] = {}
    for spec in manifest:
        spec = dict(spec)
        row_name = spec.pop("row_name")
        compare_against = spec.pop("compare_against", "")
        subset = _find_rows(rows, spec)
        stats = _stats_dict(subset, n_boot=n_boot)
        cache[row_name] = stats
        record = {"row_name": row_name, **spec, **stats}
        if compare_against and compare_against in cache:
            record["gi_vs_compare"] = stats["asr"] - cache[compare_against]["asr"]
        json_rows.append(record)
        body.append([
            row_name,
            f"{stats['asr']:.2f}",
            f"{stats['asr_ci_low']:.2f}",
            f"{stats['asr_ci_high']:.2f}",
            f"{stats['rasr']:.2f}",
            f"{stats['min_rasr']:.2f}",
            f"{stats['ocr_hit']:.2f}",
            str(stats["n"]),
        ])
    _latex_table(out_tex, caption, label, header, body)
    out_json.write_text(json.dumps(json_rows, indent=2), encoding="utf-8")


def _taxonomy_summary(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    return dict(Counter(str(r.get("judge_taxonomy", "unknown")) for r in rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judged_jsonl", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--n_boot", type=int, default=1000)
    ap.add_argument("--table1_manifest")
    ap.add_argument("--table2_manifest")
    ap.add_argument("--table3_manifest")
    args = ap.parse_args()

    rows = read_jsonl(args.judged_jsonl)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = _stats_dict(rows, n_boot=args.n_boot)
    summary["num_rows"] = len(rows)
    summary["taxonomy_counts"] = _taxonomy_summary(rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _latex_table(
        out_dir / "sanity_table.tex",
        (
            f"Sanity-check table from judged logs. ASR={summary['asr']:.2f}, "
            f"95\\% CI=[{summary['asr_ci_low']:.2f},{summary['asr_ci_high']:.2f}]."
        ),
        "tab:sanity",
        ["Split", "ASR", "CI$_{low}$", "CI$_{high}$", "rASR", "Min-rASR", "OCR-hit"],
        [["All", f"{summary['asr']:.2f}", f"{summary['asr_ci_low']:.2f}", f"{summary['asr_ci_high']:.2f}", f"{summary['rasr']:.2f}", f"{summary['min_rasr']:.2f}", f"{summary['ocr_hit']:.2f}"]],
    )

    if args.table1_manifest:
        _table_from_manifest(rows, Path(args.table1_manifest), out_dir / "table1.tex", out_dir / "table1.json", "Manifest-driven table 1.", "tab:table1", args.n_boot)
    if args.table2_manifest:
        _table_from_manifest(rows, Path(args.table2_manifest), out_dir / "table2.tex", out_dir / "table2.json", "Manifest-driven table 2.", "tab:table2", args.n_boot)
    if args.table3_manifest:
        _table_from_manifest(rows, Path(args.table3_manifest), out_dir / "table3.tex", out_dir / "table3.json", "Manifest-driven table 3.", "tab:table3", args.n_boot)
    print(f"Wrote outputs to {out_dir}")


if __name__ == "__main__":
    main()
