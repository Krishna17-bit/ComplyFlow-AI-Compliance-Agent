from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    ok: bool
    text: str
    error: str | None = None


class GeminiClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro").strip() or "gemini-2.5-pro"
        self._client = None
        self._types = None
        self.error: str | None = None

        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            self.error = "API key not configured"
            return

        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore

            self._client = genai.Client(api_key=self.api_key)
            self._types = types
        except Exception as exc:  # pragma: no cover
            self.error = str(exc)

    @property
    def configured(self) -> bool:
        return self._client is not None and self.error is None

    def generate(self, prompt: str, *, temperature: float = 0.15, json_mode: bool = False) -> LLMResponse:
        if not self.configured:
            return LLMResponse(False, "", self.error or "AI engine is not configured")
        try:
            config_kwargs: dict[str, Any] = {"temperature": temperature}
            if json_mode:
                config_kwargs["response_mime_type"] = "application/json"
            config = self._types.GenerateContentConfig(**config_kwargs)
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return LLMResponse(True, response.text or "")
        except Exception as exc:
            return LLMResponse(False, "", str(exc))


def extract_json(text: str, fallback: Any) -> Any:
    if not text:
        return fallback
    stripped = text.strip()
    try:
        return json.loads(stripped)
    except Exception:
        pass
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.S | re.I)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    first_obj = stripped.find("{")
    first_arr = stripped.find("[")
    starts = [x for x in [first_obj, first_arr] if x >= 0]
    if starts:
        start = min(starts)
        for end in range(len(stripped), start, -1):
            try:
                return json.loads(stripped[start:end])
            except Exception:
                continue
    return fallback
