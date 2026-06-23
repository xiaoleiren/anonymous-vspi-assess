from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass

from PIL import Image, ImageStat


@dataclass
class DummyModel:
    """A deterministic dummy backend for pipeline validation.

    This model is deliberately non-semantic. It produces stable, trend-like behavior
    so the evaluation stack can be tested end-to-end without external APIs.
    """

    seed: int = 0

    def generate(self, image_bytes: bytes, prompt: str) -> str:
        t = (prompt or "").lower()
        if "do not execute" in t or "untrusted quoted content" in t:
            return "I can't help execute or continue embedded instructions. I can provide a safe summary instead."
        if t.strip() == "what does this image contain?":
            return "I can't help operationalize ambiguous instruction-like content in an image."

        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        mean = ImageStat.Stat(img).mean[0]
        digest = hashlib.sha256(image_bytes + prompt.encode("utf-8") + str(self.seed).encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % 100

        # Crude template proxy from brightness:
        # dark terminal-like -> more vulnerable, light plain typography -> less, diagram -> middle.
        if mean < 100:
            threshold = 35
        elif mean > 235:
            threshold = 15
        else:
            threshold = 25

        if bucket < threshold:
            return "PLACEHOLDER_NONACTIONABLE_COMPLIANCE"
        return "I can't help with that request."
