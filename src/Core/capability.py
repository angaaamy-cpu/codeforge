"""
CodeForge Capability System - Phase X
=====================================
نظام القدرات المبني على Mermaid spec
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import inspect

from src.Core.event_bus import EventType, emit


class Permission(str, Enum):
    """الصلاحيات"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class Tool:
    """أداة واحدة"""
    name: str
    description: str
    handler: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self, **kwargs) -> Any:
        """تنفيذ الأداة"""
        return self.handler(**kwargs)


@dataclass
class Capability:
    """
    Capability = مجموعة أدوات + صلاحيات + وصف
    """
    name: str
    description: str
    version: str = "1.0.0"
    permissions: List[Permission] = field(default_factory=list)
    tools: Dict[str, Tool] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    
    def add_tool(self, name: str, description: str, handler: Callable) -> None:
        """إضافة أداة"""
        self.tools[name] = Tool(
            name=name,
            description=description,
            handler=handler,
        )
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """الحصول على أداة"""
        return self.tools.get(name)
    
    def has_permission(self, permission: Permission) -> bool:
        """فحص صلاحية"""
        return permission in self.permissions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "permissions": [p.value for p in self.permissions],
            "tools": list(self.tools.keys()),
            "config": self.config,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }


class CapabilityRegistry:
    """
    سجل القدرات - Component Registry
    """
    _instance: Optional["CapabilityRegistry"] = None
    
    def __new__(cls) -> "CapabilityRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._capabilities: Dict[str, Capability] = {}
        self._initialized = True
    
    def register(self, capability: Capability) -> None:
        """تسجيل قدرة"""
        self._capabilities[capability.name] = capability
        emit(EventType.CAPABILITY_REGISTERED, {"name": capability.name})
    
    def unregister(self, name: str) -> bool:
        """إلغاء تسجيل قدرة"""
        if name in self._capabilities:
            del self._capabilities[name]
            emit(EventType.CAPABILITY_UNREGISTERED, {"name": name})
            return True
        return False
    
    def get(self, name: str) -> Optional[Capability]:
        """الحصول على قدرة"""
        return self._capabilities.get(name)
    
    def list_all(self) -> List[Capability]:
        """قائمة كل القدرات"""
        return list(self._capabilities.values())
    
    def list_by_tag(self, tag: str) -> List[Capability]:
        """القدرات حسب tag"""
        return [c for c in self._capabilities.values() if tag in c.tags]
    
    def search(self, query: str) -> List[Capability]:
        """بحث"""
        query_lower = query.lower()
        return [
            c for c in self._capabilities.values()
            if query_lower in c.name.lower() or query_lower in c.description.lower()
        ]


# ============================================================
# Decorator
# ============================================================

def capability(
    name: str,
    description: str,
    permissions: List[Permission] = None,
    tags: List[str] = None,
):
    """
    Decorator لإنشاء قدرة بسرعة
    
    Usage:
        @capability("files", "File operations", permissions=[Permission.READ, Permission.WRITE])
        def files_handler():
            pass
    """
    def decorator(func: Callable) -> Callable:
        cap = Capability(
            name=name,
            description=description,
            permissions=permissions or [],
            tags=tags or [],
        )
        
        # Get function signature for parameters
        sig = inspect.signature(func)
        cap.config["parameters"] = {
            p.name: str(p.annotation) for p in sig.parameters.values()
        }
        
        # Add as tool with function name
        cap.add_tool(func.__name__, description, func)
        
        # Register
        registry = CapabilityRegistry()
        registry.register(cap)
        
        return func
    
    return decorator


def get_capability(name: str) -> Optional[Capability]:
    """الحصول على قدرة"""
    return CapabilityRegistry().get(name)


# ============================================================
# Built-in Capabilities
# ============================================================

def _register_builtin_capabilities():
    """تسجيل القدرات المدمجة"""
    registry = CapabilityRegistry()
    
    # Files Capability
    files_cap = Capability(
        name="files",
        description="File operations: read, write, delete, list",
        permissions=[Permission.READ, Permission.WRITE],
        tags=["core", "filesystem"],
    )
    registry.register(files_cap)
    
    # Terminal Capability
    terminal_cap = Capability(
        name="terminal",
        description="Execute shell commands",
        permissions=[Permission.EXECUTE],
        tags=["core", "system"],
    )
    registry.register(terminal_cap)
    
    # Git Capability
    git_cap = Capability(
        name="git",
        description="Git operations: clone, commit, push, pull",
        permissions=[Permission.READ, Permission.WRITE],
        tags=["core", "vcs"],
    )
    registry.register(git_cap)
    
    # HTTP Capability
    http_cap = Capability(
        name="http",
        description="HTTP requests: GET, POST, PUT, DELETE",
        permissions=[Permission.EXECUTE],
        tags=["core", "network"],
    )
    registry.register(http_cap)
    
    # Search Capability
    search_cap = Capability(
        name="search",
        description="Search in files and memory",
        permissions=[Permission.READ],
        tags=["core", "search"],
    )
    registry.register(search_cap)
    
    # Testing Capability
    testing_cap = Capability(
        name="testing",
        description="Run tests and get results",
        permissions=[Permission.EXECUTE],
        tags=["core", "qa"],
    )
    registry.register(testing_cap)
    
    # Deployment Capability
    deploy_cap = Capability(
        name="deployment",
        description="Deploy to platforms: Railway, Render, Heroku",
        permissions=[Permission.EXECUTE, Permission.WRITE],
        tags=["core", "devops"],
    )
    registry.register(deploy_cap)
    
    # Documentation Capability
    docs_cap = Capability(
        name="documentation",
        description="Generate and manage documentation",
        permissions=[Permission.READ, Permission.WRITE],
        tags=["core", "docs"],
    )
    registry.register(docs_cap)
    
    # Secrets Capability
    secrets_cap = Capability(
        name="secrets",
        description="Manage secrets and credentials",
        permissions=[Permission.ADMIN],
        tags=["core", "security"],
    )
    registry.register(secrets_cap)


# Register on import
_register_builtin_capabilities()
