"""
CodeForge Configuration - Phase 5
================================
وحدة الإعدادات المركزية
"""

from config.paths import *
from config.models import *
from config.settings import *

__all__ = [
    # Paths
    "ROOT_DIR", "SRC_DIR", "DOCS_DIR", "PROJECTS_DIR",
    "STATE_FILE", "EVENTS_LOG", "PROGRESS_FILE",
    # Models
    "MODELS", "DEFAULT_MODEL", "get_model", "get_model_name",
    # Settings
    "APP_NAME", "APP_VERSION", "CURRENT_PHASE",
    "FLASK_HOST", "FLASK_PORT",
    "MAX_ATTEMPTS", "AGENT_ROLES",
    "GIT_AUTO_COMMIT", "GIT_AUTO_PUSH",
    "get_llm_config", "ensure_directories",
]
