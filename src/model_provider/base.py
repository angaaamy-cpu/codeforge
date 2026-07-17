"""
CodeForge Base Provider - Agent OS
==================================
Base interface for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ProviderConfig:
    """إعدادات المزود"""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "default"
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 60


class BaseProvider(ABC):
    """
    الواجهة الأساسية لكل مزود LLM
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """اسم المزود"""
        pass
    
    @property
    @abstractmethod
    def configured(self) -> bool:
        """هل المزود مهيأ؟"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        توليد استجابة
        
        Args:
            prompt: Prompt
            
        Returns:
            نص الاستجابة
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """فحص الاتصال"""
        pass
    
    def list_capabilities(self) -> List[str]:
        """قائمة القدرات المدعومة"""
        return [
            "generate_code",
            "generate_readme",
            "summarize_project",
            "explain_code",
            "review_code",
            "generate_docs",
        ]
    
    def get_config(self) -> ProviderConfig:
        """الحصول على الإعدادات الحالية"""
        return ProviderConfig(name=self.name)
