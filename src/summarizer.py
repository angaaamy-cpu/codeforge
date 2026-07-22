"""
CodeForge Weekly Summarizer - Phase 6A
=====================================
إنشاء ملخصات أسبوعية
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from src.storage import docs_storage
from src.logger import logger
from src.project_manager import project_manager, list_projects


class WeeklySummarizer:
    """مولد الملخصات الأسبوعية"""

    def __init__(self):
        self.report_dir = Path("docs/reports")
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def get_week_range(self) -> tuple:
        """الحصول على نطاق الأسبوع"""
        today = datetime.now()
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=6)  # Sunday
        return start, end

    def get_tasks_summary(self) -> Dict:
        """ملخص المهام"""
        reports = docs_storage.list_reports()
        tasks = {
            "total": len(reports),
            "completed": 0,
            "failed": 0,
            "in_progress": 0,
            "list": []
        }
        
        start, end = self.get_week_range()
        
        for report in reports:
            # Simple date check (approximate)
            if report.created_at:
                created = report.created_at
                if isinstance(created, str):
                    try:
                        created = datetime.fromisoformat(created)
                    except:
                        continue
                
                # Include all tasks for now
                tasks["list"].append({
                    "id": report.task_id,
                    "description": report.description,
                    "status": report.status,
                })
                
                if report.status in ("مكتمل", "completed", "✅"):
                    tasks["completed"] += 1
                elif report.status in ("فشل", "failed", "❌"):
                    tasks["failed"] += 1
                else:
                    tasks["in_progress"] += 1
        
        return tasks

    def get_projects_summary(self) -> Dict:
        """ملخص المشاريع"""
        projects = list_projects()
        
        return {
            "total": len(projects),
            "active": len([p for p in projects if p.get("status") == "active"]),
            "archived": len([p for p in projects if p.get("status") == "archived"]),
            "projects": projects,
        }

    def get_errors_summary(self) -> Dict:
        """ملخص الأخطاء"""
        errors = logger.get_errors(100)
        
        return {
            "total": len(errors),
            "recent": errors[-10:] if errors else [],
        }

    def get_agents_summary(self) -> Dict:
        """ملخص نشاط الوكلاء"""
        stats = logger.get_stats()
        
        return {
            "agents": stats.get("agents", {}),
            "total_events": stats.get("events_count", 0),
        }

    def get_adrs_summary(self) -> Dict:
        """ملخص القرارات المعمارية"""
        adrs = docs_storage.list_adrs()
        
        return {
            "total": len(adrs),
            "recent": [a.to_dict() for a in adrs[-5:]] if adrs else [],
        }

    def get_weekly_file(self) -> Path:
        """الحصول على مسار ملف الأسبوع"""
        today = datetime.now()
        year, week = today.isocalendar()[:2]
        filename = f"weekly-summary-{year}-W{week:02d}.md"
        return self.report_dir / filename

    def generate_summary(self) -> str:
        """إنشاء الملخص الأسبوعي"""
        start, end = self.get_week_range()
        
        # Gather data
        tasks = self.get_tasks_summary()
        projects = self.get_projects_summary()
        errors = self.get_errors_summary()
        agents = self.get_agents_summary()
        adrs = self.get_adrs_summary()
        
        # Build report
        report = f"""# الملخص الأسبوعي - CodeForge
========================

## معلومات الأسبوع

| الحقل | القيمة |
|-------|--------|
| **من** | {start.strftime('%Y-%m-%d')} |
| **إلى** | {end.strftime('%Y-%m-%d')} |
| **تاريخ الإنشاء** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |

---

## 📊 ملخص عام

| المقياس | القيمة |
|---------|--------|
| المشاريع النشطة | {projects['active']} |
| إجمالي المهام | {tasks['total']} |
| المهام المكتملة | {tasks['completed']} |
| المهام الفاشلة | {tasks['failed']} |
| الأخطاء | {errors['total']} |
| ADRs | {adrs['total']} |

---

## 📂 المشاريع

"""
        
        if projects["projects"]:
            for p in projects["projects"]:
                status_icon = "🟢" if p.get("status") == "active" else "🟡"
                report += f"- {status_icon} **{p['name']}** - {p.get('status', 'unknown')}\n"
                if p.get("description"):
                    report += f"  - {p['description']}\n"
        else:
            report += "_لا توجد مشاريع_\n"
        
        report += "\n## 📝 المهام\n\n"
        
        if tasks["list"]:
            for task in tasks["list"][-10:]:  # Last 10
                status_icon = {
                    "مكتمل": "✅",
                    "completed": "✅",
                    "فشل": "❌",
                    "failed": "❌",
                }.get(task["status"], "📋")
                report += f"- {status_icon} **{task['id']}**: {task['description'][:50]}\n"
        else:
            report += "_لا توجد مهام_\n"
        
        report += "\n## 🤖 نشاط الوكلاء\n\n"
        
        if agents["agents"]:
            for agent, stats in agents["agents"].items():
                report += f"- **{agent}**: {stats['total']} عملية"
                if stats.get("errors", 0) > 0:
                    report += f" ({stats['errors']} خطأ)"
                report += "\n"
        else:
            report += "_لا توجد بيانات_\n"
        
        report += "\n## ⚠️ الأخطاء\n\n"
        
        if errors["recent"]:
            for error in errors["recent"]:
                report += f"- `{error[:100]}`\n"
        else:
            report += "✅ لا توجد أخطاء مسجلة\n"
        
        report += "\n## 📋 القرارات المعمارية\n\n"
        
        if adrs["recent"]:
            for adr in adrs["recent"]:
                report += f"- **ADR-{adr['number']:03d}**: {adr['title']}\n"
        else:
            report += "_لا توجد قرارات_\n"
        
        report += "\n## 💡 التوصيات\n\n"
        
        # Generate recommendations
        recommendations = []
        
        if tasks["failed"] > tasks["completed"] * 0.3:
            recommendations.append("⚠️ نسبة الفشل مرتفعة - راجع أسباب فشل المهام")
        
        if errors["total"] > 20:
            recommendations.append("⚠️ عدد الأخطاء مرتفع - فكر في مراجعة الاستقرار")
        
        if projects["active"] > 5:
            recommendations.append("💡 فكر في أرشفة المشاريع غير النشطة")
        
        if not recommendations:
            recommendations.append("✅ كل شيء يسير بشكل جيد!")
        
        for rec in recommendations:
            report += f"- {rec}\n"
        
        report += f"""

---

_هذا الملخص مُنشأ تلقائياً بواسطة CodeForge - {datetime.now().strftime('%Y-%m-%d %H:%M')}_
"""
        
        return report

    def save_summary(self) -> str:
        """حفظ الملخص"""
        report = self.generate_summary()
        filepath = self.get_weekly_file()
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        
        # Also update latest summary
        latest_path = self.report_dir / "weekly-summary-latest.md"
        with open(latest_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        return str(filepath)

    def get_latest_summary(self) -> Optional[str]:
        """الحصول على آخر ملخص"""
        latest_path = self.report_dir / "weekly-summary-latest.md"
        if latest_path.exists():
            return latest_path.read_text(encoding="utf-8")
        return None


# ============================================================
# Global Instance
# ============================================================

summarizer = WeeklySummarizer()


# ============================================================
# Convenience Functions
# ============================================================

def generate_weekly_summary() -> str:
    """إنشاء وحفظ الملخص الأسبوعي"""
    return summarizer.save_summary()


def get_latest_summary() -> Optional[str]:
    """الحصول على آخر ملخص"""
    return summarizer.get_latest_summary()
