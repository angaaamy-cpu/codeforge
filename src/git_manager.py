"""
CodeForge Git Manager - Phase 3
================================
إدارة Git - commit و push فقط
"""

import os
import subprocess
import re
from datetime import datetime
from typing import Optional, Tuple

from src.state import record_git_commit, get_task_id


class GitManager:
    """مدير Git"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.remote_url = self._get_remote_url()

    def _get_remote_url(self) -> Optional[str]:
        """الحصول على رابط المستودع البعيد"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _run_git(self, args: list, check: bool = True) -> subprocess.CompletedProcess:
        """تشغيل أمر git"""
        return subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

    def has_changes(self) -> bool:
        """فحص وجود تغييرات غير محفوظة"""
        result = self._run_git(["status", "--porcelain"])
        return bool(result.stdout.strip())

    def get_changed_files(self) -> list:
        """الحصول على قائمة الملفات المتغيرة"""
        result = self._run_git(["status", "--porcelain"])
        files = []
        for line in result.stdout.strip().split("\n"):
            if line:
                # format: XY filename
                status = line[:2]
                filename = line[3:]
                files.append({"status": status.strip(), "file": filename})
        return files

    def get_status(self) -> str:
        """الحصول على حالة git"""
        result = self._run_git(["status"])
        return result.stdout

    def get_branch(self) -> str:
        """الحصول على الفرع الحالي"""
        result = self._run_git(["branch", "--show-current"])
        return result.stdout.strip()

    def auto_commit(self, message: Optional[str] = None) -> Tuple[bool, str]:
        """
        تنفيذ git add + git commit
        
        Args:
            message: رسالة commit (إذا لم تُعطَ، تُنشأ تلقائياً)
            
        Returns:
            (نجاح, رسالة/خطأ)
        """
        # فحص التغييرات
        if not self.has_changes():
            return False, "لا توجد تغييرات للcommit"

        # الحصول على قائمة الملفات
        changed_files = self.get_changed_files()
        files_summary = ", ".join([f["file"] for f in changed_files[:5]])
        if len(changed_files) > 5:
            files_summary += f" (+{len(changed_files) - 5} ملفات أخرى)"

        # إنشاء رسالة commit إذا لم تُعطَ
        if not message:
            task_id = get_task_id() or "unknown"
            timestamp = datetime.now().strftime('%Y-%m-%d')
            message = f"[{task_id}] تحديث: {files_summary} ({timestamp})"

        # git add .
        add_result = self._run_git(["add", "."])
        if add_result.returncode != 0:
            return False, f"فشل git add: {add_result.stderr}"

        # git commit
        commit_result = self._run_git(["commit", "-m", message])
        if commit_result.returncode != 0:
            return False, f"فشل git commit: {commit_result.stderr}"

        # استخراج commit hash
        hash_result = self._run_git(["rev-parse", "--short", "HEAD"])
        commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"

        # تسجيل في state
        record_git_commit(message, commit_hash)

        return True, f"تم commit بنجاح: {commit_hash}\nالملفات: {files_summary}"

    def auto_push(self) -> Tuple[bool, str]:
        """
        تنفيذ git push
        
        ملاحظة: يُستدعى فقط بعد نجاح الاختبارات وموافقة Manager
        
        Returns:
            (نجاح, رسالة/خطأ)
        """
        if not self.remote_url:
            return False, "لا يوجد remote مُعد"

        # git push
        result = self._run_git(["push", "origin", "HEAD"])
        if result.returncode != 0:
            return False, f"فشل git push: {result.stderr}"

        return True, "تم push بنجاح"

    def get_last_commit(self) -> Optional[dict]:
        """الحصول على آخر commit"""
        result = self._run_git([
            "log", "-1", 
            "--format=%H|%s|%an|%ad", 
            "--date=iso"
        ])
        
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|")
            if len(parts) >= 4:
                return {
                    "hash": parts[0],
                    "message": parts[1],
                    "author": parts[2],
                    "date": parts[3]
                }
        return None

    def get_commit_history(self, limit: int = 10) -> list:
        """الحصول على تاريخ الـ commits"""
        result = self._run_git([
            "log", f"-{limit}",
            "--format=%H|%s|%ad",
            "--date=short"
        ])
        
        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|", 2)
                if len(parts) >= 3:
                    commits.append({
                        "hash": parts[0][:8],
                        "message": parts[1],
                        "date": parts[2]
                    })
        return commits


# ============================================================
# Instance Global
# ============================================================

git_manager = GitManager()


# ============================================================
# Helper Functions
# ============================================================

def auto_commit(message: Optional[str] = None) -> Tuple[bool, str]:
    """git add + git commit"""
    return git_manager.auto_commit(message)


def auto_push() -> Tuple[bool, str]:
    """git push (بعد نجاح الاختبارات فقط)"""
    return git_manager.auto_push()


def get_git_status() -> str:
    """الحصول على حالة git"""
    return git_manager.get_status()


def has_uncommitted_changes() -> bool:
    """هل توجد تغييرات غير محفوظة"""
    return git_manager.has_changes()


def get_changed_files() -> list:
    """قائمة الملفات المتغيرة"""
    return git_manager.get_changed_files()


def get_current_branch() -> str:
    """الفرع الحالي"""
    return git_manager.get_branch()
