"""
CodeForge Execution Engine - Phase 2
====================================
محرك التنفيذ الحقيقي مع Evidence Collection
Canonical Execution Path - Phase 2 Bridge Implementation
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import traceback
import os
import uuid

from src.Core.event_bus import EventType, Event, emit
from src.Core.evidence import Evidence, EvidenceCollector, get_evidence_collector, ExitStatus, VerificationStatus


class _CapabilityNotFound(Exception):
    """القدرة/الأداة المطلوبة غير مسجَّلة - BLOCKED لا FAILED."""
    pass


class _PolicyViolation(Exception):
    """انتهاك السياسة - REJECTED_BY_POLICY."""
    pass


class ExecutionStatus(str, Enum):
    """حالة التنفيذ"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
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
    capability: Optional[str] = None
    tool: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    attempts: int = 0
    evidence: Optional[Dict[str, Any]] = None  # Phase 2: Evidence for every step

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
            "evidence": self.evidence,
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
    evidence_collector: EvidenceCollector = field(default_factory=EvidenceCollector)
    mission_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "workspace": self.workspace,
            "steps": [s.to_dict() for s in self.steps],
            "current_step": self.current_step,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "mission_id": self.mission_id,
        }
    
    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get evidence summary for context"""
        return self.evidence_collector.get_evidence_summary()
    
    def get_all_evidence(self) -> List[Dict[str, Any]]:
        """Get all evidence from context"""
        return self.evidence_collector.to_dict_list()


class ExecutionEngine:
    """
    محرك التنفيذ الحقيقي - Phase 2
    Canonical Execution Path
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
        self._evidence_collector = get_evidence_collector()
    
    def execute(
        self,
        description: str,
        workspace: str = "",
        task_id: str = None,
        steps: List[Any] = None,
        mission_id: str = None,
    ) -> ExecutionContext:
        """
        تنفيذ مهمة

        Args:
            description: وصف المهمة
            workspace: مساحة العمل
            task_id: معرف المهمة
            steps: قائمة الخطوات - كل عنصر إما:
                   - str: خطوة وصفية فقط
                   - dict: {"name": ..., "capability": ..., "tool": ..., "params": {...}}
            mission_id: معرف المهمة الكبرى (للـ Provenance)

        Returns:
            ExecutionContext
        """
        task_id = task_id or f"task-{uuid.uuid4().hex[:8]}"
        mission_id = mission_id or f"mission-{uuid.uuid4().hex[:8]}"
        
        # Create context
        context = ExecutionContext(
            task_id=task_id,
            description=description,
            workspace=workspace or os.getcwd(),
            mission_id=mission_id,
        )
        
        # Set evidence context
        context.evidence_collector.set_context(mission_id=mission_id, task_id=task_id)
        
        # Default steps if not provided
        if steps is None:
            steps = [
                "planning",
                "execution",
                "testing",
                "security",
                "documentation",
            ]
        
        # Create execution steps
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
            "mission_id": mission_id,
        })
        
        return context
    
    def run_steps(self, context: ExecutionContext) -> ExecutionContext:
        """
        تشغيل الخطوات بالتسلسل مع Evidence Collection
        """
        context.current_step = 0
        
        for step in context.steps:
            step.status = ExecutionStatus.RUNNING
            step.started_at = datetime.now(timezone.utc)
            
            emit(EventType.EXECUTION_STEP, {
                "task_id": context.task_id,
                "step": step.name,
                "step_id": step.id,
            })

            max_attempts = self._max_retries if (step.capability and step.tool) else 1
            last_error = None
            step_evidence = None

            for attempt in range(1, max_attempts + 1):
                step.attempts = attempt
                step_start = datetime.now(timezone.utc)
                
                try:
                    result = self._execute_step(step, context)
                    step.result = result
                    step.status = ExecutionStatus.COMPLETED
                    step.error = ""
                    last_error = None
                    
                    # Calculate duration
                    step_end = datetime.now(timezone.utc)
                    step.duration_seconds = (step_end - step_start).total_seconds()
                    
                    # Get evidence from result if available
                    if isinstance(result, dict) and result.get("evidence"):
                        step_evidence = result["evidence"]
                    elif isinstance(result, dict) and result.get("success") is not None:
                        # Create evidence from result
                        step_evidence = {
                            "step_id": f"step.{step.id}",
                            "success": result.get("success", True),
                            "output": result,
                            "exit_status": ExitStatus.SUCCESS.value if result.get("success") else ExitStatus.FAILURE.value,
                        }

                    emit(EventType.BUILD_STEP_COMPLETED, {
                        "task_id": context.task_id,
                        "step": step.name,
                        "attempts": attempt,
                        "evidence": step_evidence,
                    })
                    break

                except _CapabilityNotFound as e:
                    step.error = str(e)
                    step.status = ExecutionStatus.BLOCKED
                    last_error = e
                    step_end = datetime.now(timezone.utc)
                    step.duration_seconds = (step_end - step_start).total_seconds()
                    
                    step_evidence = {
                        "step_id": f"step.{step.id}",
                        "success": False,
                        "error": str(e),
                        "exit_status": ExitStatus.BLOCKED.value,
                    }
                    
                    emit(EventType.EXECUTION_FAILED, {
                        "task_id": context.task_id,
                        "step": step.name,
                        "error": str(e),
                        "status": "blocked",
                    })
                    break

                except _PolicyViolation as e:
                    step.error = str(e)
                    step.status = ExecutionStatus.BLOCKED
                    last_error = e
                    step_end = datetime.now(timezone.utc)
                    step.duration_seconds = (step_end - step_start).total_seconds()
                    
                    step_evidence = {
                        "step_id": f"step.{step.id}",
                        "success": False,
                        "error": str(e),
                        "exit_status": ExitStatus.REJECTED.value,
                        "rejected_by": "policy",
                    }
                    
                    emit(EventType.EXECUTION_FAILED, {
                        "task_id": context.task_id,
                        "step": step.name,
                        "error": str(e),
                        "status": "rejected_by_policy",
                    })
                    break

                except Exception as e:
                    last_error = e
                    step.error = str(e)
                    step_end = datetime.now(timezone.utc)
                    step.duration_seconds = (step_end - step_start).total_seconds()
                    
                    if attempt < max_attempts:
                        continue  # إعادة محاولة
                    step.status = ExecutionStatus.FAILED
                    
                    step_evidence = {
                        "step_id": f"step.{step.id}",
                        "success": False,
                        "error": str(e),
                        "exit_status": ExitStatus.FAILURE.value,
                        "attempts": attempt,
                    }
                    
                    emit(EventType.EXECUTION_FAILED, {
                        "task_id": context.task_id,
                        "step": step.name,
                        "error": str(e),
                        "attempts": attempt,
                    })

            # Store evidence in step
            step.evidence = step_evidence

            if step.started_at and not step.completed_at:
                step.completed_at = datetime.now(timezone.utc)

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
        تنفيذ خطوة واحدة مع Evidence Collection
        """
        # If step has capability and tool, execute via real tool
        if step.capability and step.tool:
            return self._execute_capability(step, context)
        
        # Descriptive step (no real execution)
        return {"status": "success", "step": step.name, "evidence": None}
    
    def _execute_capability(self, step: ExecutionStep, context: ExecutionContext) -> Any:
        """
        Execute via real capability tool
        """
        capability = step.capability
        tool = step.tool
        params = step.params
        
        # Create evidence for this step
        evidence = context.evidence_collector.create_evidence(
            step_id=f"step.{step.id}",
            capability=capability,
            tool=tool,
            action=f"{capability}.{tool}",
            input_data=params,
            exit_status=ExitStatus.RUNNING.value,
            provenance=f"ExecutionEngine._execute_capability({capability}.{tool})",
        )
        
        try:
            result = self._call_tool(capability, tool, params, context.workspace)
            
            # Complete evidence
            if isinstance(result, dict):
                context.evidence_collector.complete_evidence(
                    evidence=evidence,
                    output=result,
                    files_changed=result.get("files_changed", []),
                    git_state=result.get("git_state", {}),
                    verification_status=VerificationStatus.VERIFIED,
                    error=result.get("error", ""),
                    duration_seconds=step.duration_seconds,
                    attempts=step.attempts,
                )
                
                # Add evidence to result
                result["evidence"] = evidence.to_dict()
            else:
                context.evidence_collector.complete_evidence(
                    evidence=evidence,
                    output=str(result),
                    verification_status=VerificationStatus.VERIFIED,
                )
            
            return result
            
        except _CapabilityNotFound as e:
            context.evidence_collector.complete_evidence(
                evidence=evidence,
                verification_status=VerificationStatus.FAILED,
                error=str(e),
            )
            raise
            
        except _PolicyViolation as e:
            context.evidence_collector.complete_evidence(
                evidence=evidence,
                verification_status=VerificationStatus.FAILED,
                error=str(e),
            )
            raise
            
        except Exception as e:
            context.evidence_collector.complete_evidence(
                evidence=evidence,
                verification_status=VerificationStatus.FAILED,
                error=str(e),
            )
            raise
    
    def _call_tool(
        self,
        capability: str,
        tool: str,
        params: Dict[str, Any],
        workspace: str = None,
    ) -> Any:
        """
        Call a real capability tool
        """
        # Import tools dynamically
        from src.Core.tools import FilesTool, TerminalTool, GitTool, TestTool
        
        # Map capabilities to tools
        tool_map = {
            ("files", "read"): lambda p: FilesTool(workspace).read(p.get("path")),
            ("files", "write"): lambda p: FilesTool(workspace).write(p.get("path"), p.get("content", "")),
            ("files", "delete"): lambda p: FilesTool(workspace).delete(p.get("path")),
            ("files", "list"): lambda p: FilesTool(workspace).list(p.get("path", ".")),
            ("files", "exists"): lambda p: FilesTool(workspace).exists(p.get("path")),
            
            ("terminal", "execute"): lambda p: TerminalTool(workspace).execute(
                p.get("command"),
                timeout=p.get("timeout", 30),
                cwd=p.get("cwd", workspace),
            ),
            
            ("git", "status"): lambda p: GitTool(workspace).status(),
            ("git", "diff"): lambda p: GitTool(workspace).diff(p.get("file")),
            ("git", "log"): lambda p: GitTool(workspace).log(p.get("limit", 10)),
            ("git", "commit"): lambda p: GitTool(workspace).commit(p.get("message", "")),
            ("git", "branch"): lambda p: GitTool(workspace).branch(),
            ("git", "remote"): lambda p: GitTool(workspace).remote(),
            ("git", "verify_commit"): lambda p: GitTool(workspace).verify_commit_exists(p.get("commit_hash", "")),
            
            ("testing", "run"): lambda p: TestTool(workspace).run(
                test_path=p.get("test_path"),
                verbose=p.get("verbose", True),
            ),
            ("testing", "verify"): lambda p: TestTool(workspace).verify_test_passes(p.get("test_path")),
        }
        
        key = (capability, tool)
        if key not in tool_map:
            raise _CapabilityNotFound(
                f"Tool '{tool}' not found for capability '{capability}'"
            )
        
        return tool_map[key](params)
    
    def cancel(self, task_id: str) -> bool:
        """إلغاء تنفيذ"""
        if task_id not in self._active_contexts:
            return False
        
        context = self._active_contexts[task_id]
        
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
