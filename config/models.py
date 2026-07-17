"""
CodeForge Models Configuration - Phase 6A
=========================================
نماذج الذكاء الاصطناعي المتاحة وإعداداتها
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class ModelConfig:
    """إعدادات نموذج واحد"""
    name: str
    provider: str
    model_id: str
    api_key_env: str
    description: str
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_tier: str = "low"  # low, medium, high
    capabilities: List[str] = field(default_factory=list)  # reasoning, coding, creative, analysis

    @property
    def full_name(self) -> str:
        return f"{self.provider}/{self.model_id}"

    def is_available(self) -> bool:
        """فحص توفر النموذج"""
        import os
        return bool(os.environ.get(self.api_key_env))


# Available Models
MODELS = {
    "gemini-flash": ModelConfig(
        name="Gemini 2.0 Flash",
        provider="gemini",
        model_id="gemini-2.0-flash",
        api_key_env="GEMINI_API_KEY",
        description="سريع ورخيص، مناسب لمعظم المهام",
        max_tokens=8192,
        temperature=0.7,
        cost_tier="low",
        capabilities=["reasoning", "coding", "creative"],
    ),
    "gemini-pro": ModelConfig(
        name="Gemini 1.5 Pro",
        provider="gemini",
        model_id="gemini-1.5-pro",
        api_key_env="GEMINI_API_KEY",
        description="قوي للمهام المعقدة",
        max_tokens=32768,
        temperature=0.5,
        cost_tier="medium",
        capabilities=["reasoning", "coding", "analysis"],
    ),
    "gpt-4": ModelConfig(
        name="GPT-4",
        provider="openai",
        model_id="gpt-4",
        api_key_env="OPENAI_API_KEY",
        description="نموذج قوي من OpenAI",
        max_tokens=8192,
        temperature=0.7,
        cost_tier="high",
        capabilities=["reasoning", "coding", "creative", "analysis"],
    ),
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        provider="openai",
        model_id="gpt-4-turbo",
        api_key_env="OPENAI_API_KEY",
        description="أسرع وأرخص من GPT-4",
        max_tokens=128000,
        temperature=0.7,
        cost_tier="medium",
        capabilities=["reasoning", "coding", "creative", "analysis"],
    ),
    "claude-3": ModelConfig(
        name="Claude 3 Opus",
        provider="anthropic",
        model_id="claude-3-opus-20240229",
        api_key_env="ANTHROPIC_API_KEY",
        description="نموذج قوي جداً من Anthropic",
        max_tokens=200000,
        temperature=0.5,
        cost_tier="high",
        capabilities=["reasoning", "coding", "creative", "analysis"],
    ),
}

# Default model
DEFAULT_MODEL = "gemini-flash"

# Model Roles - maps task types to preferred models
MODEL_ROLES = {
    "planning": {
        "primary": "gemini-flash",
        "fallback": "gemini-pro",
        "description": "التخطيط وتحليل المتطلبات",
    },
    "coding": {
        "primary": "gemini-pro",
        "fallback": "gpt-4-turbo",
        "description": "كتابة الكود",
    },
    "review": {
        "primary": "gemini-flash",
        "fallback": "gemini-pro",
        "description": "مراجعة الكود",
    },
    "documentation": {
        "primary": "gemini-flash",
        "fallback": "gemini-pro",
        "description": "كتابة التوثيق",
    },
    "security": {
        "primary": "gemini-pro",
        "fallback": "gpt-4",
        "description": "فحص الأمان",
    },
    "creative": {
        "primary": "gemini-flash",
        "fallback": "gpt-4-turbo",
        "description": "أفكار إبداعية",
    },
}


def get_model(model_key: str = DEFAULT_MODEL) -> ModelConfig:
    """الحصول على إعدادات نموذج"""
    return MODELS.get(model_key, MODELS[DEFAULT_MODEL])


def get_all_models() -> dict:
    """الحصول على جميع النماذج"""
    return MODELS


def get_model_name(model_key: str = DEFAULT_MODEL) -> str:
    """الحصول على اسم النموذج الكامل"""
    return get_model(model_key).full_name


def get_available_models() -> Dict[str, ModelConfig]:
    """الحصول على النماذج المتاحة فقط"""
    return {k: v for k, v in MODELS.items() if v.is_available()}


def get_role_model(role: str) -> ModelConfig:
    """الحصول على نموذج لدور معين"""
    if role not in MODEL_ROLES:
        return get_model(DEFAULT_MODEL)
    
    role_config = MODEL_ROLES[role]
    
    # Try primary
    primary = get_model(role_config["primary"])
    if primary.is_available():
        return primary
    
    # Try fallback
    fallback = get_model(role_config["fallback"])
    if fallback.is_available():
        return fallback
    
    # Return default if nothing available
    return get_model(DEFAULT_MODEL)
