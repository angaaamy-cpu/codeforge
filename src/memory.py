"""
CodeForge Smart Memory System - Phase 3
======================================
نظام الذاكرة الذكي
"""

import os
import re
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from src.state import get_task_id, record_agent_decision


class SmartMemory:
    """نظام الذاكرة الذكي"""

    # الملفات المرتبطة بكل نوع من المهام
    TASK_FILE_MAPPING = {
        "html": ["workspace/index.html", "workspace/*.html"],
        "css": ["workspace/*.css", "workspace/*.html"],
        "python": ["src/*.py", "tests/*.py"],
        "docs": ["docs/*.md", "docs/adr/*.md"],
        "agent": ["src/agents.py", "src/state.py", "src/memory.py"],
        "git": ["docs/progress.md", "src/git_manager.py"],
        "test": ["tests/*.py", "src/*.py"],
        "architecture": ["docs/architecture.md", "docs/adr/*.md"],
        "landing": ["workspace/index.html", "docs/progress.md"],
    }

    def __init__(self, docs_dir: str = "docs", workspace_dir: str = "workspace"):
        self.docs_dir = Path(docs_dir)
        self.workspace_dir = Path(workspace_dir)
        self.adr_dir = self.docs_dir / "adr"

    def _get_relevant_files(self, task_description: str) -> List[str]:
        """تحديد الملفات المرتبطة بالمهمة فقط"""
        relevant = []
        description_lower = task_description.lower()

        # تحديد نوع المهمة
        task_types = []
        if "html" in description_lower or "صفحة" in description_lower or "landing" in description_lower:
            task_types.extend(["html", "landing"])
        if "css" in description_lower or "تصميم" in description_lower or "style" in description_lower:
            task_types.append("css")
        if "python" in description_lower or "كود" in description_lower or "src" in description_lower:
            task_types.append("python")
        if "test" in description_lower or "اختبار" in description_lower:
            task_types.append("test")
        if "agent" in description_lower or "وكيل" in description_lower:
            task_types.append("agent")
        if "git" in description_lower or "commit" in description_lower:
            task_types.append("git")
        if "architecture" in description_lower or "معماري" in description_lower or "design" in description_lower:
            task_types.append("architecture")
        if "docs" in description_lower or "توثيق" in description_lower:
            task_types.append("docs")

        # إذا لم نحدد نوع، نقرأ فقط progress.md
        if not task_types:
            relevant.append("docs/progress.md")
            return relevant

        # جمع الملفات
        for task_type in set(task_types):
            if task_type in self.TASK_FILE_MAPPING:
                for pattern in self.TASK_FILE_MAPPING[task_type]:
                    if "/" in pattern:
                        base = pattern.split("/")[0]
                        full_pattern = self.docs_dir if base == "docs" else self.workspace_dir
                        if "*" in pattern:
                            import glob
                            glob_pattern = str(self.docs_dir / pattern.replace("docs/", "")) if base == "docs" else str(self.workspace_dir / pattern.replace("workspace/", ""))
                            matches = glob.glob(glob_pattern)
                            relevant.extend([str(Path(m).relative_to(".")) for m in matches if os.path.exists(m)])
                        else:
                            full_path = self.docs_dir / pattern.split("/")[1] if base == "docs" else self.workspace_dir / pattern.split("/")[1]
                            if full_path.exists():
                                relevant.append(str(full_path.relative_to(".")))

        # دائماً أضف progress.md
        progress_path = self.docs_dir / "progress.md"
        if progress_path.exists() and str(progress_path.relative_to(".")) not in relevant:
            relevant.append(str(progress_path.relative_to(".")))

        return list(set(relevant))

    def read_context(self, task_description: str) -> Dict[str, str]:
        """
        يقرأ الملفات المرتبطة بالمهمة فقط
        
        Args:
            task_description: وصف المهمة
            
        Returns:
            dictionary من {file_path: content}
        """
        relevant_files = self._get_relevant_files(task_description)
        context = {}

        for file_path in relevant_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    context[file_path] = f.read()
            except FileNotFoundError:
                pass  # تجاهل الملفات غير الموجودة

        return context

    def _get_next_adr_number(self) -> int:
        """الحصول على رقم ADR التالي"""
        if not self.adr_dir.exists():
            return 1
        
        adr_files = list(self.adr_dir.glob("ADR-*.md"))
        if not adr_files:
            return 1
        
        numbers = []
        for f in adr_files:
            match = re.search(r"ADR-(\d+)", f.name)
            if match:
                numbers.append(int(match.group(1)))
        
        return max(numbers) + 1 if numbers else 1

    def record_decision(self, agent: str, content: str, impact: str) -> str:
        """
        تسجيل قرار
        
        Args:
            agent: اسم الوكيل
            content: محتوى القرار
            impact: "architectural" أو "operational"
            
        Returns:
            مسار الملف المسجل فيه
        """
        task_id = get_task_id() or "unknown"

        if impact == "architectural":
            # إنشاء ADR جديد
            adr_number = self._get_next_adr_number()
            filename = f"docs/adr/ADR-{adr_number:03d}-{agent.lower()}.md"
            
            adr_content = f"""# ADR-{adr_number:03d}: قرار معماري - {agent}

## الحالة
**مقبول** - {datetime.now().strftime('%Y-%m-%d')}

---

## القرار

**الوكيل**: {agent}
**المهمة**: {task_id}

{content}

---

## السبب

[يُضاف لاحقاً]

---

## النتائج

### إيجابية
- 

### سلبية
- 

---

## ملاحظات

- تاريخ التسجيل: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- هذا ADR يُنسخ من نظام الذاكرة التلقائي
"""
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(adr_content)
            
            # تسجيل في state
            record_agent_decision(agent, content, impact)
            return filename

        elif impact == "operational":
            # تسجيل في progress.md
            progress_file = self.docs_dir / "progress.md"
            if progress_file.exists():
                with open(progress_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n### قرار تشغيلي - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"**الوكيل**: {agent}\n")
                    f.write(f"**المهمة**: {task_id}\n")
                    f.write(f"**القرار**: {content}\n")
            
            # تسجيل في state
            record_agent_decision(agent, content, impact)
            return "docs/progress.md"

        else:
            raise ValueError(f"Unknown impact type: {impact}. Use 'architectural' or 'operational'")

    def update_progress(self, task: str, status: str, notes: str = ""):
        """
        تحديث ملف التقدم
        
        Args:
            task: اسم المهمة
            status: الحالة (منجزة، جارية، فاشل)
            notes: ملاحظات إضافية
        """
        progress_file = self.docs_dir / "progress.md"
        task_id = get_task_id() or "N/A"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        status_icon = {
            "منجزة": "✅",
            "جارية": "🔄",
            "فاشل": "❌",
            "معلق": "⏸️"
        }.get(status, "📋")

        entry = f"\n| {task_id} | {task} | {timestamp} | {status_icon} {status} | {notes} |"
        
        with open(progress_file, "a", encoding="utf-8") as f:
            f.write(entry)


# ============================================================
# Instance Global
# ============================================================

memory = SmartMemory()


# ============================================================
# Helper Functions
# ============================================================

def read_context(task_description: str) -> Dict[str, str]:
    """قراءة السياق المرتبط بمهمة"""
    return memory.read_context(task_description)


def record_decision(agent: str, content: str, impact: str) -> str:
    """تسجيل قرار (معماري أو تشغيلي)"""
    return memory.record_decision(agent, content, impact)


def update_progress(task: str, status: str, notes: str = ""):
    """تحديث التقدم"""
    memory.update_progress(task, status, notes)
