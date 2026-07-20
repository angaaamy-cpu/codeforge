"""
CodeForge System Diagnostics - Agent OS
=====================================
فحص شامل لحالة المنصة
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DiagnosticResult:
    """نتيجة الفحص"""
    name: str
    status: str  # ok, warning, error
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }


class SystemDiagnostics:
    """
    System Diagnostics
    يختبر حالة المنصة بالكامل
    """
    
    def __init__(self):
        self.results: List[DiagnosticResult] = []
        self.path_service = None
    
    def _add_result(self, result: DiagnosticResult):
        """إضافة نتيجة"""
        self.results.append(result)
    
    # ========== Diagnostic Tests ==========
    
    def check_workspace_root(self) -> DiagnosticResult:
        """فحص Workspace Root"""
        try:
            from src.path_service import path_service
            
            root = path_service.root
            exists = root.exists()
            writable = os.access(root, os.W_OK)
            
            return DiagnosticResult(
                name="workspace_root",
                status="ok" if (exists and writable) else "error",
                message=f"Workspace root: {root}" if exists else f"Workspace root not found: {root}",
                details={
                    "path": str(root),
                    "exists": exists,
                    "writable": writable,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                name="workspace_root",
                status="error",
                message=f"Failed to check workspace: {str(e)}",
            )
    
    def check_permissions(self) -> DiagnosticResult:
        """فحص Permissions"""
        try:
            test_file = Path("test_write.tmp")
            test_file.write_text("test")
            test_file.unlink()
            
            return DiagnosticResult(
                name="permissions",
                status="ok",
                message="Write permissions OK",
                details={"test_written": True},
            )
        except Exception as e:
            return DiagnosticResult(
                name="permissions",
                status="error",
                message=f"Write permission denied: {str(e)}",
            )
    
    def check_git(self) -> DiagnosticResult:
        """فحص Git"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            git_available = result.returncode == 0
            git_version = result.stdout.strip() if git_available else None
            
            # فحص إذا كان في repo
            is_repo = Path(".git").exists()
            
            return DiagnosticResult(
                name="git",
                status="ok" if git_available else "warning",
                message=git_version or "Git not installed",
                details={
                    "available": git_available,
                    "version": git_version,
                    "is_repository": is_repo,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                name="git",
                status="error",
                message=f"Git check failed: {str(e)}",
            )
    
    def check_python_runtime(self) -> DiagnosticResult:
        """فحص Python Runtime"""
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            # فحص المكتبات الأساسية
            libraries = {}
            required = ["flask", "gunicorn"]
            for lib in required:
                try:
                    __import__(lib)
                    libraries[lib] = "ok"
                except ImportError:
                    libraries[lib] = "missing"
            
            status = "ok" if all(v == "ok" for v in libraries.values()) else "warning"
            
            return DiagnosticResult(
                name="python_runtime",
                status=status,
                message=f"Python {version_str}",
                details={
                    "version": version_str,
                    "libraries": libraries,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                name="python_runtime",
                status="error",
                message=f"Python check failed: {str(e)}",
            )
    
    def check_directories(self) -> DiagnosticResult:
        """فحصWritable Directories"""
        try:
            dirs = ["projects", "docs", "logs", "static", "templates"]
            results = {}
            all_ok = True
            
            for d in dirs:
                p = Path(d)
                exists = p.exists()
                writable = os.access(p, os.W_OK) if exists else False
                results[d] = {"exists": exists, "writable": writable}
                if not (exists and writable):
                    all_ok = False
            
            return DiagnosticResult(
                name="directories",
                status="ok" if all_ok else "warning",
                message="All required directories accessible",
                details=results,
            )
        except Exception as e:
            return DiagnosticResult(
                name="directories",
                status="error",
                message=f"Directory check failed: {str(e)}",
            )
    
    def check_model_providers(self) -> DiagnosticResult:
        """فحص Model Providers"""
        try:
            from src.model_provider import provider_registry

            providers = provider_registry.list_all()
            has_active = provider_registry.has_provider()
            mode = provider_registry.mode  # "real" | "mock" | "unavailable" (Phase 4)
            active_provider = None

            for p in providers:
                if p["active"]:
                    active_provider = p["name"]
                    break

            # mode="mock" ليس خطأ، لكنه يستحق تنبيهاً واضحاً - لا يظهر كـ "ok"
            # صامت وكأنه ذكاء حقيقي (انظر AUDIT_REPORT.md C3 وPhase 4 rules).
            status = "warning" if mode == "mock" else ("ok" if mode == "real" else "warning")

            return DiagnosticResult(
                name="model_providers",
                status=status,
                message=f"Provider mode: {mode} (active: {active_provider or 'None'})",
                details={
                    "providers": providers,
                    "has_active": has_active,
                    "active": active_provider,
                    "mode": mode,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                name="model_providers",
                status="warning",
                message=f"Provider check failed: {str(e)}",
            )
    
    def check_capabilities(self) -> DiagnosticResult:
        """فحص Capabilities"""
        try:
            from src.model_provider.capability_requirements import capability_requirements
            
            caps = capability_requirements.list_all()
            direct = capability_requirements.list_direct_execution()
            llm = capability_requirements.list_llm_required()
            
            return DiagnosticResult(
                name="capabilities",
                status="ok",
                message=f"{len(caps)} capabilities registered",
                details={
                    "total": len(caps),
                    "direct_execution": len(direct),
                    "llm_required": len(llm),
                },
            )
        except Exception as e:
            return DiagnosticResult(
                name="capabilities",
                status="error",
                message=f"Capability check failed: {str(e)}",
            )
    
    def check_plugins(self) -> DiagnosticResult:
        """فحص Plugins"""
        try:
            from src.Core.plugin import plugin_manager
            
            manifests = plugin_manager.discover()
            loaded = plugin_manager.list_loaded()
            
            return DiagnosticResult(
                name="plugins",
                status="ok",
                message=f"{len(manifests)} plugins found, {len(loaded)} loaded",
                details={
                    "available": len(manifests),
                    "loaded": len(loaded),
                },
            )
        except Exception as e:
            return DiagnosticResult(
                name="plugins",
                status="warning",
                message=f"Plugin check failed: {str(e)}",
            )
    
    def check_event_bus(self) -> DiagnosticResult:
        """فحص Event Bus"""
        try:
            from src.Core.event_bus import event_bus
            
            history = event_bus.get_history(limit=10)
            
            return DiagnosticResult(
                name="event_bus",
                status="ok",
                message="Event Bus operational",
                details={
                    "history_count": len(history),
                },
            )
        except Exception as e:
            return DiagnosticResult(
                name="event_bus",
                status="error",
                message=f"Event Bus check failed: {str(e)}",
            )
    
    # ========== Run All ==========
    
    def run_all(self) -> Dict[str, Any]:
        """تشغيل كل الفحوصات"""
        self.results = []
        
        checks = [
            self.check_workspace_root,
            self.check_permissions,
            self.check_git,
            self.check_python_runtime,
            self.check_directories,
            self.check_model_providers,
            self.check_capabilities,
            self.check_plugins,
            self.check_event_bus,
        ]
        
        for check in checks:
            result = check()
            self._add_result(result)
        
        # حساب النتيجة النهائية
        errors = sum(1 for r in self.results if r.status == "error")
        warnings = sum(1 for r in self.results if r.status == "warning")
        
        overall_status = "ok"
        if errors > 0:
            overall_status = "error"
        elif warnings > 0:
            overall_status = "warning"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": len(self.results),
            "errors": errors,
            "warnings": warnings,
            "results": [r.to_dict() for r in self.results],
        }


# ============================================================
# Global Instance
# ============================================================

diagnostics = SystemDiagnostics()


# ============================================================
# Convenience Functions
# ============================================================

def run_diagnostics() -> Dict[str, Any]:
    """تشغيل الفحوصات"""
    return diagnostics.run_all()


def health_check() -> Dict[str, Any]:
    """فحص صحي مبسط"""
    try:
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
        }
    except:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
        }
