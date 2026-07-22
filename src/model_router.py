"""
CodeForge Model Router - Phase 6A
=================================
موجه النماذج: يختار النموذج المناسب لكل مهمة
"""

from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from config.models import (
    ModelConfig, get_model, get_role_model, 
    MODELS, DEFAULT_MODEL, MODEL_ROLES, get_available_models
)


class ModelRouter:
    """موجه النماذج"""

    def __init__(self):
        self.fallback_chain: Dict[str, list] = {}
        self.usage_stats: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}

    def get_model_for_task(self, task_type: str) -> ModelConfig:
        """
        اختيار النموذج المناسب للمهمة
        
        Args:
            task_type: نوع المهمة (planning, coding, review, etc.)
            
        Returns:
            ModelConfig للنموذج المختار
        """
        # Get role model
        model = get_role_model(task_type)
        
        # Update stats
        self.usage_stats[task_type] = self.usage_stats.get(task_type, 0) + 1
        
        return model

    def get_llm_config(self, task_type: str) -> Dict[str, Any]:
        """
        الحصول على إعدادات LLM كاملة
        
        Args:
            task_type: نوع المهمة
            
        Returns:
            Dict مع إعدادات النموذج
        """
        model = self.get_model_for_task(task_type)
        
        return {
            "model": model.full_name,
            "model_key": self._get_model_key(model),
            "provider": model.provider,
            "temperature": model.temperature,
            "max_tokens": model.max_tokens,
            "api_key_env": model.api_key_env,
        }

    def _get_model_key(self, model: ModelConfig) -> str:
        """الحصول على مفتاح النموذج"""
        for key, config in MODELS.items():
            if config.full_name == model.full_name:
                return key
        return DEFAULT_MODEL

    def handle_error(self, task_type: str, error: Exception) -> Optional[ModelConfig]:
        """
        معالجة خطأ النموذج - التحويل للاحتياطي
        
        Args:
            task_type: نوع المهمة
            error: الخطأ الذي حدث
            
        Returns:
            ModelConfig للنموذج الاحتياطي أو None
        """
        if task_type not in MODEL_ROLES:
            return None
        
        role_config = MODEL_ROLES[task_type]
        primary_key = role_config["primary"]
        fallback_key = role_config["fallback"]
        
        # Track error
        self.error_counts[primary_key] = self.error_counts.get(primary_key, 0) + 1
        
        # Check if fallback is available
        fallback_model = get_model(fallback_key)
        if fallback_model.is_available():
            return fallback_model
        
        # Try any available model
        available = get_available_models()
        if available:
            return list(available.values())[0]
        
        return None

    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات استخدام النماذج"""
        return {
            "usage_by_task": self.usage_stats,
            "error_counts": self.error_counts,
            "available_models": len(get_available_models()),
            "total_models": len(MODELS),
            "roles_configured": len(MODELS_ROLES) if "MODEL_ROLES" in dir() else 0,
        }

    def get_best_available(self) -> ModelConfig:
        """الحصول على أفضل نموذج متاح"""
        available = get_available_models()
        
        if not available:
            return get_model(DEFAULT_MODEL)
        
        # Return first available
        return list(available.values())[0]

    def detect_task_type(self, description: str) -> str:
        """
        تحديد نوع المهمة من الوصف
        
        Args:
            description: وصف المهمة
            
        Returns:
            نوع المهمة
        """
        desc_lower = description.lower()
        
        # Security checks
        if any(word in desc_lower for word in ["أمان", "security", "api key", "secret", "password", "token"]):
            return "security"
        
        # Coding
        if any(word in desc_lower for word in ["كود", "code", "python", "javascript", "html", "css", "function", "class"]):
            return "coding"
        
        # Review
        if any(word in desc_lower for word in ["مراجعة", "review", "اختبار", "test", "فحص", "check"]):
            return "review"
        
        # Documentation
        if any(word in desc_lower for word in ["توثيق", "docs", "documentation", "readme", "شرح", "report"]):
            return "documentation"
        
        # Planning
        if any(word in desc_lower for word in ["خطة", "plan", "تصميم", "design", "معماري", "architecture"]):
            return "planning"
        
        # Default to planning for unknown
        return "planning"


# ============================================================
# Global Instance
# ============================================================

model_router = ModelRouter()


# ============================================================
# Convenience Functions
# ============================================================

def get_model_for_task(task_type: str) -> ModelConfig:
    """الحصول على نموذج للمهمة"""
    return model_router.get_model_for_task(task_type)


def get_llm_config(task_type: str) -> Dict[str, Any]:
    """الحصول على إعدادات LLM للمهمة"""
    return model_router.get_llm_config(task_type)


def handle_model_error(task_type: str, error: Exception) -> Optional[ModelConfig]:
    """معالجة خطأ النموذج"""
    return model_router.handle_error(task_type, error)


def detect_task_type(description: str) -> str:
    """تحديد نوع المهمة"""
    return model_router.detect_task_type(description)


def get_available_model_count() -> int:
    """عدد النماذج المتاحة"""
    return len(get_available_models())
