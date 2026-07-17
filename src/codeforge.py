"""
CodeForge - Phase X
===================
الواجهة الموحدة للمنصة - CodeForge X Architecture
"""

from typing import Optional, List
from src.build_engine import BuildEngine
from src.build_result import BuildResult

# CodeForge X Core (if available)
try:
    from src.Core import (
        CapabilityRegistry,
        EventBus,
        WorkspaceManager,
        ExecutionEngine,
        ProjectMemory,
        PluginManager,
        DeploymentManager,
        SecretsManager,
    )
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


class CodeForge:
    """
    CodeForge X: Autonomous Software Factory
    الواجهة الموحدة للمنصة
    """

    def __init__(self):
        self.engine = BuildEngine()
        
        # CodeForge X Core
        if CORE_AVAILABLE:
            self.capabilities = CapabilityRegistry()
            self.events = EventBus()
            self.workspaces = WorkspaceManager()
            self.execution = ExecutionEngine()
            self.memory = ProjectMemory()
            self.plugins = PluginManager()
            self.deployment = DeploymentManager()
            self.secrets = SecretsManager()

    def build(self, description: str) -> BuildResult:
        """يبني مشروعاً كاملاً من وصف"""
        # Emit event if Core available
        if CORE_AVAILABLE:
            try:
                from src.Core.event_bus import EventType, emit
                emit(EventType.BUILD_STARTED, {"description": description})
            except:
                pass
        
        result = self.engine.execute(description)
        
        # Emit completion event
        if CORE_AVAILABLE:
            try:
                from src.Core.event_bus import EventType, emit
                event_type = EventType.BUILD_SUCCEEDED if result.status == "success" else EventType.BUILD_FAILED
                emit(event_type, {
                    "project": result.project_name,
                    "status": result.status,
                })
            except:
                pass
        
        return result

    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def x_enabled(self) -> bool:
        """هل CodeForge X مفعّل"""
        return CORE_AVAILABLE
    
    def list_capabilities(self) -> List[dict]:
        """قائمة القدرات المتاحة"""
        if not CORE_AVAILABLE:
            return []
        return [c.to_dict() for c in self.capabilities.list_all()]
    
    def get_event_history(self, limit: int = 50) -> List[dict]:
        """سجل الأحداث"""
        if not CORE_AVAILABLE:
            return []
        return [e.to_dict() for e in self.events.get_history(limit=limit)]

    def __repr__(self) -> str:
        return f"CodeForge(v{self.version}, x={self.x_enabled})"


# ============================================================
# Instance Global
# ============================================================

codeforge = CodeForge()


# ============================================================
# Helper Functions
# ============================================================

def build(description: str) -> BuildResult:
    """بناء مشروع من وصف"""
    return codeforge.build(description)
