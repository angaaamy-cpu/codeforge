"""
CodeForge Provider Registry - Agent OS
======================================
سجل مزودي LLM
- تسجيل المزودين: mock, gemini, openai, openrouter, ollama
- أول مزود مهيأ يصبح النشط
- Fallback تلقائي بين المزودين
"""

import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field

from src.model_provider.base import BaseProvider, ProviderConfig
from src.model_provider.mock_provider import MockProvider


@dataclass
class ProviderInfo:
    """معلومات المزود"""
    name: str
    provider: BaseProvider
    priority: int = 0
    auto_enable: bool = True


class ProviderRegistry:
    """
    سجل مزودي LLM
    """
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
        
        # تسجيل Mock تلقائياً
        self._register_default_providers()
    
    def _register_default_providers(self):
        """تسجيل المزودين الافتراضيين"""
        # Mock - متاح دائماً
        mock = MockProvider()
        self.register("mock", mock, priority=0, auto_enable=True)
        
        # Gemini - إذا كان API key موجود
        if os.environ.get("GEMINI_API_KEY"):
            try:
                # من deferred import لتجنب الأخطاء
                from src.model_provider.gemini_provider import GeminiProvider
                gemini = GeminiProvider()
                self.register("gemini", gemini, priority=10, auto_enable=True)
            except ImportError:
                pass
        
        # OpenAI - إذا كان API key موجود
        if os.environ.get("OPENAI_API_KEY"):
            try:
                from src.model_provider.openai_provider import OpenAIProvider
                openai = OpenAIProvider()
                self.register("openai", openai, priority=10, auto_enable=True)
            except ImportError:
                pass
        
        # تعيين المزود النشط تلقائياً
        self._set_first_available()
    
    def _set_first_available(self):
        """تعيين أول مزود متاح"""
        if self._active_provider:
            return
        
        # ترتيب حسب الأولوية
        sorted_providers = sorted(
            self._providers.values(),
            key=lambda x: x.priority,
            reverse=True
        )
        
        for info in sorted_providers:
            if info.auto_enable and info.provider.configured:
                self._active_provider = info.name
                break
    
    def register(
        self,
        name: str,
        provider: BaseProvider,
        priority: int = 0,
        auto_enable: bool = True,
    ):
        """تسجيل مزود جديد"""
        self._providers[name] = ProviderInfo(
            name=name,
            provider=provider,
            priority=priority,
            auto_enable=auto_enable,
        )
        
        # إذا لم يكن هناك مزود نشط، اجعله هذا
        if self._active_provider is None and auto_enable and provider.configured:
            self._active_provider = name
    
    def unregister(self, name: str) -> bool:
        """إلغاء تسجيل مزود"""
        if name in self._providers:
            del self._providers[name]
            
            # إذا كان هو النشط، عيّن آخر
            if self._active_provider == name:
                self._set_first_available()
            
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseProvider]:
        """الحصول على مزود"""
        info = self._providers.get(name)
        return info.provider if info else None
    
    def get_active(self) -> Optional[BaseProvider]:
        """الحصول على المزود النشط"""
        if not self._active_provider:
            return None
        return self.get(self._active_provider)
    
    def set_active(self, name: str) -> bool:
        """تعيين مزود نشط"""
        if name not in self._providers:
            return False
        
        info = self._providers[name]
        if not info.provider.configured:
            return False
        
        self._active_provider = name
        return True
    
    def list_all(self) -> List[Dict]:
        """قائمة كل المزودين"""
        result = []
        for name, info in self._providers.items():
            result.append({
                "name": name,
                "configured": info.provider.configured,
                "active": name == self._active_provider,
                "priority": info.priority,
                "capabilities": info.provider.list_capabilities(),
            })
        return result
    
    def generate(self, prompt: str, **kwargs) -> str:
        """توليد باستخدام المزود النشط"""
        provider = self.get_active()
        
        if not provider:
            return "Error: No LLM provider configured. Please set up a provider."
        
        return provider.generate(prompt, **kwargs)
    
    def has_provider(self) -> bool:
        """هل هناك مزود مهيأ؟"""
        return self.get_active() is not None
    
    def test_connection(self, name: str = None) -> Dict:
        """فحص اتصال مزود"""
        if name:
            provider = self.get(name)
        else:
            provider = self.get_active()
        
        if not provider:
            return {"success": False, "error": "Provider not found"}
        
        success = provider.test_connection()
        return {"success": success, "provider": provider.name}


# ============================================================
# Global Instance
# ============================================================

provider_registry = ProviderRegistry()


# ============================================================
# Convenience Functions
# ============================================================

def get_active_provider() -> Optional[BaseProvider]:
    """الحصول على المزود النشط"""
    return provider_registry.get_active()


def has_llm_provider() -> bool:
    """هل هناك مزود LLM؟"""
    return provider_registry.has_provider()


def generate(prompt: str, **kwargs) -> str:
    """توليد استجابة"""
    return provider_registry.generate(prompt, **kwargs)


def set_provider(name: str) -> bool:
    """تعيين مزود"""
    return provider_registry.set_active(name)
