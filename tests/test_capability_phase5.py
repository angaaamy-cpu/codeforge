"""
Phase 5 - Capability System (files/git scope only)
====================================================
يثبت أن أدوات files/git الحقيقية مربوطة فعلياً بالقدرات المُسجَّلة، وأن
"terminal"/"http" تبقيان بلا أي أداة (متوافق مع مراجعة الأمان).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_files_capability_has_real_tools():
    import src.Core as core
    cap = core.CapabilityRegistry().get("files")
    assert set(cap.tools.keys()) >= {"read", "write", "list", "delete", "exists"}


def test_git_capability_has_real_tools():
    import src.Core as core
    cap = core.CapabilityRegistry().get("git")
    assert set(cap.tools.keys()) >= {"status", "changed_files", "current_branch", "auto_commit"}


def test_git_capability_has_no_push_tool():
    """قرار متعمَّد: لا أداة push مربوطة تلقائياً (GIT_AUTO_PUSH=False)."""
    import src.Core as core
    cap = core.CapabilityRegistry().get("git")
    assert "auto_push" not in cap.tools
    assert "push" not in cap.tools


def test_terminal_capability_still_has_zero_tools():
    """قاعدة أمان صريحة (TERMINAL_CAPABILITY_SECURITY_REVIEW.md):
    Phase 5 لا يمس terminal إطلاقاً."""
    import src.Core as core
    cap = core.CapabilityRegistry().get("terminal")
    assert cap.tools == {}


def test_http_and_search_capabilities_unaffected():
    """تأكيد أن Phase 5 لم يوسّع النطاق خارج files/git."""
    import src.Core as core
    for name in ("http", "search", "documentation", "secrets"):
        cap = core.CapabilityRegistry().get(name)
        if cap is not None:
            assert cap.tools == {}, f"'{name}' اكتسب أدوات لم تكن مخطَّطة في نطاق Phase 5"


def test_files_read_write_tool_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    for mod in list(sys.modules):
        if mod.startswith("src.Core") or mod == "src.path_service":
            del sys.modules[mod]
    import src.Core as core
    cap = core.CapabilityRegistry().get("files")
    write_tool = cap.get_tool("write")
    read_tool = cap.get_tool("read")
    write_tool.execute(path="phase5.txt", content="hello from capability tool")
    assert read_tool.execute(path="phase5.txt") == "hello from capability tool"


def test_git_status_tool_returns_string():
    import src.Core as core
    cap = core.CapabilityRegistry().get("git")
    status_tool = cap.get_tool("status")
    result = status_tool.execute()
    assert isinstance(result, str)
