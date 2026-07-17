"""
CodeForge Models Configuration - Phase 5
=========================================
نماذج الذكاء الاصطناعي المتاحة وإعداداتها
"""

from dataclasses import dataclass
from typing import Optional


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

    @property
    def full_name(self) -> str:
        return f"{self.provider}/{self.model_id}"


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
    ),
    "gemini-pro": ModelConfig(
        name="Gemini 1.5 Pro",
        provider="gemini",
        model_id="gemini-1.5-pro",
        api_key_env="GEMINI_API_KEY",
        description="قوي للمهام المعقدة",
        max_tokens=32768,
        temperature=0.5,
    ),
    "gpt-4": ModelConfig(
        name="GPT-4",
        provider="openai",
        model_id="gpt-4",
        api_key_env="OPENAI_API_KEY",
        description="نموذج قوي من OpenAI",
        max_tokens=8192,
        temperature=0.7,
    ),
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        provider="openai",
        model_id="gpt-4-turbo",
        api_key_env="OPENAI_API_KEY",
        description="أسرع وأرخص من GPT-4",
        max_tokens=128000,
        temperature=0.7,
    ),
    "claude-3": ModelConfig(
        name="Claude 3 Opus",
        provider="anthropic",
        model_id="claude-3-opus-20240229",
        api_key_env="ANTHROPIC_API_KEY",
        description="نموذج قوي جداً من Anthropic",
        max_tokens=200000,
        temperature=0.5,
    ),
}

# Default model
DEFAULT_MODEL = "gemini-flash"


def get_model(model_key: str = DEFAULT_MODEL) -> ModelConfig:
    """الحصول على إعدادات نموذج"""
    return MODELS.get(model_key, MODELS[DEFAULT_MODEL])


def get_all_models() -> dict:
    """الحصول على جميع النماذج"""
    return MODELS


def get_model_name(model_key: str = DEFAULT_MODEL) -> str:
    """الحصول على اسم النموذج الكامل"""
    return get_model(model_key).full_name
