from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class PipelineDefinition:
    pipeline_id: str
    name: str
    components: List[str]
    cost_proxy: float
    latency_proxy: float
    notes: str

    def to_dict(self):
        return asdict(self)


PIPELINES: Dict[str, PipelineDefinition] = {
    "P0": PipelineDefinition("P0", "No guard", ["MLLM"], 1.00, 1.00, "Unguarded target MLLM baseline."),
    "P1": PipelineDefinition("P1", "Explicit-untrusted wrapper", ["D1_image", "MLLM"], 1.02, 1.02, "D1 wrapper applied to original image/task context."),
    "P2": PipelineDefinition("P2", "OCR gate plus wrapper", ["D2", "D1_text", "MLLM"], 1.32, 1.35, "OCR-first gate plus explicit-untrusted wrapper on extracted text."),
    "P3": PipelineDefinition("P3", "OCR-to-text classifier", ["D2", "D3"], 0.80, 0.80, "Text-first classifier-level allow/block baseline; no target MLLM call in this baseline."),
    "P4": PipelineDefinition("P4", "Risk-routed blueprint", ["RiskScore", "P1/P2/P3/P5"], 0.0, 0.0, "Blueprint/meta-router; not evaluated as a production-certified pipeline."),
    "P5": PipelineDefinition("P5", "Human review escalation", ["human_review", "run_record"], 0.0, 0.0, "Manual review/escalation path for mandatory or strict-FRR cases."),
    "P2_D2": PipelineDefinition("P2_D2", "D2-only ablation", ["D2", "MLLM"], 1.30, 1.30, "Diagnostic ablation only; not part of the formal deployment design space."),
}


def pipeline_table() -> List[Dict[str, object]]:
    return [p.to_dict() for p in PIPELINES.values()]
