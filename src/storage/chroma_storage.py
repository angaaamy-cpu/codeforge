"""
CodeForge ChromaDB Storage - Phase 6A
====================================
طبقة تخزين ChromaDB الاختيارية
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.storage.storage import BaseStorage


class ChromaStorage(BaseStorage):
    """تخزين ChromaDB"""

    def __init__(self, persist_directory: str = "data/chromadb"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self._client = None
        self._collection = None
        self._initialized = False

    def _ensure_init(self):
        """التأكد من التهيئة"""
        if self._initialized:
            return True
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            self._client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            
            self._collection = self._client.get_or_create_collection(
                name="codeforge_memory",
                metadata={"description": "CodeForge AI Agent Memory"}
            )
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"⚠️ ChromaDB initialization failed: {e}")
            self._initialized = False
            return False

    def save(self, key: str, data: Any) -> bool:
        """حفظ بيانات في ChromaDB"""
        if not self._ensure_init():
            return False
        
        try:
            # Store with metadata
            self._collection.add(
                documents=[str(data)],
                ids=[key],
                metadatas=[{
                    "type": type(data).__name__,
                    "timestamp": datetime.now().isoformat(),
                }]
            )
            return True
        except Exception as e:
            print(f"⚠️ ChromaDB save error: {e}")
            return False

    def load(self, key: str) -> Optional[Any]:
        """تحميل بيانات من ChromaDB"""
        if not self._ensure_init():
            return None
        
        try:
            result = self._collection.get(ids=[key])
            if result and result.get("documents"):
                return result["documents"][0]
            return None
        except Exception:
            return None

    def delete(self, key: str) -> bool:
        """حذف بيانات"""
        if not self._ensure_init():
            return False
        
        try:
            self._collection.delete(ids=[key])
            return True
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """فحص وجود"""
        if not self._ensure_init():
            return False
        
        try:
            result = self._collection.get(ids=[key])
            return bool(result.get("ids"))
        except Exception:
            return False

    def list_keys(self, prefix: str = "") -> List[str]:
        """قائمة المفاتيح"""
        if not self._ensure_init():
            return []
        
        try:
            if prefix:
                result = self._collection.get(
                    where={"type": {"$contains": prefix}}
                )
            else:
                result = self._collection.get()
            
            return result.get("ids", [])
        except Exception:
            return []

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """بحث في ChromaDB"""
        if not self._ensure_init():
            return []
        
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            search_results = []
            if results and results.get("ids"):
                for i, doc_id in enumerate(results["ids"][0]):
                    search_results.append({
                        "id": doc_id,
                        "content": results["documents"][0][i] if results.get("documents") else "",
                        "distance": results["distances"][0][i] if results.get("distances") else 0,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    })
            
            return search_results
        except Exception as e:
            print(f"⚠️ ChromaDB search error: {e}")
            return []

    def get_metadata(self, key: str) -> Dict:
        """الحصول على metadata"""
        if not self._ensure_init():
            return {}
        
        try:
            result = self._collection.get(ids=[key])
            if result and result.get("metadatas"):
                return result["metadatas"][0]
            return {}
        except Exception:
            return {}

    def add_document(self, doc_id: str, content: str, metadata: Dict = None) -> bool:
        """إضافة مستند"""
        if not self._ensure_init():
            return False
        
        try:
            self._collection.add(
                documents=[content],
                ids=[doc_id],
                metadatas=[metadata or {}]
            )
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict:
        """إحصائيات التخزين"""
        if not self._ensure_init():
            return {"initialized": False}
        
        try:
            count = self._collection.count()
            return {
                "initialized": True,
                "document_count": count,
                "persist_directory": str(self.persist_directory),
            }
        except Exception as e:
            return {"initialized": False, "error": str(e)}


# Global instance (lazy initialization)
chroma_storage = ChromaStorage()
