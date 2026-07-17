"""
CodeForge Event Logger - Phase 5
================================
سجل الأحداث
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import threading


class EventLogger:
    """مسجل الأحداث"""

    def __init__(self, log_file: str = "logs/events.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def log(
        self,
        agent: str,
        action: str,
        details: str = "",
        project: Optional[str] = None,
        level: str = "INFO",
    ) -> bool:
        """
        تسجيل حدث
        
        Format: YYYY-MM-DD HH:MM Agent Action Details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        parts = [timestamp, agent, action]
        if project:
            parts.insert(2, f"[{project}]")
        if details:
            parts.append(details)
        
        line = " ".join(parts)
        
        with self._lock:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                return True
            except Exception:
                return False

    def get_recent(self, limit: int = 50) -> List[Dict]:
        """الحصول على آخر الأحداث"""
        events = []
        
        if not self.log_file.exists():
            return events
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in lines[-limit:]:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(" ", 3)
                if len(parts) >= 3:
                    event = {
                        "timestamp": parts[0] + " " + parts[1],
                        "agent": parts[2],
                        "action": parts[3] if len(parts) > 3 else "",
                    }
                    
                    # Extract project if present
                    if "[" in event["action"] and "]" in event["action"]:
                        import re
                        match = re.search(r"\[([^\]]+)\]", event["action"])
                        if match:
                            event["project"] = match.group(1)
                    
                    events.append(event)
        except Exception:
            pass
        
        return list(reversed(events))

    def get_by_agent(self, agent: str, limit: int = 20) -> List[Dict]:
        """الأحداث حسب الوكيل"""
        all_events = self.get_recent(limit * 5)
        return [e for e in all_events if e["agent"] == agent][:limit]

    def get_by_project(self, project: str, limit: int = 20) -> List[Dict]:
        """الأحداث حسب المشروع"""
        all_events = self.get_recent(limit * 5)
        return [e for e in all_events if e.get("project") == project][:limit]

    def clear_old(self, days: int = 30) -> int:
        """حذف الأحداث القديمة"""
        if not self.log_file.exists():
            return 0
        
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        kept = []
        deleted = 0
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(" ", 2)
                    if len(parts) >= 2:
                        try:
                            ts = datetime.strptime(parts[0] + " " + parts[1], "%Y-%m-%d %H:%M")
                            if ts.timestamp() >= cutoff:
                                kept.append(line)
                            else:
                                deleted += 1
                        except ValueError:
                            kept.append(line)
            
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.writelines(kept)
        except Exception:
            return 0
        
        return deleted


# ============================================================
# Global Instance
# ============================================================

from config import EVENTS_LOG

event_logger = EventLogger(EVENTS_LOG)


# ============================================================
# Convenience Functions
# ============================================================

def log_event(agent: str, action: str, details: str = "", project: Optional[str] = None):
    """تسجيل حدث"""
    return event_logger.log(agent, action, details, project)


def log_project_created(project: str):
    """تسجيل إنشاء مشروع"""
    return log_event("Manager", "Created", f"Project: {project}", project)


def log_project_archived(project: str):
    """تسجيل أرشفة مشروع"""
    return log_event("Manager", "Archived", f"Project: {project}", project)


def log_project_deleted(project: str):
    """تسجيل حذف مشروع"""
    return log_event("Manager", "Deleted", f"Project: {project}", project)


def log_task_started(task_id: str, project: str = ""):
    """تسجيل بدء مهمة"""
    return log_event("Manager", "Started", f"Task: {task_id}", project)


def log_task_completed(task_id: str, project: str = ""):
    """تسجيل اكتمال مهمة"""
    return log_event("Manager", "Completed", f"Task: {task_id}", project)


def log_adr_created(adr_number: int, title: str, project: str = ""):
    """تسجيل إنشاء ADR"""
    return log_event("Architect", "Created", f"ADR-{adr_number:03d}: {title}", project)


def log_file_modified(file: str, project: str = ""):
    """تسجيل تعديل ملف"""
    return log_event("Developer", "Modified", f"File: {file}", project)


def log_commit(message: str):
    """تسجيل commit"""
    return log_event("Git", "Commit", message)


def get_events(limit: int = 50) -> List[Dict]:
    """الحصول على الأحداث"""
    return event_logger.get_recent(limit)
