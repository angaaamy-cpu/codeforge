"""
Phase 6 - Execution Engine
===========================
يثبت أن ExecutionEngine ينفّذ فعلياً عبر CapabilityRegistry (Phase 5)
بدل النجاح الوهمي السابق، وأن BLOCKED != FAILED، وأن retry يعمل فعلياً.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _fresh_engine():
    for mod in list(sys.modules):
        if mod == "src.Core.execution":
            del sys.modules[mod]
    import src.Core.execution as execmod
    return execmod


def test_legacy_string_steps_still_use_placeholder():
    """التوافق الخلفي: خطوات نصية بلا capability/tool تبقى بسلوكها القديم."""
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()
    ctx = engine.execute("legacy test", steps=["planning", "testing"])
    result = engine.run_steps(ctx)
    assert all(s.status == execmod.ExecutionStatus.COMPLETED for s in result.steps)
    assert result.steps[0].result == {"status": "success", "step": "planning"}


def test_real_capability_step_executes_actual_file_write(monkeypatch, tmp_path):
    """يثبت تنفيذاً حقيقياً فعلياً على القرص - لا نجاحاً مُختلَقاً."""
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    for mod in list(sys.modules):
        if mod.startswith("src.Core") or mod == "src.path_service":
            del sys.modules[mod]
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()

    ctx = engine.execute("real write test", steps=[
        {"name": "write-file", "capability": "files", "tool": "write",
         "params": {"path": "phase6.txt", "content": "real execution"}},
    ])
    result = engine.run_steps(ctx)
    assert result.steps[0].status == execmod.ExecutionStatus.COMPLETED
    assert (tmp_path / "phase6.txt").read_text() == "real execution"


def test_unknown_capability_is_blocked_not_failed():
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()
    ctx = engine.execute("bad capability", steps=[
        {"name": "bad-step", "capability": "does-not-exist", "tool": "whatever", "params": {}},
    ])
    result = engine.run_steps(ctx)
    assert result.steps[0].status == execmod.ExecutionStatus.BLOCKED
    assert result.steps[0].attempts == 1  # لا فائدة من إعادة محاولة شيء غير موجود


def test_unknown_tool_on_known_capability_is_blocked():
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()
    ctx = engine.execute("bad tool", steps=[
        {"name": "bad-tool-step", "capability": "files", "tool": "does-not-exist", "params": {}},
    ])
    result = engine.run_steps(ctx)
    assert result.steps[0].status == execmod.ExecutionStatus.BLOCKED


def test_real_failure_retries_up_to_max_then_fails():
    """يثبت أن self._max_retries (كان مُعرَّفاً بلا استخدام) يُطبَّق فعلياً."""
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()
    engine._max_retries = 3

    from src.Core.capability import CapabilityRegistry
    reg = CapabilityRegistry()
    files_cap = reg.get("files")

    call_count = {"n": 0}

    def _always_fails(**kwargs):
        call_count["n"] += 1
        raise RuntimeError("simulated real failure")

    files_cap.add_tool("always_fails_test_only", "for testing retry", _always_fails)

    ctx = engine.execute("retry test", steps=[
        {"name": "flaky", "capability": "files", "tool": "always_fails_test_only", "params": {}},
    ])
    result = engine.run_steps(ctx)
    assert result.steps[0].status == execmod.ExecutionStatus.FAILED
    assert result.steps[0].attempts == 3
    assert call_count["n"] == 3


def test_retry_succeeds_on_second_attempt():
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()
    engine._max_retries = 3

    from src.Core.capability import CapabilityRegistry
    reg = CapabilityRegistry()
    files_cap = reg.get("files")

    call_count = {"n": 0}

    def _fails_once(**kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("transient failure")
        return {"ok": True}

    files_cap.add_tool("fails_once_test_only", "for testing retry", _fails_once)

    ctx = engine.execute("retry-success test", steps=[
        {"name": "flaky-ok", "capability": "files", "tool": "fails_once_test_only", "params": {}},
    ])
    result = engine.run_steps(ctx)
    assert result.steps[0].status == execmod.ExecutionStatus.COMPLETED
    assert result.steps[0].attempts == 2
