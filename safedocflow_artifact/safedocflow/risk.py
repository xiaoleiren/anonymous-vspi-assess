from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Mapping, Optional

DEFAULT_WEIGHTS = {
    "R": 0.25,   # OCR recoverability
    "S_T": 0.20, # visual/structural cue strength
    "F": 0.25,   # task-framing risk
    "C": 0.30,   # content/workflow consequence
}
TAU_LOW = 40.0
TAU_HIGH = 70.0
BOUNDARY_WIDTH = 5.0


@dataclass(frozen=True)
class WorkflowProfile:
    """Cold-start workflow profile used by Algorithm 1.

    The numeric cost ratio fields are local deployment inputs. The manuscript's
    pooled diagnostic value lambda ~= 3.55 is deliberately not hard-coded here;
    deployment use should compare against a locally recalibrated lambda_star.
    """

    name: str
    fn_cost_level: str = "medium"  # low | medium | high | very_high
    false_negative_to_false_reject_cost_ratio: Optional[float] = None
    lambda_star_local: Optional[float] = None
    safety_critical_domain: bool = False
    strict_frr_tolerance: bool = False
    mandatory_review: bool = False
    regulated_compliance: bool = False
    human_review_capacity: str = "limited"  # none | limited | available
    text_first_required: bool = False
    ocr_available: bool = True
    classifier_available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_weights(weights: Mapping[str, float]) -> Dict[str, float]:
    total = float(sum(weights.values()))
    if total <= 0:
        raise ValueError("RiskScore weights must have positive sum")
    return {k: float(v) / total for k, v in weights.items()}


def risk_score(features: Mapping[str, float], weights: Mapping[str, float] | None = None) -> float:
    """Compute SafeDocFlow-RiskScore in [0, 100]."""
    w = normalize_weights(weights or DEFAULT_WEIGHTS)
    missing = [k for k in ("R", "S_T", "F", "C") if k not in features]
    if missing:
        raise KeyError(f"Missing RiskScore features: {missing}")
    score = 100.0 * sum(float(features[k]) * w[k] for k in ("R", "S_T", "F", "C"))
    return round(score, 6)


def in_boundary_band(score: float, tau_low: float = TAU_LOW, tau_high: float = TAU_HIGH, width: float = BOUNDARY_WIDTH) -> bool:
    """Return True if score is close to either routing threshold.

    Boundary band is an audit/review-priority flag, not an independent routing
    branch. Local policies may map this flag to P5, but Algorithm 1 continues to
    use the normal risk branch unless mandatory_review is triggered.
    """
    return abs(score - tau_low) <= width or abs(score - tau_high) <= width


def workflow_predicates(profile: WorkflowProfile) -> Dict[str, bool]:
    """Evaluate the executable workflow predicates used by Algorithm 1.

    high_fn_cost is true when the workflow explicitly marks FN cost high, when
    policy assigns the artifact to a regulated/high-consequence context, or when
    a local cost ratio exceeds the locally recalibrated lambda_star_local. The
    manuscript's pooled diagnostic reference (about 3.55) is not used as a
    universal threshold.
    """
    level = (profile.fn_cost_level or "").lower()
    local_ratio_exceeds = False
    if profile.false_negative_to_false_reject_cost_ratio is not None and profile.lambda_star_local is not None:
        local_ratio_exceeds = profile.false_negative_to_false_reject_cost_ratio >= profile.lambda_star_local
    return {
        "high_fn_cost": level in {"high", "very_high"} or profile.regulated_compliance or local_ratio_exceeds,
        "safety_critical_domain": bool(profile.safety_critical_domain or profile.regulated_compliance),
        "strict_frr_tolerance": bool(profile.strict_frr_tolerance),
        "mandatory_review": bool(profile.mandatory_review),
        "text_first_required": bool(profile.text_first_required),
        "ocr_available": bool(profile.ocr_available),
        "classifier_available": bool(profile.classifier_available),
    }


def route_pipeline(
    features: Mapping[str, float],
    profile: WorkflowProfile,
    weights: Mapping[str, float] | None = None,
    tau_low: float = TAU_LOW,
    tau_high: float = TAU_HIGH,
) -> Dict[str, Any]:
    """Executable SafeDocFlow routing logic corresponding to Algorithm 1."""
    score = risk_score(features, weights)
    preds = workflow_predicates(profile)
    boundary = in_boundary_band(score, tau_low=tau_low, tau_high=tau_high)
    audit_flags = []
    if boundary:
        audit_flags.append("boundary_band")

    if preds["mandatory_review"]:
        selected = "P5"
        reason = "mandatory_review"
    elif score >= tau_high:
        if preds["high_fn_cost"]:
            if preds["strict_frr_tolerance"]:
                selected = "P5"
                reason = "high_risk_high_fn_strict_frr"
            elif preds["text_first_required"] and preds["classifier_available"]:
                selected = "P3"
                reason = "high_risk_high_fn_text_first"
            else:
                selected = "P2"
                reason = "high_risk_high_fn"
        else:
            selected = "P1"
            reason = "high_risk_without_high_fn_cost"
            audit_flags.append("high_risk_audit")
    elif score >= tau_low:
        if preds["high_fn_cost"] and preds["safety_critical_domain"]:
            if preds["strict_frr_tolerance"]:
                selected = "P5"
                reason = "medium_risk_high_fn_safety_critical_strict_frr"
            else:
                selected = "P2"
                reason = "medium_risk_high_fn_safety_critical"
                audit_flags.append("audit_flag")
        else:
            selected = "P1"
            reason = "medium_risk_default_wrapper"
            audit_flags.append("enhanced_audit_logging")
    else:
        selected = "P1"
        reason = "low_risk_default_wrapper"

    return {
        "risk_score": score,
        "selected_pipeline": selected,
        "routing_reason": reason,
        "boundary_band": boundary,
        "workflow_predicates": preds,
        "audit_flags": audit_flags,
    }
