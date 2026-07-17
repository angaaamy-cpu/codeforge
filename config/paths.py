"""
CodeForge Paths Configuration - Production Ready
==============================================
جميع مسارات المشروع في مكان واحد
Uses PathService for centralized path management
"""

import os
from pathlib import Path

# Import from PathService to ensure consistency
from src.path_service import WORKSPACE_ROOT, path_service

# Root directory (from PathService)
ROOT_DIR = WORKSPACE_ROOT

# Core directories (use PathService properties)
SRC_DIR = path_service.root / "src"
DOCS_DIR = path_service.docs_dir
AGENTS_DIR = path_service.root / "agents"
MEMORY_DIR = path_service.root / "memory"
TESTS_DIR = path_service.root / "tests"
WORKSPACE_DIR = path_service.root / "workspace"
PROJECTS_DIR = path_service.projects_dir
CONFIG_DIR = path_service.root / "config"
STATIC_DIR = path_service.root / "static"
TEMPLATES_DIR = path_service.root / "templates"

# Sub-directories
DOCS_ADR_DIR = DOCS_DIR / "adr"
DOCS_REPORTS_DIR = DOCS_DIR / "reports"
DOCS_PROJECTS_DIR = DOCS_DIR / "projects"
PROJECTS_ARCHIVE_DIR = PROJECTS_DIR / "archive"

# Files
STATE_FILE = path_service.root / ".codeforge_state.json"
EVENTS_LOG = path_service.logs_dir / "events.log"
PROGRESS_FILE = DOCS_DIR / "progress.md"
README_FILE = path_service.root / "README.md"
PYPROJECT_FILE = path_service.root / "pyproject.toml"

# Flask files
APP_FILE = SRC_DIR / "app.py"

# Storage
STORAGE_DIR = SRC_DIR / "storage"

# Get paths as strings
def get_paths():
    """Return all paths as strings"""
    return {
        "root": str(ROOT_DIR),
        "src": str(SRC_DIR),
        "docs": str(DOCS_DIR),
        "projects": str(PROJECTS_DIR),
        "workspace": str(WORKSPACE_DIR),
        "state_file": str(STATE_FILE),
        "events_log": str(EVENTS_LOG),
    }
