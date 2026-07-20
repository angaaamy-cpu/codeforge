"""
CodeForge Execution Engine - Phase X
====================================
محرك التنفيذ
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import traceback

from src.Core.event_bus import EventType, Event, emit


class _CapabilityNotFound(Exception):
    """Phase 6: القدرة/الأداة المطلوبة غير مسجَّلة - BLOCKED لا FAILED."""
    pass


class ExecutionStatus(str, Enum):
    """حالة التنفيذ"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Phase 6: القدرة/الأداة غير موجودة - لم يُحاول التنفيذ أصلاً، ليس فشلاً بعد محاولة حقيقية
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class ExecutionStep:
    """خطوة تنفيذ"""
    id: int
    name: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Any = None
    error: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    # Phase 6: خطوة قد ترتبط بقدرة/أداة حقيقية (src.Core.capability). إن لم
    # تُحدَّد capability/tool، تبقى خطوة وصفية (سلوك ما قبل Phase 6، محفوظ
    # للتوافق الخلفي - لا يُنفَّذ عبرها شيء حقيقي).
    capability: Optional[str] = None
    tool: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value if isinstance(self.status, ExecutionStatus) else self.status,
            "result": str(self.result) if self.result else None,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "capability": self.capability,
            "tool": self.tool,
            "attempts": self.attempts,
        }


@dataclass
class ExecutionContext:
    """سياق التنفيذ"""
    task_id: str
    description: str
    workspace: str = ""
    steps: List[ExecutionStep] = field(default_factory=list)
    current_step: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "workspace": self.workspace,
            "steps": [s.to_dict() for s in self.steps],
            "current_step": self.current_step,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class ExecutionEngine:
    """
    محرك التنفيذ - Phase X
    """
    _instance: Optional["ExecutionEngine"] = None
    
    def __new__(cls) -> "ExecutionEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._active_contexts: Dict[str, ExecutionContext] = {}
        self._max_retries = 3
        self._initialized = True
    
    def execute(
        self,
        description: str,
        workspace: str = "",
        task_id: str = None,
        steps: List[Any] = None,
    ) -> ExecutionContext:
        """
        تنفيذ مهمة

        Args:
            description: وصف المهمة
            workspace: مساحة العمل
            task_id: معرف المهمة
            steps: قائمة الخطوات - كل عنصر إما:
                   - str: خطوة وصفية فقط (سلوك ما قبل Phase 6، بلا تنفيذ حقيقي)
                   - dict: {"name": ..., "capability": ..., "tool": ..., "params": {...}}
                     لتنفيذ حقيقي عبر src.Core.capability.CapabilityRegistry

        Returns:
            ExecutionContext
        """
        import uuid
        task_id = task_id or f"task-{uuid.uuid4().hex[:8]}"
        
        # Create context
        context = ExecutionContext(
            task_id=task_id,
            description=description,
            workspace=workspace,
        )
        
        # Default steps if not provided
        if steps is None:
            steps = [
                "planning",
                "execution",
                "testing",
                "security",
                "documentation",
            ]
        
        # Create execution steps (str = وصفية، dict = مرتبطة بقدرة حقيقية)
        for i, step_def in enumerate(steps):
            if isinstance(step_def, dict):
                context.steps.append(ExecutionStep(
                    id=i,
                    name=step_def.get("name", f"step-{i}"),
                    capability=step_def.get("capability"),
                    tool=step_def.get("tool"),
                    params=step_def.get("params", {}),
                ))
            else:
                context.steps.append(ExecutionStep(id=i, name=step_def))
        
        # Store context
        self._active_contexts[task_id] = context
        
        # Emit start event
        emit(EventType.EXECUTION_STARTED, {
            "task_id": task_id,
            "description": description,
            "workspace": workspace,
        })
        
        return context
    
    def run_steps(self, context: ExecutionContext) -> ExecutionContext:
        """
        تشغيل الخطوات بالتسلسل، مع إعادة محاولة (retry) للخطوات المرتبطة
        بقدرة/أداة حقيقية فقط (Phase 6). self._max_retries كان مُعرَّفاً
        بلا استخدام فعلي قبل هذا - الآن يُطبَّق فعلياً.
        """
        context.current_step = 0
        
        for step in context.steps:
            step.status = ExecutionStatus.RUNNING
            step.started_at = datetime.now()
            
            emit(EventType.EXECUTION_STEP, {
                "task_id": context.task_id,
                "step": step.name,
                "step_id": step.id,
            })

            max_attempts = self._max_retries if (step.capability and step.tool) else 1
            last_error = None

            for attempt in range(1, max_attempts + 1):
                step.attempts = attempt
                try:
                    result = self._execute_step(step, context)
                    step.result = result
                    step.status = ExecutionStatus.COMPLETED
                    step.error = ""
                    last_error = None

                    emit(EventType.BUILD_STEP_COMPLETED, {
                        "task_id": context.task_id,
                        "step": step.name,
                        "attempts": attempt,
                    })
                    break

                except _CapabilityNotFound as e:
                    # BLOCKED: لا يوجد ما يمكن محاولته أصلاً - لا فائدة من
                    # إعادة المحاولة، وليس "فشلاً" بعد تنفيذ حقيقي.
                    step.error = str(e)
                    step.status = ExecutionStatus.BLOCKED
                    last_error = e
                    emit(EventType.EXECUTION_FAILED, {
                        "task_id": context.task_id,
                        "step": step.name,
                        "error": str(e),
                        "status": "blocked",
                    })
                    break

                except Exception as e:
                    last_error = e
                    step.error = str(e)
                    if attempt < max_attempts:
                        continue  # إعادة محاولة حقيقية
                    step.status = ExecutionStatus.FAILED
                    emit(EventType.EXECUTION_FAILED, {
                        "task_id": context.task_id,
                        "step": step.name,
                        "error": str(e),
                        "attempts": attempt,
                    })

            if step.started_at:
                step.completed_at = datetime.now()
                step.duration_seconds = (step.completed_at - step.started_at).total_seconds()

            if step.status in (ExecutionStatus.FAILED, ExecutionStatus.BLOCKED):
                return context

            context.current_step += 1
        
        # All steps completed
        emit(EventType.EXECUTION_COMPLETED, {
            "task_id": context.task_id,
        })
        
        return context
    
    def _execute_step(self, step: ExecutionStep, context: ExecutionContext) -> Any:
        """
        تنفيذ خطوة واحدة.

        Phase 6: إن كانت الخطوة مرتبطة بـ capability+tool حقيقيين، يُنفَّذ
        الاستدعاء الفعلي عبر src.Core.capability.CapabilityRegistry - لا
        نجاح مُختلَق. خطوات بلا capability/tool (السلوك القديم قبل
        Phase 6، مثل "planning"/"testing" الوصفية) تبقى كما كانت.
        """
        if step.capability and step.tool:
            from src.Core.capability import CapabilityRegistry
            cap = CapabilityRegistry().get(step.capability)
            if cap is None:
                raise _CapabilityNotFound(
                    f"القدرة '{step.capability}' غير مُسجَّلة"
                )
            tool = cap.get_tool(step.tool)
            if tool is None:
                raise _CapabilityNotFound(
                    f"الأداة '{step.tool}' غير موجودة في القدرة '{step.capability}' "
                    f"(الأدوات المتاحة: {list(cap.tools.keys())})"
                )
            return tool.execute(**step.params)

        # سلوك ما قبل Phase 6: خطوة وصفية بلا ربط حقيقي - Placeholder مقصود
        return {"status": "success", "step": step.name}
    
    def cancel(self, task_id: str) -> bool:
        """إلغاء تنفيذ"""
        if task_id not in self._active_contexts:
            return False
        
        context = self._active_contexts[task_id]
        
        # Mark current step as cancelled
        if context.current_step < len(context.steps):
            context.steps[context.current_step].status = ExecutionStatus.CANCELLED
        
        emit(EventType.EXECUTION_FAILED, {
            "task_id": task_id,
            "reason": "cancelled",
        })
        
        return True
    
    def get_context(self, task_id: str) -> Optional[ExecutionContext]:
        """الحصول على سياق التنفيذ"""
        return self._active_contexts.get(task_id)
    
    def get_active_contexts(self) -> List[ExecutionContext]:
        """الحصول على كل السياقات النشطة"""
        return list(self._active_contexts.values())


# ============================================================
# Global Instance
# ============================================================

execution_engine = ExecutionEngine()
