"""
CodeForge OpenAI Provider - Phase 4 (Provider Layer)
=====================================================
كان هذا الملف مفقوداً تماماً من المستودع (انظر AUDIT_REPORT.md C3)، بنفس
الوضع الخاص بـ gemini_provider.py.
"""

import os
from typing import Optional

import requests

from src.model_provider.base import BaseProvider, ProviderConfig

OPENAI_API_BASE = "https://api.openai.com/v1"


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str = "gpt-4o-mini"):
        self._api_key: Optional[str] = os.environ.get("OPENAI_API_KEY", "").strip() or None
        self._config = ProviderConfig(
            name="openai",
            api_key=self._api_key,
            model=model,
            timeout=int(os.environ.get("OPENAI_TIMEOUT", "60")),
        )
        self._last_health_check: Optional[bool] = None
        self._last_health_error: Optional[str] = None

    @property
    def name(self) -> str:
        return "openai"

    @property
    def configured(self) -> bool:
        return bool(self._api_key)

    @property
    def available(self) -> bool:
        return self.configured

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}"}

    def test_connection(self) -> bool:
        if not self.configured:
            self._last_health_error = "OPENAI_API_KEY غير مضبوط"
            self._last_health_check = False
            return False
        try:
            resp = requests.get(
                f"{OPENAI_API_BASE}/models/{self._config.model}",
                headers=self._headers(),
                timeout=self._config.timeout,
            )
            ok = resp.status_code == 200
            self._last_health_check = ok
            self._last_health_error = None if ok else f"HTTP {resp.status_code}: {resp.text[:200]}"
            return ok
        except requests.RequestException as e:
            self._last_health_check = False
            self._last_health_error = str(e)
            return False

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.configured:
            raise RuntimeError("OpenAIProvider: OPENAI_API_KEY غير مضبوط - لا يمكن التوليد")

        model = kwargs.get("model", self._config.model)
        temperature = kwargs.get("temperature", self._config.temperature)
        max_tokens = kwargs.get("max_tokens", self._config.max_tokens)

        resp = requests.post(
            f"{OPENAI_API_BASE}/chat/completions",
            headers=self._headers(),
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=self._config.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"OpenAIProvider: استجابة غير متوقعة من API: {data}") from e

    def get_config(self) -> ProviderConfig:
        return self._config
