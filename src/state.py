"""
CodeForge State Management - Phase 3
====================================
نظام حالة المشروع الكامل
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import json
import os


class TaskStatus(Enum):
    """حالة المهمة"""
    PLANNING = "قيد التخطيط"
    EXECUTING = "قيد التنفيذ"
    TESTING = "قيد الاختبار"
    COMPLETED = "مكتمل"
    FAILED = "فاشل"
    BLOCKED = "محظور"


class AgentType(Enum):
    """أنواع الوكلاء"""
    MANAGER = "manager"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    QA = "qa"


@dataclass
class AgentState:
    """حالة وكيل واحد"""
    name: AgentType
    attempts: int = 0
    last_active: Optional[datetime] = None
    status: str = "idle"
    current_task: Optional[str] = None

    def increment_attempts(self):
        """زيادة عدد المحاولات"""
        self.attempts += 1
        self.last_active = datetime.now()

    def reset_attempts(self):
        """إعادة تعيين المحاولات"""
        self.attempts = 0


@dataclass
class Decision:
    """قرار واحد"""
    agent: str
    content: str
    impact: str  # "architectural" or "operational"
    timestamp: datetime = field(default_factory=datetime.now)
    task_id: Optional[str] = None

    def to_dict(self):
        return {
            "agent": self.agent,
            "content": self.content,
            "impact": self.impact,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id
        }


@dataclass
class ProjectState:
    """حالة المشروع الكاملة"""
    current_task: Optional[str] = None
    current_task_id: Optional[str] = None
    active_agent: Optional[AgentType] = None
    task_status: TaskStatus = TaskStatus.PLANNING
    attempts: dict = field(default_factory=dict)
    last_decision: Optional[Decision] = None
    last_commit: Optional[str] = None
    last_commit_hash: Optional[str] = None
    last_commit_time: Optional[datetime] = None
    phase: str = "phase4"
    task_count: int = 0
    completed_tasks: int = 0
    agent_states: dict = field(default_factory=dict)
    execution_history: list = field(default_factory=list)

    def summary(self) -> str:
        """عرض ملخص نصي للوحة التحكم"""
        status_text = self.task_status.value
        agent_text = self.active_agent.value if self.active_agent else "لا يوجد"
        
        lines = [
            "╔══════════════════════════════════════╗",
            "║      لوحة تحكم CodeForge           ║",
            "╚══════════════════════════════════════╝",
            "",
            f"📊 الحالة الحالية: {status_text}",
            f"🤖 الوكيل النشط: {agent_text}",
            f"📋 إجمالي المهام: {self.task_count}",
            f"✅ المهام المنجزة: {self.completed_tasks}",
            "",
        ]
        
        if self.current_task:
            lines.append(f"🔄 المهمة الحالية: {self.current_task}")
            if self.current_task_id:
                lines.append(f"   المعرف: {self.current_task_id}")
        
        if self.attempts:
            lines.append("")
            lines.append("📈 محاولات الوكلاء:")
            for agent, count in self.attempts.items():
                lines.append(f"   {agent}: {count} محاولة")
        
        if self.last_commit:
            lines.append("")
            lines.append(f"💾 آخر commit: {self.last_commit[:50]}...")
        
        if self.last_commit_time:
            lines.append(f"   الوقت: {self.last_commit_time.strftime('%Y-%m-%d %H:%M')}")
        
        lines.append("")
        lines.append("╔══════════════════════════════════════╗")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """تحويل إلى dictionary للـ API"""
        return {
            "current_task": self.current_task,
            "current_task_id": self.current_task_id,
            "active_agent": self.active_agent.value if self.active_agent else None,
            "task_status": self.task_status.value,
            "phase": self.phase,
            "task_count": self.task_count,
            "completed_tasks": self.completed_tasks,
            "last_commit": self.last_commit,
            "last_commit_hash": self.last_commit_hash,
            "last_commit_time": self.last_commit_time.isoformat() if self.last_commit_time else None,
            "execution_history": self.execution_history[-10:]  # آخر 10
        }

    def __post_init__(self):
        """تهيئة الوكلاء"""
        if not self.agent_states:
            for agent_type in AgentType:
                self.agent_states[agent_type.value] = AgentState(name=agent_type)

    def start_task(self, task_description: str) -> int:
        """بدء مهمة جديدة"""
        self.task_count += 1
        self.current_task = task_description
        self.current_task_id = f"task-{self.task_count:03d}"
        self.task_status = TaskStatus.PLANNING
        self.attempts = {}
        return self.task_count

    def set_agent(self, agent_type: AgentType):
        """تعيين الوكيل النشط"""
        self.active_agent = agent_type
        self.agent_states[agent_type.value].last_active = datetime.now()

    def record_attempt(self, agent_type: AgentType) -> int:
        """تسجيل محاولة لوكيل"""
        agent_name = agent_type.value
        if agent_name not in self.attempts:
            self.attempts[agent_name] = 0
        self.attempts[agent_name] += 1
        self.agent_states[agent_name].increment_attempts()
        return self.attempts[agent_name]

    def get_attempts(self, agent_type: AgentType) -> int:
        """الحصول على عدد محاولات وكيل"""
        return self.attempts.get(agent_type.value, 0)

    def reset_attempts(self, agent_type: AgentType):
        """إعادة تعيين محاولات وكيل"""
        if agent_type.value in self.attempts:
            self.attempts[agent_type.value] = 0
        self.agent_states[agent_type.value].reset_attempts()

    def update_status(self, status: TaskStatus):
        """تحديث حالة المهمة"""
        self.task_status = status

    def record_decision(self, agent: str, content: str, impact: str):
        """تسجيل قرار"""
        self.last_decision = Decision(
            agent=agent,
            content=content,
            impact=impact,
            task_id=self.current_task_id
        )

    def record_commit(self, message: str, commit_hash: str):
        """تسجيل commit"""
        self.last_commit = message
        self.last_commit_hash = commit_hash
        self.last_commit_time = datetime.now()

    def to_dict(self):
        """تحويل إلى dictionary"""
        return {
            "current_task": self.current_task,
            "current_task_id": self.current_task_id,
            "active_agent": self.active_agent.value if self.active_agent else None,
            "task_status": self.task_status.value,
            "attempts": self.attempts,
            "last_decision": self.last_decision.to_dict() if self.last_decision else None,
            "last_commit": self.last_commit,
            "last_commit_hash": self.last_commit_hash,
            "last_commit_time": self.last_commit_time.isoformat() if self.last_commit_time else None,
            "phase": self.phase,
            "task_count": self.task_count,
            "completed_tasks": self.completed_tasks,
            "execution_history": self.execution_history[-10:]
        }

    def increment_completed_tasks(self):
        """زيادة عدد المهام المنجزة"""
        self.completed_tasks += 1

    def add_to_history(self, task_id: str, description: str, status: str):
        """إضافة مهمة إلى سجل التنفيذ"""
        self.execution_history.append({
            "task_id": task_id,
            "description": description,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectState":
        """إنشاء من dictionary"""
        state = cls()
        state.current_task = data.get("current_task")
        state.current_task_id = data.get("current_task_id")
        state.phase = data.get("phase", "phase4")
        state.task_count = data.get("task_count", 0)
        state.completed_tasks = data.get("completed_tasks", 0)
        state.execution_history = data.get("execution_history", [])
        
        if data.get("last_commit_time"):
            state.last_commit_time = datetime.fromisoformat(data["last_commit_time"])
        
        return state


class StateManager:
    """مدير الحالة - يحفظ الحالة في ملف"""

    def __init__(self, state_file: str = ".codeforge_state.json"):
        self.state_file = state_file
        self.state = self._load()

    def _load(self) -> ProjectState:
        """تحميل الحالة من الملف"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return ProjectState.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return ProjectState()

    def save(self):
        """حفظ الحالة في الملف"""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)

    def get_state(self) -> ProjectState:
        """الحصول على الحالة الحالية"""
        return self.state

    def start_task(self, description: str) -> int:
        """بدء مهمة جديدة"""
        task_num = self.state.start_task(description)
        self.save()
        return task_num

    def set_agent(self, agent_type: AgentType):
        """تعيين الوكيل النشط"""
        self.state.set_agent(agent_type)
        self.save()

    def record_attempt(self, agent_type: AgentType) -> int:
        """تسجيل محاولة"""
        attempts = self.state.record_attempt(agent_type)
        self.save()
        return attempts

    def get_attempts(self, agent_type: AgentType) -> int:
        """الحصول على عدد المحاولات"""
        return self.state.get_attempts(agent_type)

    def update_status(self, status: TaskStatus):
        """تحديث الحالة"""
        self.state.update_status(status)
        self.save()

    def record_decision(self, agent: str, content: str, impact: str):
        """تسجيل قرار"""
        self.state.record_decision(agent, content, impact)
        self.save()

    def record_commit(self, message: str, commit_hash: str):
        """تسجيل commit"""
        self.state.record_commit(message, commit_hash)
        self.save()


# ============================================================
# Instance Global
# ============================================================

state_manager = StateManager()


# ============================================================
# Helper Functions
# ============================================================

def get_state() -> ProjectState:
    """الحصول على الحالة الحالية"""
    return state_manager.get_state()


def get_state_summary() -> str:
    """الحصول على ملخص نصي للحالة"""
    return state_manager.get_state().summary()


def get_state_dict() -> dict:
    """الحصول على الحالة كـ dictionary"""
    return state_manager.get_state().to_dict()


def increment_completed() -> int:
    """زيادة عدد المهام المنجزة"""
    state_manager.state.increment_completed_tasks()
    state_manager.save()
    return state_manager.state.completed_tasks


def add_history(task_id: str, description: str, status: str):
    """إضافة مهمة إلى السجل"""
    state_manager.state.add_to_history(task_id, description, status)
    state_manager.save()


def start_new_task(description: str) -> int:
    """بدء مهمة جديدة"""
    return state_manager.start_task(description)


def set_active_agent(agent_type: AgentType):
    """تعيين الوكيل النشط"""
    state_manager.set_agent(agent_type)


def record_attempt(agent_type: AgentType) -> int:
    """تسجيل محاولة"""
    return state_manager.record_attempt(agent_type)


def check_3_attempts_limit(agent_type: AgentType) -> bool:
    """فحص قاعدة الـ 3 محاولات"""
    return state_manager.get_attempts(agent_type) >= 3


def update_task_status(status: TaskStatus):
    """تحديث حالة المهمة"""
    state_manager.update_status(status)


def record_agent_decision(agent: str, content: str, impact: str):
    """تسجيل قرار وكيل"""
    state_manager.record_decision(agent, content, impact)


def record_git_commit(message: str, commit_hash: str):
    """تسجيل commit"""
    state_manager.record_commit(message, commit_hash)


def get_task_id() -> Optional[str]:
    """الحصول على معرف المهمة الحالية"""
    return state_manager.get_state().current_task_id
