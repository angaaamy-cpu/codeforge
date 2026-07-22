"""
CodeForge Storage Router - Phase 6A
==================================
موجه التخزين: Markdown + ChromaDB (Hybrid)
"""

from typing import List, Optional, Dict, Any

from src.storage.storage import BaseStorage
from src.storage.docs_storage import DocsStorage, docs_storage

# Try to import ChromaDB
try:
    from src.storage.chroma_storage import ChromaStorage, chroma_storage
    
    CHROMADB_AVAILABLE = True
    _chroma = chroma_storage
except ImportError:
    CHROMADB_AVAILABLE = False
    _chroma = None


class StorageRouter:
    """موجه التخزين"""

    def __init__(self):
        self.docs_storage = docs_storage  # Always available (source of truth)
        self.chroma_storage = _chroma  # Optional
        self.use_chroma = CHROMADB_AVAILABLE

    @property
    def is_hybrid(self) -> bool:
        """هل يعمل بالطريقتين"""
        return self.use_chroma and self.chroma_storage is not None

    def save(self, key: str, data: Any, use_chroma: bool = False) -> bool:
        """حفظ بيانات"""
        # Always save to Markdown
        result = self.docs_storage.save(key, data)
        
        # Optionally save to ChromaDB
        if use_chroma and self.use_chroma:
            self.chroma_storage.save(key, data)
        
        return result

    def load(self, key: str) -> Optional[Any]:
        """تحميل بيانات"""
        return self.docs_storage.load(key)

    def delete(self, key: str) -> bool:
        """حذف بيانات"""
        # Delete from both
        result = self.docs_storage.delete(key)
        
        if self.use_chroma:
            self.chroma_storage.delete(key)
        
        return result

    def exists(self, key: str) -> bool:
        """فحص وجود"""
        return self.docs_storage.exists(key)

    def list_keys(self, prefix: str = "") -> List[str]:
        """قائمة المفاتيح"""
        return self.docs_storage.list_keys(prefix)

    def search(self, query: str, limit: int = 10, use_chroma: bool = False) -> List[Dict]:
        """
        بحث في الذاكرة
        
        Args:
            query: نص البحث
            limit: عدد النتائج
            use_chroma: استخدام ChromaDB أم Markdown فقط
        """
        if use_chroma and self.use_chroma:
            # Try ChromaDB first
            chroma_results = self.chroma_storage.search(query, limit)
            if chroma_results:
                return chroma_results
        
        # Fallback to Markdown
        return self.docs_storage.search(query, limit)

    def get_metadata(self, key: str) -> Dict:
        """الحصول على metadata"""
        return self.docs_storage.get_metadata(key)

    def search_hybrid(self, query: str, limit: int = 10) -> Dict:
        """
        بحث هجين: Markdown + ChromaDB
        
        Returns:
            Dict with results from both sources
        """
        results = {
            "markdown": [],
            "chromadb": [],
            "combined": [],
        }
        
        # Markdown search
        markdown_results = self.docs_storage.search(query, limit)
        results["markdown"] = markdown_results
        
        # ChromaDB search
        if self.use_chroma:
            chroma_results = self.chroma_storage.search(query, limit)
            results["chromadb"] = chroma_results
            
            # Combine and dedupe
            seen_ids = set()
            for r in markdown_results:
                r["source"] = "markdown"
                if r["id"] not in seen_ids:
                    results["combined"].append(r)
                    seen_ids.add(r["id"])
            
            for r in chroma_results:
                r["source"] = "chromadb"
                if r["id"] not in seen_ids:
                    results["combined"].append(r)
                    seen_ids.add(r["id"])
        else:
            results["combined"] = markdown_results
        
        return results

    def get_stats(self) -> Dict:
        """إحصائيات التخزين"""
        stats = {
            "backend": "markdown",
            "chroma_available": self.use_chroma,
            "is_hybrid": self.is_hybrid,
            "docs_storage": {
                "projects": len(self.docs_storage.list_projects()),
                "adrs": len(self.docs_storage.list_adrs()),
                "reports": len(self.docs_storage.list_reports()),
            },
        }
        
        if self.use_chroma:
            chroma_stats = self.chroma_storage.get_stats()
            stats["chroma_storage"] = chroma_stats
        
        return stats

    def enable_chroma(self) -> bool:
        """تفعيل ChromaDB"""
        if not CHROMADB_AVAILABLE:
            return False
        
        self.use_chroma = True
        return True

    def disable_chroma(self):
        """إلغاء تفعيل ChromaDB"""
        self.use_chroma = False


# ============================================================
# Global Instance
# ============================================================

storage_router = StorageRouter()


# ============================================================
# Convenience Functions
# ============================================================

def search_memory(query: str, limit: int = 10, use_chroma: bool = False) -> List[Dict]:
    """بحث في الذاكرة"""
    return storage_router.search(query, limit, use_chroma)


def search_hybrid(query: str, limit: int = 10) -> Dict:
    """بحث هجين"""
    return storage_router.search_hybrid(query, limit)


def get_storage_stats() -> Dict:
    """إحصائيات التخزين"""
    return storage_router.get_stats()


def is_chroma_available() -> bool:
    """هل ChromaDB متاح"""
    return CHROMADB_AVAILABLE


def is_hybrid_mode() -> bool:
    """هل يعمل بالطريقتين"""
    return storage_router.is_hybrid
