"""
CodeForge - Phase 8
===================
الواجهة الموحدة للمنصة
"""

from src.build_engine import BuildEngine
from src.build_result import BuildResult


class CodeForge:
    """منصة CodeForge - الواجهة الموحدة"""

    def __init__(self):
        self.engine = BuildEngine()

    def build(self, description: str) -> BuildResult:
        """يبني مشروعاً كاملاً من وصف"""
        return self.engine.execute(description)

    @property
    def version(self) -> str:
        return "1.0.0"

    def __repr__(self) -> str:
        return f"CodeForge(v{self.version})"


# ============================================================
# Instance Global
# ============================================================

codeforge = CodeForge()


# ============================================================
# Helper Functions
# ============================================================

def build(description: str) -> BuildResult:
    """بناء مشروع من وصف"""
    return codeforge.build(description)
