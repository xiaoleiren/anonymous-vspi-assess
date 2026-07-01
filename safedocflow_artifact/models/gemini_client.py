from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class GeminiModel:
    """Gemini multimodal wrapper using the Google GenAI SDK."""

    model_name: str
    max_output_tokens: int = 512
    temperature: float = 0.0

    def generate(self, image_bytes: bytes, prompt: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key or api_key == "XX":
            raise RuntimeError("GEMINI_API_KEY not set. Put it in .env or environment variables.")

        try:
            from google import genai
            from google.genai import types
        except Exception as e:
            raise RuntimeError(
                "The google-genai package is required for the Gemini backend. Install it with `pip install google-genai`."
            ) from e

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            ),
        )
        text = getattr(response, "text", None)
        if text:
            return text
        parts = []
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                if getattr(part, "text", None):
                    parts.append(part.text)
        return "\n".join(parts).strip()
