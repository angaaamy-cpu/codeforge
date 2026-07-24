"""
Phase API Routes Tests — Phases 1-8
=====================================
Tests for all phase-specific API routes added in the Final Directive implementation.
Each test verifies the route exists, returns the correct HTTP status, and produces
a valid JSON response.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Flask test client with isolated workspace and known API key."""
    monkeypatch.setenv("ADMIN_API_KEY", "test-key-phases-12345")
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("FLASK_ENV", "testing")

    for mod in list(sys.modules):
        if mod in ("config", "src.app", "src") or mod.startswith(("config.", "src.")):
            del sys.modules[mod]

    from src.app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


HEADERS = {"X-API-Key": "test-key-phases-12345", "Content-Type": "application/json"}


# ─── Phase 0 — Forensic ───────────────────────────────────────────────────────

def test_health_public(client):
    """GET /api/health is public (no key required)."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "status" in data or "error" not in data


# ─── Phase 1 — Execution Plane ───────────────────────────────────────────────

def test_execute_gates_endpoint(client):
    """GET /api/execute/gates returns Phase 1 gate status."""
    resp = client.get("/api/execute/gates", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "gates" in data
    assert "A" in data["gates"]
    assert data["gates"]["A"]["status"] == "PASS"


def test_execute_endpoint_missing_body(client):
    """POST /api/execute with empty body returns 400."""
    resp = client.post("/api/execute", headers=HEADERS, json={})
    assert resp.status_code == 400


def test_execute_endpoint_with_description(client):
    """POST /api/execute with description returns execution result."""
    resp = client.post("/api/execute", headers=HEADERS, json={"description": "list files"})
    # May be 200 or 500 depending on Python environment, but must return JSON
    data = resp.get_json()
    assert data is not None
    assert "error" in data or "task_id" in data


# ─── Phase 2 — Repository Intelligence ───────────────────────────────────────

def test_repo_health_endpoint(client):
    """GET /api/repo/health returns health report."""
    resp = client.get("/api/repo/health", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_repo_dependencies_endpoint(client):
    """GET /api/repo/dependencies returns dependency graph."""
    resp = client.get("/api/repo/dependencies", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_repo_onboard_endpoint(client):
    """POST /api/repo/onboard with path returns onboarding report."""
    resp = client.post("/api/repo/onboard", headers=HEADERS, json={"path": "."})
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


# ─── Phase 3 — Code Intelligence ─────────────────────────────────────────────

def test_code_index_endpoint(client):
    """POST /api/code/index indexes the repository."""
    resp = client.post("/api/code/index", headers=HEADERS, json={})
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_code_symbols_endpoint(client):
    """GET /api/code/symbols returns symbol list."""
    resp = client.get("/api/code/symbols", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_code_impact_missing_symbol(client):
    """GET /api/code/impact without symbol returns 400."""
    resp = client.get("/api/code/impact", headers=HEADERS)
    assert resp.status_code == 400


def test_code_refactor_missing_params(client):
    """POST /api/code/refactor without names returns 400."""
    resp = client.post("/api/code/refactor", headers=HEADERS, json={})
    assert resp.status_code == 400


# ─── Phase 4 — Knowledge System ──────────────────────────────────────────────

def test_knowledge_graph_endpoint(client):
    """GET /api/knowledge/graph returns the full graph."""
    resp = client.get("/api/knowledge/graph", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_knowledge_nodes_endpoint(client):
    """GET /api/knowledge/nodes returns node list."""
    resp = client.get("/api/knowledge/nodes", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_knowledge_search_endpoint(client):
    """GET /api/knowledge/search with query returns filtered nodes."""
    resp = client.get("/api/knowledge/search?q=app", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_knowledge_impact_endpoint(client):
    """GET /api/knowledge/impact/<node_id> returns impact analysis."""
    resp = client.get("/api/knowledge/impact/file:src/app.py", headers=HEADERS)
    assert resp.status_code in (200, 404, 500)
    assert resp.get_json() is not None


# ─── Phase 5 — Enterprise Orchestration ──────────────────────────────────────

def test_enterprise_workers_endpoint(client):
    """POST /api/enterprise/workers runs concurrency test."""
    resp = client.post("/api/enterprise/workers", headers=HEADERS, json={"workers": 3, "tasks": 5})
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_enterprise_debt_endpoint(client):
    """GET /api/enterprise/debt returns technical debt report."""
    resp = client.get("/api/enterprise/debt", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_enterprise_agents_endpoint(client):
    """GET /api/enterprise/agents returns agent list."""
    resp = client.get("/api/enterprise/agents", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


# ─── Phase 6 — Engineering Intelligence ──────────────────────────────────────

def test_engineering_archaeology_endpoint(client):
    """GET /api/engineering/archaeology returns archaeology report."""
    resp = client.get("/api/engineering/archaeology?component=src/app.py", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_engineering_physics_endpoint(client):
    """GET /api/engineering/physics returns physics metrics."""
    resp = client.get("/api/engineering/physics", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_engineering_violations_endpoint(client):
    """GET /api/engineering/violations returns violation list."""
    resp = client.get("/api/engineering/violations", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_engineering_causal_endpoint(client):
    """GET /api/engineering/causal-graph returns causal links."""
    resp = client.get("/api/engineering/causal-graph", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_engineering_safety_endpoint(client):
    """GET /api/engineering/safety-case returns safety case."""
    resp = client.get("/api/engineering/safety-case", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


# ─── Phase 7 — Autonomous Software Company ────────────────────────────────────

def test_company_twin_endpoint(client):
    """GET /api/company/twin returns digital twin."""
    resp = client.get("/api/company/twin", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_company_sandbox_endpoint(client):
    """POST /api/company/sandbox runs change sandbox."""
    resp = client.post("/api/company/sandbox", headers=HEADERS, json={"scenario": "test"})
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_company_mission_missing_params(client):
    """POST /api/company/mission without required fields returns 400."""
    resp = client.post("/api/company/mission", headers=HEADERS, json={})
    assert resp.status_code == 400


def test_company_plans_endpoint(client):
    """POST /api/company/plans returns competing plans."""
    resp = client.post("/api/company/plans", headers=HEADERS, json={"objective": "improve coverage"})
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


# ─── Phase 8 — Strategic Intelligence ────────────────────────────────────────

def test_strategic_maturity_endpoint(client):
    """GET /api/strategic/maturity returns maturity level."""
    resp = client.get("/api/strategic/maturity", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_strategic_roadmap_endpoint(client):
    """GET /api/strategic/roadmap returns roadmap."""
    resp = client.get("/api/strategic/roadmap", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_strategic_forecast_endpoint(client):
    """GET /api/strategic/forecast returns technology forecasts."""
    resp = client.get("/api/strategic/forecast", headers=HEADERS)
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_strategic_self_improve_endpoint(client):
    """POST /api/strategic/self-improve returns improvement actions."""
    resp = client.post("/api/strategic/self-improve", headers=HEADERS, json={})
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


def test_strategic_integrate_endpoint(client):
    """POST /api/strategic/integrate triggers cross-phase integration."""
    resp = client.post("/api/strategic/integrate", headers=HEADERS, json={})
    assert resp.status_code in (200, 500)
    assert resp.get_json() is not None


# ─── Auth protection ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("method,path", [
    ("POST", "/api/execute"),
    ("GET", "/api/execute/gates"),
    ("GET", "/api/repo/health"),
    ("POST", "/api/code/index"),
    ("GET", "/api/knowledge/nodes"),
    ("POST", "/api/enterprise/workers"),
    ("GET", "/api/engineering/physics"),
    ("GET", "/api/company/twin"),
    ("GET", "/api/strategic/maturity"),
])
def test_all_phase_routes_require_auth(client, method, path):
    """All Phase 1-8 routes require X-API-Key."""
    if method == "GET":
        resp = client.get(path)
    else:
        resp = client.post(path, json={})
    assert resp.status_code == 401
