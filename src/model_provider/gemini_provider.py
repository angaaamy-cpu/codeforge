"""
CodeForge Gemini Provider - Phase 4 (Provider Layer)
=====================================================
كان هذا الملف مفقوداً تماماً من المستودع (انظر AUDIT_REPORT.md C3) رغم أن
registry.py يحاول استيراده، وrows.md يدّعي "ربط Gemini API ✅". هذا التنفيذ
الفعلي الأول للملف.

Health model (لا نجاح كاذب):
    configured  -> مفتاح API موجود في البيئة
    available   -> يمكن بناء العميل (لا يعني اتصالاً ناجحاً بعد)
    healthy     -> test_connection() نجح فعلياً مقابل الـ API الحقيقي
    active      -> configured AND available AND healthy (يُحدَّد في ProviderRegistry)
"""

import os
from typing import Optional

import requests

from src.model_provider.base import BaseProvider, ProviderConfig

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(BaseProvider):
    def __init__(self, model: str = "gemini-2.0-flash"):
        self._api_key: Optional[str] = os.environ.get("GEMINI_API_KEY", "").strip() or None
        self._config = ProviderConfig(
            name="gemini",
            api_key=self._api_key,
            model=model,
            timeout=int(os.environ.get("GEMINI_TIMEOUT", "60")),
        )
        self._last_health_check: Optional[bool] = None
        self._last_health_error: Optional[str] = None

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def configured(self) -> bool:
        """Configured فقط = مفتاح API موجود. لا يعني اتصالاً ناجحاً."""
        return bool(self._api_key)

    @property
    def available(self) -> bool:
        """Available = يمكن بناء طلب فعلي (مفتاح + مكتبة HTTP موجودة)."""
        return self.configured

    def test_connection(self) -> bool:
        """فحص اتصال حقيقي (Health Check) - لا يُخترَع، فشل الشبكة = False صريح."""
        if not self.configured:
            self._last_health_error = "GEMINI_API_KEY غير مضبوط"
            self._last_health_check = False
            return False
        try:
            resp = requests.get(
                f"{GEMINI_API_BASE}/models/{self._config.model}",
                params={"key": self._api_key},
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
            raise RuntimeError("GeminiProvider: GEMINI_API_KEY غير مضبوط - لا يمكن التوليد")

        model = kwargs.get("model", self._config.model)
        temperature = kwargs.get("temperature", self._config.temperature)
        max_tokens = kwargs.get("max_tokens", self._config.max_tokens)

        resp = requests.post(
            f"{GEMINI_API_BASE}/models/{model}:generateContent",
            params={"key": self._api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            },
            timeout=self._config.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"GeminiProvider: استجابة غير متوقعة من API: {data}") from e

    def get_config(self) -> ProviderConfig:
        return self._config
