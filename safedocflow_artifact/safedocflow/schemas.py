from __future__ import annotations

REQUIRED_RUN_RECORD_FIELDS = [
    "schema_version",
    "sample_id",
    "image_hash",
    "prompt_hash",
    "template_family",
    "workflow_profile",
    "feature_vector",
    "risk_score",
    "boundary_band",
    "workflow_predicates",
    "selected_pipeline",
    "model_snapshot",
    "ocr_version",
    "classifier_version",
    "judge_version",
    "guard_output",
    "review_status",
    "final_label",
]


def validate_run_record(record: dict) -> list[str]:
    missing = [k for k in REQUIRED_RUN_RECORD_FIELDS if k not in record]
    errors = [f"missing:{k}" for k in missing]
    if record.get("review_status") == "not_reviewed" and record.get("human_override") in (None, "", False):
        guard_class = str(record.get("guard_output", "")).split(":", 1)[0]
        final_label = str(record.get("final_label", ""))
        if guard_class and final_label and guard_class != final_label:
            errors.append("guard_output_final_label_mismatch")
    return errors
