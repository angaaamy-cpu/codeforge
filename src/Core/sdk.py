"""
CodeForge Python SDK - Phase X
===============================
Python SDK للمنصة
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.Core.workspace import WorkspaceManager, WorkspaceMetadata
from src.Core.capability import CapabilityRegistry, get_capability
from src.Core.event_bus import event_bus, EventType, Event
from src.Core.execution import ExecutionEngine, ExecutionContext
from src.Core.memory import ProjectMemory, MemoryEntry
from src.Core.deployment import DeploymentManager, DeploymentPlatform, Deployment
from src.Core.secrets import SecretsManager


@dataclass
class BuildResult:
    """نتيجة البناء"""
    status: str
    project_name: str
    project_path: str
    files_count: int
    run_command: str
    url: str
    duration_seconds: float
    error: Optional[str] = None
    
    @classmethod
    def from_execution(cls, context: ExecutionContext) -> "BuildResult":
        return cls(
            status="success" if all(s.status.value == "completed" for s in context.steps) else "failed",
            project_name=context.workspace,
            project_path=f"workspaces/{context.workspace}",
            files_count=0,
            run_command="python src/app.py",
            url="",
            duration_seconds=sum(s.duration_seconds for s in context.steps),
        )


class CodeForge:
    """
    Python SDK للـ CodeForge
    
    Usage:
        from src.sdk import CodeForge
        
        cf = CodeForge()
        result = cf.build("صفحة هبوط لشركة ناشئة")
        result.deploy("railway")
    """
    
    def __init__(self):
        self.workspace = WorkspaceManager()
        self.capabilities = CapabilityRegistry()
        self.events = event_bus
        self.execution = ExecutionEngine()
        self.memory = ProjectMemory()
        self.deployment = DeploymentManager()
        self.secrets = SecretsManager()
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    # ========== Workspace ==========
    
    def create_project(self, name: str, description: str = "") -> WorkspaceMetadata:
        """إنشاء مشروع"""
        return self.workspace.create(name, description)
    
    def open_project(self, name: str) -> WorkspaceMetadata:
        """فتح مشروع"""
        return self.workspace.open(name)
    
    def list_projects(self) -> List[WorkspaceMetadata]:
        """قائمة المشاريع"""
        return self.workspace.list_all()
    
    def archive_project(self, name: str) -> bool:
        """أرشفة مشروع"""
        return self.workspace.archive(name)
    
    def delete_project(self, name: str) -> bool:
        """حذف مشروع"""
        return self.workspace.delete(name)
    
    # ========== Build ==========
    
    def build(self, description: str, workspace: str = "") -> BuildResult:
        """بناء مشروع"""
        # Use existing build engine
        from src.codeforge import CodeForge as CF
        cf = CF()
        result = cf.build(description)
        
        return BuildResult(
            status=result.status,
            project_name=result.project_name,
            project_path=result.project_path,
            files_count=result.files_count,
            run_command=result.run_command,
            url=result.url,
            duration_seconds=result.duration_seconds,
            error=result.error,
        )
    
    # ========== Deployment ==========
    
    def deploy(self, platform: str, project_name: str) -> Deployment:
        """نشر مشروع"""
        platform_enum = DeploymentPlatform(platform.lower())
        return self.deployment.deploy(project_name, platform_enum)
    
    def deployment_status(self, deployment_id: str) -> Optional[Deployment]:
        """حالة النشر"""
        return self.deployment.status(deployment_id)
    
    def redeploy(self, deployment_id: str) -> bool:
        """إعادة نشر"""
        return self.deployment.redeploy(deployment_id)
    
    # ========== Memory ==========
    
    def add_decision(self, title: str, content: str) -> MemoryEntry:
        """إضافة قرار"""
        return self.memory.add_decision(title, content)
    
    def add_report(self, title: str, content: str) -> MemoryEntry:
        """إضافة تقرير"""
        return self.memory.add_report(title, content)
    
    def search_memory(self, query: str) -> List[MemoryEntry]:
        """بحث في الذاكرة"""
        return self.memory.search(query)
    
    # ========== Capabilities ==========
    
    def list_capabilities(self) -> List[Dict[str, Any]]:
        """قائمة القدرات"""
        return [c.to_dict() for c in self.capabilities.list_all()]
    
    def get_capability(self, name: str) -> Optional[Dict[str, Any]]:
        """الحصول على قدرة"""
        cap = self.capabilities.get(name)
        return cap.to_dict() if cap else None
    
    # ========== Events ==========
    
    def subscribe(self, event_type: EventType, handler) -> str:
        """الاشتراك في حدث"""
        return self.events.subscribe(event_type, handler)
    
    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Event]:
        """سجل الأحداث"""
        return self.events.get_history(event_type, limit)


# ============================================================
# Project Interface
# ============================================================

class Project:
    """
    واجهة المشروع
    
    Usage:
        cf = CodeForge()
        project = cf.open_project("my-app")
        result = project.build("أضف صفحة تسجيل")
        project.deploy("railway")
    """
    
    def __init__(self, name: str, metadata: WorkspaceMetadata):
        self.name = name
        self.metadata = metadata
        self._cf = CodeForge()
    
    def build(self, description: str) -> BuildResult:
        """بناء في المشروع"""
        return self._cf.build(description, self.name)
    
    def deploy(self, platform: str) -> Deployment:
        """نشر المشروع"""
        return self._cf.deploy(platform, self.name)
    
    def add_file(self, path: str, content: str) -> bool:
        """إضافة ملف"""
        import os
        full_path = os.path.join(self.metadata.path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return True
    
    def read_file(self, path: str) -> str:
        """قراءة ملف"""
        import os
        full_path = os.path.join(self.metadata.path, path)
        with open(full_path, "r") as f:
            return f.read()
    
    def list_files(self) -> List[str]:
        """قائمة الملفات"""
        import os
        result = []
        for root, dirs, files in os.walk(self.metadata.path):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.metadata.path)
                if not rel_path.startswith("."):
                    result.append(rel_path)
        return result


# ============================================================
# Convenience Functions
# ============================================================

def create_project(name: str, description: str = "") -> Project:
    """إنشاء مشروع بسرعة"""
    cf = CodeForge()
    metadata = cf.create_project(name, description)
    return Project(name, metadata)


def open_project(name: str) -> Project:
    """فتح مشروع بسرعة"""
    cf = CodeForge()
    metadata = cf.open_project(name)
    return Project(name, metadata)
