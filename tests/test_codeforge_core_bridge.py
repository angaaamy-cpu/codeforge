"""
ADR-013 follow-up: src/codeforge.py كان بلا أي اختبار مباشر رغم كونه
نقطة الدخول الفعلية من /api/build إلى src/Core. هذا الاختبار يثبت (لا
يفترض) أن CORE_AVAILABLE وأن الأحداث الحقيقية تُطلَق فعلاً.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_core_available_under_base_deps_only():
    """يثبت أن from src.Core import (...) ينجح فعلياً (لا يفترض ذلك)."""
    import src.codeforge as cf
    assert cf.CORE_AVAILABLE is True


def test_codeforge_instantiates_all_core_singletons():
    import src.codeforge as cf
    instance = cf.CodeForge()
    for attr in ("capabilities", "events", "workspaces", "execution",
                 "memory", "plugins", "deployment", "secrets"):
        assert hasattr(instance, attr), f"missing Core component: {attr}"


def test_builtin_capabilities_are_registered_but_have_no_real_tools():
    """يثبت النتيجة المحورية في ADR-013 كما كانت قبل Phase 5: القدرات
    المدمجة أسماء ميتاداتا فقط. Phase 5 (انظر src/Core/builtin_tools.py
    وdocs/adr/013-src-core-architectural-status.md §7) ربط أدوات حقيقية
    عمداً لـ files/git فقط - كل ما عداهما (وخصوصاً terminal، انظر
    docs/security/TERMINAL_CAPABILITY_SECURITY_REVIEW.md) يبقى فارغاً."""
    import src.codeforge as cf
    instance = cf.CodeForge()
    caps = {c["name"]: c for c in instance.list_capabilities()}
    assert "terminal" in caps
    assert "files" in caps
    assert "git" in caps

    wired_by_phase5 = {"files", "git"}
    for name, cap_dict in caps.items():
        tools = cap_dict.get("tools", [])
        if name in wired_by_phase5:
            assert tools != [], f"Phase 5 يفترض ربط أدوات حقيقية لـ '{name}'"
        else:
            assert tools == [], (
                f"القدرة '{name}' لديها tools مربوطة فعلياً خارج نطاق Phase 5 - "
                f"إن كان هذا مقصوداً، حدِّث ADR-013 وهذا الاختبار معاً"
            )


def test_event_bus_receives_real_events_on_build_start():
    import src.codeforge as cf
    instance = cf.CodeForge()
    before = len(instance.get_event_history(limit=1000))
    from src.Core.event_bus import EventType, emit
    emit(EventType.BUILD_STARTED, {"description": "adr-013 verification"})
    after = len(instance.get_event_history(limit=1000))
    assert after == before + 1
