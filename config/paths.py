"""
CodeForge Paths Configuration - Phase 5
======================================
جميع مسارات المشروع في مكان واحد
"""

import os
from pathlib import Path

# Root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# Core directories
SRC_DIR = ROOT_DIR / "src"
DOCS_DIR = ROOT_DIR / "docs"
AGENTS_DIR = ROOT_DIR / "agents"
MEMORY_DIR = ROOT_DIR / "memory"
TESTS_DIR = ROOT_DIR / "tests"
WORKSPACE_DIR = ROOT_DIR / "workspace"
PROJECTS_DIR = ROOT_DIR / "projects"
CONFIG_DIR = ROOT_DIR / "config"
STATIC_DIR = ROOT_DIR / "static"
TEMPLATES_DIR = ROOT_DIR / "templates"

# Sub-directories
DOCS_ADR_DIR = DOCS_DIR / "adr"
DOCS_REPORTS_DIR = DOCS_DIR / "reports"
DOCS_PROJECTS_DIR = DOCS_DIR / "projects"
PROJECTS_ARCHIVE_DIR = PROJECTS_DIR / "archive"

# Files
STATE_FILE = ROOT_DIR / ".codeforge_state.json"
EVENTS_LOG = ROOT_DIR / "logs" / "events.log"
PROGRESS_FILE = DOCS_DIR / "progress.md"
README_FILE = ROOT_DIR / "README.md"
PYPROJECT_FILE = ROOT_DIR / "pyproject.toml"

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
