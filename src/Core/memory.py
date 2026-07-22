"""
CodeForge Project Memory - Phase X
===================================
ذاكرة المشروع
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from src.Core.event_bus import EventType, emit


@dataclass
class MemoryEntry:
    """ entry في الذاكرة"""
    id: str
    type: str  # adr, report, decision, error, fix
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class ProjectMemory:
    """
    ذاكرة المشروع - لكل مشروع ذاكرته الخاصة
    """
    _instance: Optional["ProjectMemory"] = None
    
    def __new__(cls, memory_path: str = None) -> "ProjectMemory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, memory_path: str = None):
        if self._initialized:
            return
        
        self.memory_path = Path(memory_path) if memory_path else Path("memory")
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.adr_dir = self.memory_path / "adr"
        self.reports_dir = self.memory_path / "reports"
        self.decisions_dir = self.memory_path / "decisions"
        self.errors_dir = self.memory_path / "errors"
        self.fixes_dir = self.memory_path / "fixes"
        
        for d in [self.adr_dir, self.reports_dir, self.decisions_dir, self.errors_dir, self.fixes_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Index
        self.index_file = self.memory_path / ".index.json"
        self._index: Dict[str, MemoryEntry] = {}
        self._load_index()
        
        self._initialized = True
    
    def _load_index(self) -> None:
        """تحميل الفهرس"""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                data = json.load(f)
                for entry_data in data.values():
                    entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
                    self._index[entry_data["id"]] = MemoryEntry(**entry_data)
    
    def _save_index(self) -> None:
        """حفظ الفهرس"""
        data = {eid: entry.to_dict() for eid, entry in self._index.items()}
        with open(self.index_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_adr(self, title: str, content: str, metadata: Dict[str, Any] = None) -> MemoryEntry:
        """إضافة ADR"""
        import uuid
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type="adr",
            title=title,
            content=content,
            metadata=metadata or {},
        )
        
        # Save to file
        filename = self.adr_dir / f"{entry.id}.md"
        with open(filename, "w") as f:
            f.write(f"# ADR: {title}\n\n{content}\n")
        
        # Index
        self._index[entry.id] = entry
        self._save_index()
        
        emit(EventType.MEMORY_UPDATED, {"type": "adr", "id": entry.id})
        
        return entry
    
    def add_report(self, title: str, content: str, metadata: Dict[str, Any] = None) -> MemoryEntry:
        """إضافة تقرير"""
        import uuid
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type="report",
            title=title,
            content=content,
            metadata=metadata or {},
        )
        
        filename = self.reports_dir / f"{entry.id}.md"
        with open(filename, "w") as f:
            f.write(f"# Report: {title}\n\n{content}\n")
        
        self._index[entry.id] = entry
        self._save_index()
        
        emit(EventType.MEMORY_UPDATED, {"type": "report", "id": entry.id})
        
        return entry
    
    def add_decision(self, title: str, content: str, metadata: Dict[str, Any] = None) -> MemoryEntry:
        """إضافة قرار"""
        import uuid
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type="decision",
            title=title,
            content=content,
            metadata=metadata or {},
        )
        
        filename = self.decisions_dir / f"{entry.id}.md"
        with open(filename, "w") as f:
            f.write(f"# Decision: {title}\n\n{content}\n")
        
        self._index[entry.id] = entry
        self._save_index()
        
        emit(EventType.MEMORY_UPDATED, {"type": "decision", "id": entry.id})
        
        return entry
    
    def add_error(self, title: str, content: str, metadata: Dict[str, Any] = None) -> MemoryEntry:
        """إضافة خطأ"""
        import uuid
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type="error",
            title=title,
            content=content,
            metadata=metadata or {},
        )
        
        filename = self.errors_dir / f"{entry.id}.md"
        with open(filename, "w") as f:
            f.write(f"# Error: {title}\n\n{content}\n")
        
        self._index[entry.id] = entry
        self._save_index()
        
        emit(EventType.MEMORY_UPDATED, {"type": "error", "id": entry.id})
        
        return entry
    
    def add_fix(self, error_id: str, content: str, metadata: Dict[str, Any] = None) -> MemoryEntry:
        """إضافة إصلاح"""
        import uuid
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type="fix",
            title=f"Fix for {error_id}",
            content=content,
            metadata={**(metadata or {}), "error_id": error_id},
        )
        
        filename = self.fixes_dir / f"{entry.id}.md"
        with open(filename, "w") as f:
            f.write(f"# Fix: {entry.title}\n\n{content}\n")
        
        self._index[entry.id] = entry
        self._save_index()
        
        emit(EventType.MEMORY_UPDATED, {"type": "fix", "id": entry.id})
        
        return entry
    
    def search(self, query: str, types: List[str] = None) -> List[MemoryEntry]:
        """بحث في الذاكرة"""
        query_lower = query.lower()
        results = []
        
        for entry in self._index.values():
            if types and entry.type not in types:
                continue
            
            if (query_lower in entry.title.lower() or 
                query_lower in entry.content.lower()):
                results.append(entry)
        
        return results
    
    def get_all(self, type: str = None) -> List[MemoryEntry]:
        """الحصول على كل entries"""
        if type:
            return [e for e in self._index.values() if e.type == type]
        return list(self._index.values())
    
    def get_by_id(self, id: str) -> Optional[MemoryEntry]:
        """الحصول على entry بالمعرف"""
        return self._index.get(id)
    
    def count(self, type: str = None) -> int:
        """عدد entries"""
        if type:
            return len([e for e in self._index.values() if e.type == type])
        return len(self._index)


# ============================================================
# Global Instance
# ============================================================

project_memory = ProjectMemory()
