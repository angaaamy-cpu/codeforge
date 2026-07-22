"""
CodeForge Advanced Logger - Phase 6A
====================================
نظام تسجيل متقدم: events, errors, agents
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import threading


class CodeForgeLogger:
    """نظام تسجيل متقدم"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
        # Log files
        self.events_file = self.log_dir / "events.log"
        self.errors_file = self.log_dir / "errors.log"
        self.agent_log_file = self.log_dir / "agent.log"
        
        # Initialize files
        self._init_files()

    def _init_files(self):
        """تهيئة ملفات السجل"""
        for f in [self.events_file, self.errors_file, self.agent_log_file]:
            if not f.exists():
                f.write_text("", encoding="utf-8")

    def _format_line(self, level: str, agent: str, action: str, details: str = "", 
                     project: Optional[str] = None) -> str:
        """تنسيق سطر السجل"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parts = [timestamp, level, agent, action]
        if project:
            parts.insert(3, f"[{project}]")
        if details:
            parts.append(details)
        return " | ".join(parts)

    def log_event(self, agent: str, action: str, details: str = "",
                  project: Optional[str] = None, level: str = "INFO") -> bool:
        """تسجيل حدث في events.log"""
        line = self._format_line(level, agent, action, details, project)
        
        with self._lock:
            try:
                with open(self.events_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                return True
            except Exception:
                return False

    def log_error(self, agent: str, error: str, details: str = "",
                  project: Optional[str] = None) -> bool:
        """تسجيل خطأ في errors.log"""
        line = self._format_line("ERROR", agent, error, details, project)
        
        with self._lock:
            try:
                with open(self.errors_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                # Also log to events
                self.log_event(agent, f"ERROR: {error}", details, project, "ERROR")
                return True
            except Exception:
                return False

    def log_agent(self, agent: str, action: str, details: str = "",
                  task_id: Optional[str] = None) -> bool:
        """تسجيل نشاط وكيل في agent.log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_info = f"[{task_id}]" if task_id else "[no-task]"
        line = f"{timestamp} | {agent} | {task_info} | {action} | {details}"
        
        with self._lock:
            try:
                with open(self.agent_log_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                return True
            except Exception:
                return False

    # Convenience methods
    def info(self, agent: str, action: str, details: str = "", project: Optional[str] = None):
        """معلومات عادية"""
        return self.log_event(agent, action, details, project, "INFO")

    def warning(self, agent: str, action: str, details: str = "", project: Optional[str] = None):
        """تحذير"""
        return self.log_event(agent, action, details, project, "WARNING")

    def debug(self, agent: str, action: str, details: str = "", project: Optional[str] = None):
        """تصحيح"""
        return self.log_event(agent, action, details, project, "DEBUG")

    def error(self, agent: str, error: str, details: str = "", project: Optional[str] = None):
        """خطأ"""
        return self.log_error(agent, error, details, project)

    def agent_start(self, agent: str, task: str, task_id: Optional[str] = None):
        """وكيل بدأ مهمة"""
        return self.log_agent(agent, "START", task, task_id)

    def agent_end(self, agent: str, status: str, task_id: Optional[str] = None):
        """وكيل انتهى مهمة"""
        return self.log_agent(agent, "END", status, task_id)

    def agent_error(self, agent: str, error: str, task_id: Optional[str] = None):
        """خطأ وكيل"""
        self.log_agent(agent, "ERROR", error, task_id)
        return self.log_error(agent, error, task_id=task_id)

    # Reading methods
    def get_events(self, limit: int = 100) -> list:
        """قراءة الأحداث"""
        if not self.events_file.exists():
            return []
        
        try:
            with open(self.events_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return [l.strip() for l in lines[-limit:] if l.strip()]
        except Exception:
            return []

    def get_errors(self, limit: int = 50) -> list:
        """قراءة الأخطاء"""
        if not self.errors_file.exists():
            return []
        
        try:
            with open(self.errors_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return [l.strip() for l in lines[-limit:] if l.strip()]
        except Exception:
            return []

    def get_agent_logs(self, agent: Optional[str] = None, limit: int = 100) -> list:
        """قراءة سجل الوكيل"""
        if not self.agent_log_file.exists():
            return []
        
        try:
            with open(self.agent_log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            logs = [l.strip() for l in lines if l.strip()]
            
            if agent:
                logs = [l for l in logs if f"| {agent} |" in l]
            
            return logs[-limit:]
        except Exception:
            return []

    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات السجلات"""
        stats = {
            "events_count": 0,
            "errors_count": 0,
            "agents": {},
            "last_event": None,
            "last_error": None,
        }
        
        # Count events
        if self.events_file.exists():
            with open(self.events_file, "r", encoding="utf-8") as f:
                stats["events_count"] = len(f.readlines())
            # Last event
            with open(self.events_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    stats["last_event"] = lines[-1].strip()
        
        # Count errors
        if self.errors_file.exists():
            with open(self.errors_file, "r", encoding="utf-8") as f:
                stats["errors_count"] = len(f.readlines())
            # Last error
            with open(self.errors_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    stats["last_error"] = lines[-1].strip()
        
        # Agent stats
        if self.agent_log_file.exists():
            with open(self.agent_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if " | " in line:
                        parts = line.strip().split(" | ")
                        if len(parts) >= 2:
                            agent = parts[1].strip()
                            if agent not in stats["agents"]:
                                stats["agents"][agent] = {"total": 0, "errors": 0}
                            stats["agents"][agent]["total"] += 1
                            if "ERROR" in line or "ERROR" in parts[2] if len(parts) > 2 else False:
                                stats["agents"][agent]["errors"] += 1
        
        return stats

    def clear_old_logs(self, days: int = 30) -> Dict[str, int]:
        """حذف السجلات القديمة"""
        deleted = {"events": 0, "errors": 0, "agent": 0}
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for file_key, file_path in [
            ("events", self.events_file),
            ("errors", self.errors_file),
            ("agent", self.agent_log_file)
        ]:
            if not file_path.exists():
                continue
            
            kept = []
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(" ", 1)
                        if len(parts) >= 1:
                            try:
                                ts = datetime.strptime(parts[0], "%Y-%m-%d")
                                if ts.timestamp() >= cutoff:
                                    kept.append(line)
                                else:
                                    deleted[file_key] += 1
                            except ValueError:
                                kept.append(line)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(kept)
            except Exception:
                pass
        
        return deleted


# ============================================================
# Global Instance
# ============================================================

from config import EVENTS_LOG

_log_dir = str(Path(EVENTS_LOG).parent) if EVENTS_LOG else "logs"
logger = CodeForgeLogger(_log_dir)


# ============================================================
# Convenience Functions
# ============================================================

def log_event(agent: str, action: str, details: str = "", project: Optional[str] = None):
    """تسجيل حدث"""
    return logger.log_event(agent, action, details, project)


def log_error(agent: str, error: str, details: str = "", project: Optional[str] = None):
    """تسجيل خطأ"""
    return logger.log_error(agent, error, details, project)


def log_agent(agent: str, action: str, details: str = "", task_id: Optional[str] = None):
    """تسجيل نشاط وكيل"""
    return logger.log_agent(agent, action, details, task_id)


def info(agent: str, action: str, details: str = "", project: Optional[str] = None):
    return logger.info(agent, action, details, project)


def warning(agent: str, action: str, details: str = "", project: Optional[str] = None):
    return logger.warning(agent, action, details, project)


def error(agent: str, error: str, details: str = "", project: Optional[str] = None):
    return logger.error(agent, error, details, project)


def get_logger_stats() -> Dict[str, Any]:
    """إحصائيات السجلات"""
    return logger.get_stats()
