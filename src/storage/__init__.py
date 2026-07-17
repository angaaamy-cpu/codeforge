"""
CodeForge Storage Module - Phase 5
==================================
"""

from src.storage.storage import BaseStorage, Project, ADR, TaskReport
from src.storage.docs_storage import DocsStorage, docs_storage

__all__ = [
    "BaseStorage",
    "Project",
    "ADR",
    "TaskReport",
    "DocsStorage",
    "docs_storage",
]
