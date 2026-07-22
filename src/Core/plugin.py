"""
CodeForge Plugin System - Phase X
==================================
نظام الإضافات
"""

import os
import importlib.util
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

from src.Core.event_bus import EventType, emit
from src.Core.capability import Capability, CapabilityRegistry


@dataclass
class PluginManifest:
    """manifest الإضافة"""
    name: str
    version: str
    description: str
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    entry_point: str = "__init__.py"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            dependencies=data.get("dependencies", []),
            permissions=data.get("permissions", []),
            capabilities=data.get("capabilities", []),
            entry_point=data.get("entry_point", "__init__.py"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
            "capabilities": self.capabilities,
            "entry_point": self.entry_point,
        }


class BasePlugin(ABC):
    """
    الفئة الأساسية لكل إضافة
    """
    manifest: PluginManifest
    
    @abstractmethod
    def on_load(self) -> None:
        """استدعاء عند تحميل الإضافة"""
        pass
    
    @abstractmethod
    def on_unload(self) -> None:
        """استدعاء عند إلغاء تحميل الإضافة"""
        pass
    
    def get_capabilities(self) -> List[Capability]:
        """القدرات التي توفرها الإضافة"""
        return []


class Plugin:
    """كائن الإضافة"""
    def __init__(
        self,
        manifest: PluginManifest,
        path: str,
        module: Any = None,
        instance: BasePlugin = None,
    ):
        self.manifest = manifest
        self.path = path
        self.module = module
        self.instance = instance
        self.loaded_at: datetime = datetime.now()
        self.enabled: bool = True
        self.capabilities: List[Capability] = []
    
    def load(self) -> bool:
        """تحميل الإضافة"""
        try:
            # Import module
            spec = importlib.util.spec_from_file_location(
                self.manifest.name,
                os.path.join(self.path, self.manifest.entry_point)
            )
            if spec and spec.loader:
                self.module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.module)
                
                # Get instance if available
                if hasattr(self.module, "Plugin"):
                    self.instance = self.module.Plugin()
                    self.instance.manifest = self.manifest
                    self.instance.on_load()
                    
                    # Get capabilities
                    self.capabilities = self.instance.get_capabilities()
                    
                    # Register capabilities
                    registry = CapabilityRegistry()
                    for cap in self.capabilities:
                        registry.register(cap)
                
                emit(EventType.PLUGIN_LOADED, {
                    "name": self.manifest.name,
                    "version": self.manifest.version,
                    "capabilities": [c.name for c in self.capabilities],
                })
                
                return True
        except Exception as e:
            emit(EventType.PLUGIN_ERROR, {
                "name": self.manifest.name,
                "error": str(e),
            })
            return False
        
        return False
    
    def unload(self) -> bool:
        """إلغاء تحميل الإضافة"""
        try:
            # Unregister capabilities
            registry = CapabilityRegistry()
            for cap in self.capabilities:
                registry.unregister(cap.name)
            
            # Call unload hook
            if self.instance:
                self.instance.on_unload()
            
            emit(EventType.PLUGIN_UNLOADED, {
                "name": self.manifest.name,
            })
            
            self.enabled = False
            return True
        except Exception as e:
            emit(EventType.PLUGIN_ERROR, {
                "name": self.manifest.name,
                "error": str(e),
            })
            return False


class PluginManager:
    """
    مدير الإضافات
    """
    _instance: Optional["PluginManager"] = None
    
    def __new__(cls, plugins_dir: str = None) -> "PluginManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, plugins_dir: str = None):
        if self._initialized:
            return
        
        self.plugins_dir = Path(plugins_dir) if plugins_dir else Path("plugins")
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        self._plugins: Dict[str, Plugin] = {}
        self._manifests: Dict[str, PluginManifest] = {}
        self._initialized = True
    
    def _load_manifest(self, plugin_path: Path) -> Optional[PluginManifest]:
        """تحميل manifest"""
        manifest_file = plugin_path / "manifest.json"
        if not manifest_file.exists():
            return None
        
        with open(manifest_file, "r") as f:
            data = json.load(f)
            return PluginManifest.from_dict(data)
    
    def discover(self) -> List[PluginManifest]:
        """اكتشاف الإضافات"""
        manifests = []
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and (item / "manifest.json").exists():
                manifest = self._load_manifest(item)
                if manifest:
                    manifests.append(manifest)
                    self._manifests[manifest.name] = manifest
        
        return manifests
    
    def load(self, name: str) -> bool:
        """تحميل إضافة"""
        if name in self._plugins:
            return True  # Already loaded
        
        plugin_path = self.plugins_dir / name
        if not plugin_path.exists():
            return False
        
        manifest = self._load_manifest(plugin_path)
        if not manifest:
            return False
        
        plugin = Plugin(manifest=manifest, path=str(plugin_path))
        
        if plugin.load():
            self._plugins[name] = plugin
            return True
        
        return False
    
    def unload(self, name: str) -> bool:
        """إلغاء تحميل إضافة"""
        if name not in self._plugins:
            return False
        
        plugin = self._plugins[name]
        if plugin.unload():
            del self._plugins[name]
            return True
        
        return False
    
    def enable(self, name: str) -> bool:
        """تفعيل إضافة"""
        if name not in self._plugins:
            return self.load(name)
        
        self._plugins[name].enabled = True
        return True
    
    def disable(self, name: str) -> bool:
        """تعطيل إضافة"""
        if name not in self._plugins:
            return False
        
        return self._plugins[name].unload()
    
    def get(self, name: str) -> Optional[Plugin]:
        """الحصول على إضافة"""
        return self._plugins.get(name)
    
    def list_all(self) -> List[PluginManifest]:
        """قائمة كل الإضافات"""
        return list(self._manifests.values())
    
    def list_loaded(self) -> List[Plugin]:
        """قائمة الإضافات المحملة"""
        return list(self._plugins.values())
    
    def list_enabled(self) -> List[Plugin]:
        """قائمة الإضافات المفعلة"""
        return [p for p in self._plugins.values() if p.enabled]


# ============================================================
# Global Instance
# ============================================================

plugin_manager = PluginManager()
