"""
CodeForge Storage Module - Phase 6A
==================================
"""

from src.storage.storage import BaseStorage, Project, ADR, TaskReport
from src.storage.docs_storage import DocsStorage, docs_storage

# Optional ChromaDB components
try:
    from src.storage.chroma_storage import ChromaStorage, chroma_storage
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chroma_storage = None

from src.storage.storage_router import (
    StorageRouter,
    storage_router,
    search_memory,
    search_hybrid,
    get_storage_stats,
    is_chroma_available,
    is_hybrid_mode,
)

__all__ = [
    "BaseStorage",
    "Project",
    "ADR",
    "TaskReport",
    "DocsStorage",
    "docs_storage",
    # ChromaDB (optional)
    "CHROMADB_AVAILABLE",
    "ChromaStorage",
    "chroma_storage",
    # Router
    "StorageRouter",
    "storage_router",
    "search_memory",
    "search_hybrid",
    "get_storage_stats",
    "is_chroma_available",
    "is_hybrid_mode",
]
