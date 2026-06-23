from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenAIModel:
    """OpenAI multimodal wrapper using the Responses API.

    Safe notes:
    - This wrapper only executes user-supplied, redacted evaluation inputs.
    - It does not ship any harmful prompt suite.
    - It expects the caller to manage approved datasets and compliance review.
    """

    model_name: str
    max_output_tokens: int = 512
    detail: str = "high"
    instructions: Optional[str] = None

    def generate(self, image_bytes: bytes, prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "XX":
            raise RuntimeError("OPENAI_API_KEY not set. Put it in .env or environment variables.")

        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError(
                "The openai package is required for the OpenAI backend. Install it with `pip install openai`."
            ) from e

        client = OpenAI(api_key=api_key)
        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        response = client.responses.create(
            model=self.model_name,
            instructions=self.instructions,
            max_output_tokens=self.max_output_tokens,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{image_b64}",
                            "detail": self.detail,
                        },
                    ],
                }
            ],
        )
        text = getattr(response, "output_text", None)
        if text:
            return text
        # Fallback for older/alternative SDK response objects.
        out = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) == "message":
                for c in getattr(item, "content", []) or []:
                    if getattr(c, "type", None) in {"output_text", "text"}:
                        out.append(getattr(c, "text", ""))
        return "\n".join(x for x in out if x).strip()
