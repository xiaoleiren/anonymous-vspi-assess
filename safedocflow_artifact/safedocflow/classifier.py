from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, Tuple

CLASSIFIER_NAME = "SafeDocFlow-D3-reference-v1"
CLASSIFIER_VERSION = "SafeDocFlow-D3-reference-v1.0.0"
DECISION_THRESHOLD = 1  # rule-hit threshold for block/high-risk classification

RISK_RULES = {
    "instruction_override": [r"ignore (previous|prior)", r"override", r"bypass", r"system prompt"],
    "procedure_like": [r"step\s*1", r"run\s+[/A-Za-z0-9_.-]+", r"execute", r"command"],
    "policy_sensitive": [r"credential", r"access control", r"audit window", r"redacted"],
}


@dataclass(frozen=True)
class ClassifierDecision:
    classifier_name: str
    classifier_version: str
    threshold: int
    label: str
    score: int
    matched_rules: Dict[str, bool]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def classify_text(text: str) -> ClassifierDecision:
    t = (text or "").lower()
    matched: Dict[str, bool] = {}
    score = 0
    for name, patterns in RISK_RULES.items():
        hit = any(re.search(p, t) for p in patterns)
        matched[name] = hit
        score += int(hit)
    label = "block" if score >= DECISION_THRESHOLD else "allow"
    return ClassifierDecision(CLASSIFIER_NAME, CLASSIFIER_VERSION, DECISION_THRESHOLD, label, score, matched)
