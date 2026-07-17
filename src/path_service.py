"""
CodeForge Path Service - Production Ready
=========================================
طبقة مركزية لإدارة المسارات
جميع عمليات المسارات تمر عبر هذه الطبقة

Environment Variables:
- WORKSPACE_ROOT: المسار الجذر (افتراضي: كشف تلقائي)
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Union
from dataclasses import dataclass


# Global path configuration
def _get_workspace_root() -> Path:
    """كشف المسار الجذر من متغيرات البيئة أو الموقع"""
    # 1. Check WORKSPACE_ROOT environment variable
    if os.environ.get("WORKSPACE_ROOT"):
        return Path(os.environ["WORKSPACE_ROOT"]).resolve()
    
    # 2. Check if running on Railway
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        return Path("/app")
    
    # 3. Use the project root (parent of src/)
    # This works because path_service.py is in src/
    return Path(__file__).parent.parent.resolve()


# Global root path
WORKSPACE_ROOT = _get_workspace_root()


@dataclass
class PathInfo:
    """معلومات المسار"""
    absolute: str
    relative: str
    exists: bool
    is_file: bool
    is_dir: bool
    size: int = 0


class PathService:
    """
    طبقة مركزية لإدارة المسارات
    
    Usage:
        from src.path_service import path_service
        
        # Read file
        content = path_service.read("README.md")
        
        # Write file
        path_service.write("new-file.txt", "content")
        
        # Check path
        info = path_service.info("src/app.py")
        
        # Create directory
        path_service.mkdir("projects/new-project")
    """
    
    _instance = None
    
    def __new__(cls, root: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, root: str = None):
        if self._initialized:
            return
        
        # Use provided root, WORKSPACE_ROOT, or detect automatically
        if root:
            self.root = Path(root).resolve()
        else:
            self.root = WORKSPACE_ROOT
        
        # Ensure root exists
        self.root.mkdir(parents=True, exist_ok=True)
        
        # Initialize directories
        self._init_directories()
        
        self._initialized = True
    
    def _init_directories(self) -> None:
        """تهيئة المجلدات المطلوبة"""
        dirs = [
            "projects",
            "workspaces",
            "docs",
            "docs/projects",
            "docs/reports",
            "docs/adr",
            "logs",
            "static",
            "templates",
            "plugins",
        ]
        for d in dirs:
            (self.root / d).mkdir(parents=True, exist_ok=True)
    
    # ========== Path Resolution ==========
    
    def resolve(self, path: Union[str, Path]) -> Path:
        """
        تحويل مسار إلى مسار مطلق
        
        Args:
            path: مسار (نسبي أو مطلق)
            
        Returns:
            Path مطلق
        """
        p = Path(path)
        if p.is_absolute():
            return p.resolve()
        return (self.root / p).resolve()
    
    def relative(self, path: Union[str, Path]) -> str:
        """
        الحصول على المسار النسبي من الجذر
        
        Args:
            path: مسار
            
        Returns:
            مسار نسبي من الجذر
        """
        try:
            return str(Path(path).resolve().relative_to(self.root))
        except ValueError:
            # Not relative to root, return as-is
            return str(path)
    
    def is_within_root(self, path: Union[str, Path]) -> bool:
        """
        فحص إذا كان المسار ضمن الجذر (أمان)
        
        Args:
            path: مسار للفحص
            
        Returns:
            True إذا كان ضمن الجذر
        """
        try:
            resolved = Path(path).resolve()
            resolved.relative_to(self.root)
            return True
        except ValueError:
            return False
    
    # ========== Info ==========
    
    def info(self, path: Union[str, Path]) -> PathInfo:
        """
        الحصول على معلومات المسار
        
        Args:
            path: المسار
            
        Returns:
            PathInfo
        """
        p = self.resolve(path)
        
        return PathInfo(
            absolute=str(p),
            relative=self.relative(p),
            exists=p.exists(),
            is_file=p.is_file(),
            is_dir=p.is_dir(),
            size=p.stat().st_size if p.is_file() else 0,
        )
    
    # ========== Read/Write ==========
    
    def read(self, path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        قراءة ملف
        
        Args:
            path: المسار
            encoding: الترميز
            
        Returns:
            محتوى الملف
        """
        p = self.resolve(path)
        
        if not p.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        
        return p.read_text(encoding=encoding)
    
    def write(
        self,
        path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
    ) -> bool:
        """
        كتابة ملف
        
        Args:
            path: المسار
            content: المحتوى
            encoding: الترميز
            
        Returns:
            True إذا نجح
        """
        if not self.is_within_root(path):
            raise ValueError(f"Path outside root: {path}")
        
        p = self.resolve(path)
        
        # Create parent directories
        p.parent.mkdir(parents=True, exist_ok=True)
        
        p.write_text(content, encoding=encoding)
        return True
    
    def append(self, path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
        """
        إضافة محتوى لملف موجود
        
        Args:
            path: المسار
            content: المحتوى
            encoding: الترميز
            
        Returns:
            True إذا نجح
        """
        p = self.resolve(path)
        
        if not self.is_within_root(path):
            raise ValueError(f"Path outside root: {path}")
        
        # Create parent directories
        p.parent.mkdir(parents=True, exist_ok=True)
        
        with open(p, "a", encoding=encoding) as f:
            f.write(content)
        return True
    
    # ========== File Operations ==========
    
    def exists(self, path: Union[str, Path]) -> bool:
        """فحص وجود المسار"""
        return self.resolve(path).exists()
    
    def is_file(self, path: Union[str, Path]) -> bool:
        """فحص إذا كان ملف"""
        return self.resolve(path).is_file()
    
    def is_dir(self, path: Union[str, Path]) -> bool:
        """فحص إذا كان مجلد"""
        return self.resolve(path).is_dir()
    
    def mkdir(self, path: Union[str, Path], parents: bool = True) -> bool:
        """
        إنشاء مجلد
        
        Args:
            path: المسار
            parents: إنشاء الأبناء
            
        Returns:
            True إذا نجح
        """
        if not self.is_within_root(path):
            raise ValueError(f"Path outside root: {path}")
        
        p = self.resolve(path)
        p.mkdir(parents=parents, exist_ok=True)
        return True
    
    def delete(self, path: Union[str, Path]) -> bool:
        """
        حذف ملف أو مجلد
        
        Args:
            path: المسار
            
        Returns:
            True إذا نجح
        """
        if not self.is_within_root(path):
            raise ValueError(f"Path outside root: {path}")
        
        p = self.resolve(path)
        
        if not p.exists():
            return False
        
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
        
        return True
    
    def copy(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """
        نسخ ملف أو مجلد
        
        Args:
            src: المصدر
            dst: الوجهة
            
        Returns:
            True إذا نجح
        """
        if not self.is_within_root(src) or not self.is_within_root(dst):
            raise ValueError(f"Path outside root")
        
        src_p = self.resolve(src)
        dst_p = self.resolve(dst)
        
        if not src_p.exists():
            return False
        
        # Create parent
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        
        if src_p.is_file():
            shutil.copy2(src_p, dst_p)
        elif src_p.is_dir():
            shutil.copytree(src_p, dst_p, dirs_exist_ok=True)
        
        return True
    
    def move(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """
        نقل ملف أو مجلد
        
        Args:
            src: المصدر
            dst: الوجهة
            
        Returns:
            True إذا نجح
        """
        if not self.is_within_root(src) or not self.is_within_root(dst):
            raise ValueError(f"Path outside root")
        
        src_p = self.resolve(src)
        dst_p = self.resolve(dst)
        
        if not src_p.exists():
            return False
        
        # Create parent
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(src_p), str(dst_p))
        return True
    
    # ========== Directory Operations ==========
    
    def list(self, path: Union[str, Path] = ".", pattern: str = "*") -> List[str]:
        """
        قائمة الملفات في مجلد
        
        Args:
            path: المسار
            pattern: نمط البحث
            
        Returns:
            قائمة الملفات
        """
        p = self.resolve(path)
        
        if not p.is_dir():
            return []
        
        return [str(f.relative_to(p)) for f in p.glob(pattern) if f.is_file()]
    
    def list_dirs(self, path: Union[str, Path] = ".") -> List[str]:
        """
        قائمة المجلدات
        
        Args:
            path: المسار
            
        Returns:
            قائمة المجلدات
        """
        p = self.resolve(path)
        
        if not p.is_dir():
            return []
        
        return [str(f.relative_to(p)) for f in p.iterdir() if f.is_dir()]
    
    def walk(
        self,
        path: Union[str, Path] = ".",
        max_depth: int = None,
    ) -> List[dict]:
        """
        التجول في شجرة الملفات
        
        Args:
            path: المسار
            max_depth: أقصى عمق
            
        Returns:
            قائمة الملفات مع معلوماتها
        """
        p = self.resolve(path)
        result = []
        
        def _walk(current: Path, depth: int = 0):
            if max_depth is not None and depth > max_depth:
                return
            
            if not current.is_dir():
                return
            
            for item in current.iterdir():
                rel = item.relative_to(p)
                result.append({
                    "path": str(rel),
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0,
                    "depth": depth,
                })
                
                if item.is_dir():
                    _walk(item, depth + 1)
        
        _walk(p)
        return result
    
    # ========== Special Paths ==========
    
    @property
    def projects_dir(self) -> Path:
        """مجلد المشاريع"""
        return self.root / "projects"
    
    @property
    def workspaces_dir(self) -> Path:
        """مجلد مساحات العمل"""
        return self.root / "workspaces"
    
    @property
    def docs_dir(self) -> Path:
        """مجلد التوثيق"""
        return self.root / "docs"
    
    @property
    def logs_dir(self) -> Path:
        """مجلد السجلات"""
        return self.root / "logs"
    
    @property
    def plugins_dir(self) -> Path:
        """مجلد الإضافات"""
        return self.root / "plugins"


# ============================================================
# Global Instance
# ============================================================

path_service = PathService()
