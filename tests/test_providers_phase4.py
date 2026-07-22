"""
Phase 4 - Provider Layer Tests
===============================
ملاحظة صادقة: هذه البيئة (sandbox) لا تملك وصول شبكة فعلي لـ
generativelanguage.googleapis.com أو api.openai.com (egress proxy يمنعهما
صراحة). لذلك: منطق GeminiProvider/OpenAIProvider مُختبَر هنا عبر HTTP
مُحاكى (unittest.mock)، أما الاتصال الحي الفعلي فيبقى UNKNOWN من هذه البيئة
تحديداً (انظر FINAL_VERIFICATION.md). هذا ليس "PASS" مزيّفاً - وهذا هو بيت
القصيد من هذا التعليق.
"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _reload_provider_modules():
    for mod in list(sys.modules):
        if mod.startswith("src.model_provider"):
            del sys.modules[mod]


# ---------------------------------------------------------------------------
# GeminiProvider / OpenAIProvider - وجود الملفات وبنيتها
# ---------------------------------------------------------------------------

def test_gemini_provider_file_exists_and_importable():
    from src.model_provider.gemini_provider import GeminiProvider
    p = GeminiProvider()
    assert p.name == "gemini"


def test_openai_provider_file_exists_and_importable():
    from src.model_provider.openai_provider import OpenAIProvider
    p = OpenAIProvider()
    assert p.name == "openai"


def test_gemini_not_configured_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from src.model_provider.gemini_provider import GeminiProvider
    p = GeminiProvider()
    assert p.configured is False
    assert p.test_connection() is False


def test_gemini_generate_without_key_raises(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from src.model_provider.gemini_provider import GeminiProvider
    p = GeminiProvider()
    with pytest.raises(RuntimeError):
        p.generate("hello")


@patch("src.model_provider.gemini_provider.requests.get")
def test_gemini_healthy_on_200(mock_get, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-mocked-test")
    mock_get.return_value = MagicMock(status_code=200, text="ok")
    from src.model_provider.gemini_provider import GeminiProvider
    p = GeminiProvider()
    assert p.configured is True
    assert p.test_connection() is True


@patch("src.model_provider.gemini_provider.requests.get")
def test_gemini_unhealthy_on_error_status(mock_get, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-mocked-test")
    mock_get.return_value = MagicMock(status_code=403, text="forbidden")
    from src.model_provider.gemini_provider import GeminiProvider
    p = GeminiProvider()
    assert p.test_connection() is False


@patch("src.model_provider.openai_provider.requests.get")
def test_openai_healthy_on_200(mock_get, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key-for-mocked-test")
    mock_get.return_value = MagicMock(status_code=200, text="ok")
    from src.model_provider.openai_provider import OpenAIProvider
    p = OpenAIProvider()
    assert p.test_connection() is True


# ---------------------------------------------------------------------------
# ProviderRegistry - ProviderMode (real / mock / unavailable)
# ---------------------------------------------------------------------------

def test_mode_is_mock_when_no_real_keys_configured(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PROVIDER_ORDER", raising=False)
    _reload_provider_modules()
    from src.model_provider.registry import ProviderRegistry
    reg = ProviderRegistry()
    assert reg.mode == "mock"


def test_mode_is_unavailable_when_mock_disabled_and_no_keys(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("MOCK_PROVIDER_ENABLED", "false")
    _reload_provider_modules()
    from src.model_provider.registry import ProviderRegistry
    reg = ProviderRegistry()
    assert reg.mode == "unavailable"
    monkeypatch.delenv("MOCK_PROVIDER_ENABLED", raising=False)


@patch("src.model_provider.gemini_provider.requests.get")
def test_mode_is_real_when_gemini_configured_and_healthy(mock_get, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-mocked-test")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_get.return_value = MagicMock(status_code=200, text="ok")
    _reload_provider_modules()
    from src.model_provider.registry import ProviderRegistry
    reg = ProviderRegistry()
    assert reg.mode == "real"
    assert reg.get_active().name == "gemini"


@patch("src.model_provider.gemini_provider.requests.get")
def test_falls_back_to_mock_when_gemini_configured_but_unhealthy(mock_get, monkeypatch):
    """قاعدة أمان: فشل health check لمزود حقيقي لا يُخفى - يسقط لـ mock
    بوضوح (mode=mock)، لا يبقى مُعلَناً "real" وهو معطل."""
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-mocked-test")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_get.return_value = MagicMock(status_code=500, text="server error")
    _reload_provider_modules()
    from src.model_provider.registry import ProviderRegistry
    reg = ProviderRegistry()
    assert reg.mode == "mock"
    gemini_entry = [p for p in reg.list_all() if p["name"] == "gemini"][0]
    assert gemini_entry["healthy"] is False
    assert gemini_entry["active"] is False


def test_provider_order_env_var_respected(monkeypatch):
    monkeypatch.setenv("PROVIDER_ORDER", "mock,gemini,openai")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    _reload_provider_modules()
    from src.model_provider.registry import ProviderRegistry
    reg = ProviderRegistry()
    assert reg.mode == "mock"
    monkeypatch.delenv("PROVIDER_ORDER", raising=False)
