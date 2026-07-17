"""
CodeForge Version - Phase 6A
===========================
إدارة الإصدارات
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


# Version Info
VERSION = "1.0.0"
PHASE = "6A"
BUILD_DATE = "2026-07-17"
BUILD_NUMBER = 6


@dataclass
class VersionInfo:
    """معلومات الإصدار"""
    version: str
    phase: str
    build_date: str
    build_number: int
    changelog: List[str]

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "phase": self.phase,
            "build_date": self.build_date,
            "build_number": self.build_number,
            "changelog": self.changelog,
        }

    def __str__(self) -> str:
        return f"CodeForge v{self.version} ({self.phase}) - Build #{self.build_number}"


# Phase 6A Changelog
CHANGELOG = [
    "# Phase 6A: Production-ready Foundation",
    "",
    "## Features",
    "- Advanced logging system (events.log, errors.log, agent.log)",
    "- Model Router with fallback strategy",
    "- Security Agent for code scanning",
    "- Documentation Agent for auto-updating docs",
    "- Weekly Summarizer",
    "- ChromaDB as optional layer",
    "- Version tracking",
    "",
    "## Improvements",
    "- Unified config system",
    "- Project manager",
    "- Enhanced memory search",
    "- Better dashboard UI",
    "",
    "## Architecture",
    "- ADR-006: Production-ready decisions",
]


def get_version() -> VersionInfo:
    """الحصول على معلومات الإصدار"""
    return VersionInfo(
        version=VERSION,
        phase=PHASE,
        build_date=BUILD_DATE,
        build_number=BUILD_NUMBER,
        changelog=CHANGELOG,
    )


def get_version_string() -> str:
    """الحصول على نص الإصدار"""
    return str(get_version())


def get_version_dict() -> Dict:
    """الحصول على الإصدار كـ dict"""
    return get_version().to_dict()


def get_build_info() -> Dict:
    """معلومات البناء"""
    return {
        "version": VERSION,
        "phase": PHASE,
        "build_date": BUILD_DATE,
        "build_number": BUILD_NUMBER,
        "timestamp": datetime.now().isoformat(),
    }
