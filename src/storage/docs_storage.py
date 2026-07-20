"""
CodeForge Docs Storage - Production Ready
=========================================
تخزين يعتمد على ملفات Markdown
Uses PathService for centralized path management
"""

import os
import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.storage.storage import BaseStorage, Project, ADR, TaskReport
from src.path_service import path_service


class DocsStorage(BaseStorage):
    """تخزين يستخدم ملفات Markdown"""

    def __init__(self, docs_dir: str = None, projects_dir: str = None):
        # Use PathService for centralized paths
        self.docs_dir = path_service.docs_dir if docs_dir is None else Path(docs_dir)
        self.projects_dir = path_service.projects_dir if projects_dir is None else Path(projects_dir)
        self.adr_dir = self.docs_dir / "adr"
        self.reports_dir = self.docs_dir / "reports"
        self.projects_docs_dir = self.docs_dir / "projects"
        self.projects_index = self.projects_dir / ".projects.json"

    def _ensure_dirs(self):
        """التأكد من وجود المجلدات"""
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.projects_docs_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # BaseStorage Implementation
    # ============================================================

    def save(self, key: str, data: Any) -> bool:
        """حفظ بيانات - غير مستخدم في تخزين Markdown"""
        return False

    def load(self, key: str) -> Optional[Any]:
        """تحميل بيانات - غير مستخدم في تخزين Markdown"""
        return None

    def delete(self, key: str) -> bool:
        """حذف بيانات - غير مستخدم في تخزين Markdown"""
        return False

    def exists(self, key: str) -> bool:
        """فحص وجود"""
        if key.startswith("project:"):
            return self.project_exists(key.replace("project:", ""))
        elif key.startswith("adr:"):
            return self.adr_exists(int(key.replace("adr:", "")))
        elif key.startswith("report:"):
            return self.report_exists(key.replace("report:", ""))
        return False

    def list_keys(self, prefix: str = "") -> List[str]:
        """قائمة المفاتيح"""
        keys = []
        
        if prefix in ("", "project"):
            projects = self.list_projects()
            keys.extend([f"project:{p.name}" for p in projects])
        
        if prefix in ("", "adr"):
            adrs = self.list_adrs()
            keys.extend([f"adr:{a.number}" for a in adrs])
        
        return keys

    def search(self, query: str) -> List[Dict]:
        """بحث نصي"""
        results = []
        query_lower = query.lower()

        # Search in ADRs
        for adr in self.list_adrs():
            if query_lower in adr.title.lower() or query_lower in adr.content.lower():
                results.append({
                    "type": "adr",
                    "id": f"ADR-{adr.number:03d}",
                    "title": adr.title,
                    "content": adr.content[:200],
                    "score": self._calculate_score(query, adr.title, adr.content),
                })

        # Search in project docs
        for doc_file in self.projects_docs_dir.glob("*.md"):
            content = doc_file.read_text(encoding="utf-8")
            if query_lower in content.lower():
                results.append({
                    "type": "project_doc",
                    "id": doc_file.stem,
                    "title": doc_file.stem.replace("-", " ").title(),
                    "content": content[:200],
                    "score": self._calculate_score(query, "", content),
                })

        # Search in reports
        for report_file in self.reports_dir.glob("task-*.md"):
            content = report_file.read_text(encoding="utf-8")
            if query_lower in content.lower():
                results.append({
                    "type": "report",
                    "id": report_file.stem,
                    "title": report_file.stem,
                    "content": content[:200],
                    "score": self._calculate_score(query, "", content),
                })

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:10]

    def get_metadata(self, key: str) -> Dict:
        """الحصول على metadata"""
        return {}

    # ============================================================
    # Project Operations
    # ============================================================

    def list_projects(self) -> List[Project]:
        """قائمة المشاريع"""
        if not self.projects_index.exists():
            return []
        
        try:
            data = json.loads(self.projects_index.read_text(encoding="utf-8"))
            return [Project.from_dict(p) for p in data.get("projects", [])]
        except (json.JSONDecodeError, KeyError):
            return []

    def project_exists(self, name: str) -> bool:
        """فحص وجود مشروع"""
        projects = self.list_projects()
        return any(p.name == name for p in projects)

    def get_project(self, name: str) -> Optional[Project]:
        """الحصول على مشروع"""
        projects = self.list_projects()
        for p in projects:
            if p.name == name:
                return p
        return None

    def save_project(self, project: Project) -> bool:
        """حفظ مشروع"""
        self._ensure_dirs()
        projects = self.list_projects()
        
        # Update or add
        for i, p in enumerate(projects):
            if p.name == project.name:
                projects[i] = project
                break
        else:
            projects.append(project)
        
        data = {"projects": [p.to_dict() for p in projects]}
        self.projects_index.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True

    def delete_project(self, name: str) -> bool:
        """حذف مشروع"""
        projects = self.list_projects()
        projects = [p for p in projects if p.name != name]
        data = {"projects": [p.to_dict() for p in projects]}
        self.projects_index.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # Delete project directory
        project_dir = self.projects_dir / name
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
        
        # Delete project doc
        doc_file = self.projects_docs_dir / f"{name}.md"
        if doc_file.exists():
            doc_file.unlink()
        
        return True

    def archive_project(self, name: str) -> bool:
        """أرشفة مشروع"""
        project = self.get_project(name)
        if not project:
            return False
        
        project.status = "archived"
        project.updated_at = datetime.now()
        self.save_project(project)
        
        # Move to archive directory
        project_dir = self.projects_dir / name
        archive_dir = self.projects_dir / "archive" / name
        if project_dir.exists():
            import shutil
            shutil.move(str(project_dir), str(archive_dir))
        
        return True

    # ============================================================
    # ADR Operations
    # ============================================================

    def list_adrs(self) -> List[ADR]:
        """قائمة القرارات المعمارية

        Phase 7 (Organizational Memory - narrow scope): كانت هذه الدالة
        تبحث عن ملفات بنمط "ADR-*.md" فقط، بينما كل ملف ADR حقيقي في
        المستودع (001 حتى 013) مُسمّى "NNN-slug.md" بلا بادئة "ADR-"
        إطلاقاً. النتيجة: هذه الدالة (ومعها /api/adrs) كانت تُرجع قائمة
        فارغة دائماً رغم وجود 13 قراراً معمارياً فعلياً - مُتحقَّق مباشرة
        قبل هذا الإصلاح. النمط أدناه يقبل الشكلين معاً (المُستخدَم فعلياً
        NNN-slug.md، وADR-NNN-slug.md احتياطاً لأي ملف مستقبلي بذلك الاسم).
        """
        adrs = []

        if not self.adr_dir.exists():
            return adrs

        seen_files = set()
        patterns = ["[0-9][0-9][0-9]-*.md", "ADR-*.md"]

        for pattern in patterns:
            for adr_file in sorted(self.adr_dir.glob(pattern)):
                if adr_file in seen_files:
                    continue
                seen_files.add(adr_file)
                try:
                    content = adr_file.read_text(encoding="utf-8")

                    number_match = re.search(r"(?:ADR-)?(\d+)", adr_file.name)
                    if not number_match:
                        continue
                    number = int(number_match.group(1))

                    # العنوان: أول سطر H1 في الملف - يعمل مع "# ADR-013: ..."
                    # وأيضاً مع "# اسم الملف بلا بادئة ADR" (النمط الفعلي المُستخدَم)
                    title_match = re.search(r"^#\s+(?:ADR-\d+:\s*)?(.+)$", content, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else adr_file.stem

                    status_match = re.search(r"\*\*(?:الحالة|Status)\*\*[:\s]*\**([^\n*]+)\**", content)
                    status = status_match.group(1).strip() if status_match else "unknown"

                    adrs.append(ADR(
                        number=number,
                        title=title,
                        status=status,
                        agent="unknown",
                        content=content[:500],
                    ))
                except (ValueError, AttributeError, OSError):
                    continue

        return sorted(adrs, key=lambda a: a.number)

    def adr_exists(self, number: int) -> bool:
        """فحص وجود ADR - يقبل NNN-slug.md (الفعلي) وADR-NNN-slug.md (احتياطاً)"""
        return bool(
            list(self.adr_dir.glob(f"{number:03d}-*.md"))
            or list(self.adr_dir.glob(f"ADR-{number:03d}-*.md"))
        )

    # ============================================================
    # Report Operations
    # ============================================================

    def list_reports(self) -> List[TaskReport]:
        """قائمة التقارير"""
        reports = []
        
        if not self.reports_dir.exists():
            return reports
        
        for report_file in sorted(self.reports_dir.glob("task-*.md")):
            try:
                content = report_file.read_text(encoding="utf-8")
                
                # Extract task_id
                task_id = report_file.stem
                
                # Extract description
                desc_match = re.search(r"\*\*الوصف\*\*.*?\|\s*(.+)", content)
                description = desc_match.group(1).strip() if desc_match else ""
                
                # Extract status
                status_match = re.search(r"\*\*الحالة\*\*.*?([✅❌⏳🔴📋])\s*(\w+)", content)
                status = status_match.group(2) if status_match else "unknown"
                
                reports.append(TaskReport(
                    task_id=task_id,
                    description=description,
                    status=status,
                ))
            except (ValueError, AttributeError):
                continue
        
        return reports

    def report_exists(self, task_id: str) -> bool:
        """فحص وجود تقرير"""
        return (self.reports_dir / f"{task_id}.md").exists()

    def get_report(self, task_id: str) -> Optional[str]:
        """الحصول على محتوى تقرير"""
        report_file = self.reports_dir / f"{task_id}.md"
        if report_file.exists():
            return report_file.read_text(encoding="utf-8")
        return None

    # ============================================================
    # Helper Methods
    # ============================================================

    def _calculate_score(self, query: str, title: str, content: str) -> float:
        """حساب درجة المطابقة"""
        score = 0
        query_lower = query.lower()
        
        if query_lower in title.lower():
            score += 10
        if query_lower in content.lower():
            score += 1
        
        return score


# Global instance
docs_storage = DocsStorage()
