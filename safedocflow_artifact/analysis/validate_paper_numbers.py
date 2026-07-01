from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

from safedocflow.risk import WorkflowProfile, risk_score, route_pipeline
from safedocflow.schemas import validate_run_record
from safedocflow.stats import clopper_pearson, fisher_p, mcnemar_exact_p, policy_loss, pooled_break_even, prevalence_break_even
from safedocflow.io import read_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "paper_metrics"
OUT = ROOT / "paper" / "tables" / "generated"


def read_csv(name: str) -> List[Dict[str, str]]:
    with (DATA / name).open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def assert_close(name: str, got: float, expected: float, tol: float = 5e-4) -> None:
    if abs(got - expected) > tol:
        raise AssertionError(f"{name}: got {got}, expected {expected}")


def fmt(x: float, digits: int = 3) -> float:
    return float(f"{x:.{digits}f}")


def validate_main_results(summary: Dict[str, object]) -> None:
    rows = read_csv("main_results.csv")
    expected = {
        "GPT-4o": (0.06, 0.28, 0.22),
        "Gemini 1.5 Pro": (0.07, 0.31, 0.24),
        "LLaVA-v1.6-34B": (0.10, 0.38, 0.28),
        "InternVL2-76B": (0.07, 0.34, 0.27),
    }
    out = []
    for r in rows:
        model = r["model"]
        text = int(r["text_unsafe"]) / int(r["text_total"])
        vspi = int(r["vspi_unsafe"]) / int(r["vspi_total"])
        gi = vspi - text
        exp_text, exp_vspi, exp_gi = expected[model]
        assert_close(f"{model} text", text, exp_text)
        assert_close(f"{model} vspi", vspi, exp_vspi)
        assert_close(f"{model} gi", gi, exp_gi)
        p = mcnemar_exact_p(int(r["b_vspi_unsafe_text_safe"]), int(r["c_text_unsafe_vspi_safe"]))
        assert p < 0.001
        total = sum(int(r[k]) for k in ["a_both_unsafe", "b_vspi_unsafe_text_safe", "c_text_unsafe_vspi_safe", "d_both_safe"])
        if total != 100:
            raise AssertionError(f"{model} paired table does not sum to 100")
        out.append({"model": model, "text_asr": text, "vspi_asr": vspi, "gap": gi, "mcnemar_p": p})
    summary["main_results"] = out


def validate_defense(summary: Dict[str, object]) -> None:
    rows = read_csv("pipeline_summary.csv")
    by_pipe = {r["pipeline"]: r for r in rows}
    expected = {
        "P0": (25, 80, 0, 80, 1.00),
        "P1": (11, 80, 0, 80, 1.02),
        "P2": (7, 80, 13, 80, 1.32),
        "P3": (16, 80, 9, 80, 0.80),
        "P2_D2": (9, 80, 9, 80, 1.30),
    }
    out = {}
    for pipe, exp in expected.items():
        r = by_pipe[pipe]
        ak, an, fk, fn, cost = exp
        if tuple(map(int, [r["asr_unsafe"], r["asr_total"], r["frr_reject"], r["frr_total"]])) != (ak, an, fk, fn):
            raise AssertionError(f"bad counts for {pipe}")
        assert_close(f"{pipe} cost", float(r["cost"]), cost)
        asr_ci = clopper_pearson(ak, an)
        frr_ci = clopper_pearson(fk, fn)
        out[pipe] = {
            "asr": ak / an,
            "asr_ci": [fmt(asr_ci[0]), fmt(asr_ci[1])],
            "frr": fk / fn,
            "frr_ci": [fmt(frr_ci[0]), fmt(frr_ci[1])],
            "cost": cost,
        }
    # Core checks
    assert_close("P1 relative reduction", (25 - 11) / 25, 0.56)
    assert_close("P2 relative reduction", (25 - 7) / 25, 0.72)
    assert_close("P2 Full FRR CP upper", out["P2"]["frr_ci"][1], 0.262, tol=5e-4)
    summary["pipeline_summary"] = out


def validate_mcnemar_and_fisher(summary: Dict[str, object]) -> None:
    rows = read_csv("mcnemar_pairing.csv")
    counts = {(r["p1"], r["p2"]): int(r["count"]) for r in rows}
    b = counts[("unsafe", "safe")]
    c = counts[("safe", "unsafe")]
    p_mcn = mcnemar_exact_p(b, c)
    p_fish = fisher_p(11, 80, 7, 80)
    assert_close("mcnemar p", p_mcn, 0.125)
    assert_close("aggregate fisher p", p_fish, 0.4538, tol=1e-3)
    summary["p1_p2_tests"] = {"mcnemar_p": p_mcn, "aggregate_fisher_p": p_fish, "b": b, "c": c}


def validate_ablation(summary: Dict[str, object]) -> None:
    p1_vs_d2 = fisher_p(11, 80, 9, 80)
    d2_vs_p2 = fisher_p(9, 80, 7, 80)
    d2_frr_vs_p2_frr = fisher_p(9, 80, 13, 80)
    assert_close("P1 vs P2_D2 ASR fisher", p1_vs_d2, 0.812, tol=1e-3)
    assert_close("P2_D2 vs P2 ASR fisher", d2_vs_p2, 0.793, tol=1e-3)
    assert_close("P2_D2 vs P2 FRR fisher", d2_frr_vs_p2_frr, 0.492, tol=1e-3)
    cats = read_csv("ablation_frr_category.csv")
    d2_total = sum(int(r["p2_d2_reject"]) for r in cats)
    p2_total = sum(int(r["p2_reject"]) for r in cats)
    n_total = sum(int(r["n_ben"]) for r in cats)
    if (d2_total, p2_total, n_total) != (9, 13, 80):
        raise AssertionError("ablation FRR category totals mismatch")
    summary["ablation_tests"] = {"p1_vs_d2_fisher": p1_vs_d2, "d2_vs_p2_asr_fisher": d2_vs_p2, "d2_vs_p2_frr_fisher": d2_frr_vs_p2_frr}


def validate_loss_and_break_even(summary: Dict[str, object]) -> None:
    pipes = {r["pipeline"]: r for r in read_csv("pipeline_summary.csv")}
    rates = {}
    for k, r in pipes.items():
        rates[k] = {
            "asr": int(r["asr_unsafe"]) / int(r["asr_total"]),
            "frr": int(r["frr_reject"]) / int(r["frr_total"]),
            "cost": float(r["cost"]),
        }
    lam_star = pooled_break_even(rates["P1"]["asr"], rates["P2"]["asr"], rates["P1"]["frr"], rates["P2"]["frr"], rates["P1"]["cost"], rates["P2"]["cost"])
    assert_close("pooled break-even", lam_star, 3.55)
    prev = {float(r["benign_prevalence"]): float(r["lambda_star"]) for r in read_csv("prevalence_sensitivity.csv")}
    for rb, expected in [(0.50, 3.85), (0.80, 14.50), (0.90, 32.25), (0.99, 351.75), (0.999, 3546.75)]:
        got = prevalence_break_even(rates["P1"]["asr"], rates["P2"]["asr"], rates["P1"]["frr"], rates["P2"]["frr"], rates["P1"]["cost"], rates["P2"]["cost"], rb)
        assert_close(f"prevalence {rb}", got, expected)
        assert_close(f"prevalence table {rb}", prev[rb], expected)
    # Check policy-loss table.
    for r in read_csv("policy_loss.csv"):
        pipe = r["pipeline"]
        lam = float(r["lambda"])
        expected = float(r["loss"])
        got = policy_loss(rates[pipe]["asr"], rates[pipe]["frr"], rates[pipe]["cost"], lam)
        assert_close(f"policy loss {pipe} lambda {lam}", got, expected)
    summary["break_even"] = {"pooled_lambda_star": lam_star, "prevalence_lambda_star": prev}


def validate_llava(summary: Dict[str, object]) -> None:
    rows = {r["pipeline"]: r for r in read_csv("llava_defense.csv")}
    assert rows["P0"]["asr_unsafe"] == "15"
    lo, hi = clopper_pearson(15, 40)
    assert_close("llava P0 CI low", fmt(lo), 0.227)
    assert_close("llava P0 CI high", fmt(hi), 0.542)
    p1_total = 11 + 6
    p2_total = 7 + 4
    p2_frr = 13 + 6
    assert (p1_total, p2_total, p2_frr) == (17, 11, 19)
    summary["llava_supplement"] = {"p1_pooled": "17/120", "p2_pooled": "11/120", "p2_frr_pooled": "19/120"}


def validate_risk_and_run_records(summary: Dict[str, object]) -> None:
    features = {"R": 1.0, "S_T": 1.0, "F": 0.5, "C": 0.5}
    assert_close("default risk", risk_score(features), 72.5)
    assert_close("equal risk", risk_score(features, {"R": .25, "S_T": .25, "F": .25, "C": .25}), 75.0)
    assert_close("recoverability risk", risk_score(features, {"R": .35, "S_T": .20, "F": .20, "C": .25}), 77.5)
    assert_close("severity risk", risk_score(features, {"R": .15, "S_T": .20, "F": .15, "C": .50}), 67.5)
    profile = WorkflowProfile(name="balanced_enterprise", fn_cost_level="high", safety_critical_domain=True, strict_frr_tolerance=False, lambda_star_local=14.5, false_negative_to_false_reject_cost_ratio=5.0)
    routed = route_pipeline(features, profile)
    if routed["selected_pipeline"] != "P2":
        raise AssertionError(f"Expected P2 route, got {routed}")
    strict_profile = WorkflowProfile(name="strict_review", fn_cost_level="high", safety_critical_domain=True, strict_frr_tolerance=True, lambda_star_local=14.5, false_negative_to_false_reject_cost_ratio=5.0)
    strict_route = route_pipeline({"R":1,"S_T":1,"F":1,"C":1}, strict_profile)
    if strict_route["selected_pipeline"] != "P5":
        raise AssertionError("strict high-risk profile should route to P5")
    records = read_jsonl(ROOT / "data" / "run_records" / "redacted_example_run_records.jsonl")
    for rec in records:
        errors = validate_run_record(rec)
        if errors:
            raise AssertionError(f"run-record validation failed: {errors}")
    summary["risk_score"] = {"worked_example_default": risk_score(features), "strict_high_risk_route": strict_route}


def validate_risk_stability(summary: Dict[str, object]) -> None:
    rows = read_csv("risk_score_stability.csv")
    total = sum(int(r["samples"]) for r in rows)
    crossed = sum(int(r["crossed_threshold"]) for r in rows)
    if (total, crossed) != (100, 4):
        raise AssertionError("risk stability totals mismatch")
    summary["risk_stability"] = {"samples": total, "crossed": crossed, "volatility": crossed / total}


def validate_p3_classifier(summary: Dict[str, object]) -> None:
    from safedocflow.classifier import CLASSIFIER_NAME, CLASSIFIER_VERSION, classify_text
    card = json.loads((ROOT / "configs" / "p3_classifier_card.json").read_text(encoding="utf-8"))
    if card["classifier_name"] != CLASSIFIER_NAME:
        raise AssertionError("classifier card/name mismatch")
    decision = classify_text("redacted maintenance note: run review command before audit window")
    if decision.classifier_version != CLASSIFIER_VERSION:
        raise AssertionError("classifier version mismatch")
    summary["p3_classifier"] = {"classifier_name": CLASSIFIER_NAME, "classifier_version": CLASSIFIER_VERSION, "demo_label": decision.label}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary: Dict[str, object] = {}
    validate_main_results(summary)
    validate_defense(summary)
    validate_mcnemar_and_fisher(summary)
    validate_ablation(summary)
    validate_loss_and_break_even(summary)
    validate_llava(summary)
    validate_risk_and_run_records(summary)
    validate_risk_stability(summary)
    validate_p3_classifier(summary)
    (OUT / "validation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print("Validated SafeDocFlow artifact numbers and routing invariants.")
    print(f"Wrote {OUT / 'validation_summary.json'}")


if __name__ == "__main__":
    main()
