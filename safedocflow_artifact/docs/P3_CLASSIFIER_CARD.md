# P3 classifier card: SafeDocFlow-D3-reference-v1

**Classifier ID:** `SafeDocFlow-D3-reference-v1`  
**Version:** `SafeDocFlow-D3-reference-v1.0.0`  
**Input:** OCR-extracted text only.  
**Output:** `allow` or `block`.  
**Threshold:** `decision_threshold = 1` rule hit in the public scaffold implementation.

P3 is an OCR-to-text classifier baseline. In the manuscript and this artifact, P3 is not an MLLM refusal mechanism: it does not call the target MLLM, and its reported ASR/FRR reflect classifier-level allow/block behavior. This is why P3's cost proxy excludes `n_M`.

The public scaffold classifier is deterministic and intentionally conservative. It exists to make the artifact runnable and auditable without releasing private classifier prompts or unsafe strings. If the private study used a different classifier, the anonymized artifact should replace this card with the exact model name/version/hash and decision threshold.
