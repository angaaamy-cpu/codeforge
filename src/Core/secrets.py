"""
CodeForge Secrets Manager - Phase X
====================================
إدارة الأسرار
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from src.Core.event_bus import EventType, emit


@dataclass
class Secret:
    """كائن السر"""
    name: str
    value: str  # Only in memory, never persisted
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }


@dataclass
class SecretMetadata:
    """metadata السر (بدون القيمة)"""
    name: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }
    
    @classmethod
    def from_secret(cls, secret: Secret) -> "SecretMetadata":
        return cls(
            name=secret.name,
            description=secret.description,
            metadata=secret.metadata,
            created_at=secret.created_at,
            last_used=secret.last_used,
        )


class SecretsManager:
    """
    مدير الأسرار
    ⚠️ لا تحفظ الأسرار في Git أبداً
    """
    _instance: Optional["SecretsManager"] = None
    
    def __new__(cls, secrets_path: str = None) -> "SecretsManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, secrets_path: str = None):
        if self._initialized:
            return
        
        # Secrets stored in memory only
        # Metadata stored in file (without values)
        self.secrets_path = Path(secrets_path) if secrets_path else Path(".secrets")
        self.secrets_path.mkdir(parents=True, exist_ok=True)
        
        # Metadata file (values never stored)
        self.metadata_file = self.secrets_path / ".metadata.json"
        self._metadata: Dict[str, SecretMetadata] = {}
        self._load_metadata()
        
        # Runtime secrets (in memory only)
        self._secrets: Dict[str, Secret] = {}
        
        self._initialized = True
    
    def _load_metadata(self) -> None:
        """تحميل metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                data = json.load(f)
                for name, info in data.items():
                    info["created_at"] = datetime.fromisoformat(info["created_at"])
                    if info.get("last_used"):
                        info["last_used"] = datetime.fromisoformat(info["last_used"])
                    self._metadata[name] = SecretMetadata(**info)
    
    def _save_metadata(self) -> None:
        """حفظ metadata"""
        data = {name: meta.to_dict() for name, meta in self._metadata.items()}
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def add(
        self,
        name: str,
        value: str,
        description: str = "",
        metadata: Dict[str, Any] = None,
    ) -> Secret:
        """
        إضافة سر جديد
        
        ⚠️ لا تحفظ القيمة في ملف
        """
        if name in self._secrets:
            raise ValueError(f"Secret '{name}' already exists")
        
        # Create secret
        secret = Secret(
            name=name,
            value=value,
            description=description,
            metadata=metadata or {},
        )
        
        # Store in memory only
        self._secrets[name] = secret
        
        # Save metadata (no value!)
        self._metadata[name] = SecretMetadata.from_secret(secret)
        self._save_metadata()
        
        return secret
    
    def get(self, name: str) -> Optional[Secret]:
        """الحصول على سر"""
        if name not in self._secrets:
            return None
        
        secret = self._secrets[name]
        secret.last_used = datetime.now()
        self._metadata[name].last_used = secret.last_used
        self._save_metadata()
        
        return secret
    
    def get_value(self, name: str) -> Optional[str]:
        """الحصول على قيمة السر فقط"""
        secret = self.get(name)
        return secret.value if secret else None
    
    def remove(self, name: str) -> bool:
        """حذف سر"""
        if name not in self._secrets:
            return False
        
        # Remove from memory
        del self._secrets[name]
        
        # Remove metadata
        del self._metadata[name]
        self._save_metadata()
        
        return True
    
    def list_all(self) -> List[SecretMetadata]:
        """قائمة كل الأسرار (بدون قيم)"""
        return list(self._metadata.values())
    
    def exists(self, name: str) -> bool:
        """فحص وجود سر"""
        return name in self._secrets
    
    def inject_to_env(self, name: str) -> bool:
        """حقن السر في environment variables"""
        secret = self.get(name)
        if not secret:
            return False
        
        os.environ[name] = secret.value
        return True
    
    def inject_all_to_env(self) -> None:
        """حقن كل الأسرار في environment"""
        for name, secret in self._secrets.items():
            os.environ[name] = secret.value
    
    def get_by_prefix(self, prefix: str) -> List[SecretMetadata]:
        """الأسرار التي تبدأ بprefix معين"""
        return [
            meta for name, meta in self._metadata.items()
            if name.startswith(prefix)
        ]


# ============================================================
# Global Instance
# ============================================================

secrets_manager = SecretsManager()
