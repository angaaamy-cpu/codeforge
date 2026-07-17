"""
CodeForge Core - Phase X
=========================
النواة الجديدة للمنصة
"""

from src.Core.capability import CapabilityRegistry, capability, get_capability, Capability, Tool, Permission
from src.Core.event_bus import EventBus, event_bus, emit, subscribe, EventType, Event
from src.Core.workspace import WorkspaceManager, workspace_manager, WorkspaceMetadata
from src.Core.execution import ExecutionEngine, execution_engine, ExecutionContext, ExecutionStep, ExecutionStatus
from src.Core.memory import ProjectMemory, project_memory, MemoryEntry
from src.Core.plugin import PluginManager, plugin_manager, BasePlugin, Plugin, PluginManifest
from src.Core.secrets import SecretsManager, secrets_manager, Secret, SecretMetadata
from src.Core.deployment import DeploymentManager, deployment_manager, Deployment, DeploymentPlatform, DeploymentStatus, DeploymentConfig

__all__ = [
    # Capability System
    "CapabilityRegistry",
    "capability",
    "get_capability",
    "Capability",
    "Tool",
    "Permission",
    # Event Bus
    "EventBus",
    "event_bus",
    "emit",
    "subscribe",
    "EventType",
    "Event",
    # Workspace
    "WorkspaceManager",
    "workspace_manager",
    "WorkspaceMetadata",
    # Execution
    "ExecutionEngine",
    "execution_engine",
    "ExecutionContext",
    "ExecutionStep",
    "ExecutionStatus",
    # Memory
    "ProjectMemory",
    "project_memory",
    "MemoryEntry",
    # Plugin
    "PluginManager",
    "plugin_manager",
    "BasePlugin",
    "Plugin",
    "PluginManifest",
    # Secrets
    "SecretsManager",
    "secrets_manager",
    "Secret",
    "SecretMetadata",
    # Deployment
    "DeploymentManager",
    "deployment_manager",
    "Deployment",
    "DeploymentPlatform",
    "DeploymentStatus",
    "DeploymentConfig",
]
