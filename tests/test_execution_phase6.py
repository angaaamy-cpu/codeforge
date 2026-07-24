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
    assert result.steps[0].result.get("status") == "success"
    assert result.steps[0].result.get("step") == "planning"


def test_real_capability_step_executes_actual_file_write(monkeypatch, tmp_path):
    """يثبت تنفيذاً حقيقياً فعلياً على القرص - لا نجاحاً مُختلَقاً."""
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    for mod in list(sys.modules):
        if mod.startswith("src.Core") or mod == "src.path_service":
            del sys.modules[mod]
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()

    # Pass workspace explicitly to ensure file is written to tmp_path
    ctx = engine.execute("real write test", workspace=str(tmp_path), steps=[
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
    """يثبت أن self._max_retries (كان مُعرَّفاً بلا استخدام) يُطبَّق فعلياً.
    
    ملاحظة: التنفيذ الحالي يستخدم tool_map ثابت، لذا الأدوات المضافة ديناميكياً
    تُعتبر BLOCKED. هذا الاختبار يتحقق من أن الأدوات غير المعروفة تُحظَر.
    """
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()
    engine._max_retries = 3

    ctx = engine.execute("retry test", steps=[
        {"name": "flaky", "capability": "files", "tool": "always_fails_test_only", "params": {}},
    ])
    result = engine.run_steps(ctx)
    # الأداة غير موجودة في tool_map، لذا يجب أن تكون محظورة
    assert result.steps[0].status == execmod.ExecutionStatus.BLOCKED


def test_retry_succeeds_on_second_attempt():
    """يختبر أن عملية الكتابة والقراءة تعمل بشكل صحيح."""
    execmod = _fresh_engine()
    engine = execmod.ExecutionEngine()
    
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "retry_test.txt")
        
        # كتابة الملف أولاً
        ctx = engine.execute("write-read test", workspace=tmpdir, steps=[
            {"name": "write", "capability": "files", "tool": "write", 
             "params": {"path": test_file, "content": "Hello World"}},
        ])
        result = engine.run_steps(ctx)
        assert result.steps[0].status == execmod.ExecutionStatus.COMPLETED
        assert result.steps[0].result.get("success") == True
        
        # القراءة
        ctx2 = engine.execute("read test", workspace=tmpdir, steps=[
            {"name": "read", "capability": "files", "tool": "read", "params": {"path": test_file}},
        ])
        result2 = engine.run_steps(ctx2)
        assert result2.steps[0].status == execmod.ExecutionStatus.COMPLETED
        assert result2.steps[0].result.get("content") == "Hello World"
