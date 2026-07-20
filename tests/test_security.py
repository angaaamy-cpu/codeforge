"""
Phase 1 - Security Regression Tests
====================================
يضمن Default Deny على كل /api/* عدا GET /api/health.
"""

import os
import sys
import importlib

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key-12345")
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    # Fresh import so env vars above take effect (config/settings.py reads
    # ADMIN_API_KEY at import time).
    for mod in list(sys.modules):
        if mod == "config" or mod.startswith("config.") or mod == "src.app" or mod.startswith("src."):
            del sys.modules[mod]

    from src.app import app as flask_app

    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# Public allowlist: GET /api/health only
def test_health_is_public(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200


PROTECTED_ENDPOINTS = [
    ("GET", "/api/projects"),
    ("POST", "/api/projects"),
    ("GET", "/api/state"),
    ("GET", "/api/summary"),
    ("GET", "/api/tasks"),
    ("POST", "/api/tasks"),
    ("GET", "/api/history"),
    ("GET", "/api/events"),
    ("GET", "/api/search"),
    ("GET", "/api/adrs"),
    ("POST", "/api/build"),
    ("DELETE", "/api/projects/some-project"),
    ("POST", "/api/projects/some-project/archive"),
    ("POST", "/api/projects/some-project/activate"),
]


@pytest.mark.parametrize("method,path", PROTECTED_ENDPOINTS)
def test_protected_endpoint_without_auth_is_401(client, method, path):
    resp = client.open(path, method=method, json={"description": "x", "name": "x"})
    assert resp.status_code == 401


@pytest.mark.parametrize("method,path", PROTECTED_ENDPOINTS)
def test_protected_endpoint_with_wrong_key_is_401(client, method, path):
    resp = client.open(
        path, method=method,
        json={"description": "x", "name": "x"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


@pytest.mark.parametrize("method,path", PROTECTED_ENDPOINTS)
def test_protected_endpoint_with_empty_key_is_401(client, method, path):
    resp = client.open(
        path, method=method,
        json={"description": "x", "name": "x"},
        headers={"X-API-Key": ""},
    )
    assert resp.status_code == 401


def test_malformed_auth_header_is_401(client):
    resp = client.get("/api/state", headers={"X-API-Key": "\x00\x01garbage"})
    assert resp.status_code == 401


def test_valid_auth_is_not_401(client):
    resp = client.get("/api/state", headers={"X-API-Key": "test-admin-key-12345"})
    # قد يكون 200 أو رمز خطأ تشغيلي آخر (500 إن فشل مكوّن داخلي)، لكن ليس 401
    assert resp.status_code != 401


def test_non_api_routes_are_unaffected(client):
    resp = client.get("/")
    assert resp.status_code != 401
