"""
CodeForge Settings - Phase 5
============================
إعدادات المنصة المركزية
"""

import os
from pathlib import Path
from datetime import timedelta

# Import paths and models
from config.paths import (
    ROOT_DIR, SRC_DIR, DOCS_DIR, PROJECTS_DIR, WORKSPACE_DIR,
    STATE_FILE, EVENTS_LOG, PROGRESS_FILE,
    DOCS_ADR_DIR, DOCS_REPORTS_DIR, DOCS_PROJECTS_DIR,
    PROJECTS_ARCHIVE_DIR, STATIC_DIR, TEMPLATES_DIR,
    get_paths
)
from config.models import DEFAULT_MODEL, get_model, get_model_name

# ============================================================
# Application Settings
# ============================================================

APP_NAME = "CodeForge"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "منصة بناء المشاريع بالذكاء الاصطناعي"

# Phase
CURRENT_PHASE = "phase8.1"

# ============================================================
# Flask Settings
# ============================================================

FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "codeforge-secret-key-change-in-production")

# ============================================================
# Agent Settings
# ============================================================

MAX_ATTEMPTS = 3  # قاعدة الـ 3 محاولات
AGENT_TIMEOUT = 300  # 5 دقائق

# Agent Roles
AGENT_ROLES = {
    "manager": "مدير المشروع",
    "architect": "المعماري",
    "developer": "المطور",
    "qa": "ضمان الجودة",
}

# ============================================================
# Git Settings
# ============================================================

GIT_AUTO_COMMIT = True
GIT_AUTO_PUSH = False  # لا push تلقائي
GIT_COMMIT_PREFIX = "[CodeForge]"
GIT_MAX_COMMIT_MESSAGE = 100

# ============================================================
# Logging Settings
# ============================================================

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M"

# ============================================================
# Storage Settings
# ============================================================

STORAGE_BACKEND = "markdown"  # markdown or chromadb
CHROMADB_PATH = ROOT_DIR / "data" / "chromadb"

# ============================================================
# Project Settings
# ============================================================

ACTIVE_PROJECT_FILE = ROOT_DIR / ".active_project"
MAX_PROJECTS = 100

# ============================================================
# Task Settings
# ============================================================

TASK_REPORT_DIR = DOCS_REPORTS_DIR
TASK_ID_PREFIX = "task"
TASK_ID_PADDING = 3

# ============================================================
# Memory Settings
# ============================================================

MEMORY_SEARCH_LIMIT = 10
MEMORY_CONTEXT_FILES = [
    "docs/progress.md",
    "docs/roadmap.md",
    "docs/architecture.md",
]

# ============================================================
# Helper Functions
# ============================================================

def get_llm_config():
    """الحصول على إعدادات LLM"""
    model = get_model(DEFAULT_MODEL)
    return {
        "model": model.full_name,
        "api_key_env": model.api_key_env,
        "max_tokens": model.max_tokens,
        "temperature": model.temperature,
    }


def ensure_directories():
    """التأكد من وجود جميع المجلدات"""
    dirs = [
        PROJECTS_DIR,
        PROJECTS_ARCHIVE_DIR,
        DOCS_PROJECTS_DIR,
        DOCS_REPORTS_DIR,
        ROOT_DIR / "logs",
        CHROMADB_PATH,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


# Initialize directories on import
ensure_directories()
