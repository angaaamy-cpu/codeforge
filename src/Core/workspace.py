"""
CodeForge Workspace Manager - Phase X
======================================
إدارة المشاريع والملفات
"""

import os
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from src.Core.event_bus import EventType, emit
from src.Core.memory import ProjectMemory


@dataclass
class WorkspaceMetadata:
    """metadata المشروع"""
    name: str
    description: str = ""
    status: str = "active"  # active, archived, deleted
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    path: str = ""
    memory_path: str = ""
    reports_path: str = ""
    secrets_path: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "path": self.path,
        }


class WorkspaceManager:
    """
    مدير مساحة العمل
    """
    _instance: Optional["WorkspaceManager"] = None
    
    def __new__(cls, root_path: str = None) -> "WorkspaceManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, root_path: str = None):
        if self._initialized:
            return
        
        # Root directory for all workspaces
        self.root_path = Path(root_path) if root_path else Path("workspaces")
        self.root_path.mkdir(parents=True, exist_ok=True)
        
        # Index file
        self.index_file = self.root_path / ".workspaces.json"
        self._index: Dict[str, WorkspaceMetadata] = {}
        self._load_index()
        
        # Active workspace
        self._active_workspace: Optional[str] = None
        
        self._initialized = True
    
    def _load_index(self) -> None:
        """تحميل فهرس المشاريع"""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                data = json.load(f)
                for name, info in data.items():
                    info["created_at"] = datetime.fromisoformat(info["created_at"])
                    info["updated_at"] = datetime.fromisoformat(info["updated_at"])
                    self._index[name] = WorkspaceMetadata(**info)
    
    def _save_index(self) -> None:
        """حفظ فهرس المشاريع"""
        data = {name: meta.to_dict() for name, meta in self._index.items()}
        with open(self.index_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def create(
        self,
        name: str,
        description: str = "",
        template: str = None,
    ) -> WorkspaceMetadata:
        """
        إنشاء مساحة عمل جديدة
        
        Args:
            name: اسم المشروع
            description: الوصف
            template: قالب (اختياري)
            
        Returns:
            WorkspaceMetadata
        """
        if name in self._index:
            raise ValueError(f"Workspace '{name}' already exists")
        
        # Create directory structure
        workspace_path = self.root_path / name
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (workspace_path / "src").mkdir(exist_ok=True)
        (workspace_path / "tests").mkdir(exist_ok=True)
        (workspace_path / "docs").mkdir(exist_ok=True)
        (workspace_path / "memory").mkdir(exist_ok=True)
        
        # Create metadata
        metadata = WorkspaceMetadata(
            name=name,
            description=description,
            path=str(workspace_path),
            memory_path=str(workspace_path / "memory"),
            reports_path=str(workspace_path / "docs"),
            secrets_path=str(workspace_path / ".secrets"),
        )
        
        # Save metadata
        self._index[name] = metadata
        self._save_index()
        
        # Emit event
        emit(EventType.PROJECT_CREATED, {
            "name": name,
            "path": str(workspace_path),
        })
        
        return metadata
    
    def open(self, name: str) -> WorkspaceMetadata:
        """فتح مساحة عمل"""
        if name not in self._index:
            raise ValueError(f"Workspace '{name}' not found")
        
        self._active_workspace = name
        
        metadata = self._index[name]
        metadata.updated_at = datetime.now()
        self._save_index()
        
        emit(EventType.PROJECT_OPENED, {"name": name})
        
        return metadata
    
    def close(self) -> None:
        """إغلاق مساحة العمل النشطة"""
        self._active_workspace = None
    
    def get_active(self) -> Optional[WorkspaceMetadata]:
        """الحصول على مساحة العمل النشطة"""
        if not self._active_workspace:
            return None
        return self._index.get(self._active_workspace)
    
    def archive(self, name: str) -> bool:
        """أرشفة مساحة عمل"""
        if name not in self._index:
            return False
        
        metadata = self._index[name]
        metadata.status = "archived"
        metadata.updated_at = datetime.now()
        
        # Move to archive
        archive_path = self.root_path / "archive" / name
        workspace_path = Path(metadata.path)
        
        if workspace_path.exists():
            shutil.move(str(workspace_path), str(archive_path))
            metadata.path = str(archive_path)
        
        self._save_index()
        emit(EventType.PROJECT_ARCHIVED, {"name": name})
        
        return True
    
    def delete(self, name: str) -> bool:
        """حذف مساحة عمل"""
        if name not in self._index:
            return False
        
        metadata = self._index[name]
        
        # Delete files
        workspace_path = Path(metadata.path)
        if workspace_path.exists():
            shutil.rmtree(workspace_path)
        
        # Remove from index
        del self._index[name]
        self._save_index()
        
        emit(EventType.PROJECT_DELETED, {"name": name})
        
        return True
    
    def list_all(self) -> List[WorkspaceMetadata]:
        """قائمة كل مساحات العمل"""
        return list(self._index.values())
    
    def list_active(self) -> List[WorkspaceMetadata]:
        """قائمة المساحات النشطة"""
        return [m for m in self._index.values() if m.status == "active"]
    
    def list_archived(self) -> List[WorkspaceMetadata]:
        """قائمة المساحات المؤرشفة"""
        return [m for m in self._index.values() if m.status == "archived"]
    
    def exists(self, name: str) -> bool:
        """فحص وجود مساحة عمل"""
        return name in self._index
    
    def get(self, name: str) -> Optional[WorkspaceMetadata]:
        """الحصول على metadata"""
        return self._index.get(name)


# ============================================================
# Global Instance
# ============================================================

workspace_manager = WorkspaceManager()
