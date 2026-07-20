"""
Phase 3 - Runtime Stability: Path System Tests
================================================
يتحقق أن كشف WORKSPACE_ROOT لم يعد يفترض "/app" ثابتاً على Railway،
وأن WORKSPACE_ROOT الصريح له الأولوية دائماً.
"""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _reload_path_service():
    for mod in list(sys.modules):
        if mod == "src.path_service":
            del sys.modules[mod]
    import src.path_service as ps
    return ps


def test_no_hardcoded_app_path_on_railway_env(monkeypatch, tmp_path):
    """كان الكود القديم يُرجع Path('/app') دوماً عند RAILWAY_ENVIRONMENT
    بصرف النظر عن كتابة القرص فعلياً - الآن يعتمد على موقع الملف الفعلي."""
    monkeypatch.delenv("WORKSPACE_ROOT", raising=False)
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    ps = _reload_path_service()
    assert str(ps.WORKSPACE_ROOT) != "/app"
    # يجب أن يكون هو المسار الفعلي لجذر المشروع (أب src/)
    assert ps.WORKSPACE_ROOT == ps.Path(ps.__file__).parent.parent.resolve()


def test_explicit_workspace_root_still_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    ps = _reload_path_service()
    assert ps.WORKSPACE_ROOT == tmp_path.resolve()


def test_write_and_read_roundtrip_within_workspace_root(monkeypatch, tmp_path):
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    ps = _reload_path_service()
    svc = ps.PathService(root=str(tmp_path))
    svc.write("test.txt", "phase3-reality-check")
    assert svc.read("test.txt") == "phase3-reality-check"
    assert (tmp_path / "test.txt").exists()
