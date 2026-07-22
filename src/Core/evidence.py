"""
CodeForge Evidence System - Phase 2
===================================
Structured evidence for every real operation.
Every operation produces: step_id, timestamp, mission_id, task_id, worker_id,
input, action, output, exit_status, files_changed, git_state, verification_result, provenance
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import json


class ExitStatus(str, Enum):
    """Exit status for evidence"""
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    REJECTED = "rejected"
    RECOVERED = "recovered"
    RUNNING = "running"


class VerificationStatus(str, Enum):
    """Verification status"""
    VERIFIED = "verified"
    FAILED = "failed"
    PENDING = "pending"
    SKIPPED = "skipped"


@dataclass
class Evidence:
    """Evidence for a single execution step"""
    step_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mission_id: str = ""
    task_id: str = ""
    worker_id: str = ""
    capability: str = ""
    tool: str = ""
    
    # Input/Action/Output
    input: Dict[str, Any] = field(default_factory=dict)
    action: str = ""
    output: Any = None
    exit_status: str = ExitStatus.SUCCESS.value
    
    # Files changed
    files_changed: List[str] = field(default_factory=list)
    
    # Git state
    git_state: Dict[str, Any] = field(default_factory=dict)
    
    # Verification
    verification_result: str = ""
    verification_status: str = VerificationStatus.VERIFIED.value
    
    # Provenance
    provenance: str = ""
    error: str = ""
    
    # Runtime info
    duration_seconds: float = 0.0
    attempts: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Ensure ISO format for timestamp
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data
    
    @property
    def is_success(self) -> bool:
        """Check if operation was successful"""
        return self.exit_status == ExitStatus.SUCCESS.value and \
               self.verification_status == VerificationStatus.VERIFIED.value


class EvidenceCollector:
    """
    Collects and manages evidence for all execution operations.
    Singleton pattern for global evidence collection.
    """
    _instance: Optional["EvidenceCollector"] = None
    
    def __new__(cls) -> "EvidenceCollector":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._evidence: List[Evidence] = []
        self._mission_id: Optional[str] = None
        self._task_id: Optional[str] = None
        self._worker_id: str = str(uuid.uuid4())[:8]
        self._max_evidence = 10000
        self._initialized = True
    
    def set_context(self, mission_id: str = "", task_id: str = "") -> None:
        """Set execution context"""
        if mission_id:
            self._mission_id = mission_id
        if task_id:
            self._task_id = task_id
    
    def create_evidence(
        self,
        step_id: str,
        capability: str = "",
        tool: str = "",
        action: str = "",
        input_data: Dict[str, Any] = None,
        exit_status: Any = ExitStatus.SUCCESS,
        provenance: str = "",
    ) -> Evidence:
        """Create a new evidence record"""
        # Handle both string and enum for exit_status
        if isinstance(exit_status, str):
            exit_status_value = exit_status
        else:
            exit_status_value = exit_status.value if hasattr(exit_status, 'value') else str(exit_status)
        
        evidence = Evidence(
            step_id=step_id,
            mission_id=self._mission_id or "",
            task_id=self._task_id or "",
            worker_id=self._worker_id,
            capability=capability,
            tool=tool,
            action=action,
            input=input_data or {},
            exit_status=exit_status_value,
            provenance=provenance or f"{capability}.{tool}" if tool else capability,
        )
        self._evidence.append(evidence)
        
        # Limit evidence size
        if len(self._evidence) > self._max_evidence:
            self._evidence = self._evidence[-self._max_evidence:]
        
        return evidence
    
    def complete_evidence(
        self,
        evidence: Evidence,
        output: Any = None,
        files_changed: List[str] = None,
        git_state: Dict[str, Any] = None,
        verification_result: str = "",
        verification_status: VerificationStatus = VerificationStatus.VERIFIED,
        error: str = "",
        duration_seconds: float = 0.0,
        attempts: int = 1,
    ) -> Evidence:
        """Complete an evidence record with results"""
        evidence.output = output
        evidence.files_changed = files_changed or []
        evidence.git_state = git_state or {}
        evidence.verification_result = verification_result
        evidence.verification_status = verification_status.value
        evidence.error = error
        evidence.duration_seconds = duration_seconds
        evidence.attempts = attempts
        
        # Set exit status based on verification
        if verification_status == VerificationStatus.FAILED:
            evidence.exit_status = ExitStatus.FAILURE.value
        elif error and "blocked" in error.lower():
            evidence.exit_status = ExitStatus.BLOCKED.value
        elif error:
            evidence.exit_status = ExitStatus.FAILURE.value
        
        return evidence
    
    def get_evidence(self, limit: int = 100) -> List[Evidence]:
        """Get recent evidence"""
        return self._evidence[-limit:]
    
    def get_evidence_for_step(self, step_id: str) -> List[Evidence]:
        """Get evidence for a specific step"""
        return [e for e in self._evidence if e.step_id == step_id]
    
    def get_all_evidence(self) -> List[Evidence]:
        """Get all evidence"""
        return list(self._evidence)
    
    def clear_evidence(self) -> None:
        """Clear all evidence"""
        self._evidence.clear()
    
    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get summary of evidence"""
        total = len(self._evidence)
        success = sum(1 for e in self._evidence if e.is_success)
        failed = sum(1 for e in self._evidence if e.exit_status == ExitStatus.FAILURE.value)
        blocked = sum(1 for e in self._evidence if e.exit_status == ExitStatus.BLOCKED.value)
        
        return {
            "total_operations": total,
            "successful": success,
            "failed": failed,
            "blocked": blocked,
            "success_rate": success / total if total > 0 else 0,
            "mission_id": self._mission_id,
            "task_id": self._task_id,
            "worker_id": self._worker_id,
        }
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Export all evidence as list of dicts"""
        return [e.to_dict() for e in self._evidence]
    
    def to_json(self) -> str:
        """Export all evidence as JSON"""
        return json.dumps(self.to_dict_list(), ensure_ascii=False, indent=2)


# Global instance
evidence_collector = EvidenceCollector()


def get_evidence_collector() -> EvidenceCollector:
    """Get the global evidence collector"""
    return evidence_collector
