"""
CodeForge Capability Requirements - Agent OS
===========================================
نظام متطلبات القدرات
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum


class RequirementType(str, Enum):
    NONE = "none"
    LLM = "llm"
    GIT = "git"
    NETWORK = "network"
    SECRETS = "secrets"


@dataclass
class CapabilityRequirement:
    name: str
    display_name: str
    description: str
    requires_llm: bool = False
    requires_git: bool = False
    requires_network: bool = False
    requires_secrets: bool = False
    execution_type: RequirementType = RequirementType.NONE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "requires_llm": self.requires_llm,
            "requires_git": self.requires_git,
            "requires_network": self.requires_network,
            "requires_secrets": self.requires_secrets,
            "execution_type": self.execution_type.value,
        }


class CapabilityRequirementsRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._requirements: Dict[str, CapabilityRequirement] = {}
        self._register_defaults()
        self._initialized = True
    
    def _register_defaults(self):
        defaults = [
            CapabilityRequirement("create_file", "إنشاء ملف", "إنشاء ملف جديد", requires_llm=False),
            CapabilityRequirement("read_file", "قراءة ملف", "قراءة محتوى ملف", requires_llm=False),
            CapabilityRequirement("write_file", "كتابة ملف", "كتابة محتوى لملف", requires_llm=False),
            CapabilityRequirement("delete_file", "حذف ملف", "حذف ملف أو مجلد", requires_llm=False),
            CapabilityRequirement("list_files", "قائمة الملفات", "عرض قائمة الملفات", requires_llm=False),
            CapabilityRequirement("git_init", "تهيئة Git", "تهيئة مستودع Git", requires_git=True),
            CapabilityRequirement("git_add", "إضافة ملفات", "إضافة ملفات للتتبع", requires_git=True),
            CapabilityRequirement("git_commit", "تسجيل commit", "تسجيل التغييرات", requires_git=True),
            CapabilityRequirement("git_push", "رفع التغييرات", "رفع commits", requires_git=True, requires_network=True),
            CapabilityRequirement("git_clone", "استنساخ", "استنساخ مستودع", requires_git=True, requires_network=True),
            CapabilityRequirement("generate_code", "توليد كود", "توليد كود بالذكاء", requires_llm=True),
            CapabilityRequirement("generate_readme", "توليد README", "توليد README", requires_llm=True),
            CapabilityRequirement("summarize_project", "تلخيص المشروع", "تلخيص محتوى المشروع", requires_llm=True),
            CapabilityRequirement("create_project", "إنشاء مشروع", "إنشاء مشروع جديد", requires_llm=False),
            CapabilityRequirement("list_projects", "قائمة المشاريع", "عرض قائمة المشاريع", requires_llm=False),
            CapabilityRequirement("deploy_railway", "نشر Railway", "نشر على Railway", requires_network=True),
            CapabilityRequirement("run_tests", "تشغيل الاختبارات", "تشغيل اختبارات", requires_llm=False),
            CapabilityRequirement("add_secret", "إضافة سر", "إضافة مفتاح سري", requires_secrets=True),
            CapabilityRequirement("list_secrets", "قائمة الأسرار", "عرض المفاتيح", requires_llm=False),
        ]
        for req in defaults:
            self._requirements[req.name] = req
    
    def get(self, name: str) -> CapabilityRequirement:
        return self._requirements.get(name)
    
    def list_all(self) -> List[CapabilityRequirement]:
        return list(self._requirements.values())
    
    def list_direct_execution(self) -> List[CapabilityRequirement]:
        return [r for r in self._requirements.values() if not r.requires_llm]
    
    def list_llm_required(self) -> List[CapabilityRequirement]:
        return [r for r in self._requirements.values() if r.requires_llm]
    
    def needs_llm(self, name: str) -> bool:
        req = self._requirements.get(name)
        return req.requires_llm if req else False


capability_requirements = CapabilityRequirementsRegistry()
