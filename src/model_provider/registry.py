"""
CodeForge Provider Registry - Phase 4 (Provider Layer)
======================================================
سجل مزودي LLM.

Phase 4 rules (لا نجاح كاذب لمزود ذكاء اصطناعي):
- ProviderMode:
    "real"        -> مزود حقيقي (gemini/openai) configured+available+healthy ونشط.
    "mock"        -> Mock نشط - **للتطوير/الاختبار المحلي فقط**، لا يُعرَض أبداً
                     على أنه استدلال نموذج حقيقي.
    "unavailable" -> لا يوجد أي مزود مهيأ إطلاقاً (لا حتى Mock مُفعَّل صراحة).
- ترتيب Fallback قابل للتهيئة عبر PROVIDER_ORDER (مثال: "gemini,openai,mock").
  الافتراضي: gemini -> openai -> mock (تفضيل الذكاء الحقيقي دائماً عند توفره).
- Mock لا يُفعَّل تلقائياً ليحل محل مزود حقيقي فشل health check بصمت وكأن شيئاً
  لم يحدث - يبقى ظاهراً في /api/health كـ mode=mock بوضوح.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.model_provider.base import BaseProvider, ProviderConfig
from src.model_provider.mock_provider import MockProvider

DEFAULT_PROVIDER_ORDER = ["gemini", "openai", "mock"]


@dataclass
class ProviderInfo:
    name: str
    provider: BaseProvider
    priority: int = 0
    auto_enable: bool = True
    healthy: Optional[bool] = None          # None = لم يُفحَص بعد
    health_error: Optional[str] = None


class ProviderRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._providers: Dict[str, ProviderInfo] = {}
        self._active_provider: Optional[str] = None
        self._initialized = True

        self._register_default_providers()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def _provider_order(self) -> List[str]:
        raw = os.environ.get("PROVIDER_ORDER", "").strip()
        if not raw:
            return list(DEFAULT_PROVIDER_ORDER)
        order = [p.strip() for p in raw.split(",") if p.strip()]
        return order or list(DEFAULT_PROVIDER_ORDER)

    def _register_default_providers(self):
        order = self._provider_order()
        priorities = {name: (len(order) - i) * 10 for i, name in enumerate(order)}

        mock_allowed = os.environ.get("MOCK_PROVIDER_ENABLED", "true").lower() != "false"
        mock = MockProvider()
        self.register(
            "mock", mock,
            priority=priorities.get("mock", 0),
            auto_enable=mock_allowed,
        )
        if "mock" in self._providers:
            self._providers["mock"].healthy = True  # deterministic, لا شبكة

        if os.environ.get("GEMINI_API_KEY"):
            try:
                from src.model_provider.gemini_provider import GeminiProvider
                gemini = GeminiProvider()
                self.register("gemini", gemini, priority=priorities.get("gemini", 10))
                self._run_health_check("gemini")
            except ImportError as e:
                print(f"⚠️ GeminiProvider غير متاح: {e}")

        if os.environ.get("OPENAI_API_KEY"):
            try:
                from src.model_provider.openai_provider import OpenAIProvider
                openai_p = OpenAIProvider()
                self.register("openai", openai_p, priority=priorities.get("openai", 10))
                self._run_health_check("openai")
            except ImportError as e:
                print(f"⚠️ OpenAIProvider غير متاح: {e}")

        self._select_active(order)

    def _run_health_check(self, name: str):
        info = self._providers.get(name)
        if not info or not info.provider.configured:
            return
        try:
            ok = info.provider.test_connection()
        except Exception as e:
            ok = False
            info.health_error = str(e)
        info.healthy = ok
        if not ok and info.health_error is None:
            info.health_error = getattr(info.provider, "_last_health_error", None)

    def _select_active(self, order: List[str]):
        self._active_provider = None
        for name in order:
            info = self._providers.get(name)
            if not info or not info.auto_enable:
                continue
            if not info.provider.configured:
                continue
            if info.healthy is False:
                continue
            self._active_provider = name
            return
        self._active_provider = None

    # ------------------------------------------------------------------
    # Public API (متوافق مع الواجهة السابقة)
    # ------------------------------------------------------------------

    def register(self, name: str, provider: BaseProvider, priority: int = 0, auto_enable: bool = True):
        self._providers[name] = ProviderInfo(
            name=name, provider=provider, priority=priority, auto_enable=auto_enable,
        )

    def unregister(self, name: str) -> bool:
        if name in self._providers:
            del self._providers[name]
            if self._active_provider == name:
                self._select_active(self._provider_order())
            return True
        return False

    def get(self, name: str) -> Optional[BaseProvider]:
        info = self._providers.get(name)
        return info.provider if info else None

    def get_active(self) -> Optional[BaseProvider]:
        if not self._active_provider:
            return None
        return self.get(self._active_provider)

    def set_active(self, name: str) -> bool:
        info = self._providers.get(name)
        if not info or not info.provider.configured:
            return False
        if info.healthy is False:
            return False
        self._active_provider = name
        return True

    @property
    def mode(self) -> str:
        if not self._active_provider:
            return "unavailable"
        if self._active_provider == "mock":
            return "mock"
        return "real"

    def list_all(self) -> List[Dict]:
        result = []
        for name, info in self._providers.items():
            result.append({
                "name": name,
                "configured": info.provider.configured,
                "available": getattr(info.provider, "available", info.provider.configured),
                "healthy": info.healthy,
                "active": name == self._active_provider,
                "priority": info.priority,
                "health_error": info.health_error,
                "capabilities": info.provider.list_capabilities(),
            })
        return result

    def generate(self, prompt: str, **kwargs) -> str:
        provider = self.get_active()
        if not provider:
            return "Error: No LLM provider configured. Please set up a provider."
        return provider.generate(prompt, **kwargs)

    def has_provider(self) -> bool:
        return self.get_active() is not None

    def test_connection(self, name: str = None) -> Dict:
        target = name or self._active_provider
        provider = self.get(target) if target else None
        if not provider:
            return {"success": False, "error": "Provider not found"}
        success = provider.test_connection()
        if target in self._providers:
            self._providers[target].healthy = success
        return {"success": success, "provider": provider.name}


# ============================================================
# Global Instance
# ============================================================

provider_registry = ProviderRegistry()


# ============================================================
# Convenience Functions
# ============================================================

def get_active_provider() -> Optional[BaseProvider]:
    return provider_registry.get_active()


def has_llm_provider() -> bool:
    return provider_registry.has_provider()


def generate(prompt: str, **kwargs) -> str:
    return provider_registry.generate(prompt, **kwargs)


def set_provider(name: str) -> bool:
    return provider_registry.set_active(name)


def get_provider_mode() -> str:
    return provider_registry.mode
