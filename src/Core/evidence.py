"""
Evidence Collection System - Phase 2: Execution Engine Bridge
========================================================

Provides structured evidence for every operation with full provenance tracking.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ExitStatus(Enum):
    """Exit status for operations"""
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"
    BLOCKED = "blocked"


class VerificationStatus(Enum):
    """Verification status for operations"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass
class Evidence:
    """
    Evidence record for an operation.
    
    Every operation produces structured evidence that can be audited and verified.
    """
    step_id: str = ""
    timestamp: datetime = None
    mission_id: str = ""
    task_id: str = ""
    worker_id: str = ""
    
    # Operation details
    capability: str = ""
    tool: str = ""
    action: str = ""
    input: Dict[str, Any] = None
    
    # Results
    output: Any = None
    exit_status: str = ExitStatus.SUCCESS.value
    files_changed: List[str] = None
    git_state: Dict[str, Any] = None
    
    # Verification
    verification_status: str = VerificationStatus.VERIFIED.value
    verification_result: str = ""
    
    # Provenance
    provenance: str = ""
    error: str = ""
    
    # Runtime info
    duration_seconds: float = 0.0
    attempts: int = 1
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.input is None:
            self.input = {}
        if self.files_changed is None:
            self.files_changed = []
        if self.git_state is None:
            self.git_state = {}
    
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
        evidence.verification_status = verification_status.value if hasattr(verification_status, 'value') else str(verification_status)
        evidence.error = error
        evidence.duration_seconds = duration_seconds
        evidence.attempts = attempts
        return evidence
    
    def get_all_evidence(self) -> List[Dict[str, Any]]:
        """Get all evidence as dictionaries"""
        return [e.to_dict() for e in self._evidence]
    
    def get_evidence_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Get evidence filtered by capability"""
        return [e.to_dict() for e in self._evidence if e.capability == capability]
    
    def get_successful_operations(self) -> List[Dict[str, Any]]:
        """Get all successful operations"""
        return [e.to_dict() for e in self._evidence if e.is_success]
    
    def get_failed_operations(self) -> List[Dict[str, Any]]:
        """Get all failed operations"""
        return [e.to_dict() for e in self._evidence if not e.is_success]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        total = len(self._evidence)
        successful = sum(1 for e in self._evidence if e.is_success)
        failed = sum(1 for e in self._evidence if not e.is_success and e.exit_status == ExitStatus.FAILURE.value)
        
        return {
            "total_operations": total,
            "successful": successful,
            "failed": failed,
            "pending": total - successful - failed,
            "mission_id": self._mission_id,
            "task_id": self._task_id,
            "worker_id": self._worker_id,
        }
    
    def clear_evidence(self) -> None:
        """Clear all evidence"""
        self._evidence = []
        self._mission_id = None
        self._task_id = None
        self._worker_id = str(uuid.uuid4())[:8]


# Global singleton instance
evidence_collector = EvidenceCollector()
