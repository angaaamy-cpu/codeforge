"""
CodeForge Project Manager - Phase 5
===================================
مدير المشاريع
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

from config import PROJECTS_DIR, DOCS_PROJECTS_DIR, PROGRESS_FILE, ACTIVE_PROJECT_FILE
from src.storage import Project, docs_storage
from src.event_logger import log_project_created, log_project_archived, log_project_deleted


class ProjectManager:
    """مدير المشاريع"""

    def __init__(self):
        self.projects_dir = Path(PROJECTS_DIR)
        self.docs_dir = Path(DOCS_PROJECTS_DIR)
        self._ensure_dirs()

    def _ensure_dirs(self):
        """التأكد من وجود المجلدات"""
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str, description: str = "") -> Dict:
        """
        إنشاء مشروع جديد
        
        Returns:
            Dict with success status and project info
        """
        # Validate name
        if not name or not name.strip():
            return {"success": False, "error": "اسم المشروع مطلوب"}
        
        name = name.strip().lower().replace(" ", "-")
        
        # Check if exists
        if docs_storage.project_exists(name):
            return {"success": False, "error": f"المشروع '{name}' موجود بالفعل"}
        
        # Create project directory
        project_dir = self.projects_dir / name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create project doc
        self._create_project_doc(name, description)
        
        # Create project in storage
        project = Project(
            name=name,
            description=description,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        docs_storage.save_project(project)
        
        # Log event
        log_project_created(name)
        
        # Update progress
        self._update_progress(name, "created")
        
        return {
            "success": True,
            "project": project.to_dict(),
            "message": f"تم إنشاء المشروع '{name}' بنجاح"
        }

    def _create_project_doc(self, name: str, description: str):
        """إنشاء وثيقة المشروع"""
        content = f"""# {name}

## معلومات المشروع

| الحقل | القيمة |
|-------|--------|
| **الاسم** | {name} |
| **الوصف** | {description or "بدون وصف"} |
| **تاريخ الإنشاء** | {datetime.now().strftime('%Y-%m-%d')} |
| **الحالة** | نشط |

---

## المهام

- [ ] المهمة الأولى

---

## ملاحظات

*ابدأ بإضافة ملاحظاتك هنا*
"""
        doc_file = self.docs_dir / f"{name}.md"
        doc_file.write_text(content, encoding="utf-8")

    def delete_project(self, name: str) -> Dict:
        """حذف مشروع"""
        if not docs_storage.project_exists(name):
            return {"success": False, "error": f"المشروع '{name}' غير موجود"}
        
        # Delete from storage
        docs_storage.delete_project(name)
        
        # Log event
        log_project_deleted(name)
        
        return {
            "success": True,
            "message": f"تم حذف المشروع '{name}' بنجاح"
        }

    def archive_project(self, name: str) -> Dict:
        """أرشفة مشروع"""
        if not docs_storage.project_exists(name):
            return {"success": False, "error": f"المشروع '{name}' غير موجود"}
        
        # Archive in storage
        success = docs_storage.archive_project(name)
        if not success:
            return {"success": False, "error": "فشل في الأرشفة"}
        
        # Update project doc
        doc_file = self.docs_dir / f"{name}.md"
        if doc_file.exists():
            content = doc_file.read_text(encoding="utf-8")
            content = content.replace("**الحالة** | نشط", "**الحالة** | مؤرشف")
            doc_file.write_text(content, encoding="utf-8")
        
        # Log event
        log_project_archived(name)
        
        return {
            "success": True,
            "message": f"تم أرشفة المشروع '{name}' بنجاح"
        }

    def switch_project(self, name: str) -> Dict:
        """تبديل المشروع النشط"""
        if name and not docs_storage.project_exists(name):
            return {"success": False, "error": f"المشروع '{name}' غير موجود"}
        
        # Save active project
        if name:
            ACTIVE_PROJECT_FILE.write_text(name, encoding="utf-8")
        elif ACTIVE_PROJECT_FILE.exists():
            ACTIVE_PROJECT_FILE.unlink()
        
        return {
            "success": True,
            "active_project": name,
            "message": f"تم التبديل إلى '{name or 'بدون مشروع'}'"
        }

    def get_active_project(self) -> Optional[str]:
        """الحصول على المشروع النشط"""
        if ACTIVE_PROJECT_FILE.exists():
            return ACTIVE_PROJECT_FILE.read_text().strip()
        return None

    def list_projects(self, status: Optional[str] = None) -> List[Dict]:
        """قائمة المشاريع"""
        projects = docs_storage.list_projects()
        
        if status:
            projects = [p for p in projects if p.status == status]
        
        active = self.get_active_project()
        
        return [
            {
                **p.to_dict(),
                "is_active": p.name == active
            }
            for p in projects
        ]

    def get_project_status(self, name: str) -> Optional[Dict]:
        """حالة مشروع"""
        project = docs_storage.get_project(name)
        if not project:
            return None
        
        active = self.get_active_project()
        
        return {
            **project.to_dict(),
            "is_active": project.name == active,
            "directory": str(self.projects_dir / name),
            "doc_file": str(self.docs_dir / f"{name}.md"),
        }

    def _update_progress(self, project_name: str, action: str):
        """تحديث ملف التقدم"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        entry = f"\n| project-{project_name} | {action} | {timestamp} | ✅ {action} | {project_name} |"
        
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
                f.write(entry)


# ============================================================
# Global Instance
# ============================================================

project_manager = ProjectManager()


# ============================================================
# Convenience Functions
# ============================================================

def create_project(name: str, description: str = "") -> Dict:
    return project_manager.create_project(name, description)


def delete_project(name: str) -> Dict:
    return project_manager.delete_project(name)


def archive_project(name: str) -> Dict:
    return project_manager.archive_project(name)


def switch_project(name: str) -> Dict:
    return project_manager.switch_project(name)


def get_active_project() -> Optional[str]:
    return project_manager.get_active_project()


def list_projects(status: Optional[str] = None) -> List[Dict]:
    return project_manager.list_projects(status)


def get_project_status(name: str) -> Optional[Dict]:
    return project_manager.get_project_status(name)
