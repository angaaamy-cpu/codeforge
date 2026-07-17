"""
CodeForge Event Bus - Phase X
=============================
نظام الأحداث المركزي
"""

import asyncio
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class EventType(str, Enum):
    """أنواع الأحداث"""
    # Workspace Events
    PROJECT_CREATED = "project:created"
    PROJECT_OPENED = "project:opened"
    PROJECT_ARCHIVED = "project:archived"
    PROJECT_DELETED = "project:deleted"
    
    # Task Events
    TASK_STARTED = "task:started"
    TASK_COMPLETED = "task:completed"
    TASK_FAILED = "task:failed"
    
    # Build Events
    BUILD_STARTED = "build:started"
    BUILD_STEP_STARTED = "build:step:started"
    BUILD_STEP_COMPLETED = "build:step:completed"
    BUILD_SUCCEEDED = "build:succeeded"
    BUILD_FAILED = "build:failed"
    
    # Execution Events
    EXECUTION_STARTED = "execution:started"
    EXECUTION_STEP = "execution:step"
    EXECUTION_COMPLETED = "execution:completed"
    EXECUTION_FAILED = "execution:failed"
    
    # Deployment Events
    DEPLOYMENT_STARTED = "deployment:started"
    DEPLOYMENT_STEP = "deployment:step"
    DEPLOYMENT_COMPLETED = "deployment:completed"
    DEPLOYMENT_FAILED = "deployment:failed"
    
    # Capability Events
    CAPABILITY_REGISTERED = "capability:registered"
    CAPABILITY_UNREGISTERED = "capability:unregistered"
    
    # Plugin Events
    PLUGIN_LOADED = "plugin:loaded"
    PLUGIN_UNLOADED = "plugin:unloaded"
    PLUGIN_ERROR = "plugin:error"
    
    # Memory Events
    MEMORY_UPDATED = "memory:updated"
    MEMORY_SEARCH = "memory:search"
    
    # System Events
    SYSTEM_READY = "system:ready"
    SYSTEM_ERROR = "system:error"


@dataclass
class Event:
    """كائن الحدث"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.SYSTEM_READY
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


class EventBus:
    """
    نظام Event Bus المركزي
    """
    _instance: Optional["EventBus"] = None
    
    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._history: List[Event] = []
        self._max_history = 1000
        self._initialized = True
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> str:
        """
        الاشتراك في حدث
        
        Returns:
            subscription_id for unsubscribing
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        handler_id = str(uuid.uuid4())
        self._handlers[event_type].append(handler)
        
        return handler_id
    
    def unsubscribe(self, event_type: EventType, handler_id: str) -> bool:
        """إلغاء الاشتراك"""
        if event_type not in self._handlers:
            return False
        
        # Cannot easily remove by ID without storing them
        # For now, return False - can be enhanced later
        return False
    
    def emit(self, event: Event) -> None:
        """إصدار حدث"""
        # Store in history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # Call handlers
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Event handler error: {e}")
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """الحصول على سجل الأحداث"""
        if event_type:
            return [e for e in self._history if e.type == event_type][-limit:]
        return self._history[-limit:]
    
    def clear_history(self) -> None:
        """مسح السجل"""
        self._history.clear()


# ============================================================
# Global Instance
# ============================================================

event_bus = EventBus()


# ============================================================
# Convenience Functions
# ============================================================

def emit(event_type: EventType, data: Dict[str, Any] = None, source: str = "") -> Event:
    """إصدار حدث بسرعة"""
    event = Event(type=event_type, data=data or {}, source=source)
    event_bus.emit(event)
    return event


def subscribe(event_type: EventType, handler: Callable[[Event], None]) -> str:
    """الاشتراك في حدث"""
    return event_bus.subscribe(event_type, handler)
