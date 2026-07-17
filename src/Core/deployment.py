"""
CodeForge Deployment Manager - Phase X
=======================================
إدارة النشر
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.Core.event_bus import EventType, emit


class DeploymentPlatform(str, Enum):
    """منصات النشر"""
    RAILWAY = "railway"
    RENDER = "render"
    HEROKU = "heroku"
    DOCKER = "docker"
    LOCAL = "local"


class DeploymentStatus(str, Enum):
    """حالة النشر"""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DeploymentConfig:
    """إعدادات النشر"""
    platform: DeploymentPlatform
    project_path: str
    region: str = "us-east"
    branch: str = "main"
    build_command: str = "pip install -e ."
    start_command: str = "gunicorn src.app:app --bind 0.0.0.0:$PORT"
    env_vars: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Deployment:
    """كائن النشر"""
    id: str
    platform: DeploymentPlatform
    project_name: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    url: str = ""
    logs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "platform": self.platform.value if isinstance(self.platform, DeploymentPlatform) else self.platform,
            "project_name": self.project_name,
            "status": self.status.value if isinstance(self.status, DeploymentStatus) else self.status,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "metadata": self.metadata,
        }


class DeploymentManager:
    """
    مدير النشر
    """
    _instance: Optional["DeploymentManager"] = None
    
    def __new__(cls) -> "DeploymentManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._deployments: Dict[str, Deployment] = {}
        self._platform_configs: Dict[DeploymentPlatform, Dict[str, Any]] = {
            DeploymentPlatform.RAILWAY: {
                "default_command": "gunicorn src.app:app --bind 0.0.0.0:${PORT} --workers 2",
                "builder": "NIXPACKS",
            },
            DeploymentPlatform.RENDER: {
                "default_command": "gunicorn src.app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4",
                "health_check": "/api/health",
            },
            DeploymentPlatform.HEROKU: {
                "default_command": "gunicorn src.app:app --bind 0.0.0.0:$PORT",
            },
        }
        
        self._initialized = True
    
    def deploy(
        self,
        project_name: str,
        platform: DeploymentPlatform,
        config: DeploymentConfig = None,
    ) -> Deployment:
        """
        بدء نشر
        
        Args:
            project_name: اسم المشروع
            platform: المنصة
            config: إعدادات إضافية
            
        Returns:
            Deployment
        """
        import uuid
        
        deployment = Deployment(
            id=str(uuid.uuid4())[:8],
            platform=platform,
            project_name=project_name,
        )
        
        self._deployments[deployment.id] = deployment
        
        emit(EventType.DEPLOYMENT_STARTED, {
            "deployment_id": deployment.id,
            "project": project_name,
            "platform": platform.value if isinstance(platform, DeploymentPlatform) else platform,
        })
        
        # Note: Actual deployment requires credentials
        # This is a placeholder that documents the interface
        
        return deployment
    
    def status(self, deployment_id: str) -> Optional[Deployment]:
        """الحصول على حالة نشر"""
        return self._deployments.get(deployment_id)
    
    def logs(self, deployment_id: str) -> List[str]:
        """الحصول على سجلات نشر"""
        deployment = self._deployments.get(deployment_id)
        return deployment.logs if deployment else []
    
    def redeploy(self, deployment_id: str) -> bool:
        """إعادة نشر"""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return False
        
        # Reset status
        deployment.status = DeploymentStatus.PENDING
        deployment.error = ""
        deployment.logs = []
        deployment.created_at = datetime.now()
        
        emit(EventType.DEPLOYMENT_STARTED, {
            "deployment_id": deployment.id,
            "redeploy": True,
        })
        
        return True
    
    def cancel(self, deployment_id: str) -> bool:
        """إلغاء نشر"""
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return False
        
        deployment.status = DeploymentStatus.CANCELLED
        deployment.completed_at = datetime.now()
        
        return True
    
    def list_deployments(self, project_name: str = None) -> List[Deployment]:
        """قائمة عمليات النشر"""
        if project_name:
            return [d for d in self._deployments.values() if d.project_name == project_name]
        return list(self._deployments.values())
    
    def get_platform_config(self, platform: DeploymentPlatform) -> Dict[str, Any]:
        """الحصول على إعدادات المنصة"""
        return self._platform_configs.get(platform, {})
    
    def generate_render_yaml(self, project_path: str, **kwargs) -> str:
        """توليد render.yaml"""
        config = kwargs.get("config", DeploymentConfig(
            platform=DeploymentPlatform.RENDER,
            project_path=project_path,
        ))
        
        yaml = f"""services:
  - type: web
    name: {config.project_path}
    runtime: python
    region: {config.region}
    buildCommand: {config.build_command}
    startCommand: {config.start_command}
    envVars:
      - key: PORT
        value: 10000
      - key: FLASK_ENV
        value: production
"""
        return yaml
    
    def generate_railway_json(self, project_path: str, **kwargs) -> str:
        """توليد railway.json"""
        config = kwargs.get("config", DeploymentConfig(
            platform=DeploymentPlatform.RAILWAY,
            project_path=project_path,
        ))
        
        import json
        data = {
            "$schema": "https://railway.app/railway.schema.json",
            "build": {
                "builder": "NIXPACKS",
                "buildCommand": config.build_command,
                "startCommand": config.start_command,
            },
            "deploy": {
                "numReplicas": 1,
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10,
                "healthCheckPath": "/api/health",
            },
            "port": 8000,
        }
        
        return json.dumps(data, indent=2)
    
    def generate_dockerfile(self, project_path: str, **kwargs) -> str:
        """توليد Dockerfile"""
        dockerfile = f"""FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

EXPOSE 8000

CMD ["gunicorn", "src.app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
"""
        return dockerfile


# ============================================================
# Global Instance
# ============================================================

deployment_manager = DeploymentManager()
