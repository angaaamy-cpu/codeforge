"""
CodeForge Core - Phase 5 (Capability System, files/git scope only)
====================================================================
Adapter يربط أدوات (Tools) حقيقية بالقدرات المُسجَّلة أصلاً (ميتاداتا
فقط) في capability.py - بدون إنشاء نظام قدرات جديد (ADR-013: نمط
Adapter/Strangler، لا معمارية موازية).

النطاق: `files` و`git` فقط - كلاهما مبنيان فوق كود إنتاجي موجود فعلاً
ومُقيَّد أصلاً بضوابط أمان (PathService sandbox, GIT_AUTO_PUSH=False).

**عمداً لا يوجد شيء هنا لـ "terminal" أو "http" أو "browser"** - انظر
docs/security/TERMINAL_CAPABILITY_SECURITY_REVIEW.md. أي محاولة مستقبلية
لربط tools حقيقية لقدرة "terminal" يجب أن تمر أولاً بتلك المراجعة، لا أن
تُضاف هنا بصمت.
"""

from typing import List

from src.Core.capability import CapabilityRegistry
from src.path_service import path_service
from src import git_manager


def _wire_files_tools(registry: CapabilityRegistry) -> None:
    files_cap = registry.get("files")
    if files_cap is None:
        return  # capability غير مسجَّلة - لا شيء لربطه (لا نفترض، نتأكد)

    files_cap.add_tool(
        "read", "قراءة محتوى ملف نصي ضمن WORKSPACE_ROOT",
        lambda path, encoding="utf-8": path_service.read(path, encoding=encoding),
    )
    files_cap.add_tool(
        "write", "كتابة محتوى لملف ضمن WORKSPACE_ROOT",
        lambda path, content, encoding="utf-8": path_service.write(path, content, encoding=encoding),
    )
    files_cap.add_tool(
        "list", "سرد الملفات المطابقة لنمط ضمن مسار",
        lambda path=".", pattern="*": path_service.list(path, pattern=pattern),
    )
    files_cap.add_tool(
        "delete", "حذف ملف أو مجلد ضمن WORKSPACE_ROOT",
        lambda path: path_service.delete(path),
    )
    files_cap.add_tool(
        "exists", "فحص وجود مسار",
        lambda path: path_service.exists(path),
    )


def _wire_git_tools(registry: CapabilityRegistry) -> None:
    git_cap = registry.get("git")
    if git_cap is None:
        return

    git_cap.add_tool(
        "status", "حالة git الحالية (نص git status)",
        lambda: git_manager.get_git_status(),
    )
    git_cap.add_tool(
        "changed_files", "قائمة الملفات المتغيّرة غير المُلتزَمة",
        lambda: git_manager.get_changed_files(),
    )
    git_cap.add_tool(
        "current_branch", "اسم الفرع الحالي",
        lambda: git_manager.get_current_branch(),
    )
    git_cap.add_tool(
        "auto_commit", "commit تلقائي محلي فقط (يحترم GIT_AUTO_COMMIT، لا push)",
        lambda message=None: git_manager.auto_commit(message),
    )
    # عمداً: لا "auto_push" هنا. GIT_AUTO_PUSH=False افتراضياً (config/settings.py)
    # وربط أداة push حقيقية يحتاج قراره الخاص لاحقاً، وليس ضمن هذا الـ Adapter.


_WIRED = False


def wire_production_tools() -> List[str]:
    """يُستدعى مرة واحدة عند استيراد src.Core. Idempotent."""
    global _WIRED
    registry = CapabilityRegistry()
    _wire_files_tools(registry)
    _wire_git_tools(registry)
    _WIRED = True
    return ["files", "git"]


wire_production_tools()
