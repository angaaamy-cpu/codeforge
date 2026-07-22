"""
CodeForge Health Check - Phase 5
=================================
فحص صحة النظام
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import (
    APP_NAME, APP_VERSION, CURRENT_PHASE,
    PROJECTS_DIR, DOCS_DIR, SRC_DIR,
    EVENTS_LOG, STATE_FILE,
)
from src.state import get_state, state_manager
from src.project_manager import project_manager, list_projects
from src.storage import docs_storage


class HealthChecker:
    """فاحص الصحة"""

    def __init__(self):
        self.timestamp = datetime.now()

    def check_system(self) -> Dict:
        """فحص النظام الكامل"""
        return {
            "status": self._get_overall_status(),
            "timestamp": self.timestamp.isoformat(),
            "version": APP_VERSION,
            "phase": CURRENT_PHASE,
            "components": self._check_components(),
            "agents": self._check_agents(),
            "memory": self._check_memory(),
            "projects": self._check_projects(),
            "recent_error": self._get_last_error(),
            "last_successful_task": self._get_last_successful_task(),
        }

    def _get_overall_status(self) -> str:
        """الحصول على الحالة العامة"""
        state = get_state()
        
        if state.task_status.value in ("فاشل", "محظور"):
            return "warning"
        
        return "ok"

    def _check_components(self) -> Dict:
        """فحص المكونات"""
        components = {}
        
        # Directories
        components["directories"] = {
            "projects": PROJECTS_DIR.exists(),
            "docs": DOCS_DIR.exists(),
            "src": SRC_DIR.exists(),
            "logs": Path("logs").exists(),
        }
        
        # Files
        components["files"] = {
            "state": STATE_FILE.exists(),
            "events_log": EVENTS_LOG.exists(),
            "pyproject": Path("pyproject.toml").exists(),
        }
        
        # Python modules
        components["modules"] = {}
        required_modules = ["flask", "crewai", "litellm"]
        for module in required_modules:
            try:
                __import__(module)
                components["modules"][module] = "ok"
            except ImportError:
                components["modules"][module] = "missing"
        
        return components

    def _check_agents(self) -> Dict:
        """فحص الوكلاء"""
        state = get_state()
        
        agents = {}
        for agent_type in state.agent_states:
            agent = state.agent_states[agent_type]
            agents[agent_type] = {
                "status": agent.status,
                "attempts": agent.attempts,
                "last_active": agent.last_active.isoformat() if agent.last_active else None,
            }
        
        return {
            "active": state.active_agent.value if state.active_agent else None,
            "all_agents": agents,
        }

    def _check_memory(self) -> Dict:
        """فحص الذاكرة"""
        # Count ADRs
        adrs = docs_storage.list_adrs()
        
        # Count reports
        reports = docs_storage.list_reports()
        
        return {
            "adr_count": len(adrs),
            "report_count": len(reports),
            "storage_backend": "markdown",
        }

    def _check_projects(self) -> Dict:
        """فحص المشاريع"""
        projects = list_projects()
        
        active = project_manager.get_active_project()
        
        return {
            "total": len(projects),
            "active_count": len([p for p in projects if p.get("status") == "active"]),
            "archived_count": len([p for p in projects if p.get("status") == "archived"]),
            "current_active": active,
        }

    def _get_last_error(self) -> Optional[Dict]:
        """آخر خطأ"""
        events = docs_storage.list_reports()
        
        # Get failed tasks
        for report in reversed(events):
            if report.status in ("فشل", "failed", "❌"):
                return {
                    "task_id": report.task_id,
                    "description": report.description,
                }
        
        return None

    def _get_last_successful_task(self) -> Optional[Dict]:
        """آخر مهمة ناجحة"""
        reports = docs_storage.list_reports()
        
        for report in reversed(reports):
            if report.status in ("مكتمل", "completed", "✅"):
                return {
                    "task_id": report.task_id,
                    "description": report.description,
                }
        
        return None

    def to_json(self) -> Dict:
        """تصدير كـ JSON"""
        return self.check_system()

    def to_summary(self) -> str:
        """ملخص نصي"""
        health = self.check_system()
        
        lines = [
            f"╔══════════════════════════════════════╗",
            f"║     CodeForge Health Report      ║",
            f"╚══════════════════════════════════════╝",
            "",
            f"📊 الحالة: {health['status'].upper()}",
            f"📱 Version: {APP_VERSION} ({CURRENT_PHASE})",
            f"🕐 الوقت: {self.timestamp.strftime('%Y-%m-%d %H:%M')}",
            "",
            "📁 المكونات:",
        ]
        
        for comp_type, items in health["components"].items():
            ok_count = sum(1 for v in items.values() if v == "ok" or v is True)
            total = len(items)
            status = "✅" if ok_count == total else "⚠️"
            lines.append(f"   {status} {comp_type}: {ok_count}/{total}")
        
        lines.extend([
            "",
            "🤖 الوكلاء:",
            f"   النشط: {health['agents']['active'] or 'لا يوجد'}",
            "",
            "💾 الذاكرة:",
            f"   ADRs: {health['memory']['adr_count']}",
            f"   التقارير: {health['memory']['report_count']}",
            "",
            "📂 المشاريع:",
            f"   المجموع: {health['projects']['total']}",
            f"   النشط: {health['projects']['active_count']}",
            f"   الحالي: {health['projects']['current_active'] or 'لا يوجد'}",
            "",
        ])
        
        if health["last_error"]:
            lines.append(f"❌ آخر خطأ: {health['last_error']['task_id']}")
        else:
            lines.append("✅ لا توجد أخطاء")
        
        if health["last_successful_task"]:
            lines.append(f"✅ آخر نجاح: {health['last_successful_task']['task_id']}")
        
        return "\n".join(lines)


# ============================================================
# Global Instance
# ============================================================

health_checker = HealthChecker()


# ============================================================
# Convenience Functions
# ============================================================

def check_health() -> Dict:
    """فحص الصحة"""
    return health_checker.check_system()


def get_health_summary() -> str:
    """ملخص الصحة"""
    return health_checker.to_summary()
