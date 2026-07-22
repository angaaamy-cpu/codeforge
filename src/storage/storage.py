"""
CodeForge Storage Interface - Phase 5
=====================================
واجهة مجردة للتخزين
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime


class BaseStorage(ABC):
    """الواجهة الأساسية للتخزين"""

    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """حفظ بيانات"""
        pass

    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """تحميل بيانات"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """حذف بيانات"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """فحص وجود بيانات"""
        pass

    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """قائمة المفاتيح"""
        pass

    @abstractmethod
    def search(self, query: str) -> List[Dict]:
        """بحث في البيانات"""
        pass

    @abstractmethod
    def get_metadata(self, key: str) -> Dict:
        """الحصول على metadata"""
        pass


class Project:
    """كيان المشروع"""

    def __init__(
        self,
        name: str,
        description: str = "",
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        task_count: int = 0,
        completed_tasks: int = 0,
    ):
        self.name = name
        self.description = description
        self.status = status  # active, archived, deleted
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.task_count = task_count
        self.completed_tasks = completed_tasks

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "task_count": self.task_count,
            "completed_tasks": self.completed_tasks,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            status=data.get("status", "active"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
            task_count=data.get("task_count", 0),
            completed_tasks=data.get("completed_tasks", 0),
        )


class ADR:
    """كيان قرار معماري"""

    def __init__(
        self,
        number: int,
        title: str,
        status: str,
        agent: str,
        content: str,
        project: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.number = number
        self.title = title
        self.status = status
        self.agent = agent
        self.content = content
        self.project = project
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "title": self.title,
            "status": self.status,
            "agent": self.agent,
            "content": self.content,
            "project": self.project,
            "created_at": self.created_at.isoformat(),
        }


class TaskReport:
    """كيان تقرير مهمة"""

    def __init__(
        self,
        task_id: str,
        description: str,
        status: str,
        project: Optional[str] = None,
        plan: Optional[List[str]] = None,
        modified_files: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.task_id = task_id
        self.description = description
        self.status = status
        self.project = project
        self.plan = plan or []
        self.modified_files = modified_files or []
        self.errors = errors or []
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status,
            "project": self.project,
            "plan": self.plan,
            "modified_files": self.modified_files,
            "errors": self.errors,
            "created_at": self.created_at.isoformat(),
        }
