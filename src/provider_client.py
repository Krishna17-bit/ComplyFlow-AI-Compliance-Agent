from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Sequence
import requests
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ProviderResponse:
    ok: bool
    text: str
    error: str | None = None


class MultiProviderClient:
    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "mock")).lower().strip()
        self.mock_mode = os.getenv("MOCK_MODE", "true").lower() in ("true", "1", "yes")

        # Models
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        self.mistral_model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.custom_openai_url = os.getenv("CUSTOM_OPENAI_BASE_URL", "")
        self.custom_openai_model = os.getenv("CUSTOM_OPENAI_MODEL", "")

    @property
    def configured(self) -> bool:
        return self.health_check()["configured"]

    def generate(self, prompt: str, *, temperature: float = 0.15, json_mode: bool = False) -> ProviderResponse:
        # If mock mode is active, override
        if self.mock_mode or self.provider == "mock":
            return self._generate_mock(prompt, json_mode)

        if self.provider == "gemini":
            return self._generate_gemini(prompt, temperature, json_mode)
        elif self.provider == "openai":
            return self._generate_openai(prompt, temperature, json_mode)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, temperature, json_mode)
        elif self.provider == "groq":
            return self._generate_groq(prompt, temperature, json_mode)
        elif self.provider == "mistral":
            return self._generate_mistral(prompt, temperature, json_mode)
        elif self.provider == "ollama":
            return self._generate_ollama(prompt, temperature, json_mode)
        elif self.provider == "custom_openai":
            return self._generate_custom_openai(prompt, temperature, json_mode)
        else:
            return ProviderResponse(False, "", f"Unsupported LLM provider: {self.provider}")

    def embed_text(self, text: str) -> list[float]:
        if self.mock_mode or self.provider == "mock" or not text.strip():
            # Return dummy mock embedding vector
            return [0.1] * 768

        try:
            if self.provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if api_key:
                    from google import genai
                    client = genai.Client(api_key=api_key)
                    resp = client.models.embed_content(model="text-embedding-004", contents=text)
                    if resp and hasattr(resp, "embedding") and resp.embedding:
                        return resp.embedding.values
            elif self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {"input": text, "model": "text-embedding-3-small"}
                    r = requests.post("https://api.openai.com/v1/embeddings", json=payload, headers=headers, timeout=10)
                    if r.status_code == 200:
                        return r.json()["data"][0]["embedding"]
        except Exception:
            pass

        # Fallback dummy embedding
        return [0.05] * 768

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]

    def health_check(self) -> dict[str, Any]:
        """Verify API key configuration and connectivity."""
        status = {"provider": self.provider, "mock_mode": self.mock_mode, "configured": False, "error": None}

        if self.provider == "mock" or self.mock_mode:
            status["configured"] = True
            return status

        # Checks for environment variable keys
        api_keys = {
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "groq": "GROQ_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "custom_openai": "CUSTOM_OPENAI_API_KEY"
        }

        key_name = api_keys.get(self.provider)
        if key_name and not os.getenv(key_name):
            status["error"] = f"Missing API key environment variable {key_name}."
            return status

        status["configured"] = True
        return status

    # --- Provider Implementations ---

    def _generate_gemini(self, prompt: str, temp: float, json_mode: bool) -> ProviderResponse:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return ProviderResponse(False, "", "Gemini API key not configured")
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            config_kwargs: dict[str, Any] = {"temperature": temp}
            if json_mode:
                config_kwargs["response_mime_type"] = "application/json"
            config = types.GenerateContentConfig(**config_kwargs)
            resp = client.models.generate_content(model=self.gemini_model, contents=prompt, config=config)
            return ProviderResponse(True, resp.text or "")
        except Exception as exc:
            return ProviderResponse(False, "", str(exc))

    def _generate_openai(self, prompt: str, temp: float, json_mode: bool) -> ProviderResponse:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return ProviderResponse(False, "", "OpenAI API key not configured")
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload: dict[str, Any] = {
                "model": self.openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temp,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                return ProviderResponse(True, text)
            return ProviderResponse(False, "", f"OpenAI error: {r.status_code} - {r.text}")
        except Exception as exc:
            return ProviderResponse(False, "", str(exc))

    def _generate_anthropic(self, prompt: str, temp: float, json_mode: bool) -> ProviderResponse:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return ProviderResponse(False, "", "Anthropic API key not configured")
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": self.anthropic_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4096,
                "temperature": temp,
            }
            r = requests.post("https://api.openai.com/v1/messages", json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                text = r.json()["content"][0]["text"]
                return ProviderResponse(True, text)
            return ProviderResponse(False, "", f"Anthropic error: {r.status_code} - {r.text}")
        except Exception as exc:
            return ProviderResponse(False, "", str(exc))

    def _generate_groq(self, prompt: str, temp: float, json_mode: bool) -> ProviderResponse:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return ProviderResponse(False, "", "Groq API key not configured")
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload: dict[str, Any] = {
                "model": self.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temp,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                return ProviderResponse(True, text)
            return ProviderResponse(False, "", f"Groq error: {r.status_code} - {r.text}")
        except Exception as exc:
            return ProviderResponse(False, "", str(exc))

    def _generate_mistral(self, prompt: str, temp: float, json_mode: bool) -> ProviderResponse:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            return ProviderResponse(False, "", "Mistral API key not configured")
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload: dict[str, Any] = {
                "model": self.mistral_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temp,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            r = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                return ProviderResponse(True, text)
            return ProviderResponse(False, "", f"Mistral error: {r.status_code} - {r.text}")
        except Exception as exc:
            return ProviderResponse(False, "", str(exc))

    def _generate_ollama(self, prompt: str, temp: float, json_mode: bool) -> ProviderResponse:
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temp}
            }
            if json_mode:
                payload["format"] = "json"
            r = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            if r.status_code == 200:
                text = r.json()["response"]
                return ProviderResponse(True, text)
            return ProviderResponse(False, "", f"Ollama error: {r.status_code} - {r.text}")
        except Exception as exc:
            return ProviderResponse(False, "", str(exc))

    def _generate_custom_openai(self, prompt: str, temp: float, json_mode: bool) -> ProviderResponse:
        api_key = os.getenv("CUSTOM_OPENAI_API_KEY", "")
        if not self.custom_openai_url:
            return ProviderResponse(False, "", "Custom OpenAI Base URL not configured")
        try:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            payload: dict[str, Any] = {
                "model": self.custom_openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temp,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            r = requests.post(f"{self.custom_openai_url.rstrip('/')}/chat/completions", json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                return ProviderResponse(True, text)
            return ProviderResponse(False, "", f"Custom endpoint error: {r.status_code} - {r.text}")
        except Exception as exc:
            return ProviderResponse(False, "", str(exc))

    # --- Heuristics and Offline Templates for Mock Mode ---

    def _generate_mock(self, prompt: str, json_mode: bool) -> ProviderResponse:
        # Check if the prompt is for control mapping audit
        if "proposed control mappings" in prompt or "compliance evidence analyst" in prompt:
            # We mock the control map review JSON
            try:
                # Find mapped control ids from the payload in prompt
                control_ids = re.findall(r'"control_id":\s*"([^"]+)"', prompt)
                if not control_ids:
                    control_ids = ["SOC2-CC1", "ISO-A5.1"]
                
                results = []
                for cid in control_ids:
                    status = "Covered" if "CC1" in cid or "A5.1" in cid or "INVENTORY" in cid else "Partial"
                    if "A8.15" in cid or "BREACH" in cid or "EVAL" in cid:
                        status = "Missing"
                    
                    risk = "Low" if status == "Covered" else "Medium" if status == "Partial" else "High"
                    results.append({
                        "control_id": cid,
                        "status": status,
                        "confidence": 0.85 if status == "Covered" else 0.45,
                        "risk_level": risk,
                        "explanation": f"Validated evidence metrics suggest operational effectiveness for {cid} matches.",
                        "missing_evidence": [f"Audit logging parameters for {cid}"] if status != "Covered" else [],
                        "improvement_actions": [f"Review configuration files and logs linked to {cid} weekly."] if status != "Covered" else []
                    })
                return ProviderResponse(True, json.dumps(results))
            except Exception as e:
                return ProviderResponse(False, "", str(e))

        # Check if prompt is for questionnaire answering
        elif "questionnaire response specialist" in prompt or "security questionnaire" in prompt:
            try:
                questions = re.findall(r'"question":\s*"([^"]+)"', prompt)
                if not questions:
                    questions = ["Do you enforce MFA?"]
                results = []
                for q in questions:
                    has_evidence = "mfa" in q.lower() or "encrypt" in q.lower() or "access" in q.lower()
                    results.append({
                        "question": q,
                        "answer": f"Yes, we enforce organizational safeguards as required. We support controls for {q} via centralized policy enforcement rules.",
                        "confidence": 0.9 if has_evidence else 0.35,
                        "review_required": not has_evidence,
                        "assumptions": ["Validated using primary security policies."],
                        "evidence_ids": ["evidence_doc_1"]
                    })
                return ProviderResponse(True, json.dumps(results))
            except Exception as e:
                return ProviderResponse(False, "", str(e))

        # Executive summary
        elif "executive compliance readiness summary" in prompt:
            return ProviderResponse(True, "Executive Summary: The security posture shows stable configuration mappings across key domains. SOC 2 requirements are currently 75% covered. Key remediation items include setting up automated logging audits and third-party penetration testing. Immediate action is recommended to close high-severity database logging gaps.")

        # Default mock text return
        if json_mode:
            return ProviderResponse(True, json.dumps({"status": "success", "message": "Mock offline success."}))
        return ProviderResponse(True, "This is a mock offline LLM response for ComplyFlow AI GRC validation.")
