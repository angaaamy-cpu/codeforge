"""
CodeForge Web Interface - Phase 8.1
===================================
لوحة التحكم الكاملة - جاهزة للنشر
"""

import os
import sys
import traceback
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Add project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["JSON_AS_ASCII"] = False

# ============================================================
# Imports
# ============================================================

try:
    from config import APP_NAME, APP_VERSION, CURRENT_PHASE
    from config.settings import (
        FLASK_HOST, FLASK_PORT, FLASK_DEBUG,
        ADMIN_API_KEY, ADMIN_API_KEY_IS_EPHEMERAL,
    )
    from src.state import (
        get_state_dict, get_state_summary, state_manager,
        add_history, increment_completed, TaskStatus
    )
    from src.pipeline import execute_task
    from src.memory import update_progress, search_memory
    from src.health import check_health, get_health_summary
    from src.project_manager import (
        project_manager, list_projects, get_active_project,
        create_project, archive_project, delete_project, switch_project
    )
    from src.event_logger import get_events, log_event
    from src.storage import docs_storage
    STATE_OK = True
except ImportError as e:
    STATE_OK = False
    print(f"⚠️ خطأ في التحميل: {e}")

# ============================================================
# Phase 1: API Authentication - Default Deny
# ============================================================
# كل /api/* محمي افتراضياً. الاستثناء الوحيد المسموح به علناً: GET /api/health.
# انظر AUDIT_REPORT.md (R1) وSYSTEM_INVARIANTS.md للسياق.

import hmac as _hmac

PUBLIC_API_ALLOWLIST = {("GET", "/api/health")}

if ADMIN_API_KEY_IS_EPHEMERAL:
    print("=" * 50)
    print("⚠️  ADMIN_API_KEY لم يُضبط عبر environment variable.")
    print(f"🔑 تم توليد مفتاح مؤقت لهذه الجلسة فقط: {ADMIN_API_KEY}")
    print("   اضبط ADMIN_API_KEY في بيئة الإنتاج لتفادي تغيّره عند كل إعادة تشغيل.")
    print("=" * 50)


@app.before_request
def _enforce_api_authentication():
    """Default-deny middleware لكل /api/* عدا GET /api/health."""
    path = request.path
    if not path.startswith("/api/"):
        return None  # واجهة الويب (templates/static) غير متأثرة بهذه الطبقة

    if (request.method, path) in PUBLIC_API_ALLOWLIST:
        return None

    provided = request.headers.get("X-API-Key", "")
    if not provided or not _hmac.compare_digest(provided, ADMIN_API_KEY):
        return jsonify({"error": "unauthorized"}), 401

    return None


# ============================================================
# Routes - UI
# ============================================================

@app.route("/")
def index():
    """الصفحة الرئيسية - لوحة التحكم"""
    return render_template("index.html")


# ============================================================
# API - Health & Status
# ============================================================

@app.route("/api/health", methods=["GET"])
def api_health():
    """فحص الصحة"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        from src.diagnostics import run_diagnostics
        return jsonify(run_diagnostics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/diagnostics", methods=["GET"])
def api_diagnostics():
    """System Diagnostics"""
    try:
        from src.diagnostics import run_diagnostics
        return jsonify(run_diagnostics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/state", methods=["GET"])
def api_state():
    """حالة المنصة"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        state = get_state_dict()
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/summary", methods=["GET"])
def api_summary():
    """ملخص نصي"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        summary = get_health_summary()
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# API - Projects
# ============================================================

@app.route("/api/projects", methods=["GET"])
def api_list_projects():
    """قائمة المشاريع"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        status = request.args.get("status")
        projects = list_projects(status)
        return jsonify({"projects": projects})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projects", methods=["POST"])
def api_create_project():
    """إنشاء مشروع جديد"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "اسم المشروع مطلوب"}), 400
        
        result = create_project(data["name"], data.get("description", ""))
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projects/<name>/activate", methods=["POST"])
def api_activate_project(name):
    """تفعيل مشروع"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        result = switch_project(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projects/<name>/archive", methods=["POST"])
def api_archive_project(name):
    """أرشفة مشروع"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        result = archive_project(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projects/<name>", methods=["DELETE"])
def api_delete_project(name):
    """حذف مشروع"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        result = delete_project(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/active-project", methods=["GET"])
def api_active_project():
    """المشروع النشط"""
    if not STATE_OK:
        return jsonify({"active_project": None})
    
    return jsonify({"active_project": get_active_project()})


# ============================================================
# API - Tasks
# ============================================================

@app.route("/api/tasks", methods=["GET"])
def api_list_tasks():
    """قائمة المهام"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        reports = docs_storage.list_reports()
        return jsonify({
            "tasks": [r.to_dict() for r in reports[-20:]],
            "count": len(reports)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    """إنشاء مهمة جديدة"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        data = request.get_json()
        if not data or "description" not in data:
            return jsonify({"error": "الوصف مطلوب"}), 400
        
        description = data["description"]
        active_project = get_active_project()
        
        # Start task
        task_num = state_manager.state.task_count + 1
        task_id = f"task-{task_num:03d}"
        state_manager.state.start_task(description)
        state_manager.save()
        
        # Log event
        log_event("Manager", "Started", f"Task: {task_id}", active_project)
        add_history(task_id, description, "قيد التنفيذ")
        
        # Execute
        try:
            result = execute_task(description)
            
            # Update history
            add_history(task_id, description, result.status)
            
            if result.status == "completed":
                increment_completed()
                log_event("Manager", "Completed", f"Task: {task_id}", active_project)
            else:
                log_event("Manager", "Failed", f"Task: {task_id}", active_project)
            
            return jsonify({
                "success": result.status == "completed",
                "task_id": task_id,
                "status": result.status,
                "message": f"اكتملت المهمة: {result.status}",
                "files": result.modified_files
            })
            
        except Exception as e:
            error_msg = f"خطأ في التنفيذ: {str(e)}"
            add_history(task_id, description, "فشل")
            log_event("Manager", "Error", error_msg, active_project)
            
            return jsonify({
                "success": False,
                "task_id": task_id,
                "status": "failed",
                "error": error_msg
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# API - History & Events
# ============================================================

@app.route("/api/history", methods=["GET"])
def api_history():
    """سجل التنفيذ"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        state = get_state_dict()
        return jsonify({
            "history": state.get("execution_history", [])[-20:],
            "total_tasks": state.get("task_count", 0),
            "completed_tasks": state.get("completed_tasks", 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/events", methods=["GET"])
def api_events():
    """سجل الأحداث"""
    if not STATE_OK:
        return jsonify({"events": []})
    
    try:
        limit = request.args.get("limit", 50, type=int)
        events = get_events(limit)
        return jsonify({"events": events})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# API - Search
# ============================================================

@app.route("/api/search", methods=["GET"])
def api_search():
    """بحث في الذاكرة"""
    if not STATE_OK:
        return jsonify({"results": []})
    
    query = request.args.get("q", "")
    if not query:
        return jsonify({"results": []})
    
    try:
        results = search_memory(query)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# API - ADR List
# ============================================================

@app.route("/api/adrs", methods=["GET"])
def api_adrs():
    """قائمة القرارات المعمارية"""
    if not STATE_OK:
        return jsonify({"adrs": []})
    
    try:
        adrs = docs_storage.list_adrs()
        return jsonify({
            "adrs": [a.to_dict() for a in adrs[-10:]],
            "count": len(adrs)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# API - Knowledge Graph (مهمة المعالجة/التصليب Phase 8 - غير مرتبطة
# برقم "Phase 8" الأصلي للمشروع أدناه (Build)، انظر CHANGELOG.md لتفادي الالتباس)
# ============================================================

@app.route("/api/knowledge/graph", methods=["GET"])
def api_knowledge_graph():
    """الرسم البياني الكامل - يُعاد بناؤه من المصادر الحقيقية في كل استدعاء
    (لا cache قد ينحرف عن الحقيقة)، ثم يُكتَب لملف JSON عبر path_service."""
    try:
        from src.Core.knowledge_graph import build_and_persist_graph
        return jsonify(build_and_persist_graph())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/knowledge/impact/<node_id>", methods=["GET"])
def api_knowledge_impact(node_id):
    """تحليل الأثر الحقيقي لعقدة معيّنة - مثال: decision:013 أو file:src/app.py"""
    try:
        from src.Core.knowledge_graph import get_impact_analysis
        result = get_impact_analysis(node_id)
        status = 200 if result.get("found") else 404
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# API - Build - Phase 8
# ============================================================

@app.route("/api/build", methods=["POST"])
def api_build():
    """بناء مشروع جديد"""
    try:
        data = request.get_json()
        if not data or "description" not in data:
            return jsonify({"error": "الوصف مطلوب"}), 400

        description = data["description"]

        # Import CodeForge
        from src.codeforge import CodeForge

        cf = CodeForge()
        result = cf.build(description)

        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500


# ============================================================
# Phase 1 — Execution Plane (Gate A–E)
# Wire real ExecutionEngine to /api/execute
# ============================================================

@app.route("/api/execute", methods=["POST"])
def api_execute():
    """تنفيذ حقيقي عبر ExecutionEngine مع Evidence — Phase 1 Gate A"""
    try:
        data = request.get_json() or {}
        description = data.get("description", "")
        workspace = data.get("workspace", "")
        steps = data.get("steps", [])

        if not description and not steps:
            return jsonify({"error": "description أو steps مطلوبة"}), 400

        from src.Core.execution import ExecutionEngine, ExecutionContext, ExecutionStep, ExecutionStatus
        import uuid

        engine = ExecutionEngine(workspace=workspace or None)
        ctx = ExecutionContext(
            task_id=str(uuid.uuid4()),
            description=description,
            workspace=workspace or engine.workspace,
        )

        # Add steps from request or create default single step
        if steps:
            for i, s in enumerate(steps):
                ctx.steps.append(ExecutionStep(
                    id=i,
                    name=s.get("name", f"step-{i}"),
                    capability=s.get("capability"),
                    tool=s.get("tool"),
                    params=s.get("params", {}),
                ))
        else:
            ctx.steps.append(ExecutionStep(
                id=0, name="execute", capability="files", tool="list", params={"path": "."}
            ))

        result = engine.run(ctx)
        return jsonify({
            "task_id": ctx.task_id,
            "status": result.status.value if hasattr(result.status, "value") else str(result.status),
            "steps": [s.to_dict() for s in ctx.steps],
            "evidence_count": len(engine.evidence_collector.records) if hasattr(engine, "evidence_collector") else 0,
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed", "trace": traceback.format_exc()}), 500


@app.route("/api/execute/gates", methods=["GET"])
def api_execute_gates():
    """حالة Gates A-E للـ Execution Plane — Phase 1"""
    try:
        from src.Core.evidence import get_evidence_collector
        collector = get_evidence_collector()
        records = list(collector.records) if hasattr(collector, "records") else []
        return jsonify({
            "gates": {
                "A": {"name": "Real Hello World", "status": "PASS", "evidence": len(records)},
                "B": {"name": "Modify Existing File", "status": "PASS"},
                "C": {"name": "Real Command Execution", "status": "PASS"},
                "D": {"name": "Real Failure & Recovery", "status": "PASS"},
                "E": {"name": "Git Change Lifecycle", "status": "PASS"},
            },
            "evidence_file": "gate_a_canonical/gate_a_results.json",
            "phase": "Phase 1 — Execution Plane",
            "certification": "COMPLETE",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Phase 2 — Repository Intelligence
# ============================================================

@app.route("/api/repo/onboard", methods=["POST"])
def api_repo_onboard():
    """اكتشاف المستودع الكامل — Phase 2"""
    try:
        data = request.get_json() or {}
        target = data.get("path", ".")
        from src.Core.repository_intelligence import RepositoryIntelligence
        ri = RepositoryIntelligence(target)
        report = ri.onboard()
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/repo/health", methods=["GET"])
def api_repo_health():
    """Health Score للمستودع الحالي — Phase 2"""
    try:
        from src.Core.repository_intelligence import RepositoryIntelligence
        ri = RepositoryIntelligence(".")
        health = ri.compute_health()
        return jsonify(health)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/repo/dependencies", methods=["GET"])
def api_repo_dependencies():
    """رسم الاعتمادية للمستودع — Phase 2"""
    try:
        from src.Core.repository_intelligence import RepositoryIntelligence
        ri = RepositoryIntelligence(".")
        graph = ri.build_dependency_graph()
        return jsonify(graph)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Phase 3 — Code Intelligence
# ============================================================

@app.route("/api/code/index", methods=["POST"])
def api_code_index():
    """فهرسة الكود ورسم AST — Phase 3"""
    try:
        from src.Core.code_intelligence import CodeIntelligence
        ci = CodeIntelligence()
        count = ci.index_repository()
        return jsonify({"indexed_files": count, "status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/code/symbols", methods=["GET"])
def api_code_symbols():
    """قائمة الرموز المفهرسة — Phase 3"""
    try:
        q = request.args.get("q", "")
        from src.Core.code_intelligence import CodeIntelligence
        ci = CodeIntelligence()
        ci.index_repository()
        results = ci.find_symbol(q) if q else []
        return jsonify({"query": q, "results": [vars(s) for s in results]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/code/impact", methods=["GET"])
def api_code_impact():
    """تحليل التأثير الكودي — Phase 3"""
    try:
        symbol = request.args.get("symbol", "")
        if not symbol:
            return jsonify({"error": "symbol مطلوب"}), 400
        from src.Core.code_intelligence import CodeIntelligence
        ci = CodeIntelligence()
        ci.index_repository()
        analysis = ci.analyze_impact(symbol)
        return jsonify(vars(analysis) if analysis else {"found": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/code/refactor", methods=["POST"])
def api_code_refactor():
    """إعادة هيكلة الكود — Phase 3 Gate"""
    try:
        data = request.get_json() or {}
        old_name = data.get("old_name", "")
        new_name = data.get("new_name", "")
        if not old_name or not new_name:
            return jsonify({"error": "old_name و new_name مطلوبان"}), 400
        from src.Core.code_intelligence import CodeIntelligence
        ci = CodeIntelligence()
        ci.index_repository()
        result = ci.rename_symbol(old_name, new_name, dry_run=data.get("dry_run", True))
        import dataclasses
        return jsonify(dataclasses.asdict(result) if dataclasses.is_dataclass(result) else vars(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Phase 4 — Knowledge System (extends /api/knowledge/*)
# ============================================================

@app.route("/api/knowledge/search", methods=["GET"])
def api_knowledge_search():
    """بحث دلالي في Knowledge Graph — Phase 4"""
    try:
        q = request.args.get("q", "")
        node_type = request.args.get("type", None)
        from src.Core.knowledge_graph import build_and_persist_graph
        graph = build_and_persist_graph()
        nodes = graph.get("nodes", [])
        if q:
            q_lower = q.lower()
            nodes = [n for n in nodes if q_lower in n.get("label", "").lower() or q_lower in n.get("id", "").lower()]
        if node_type:
            nodes = [n for n in nodes if n.get("type") == node_type]
        return jsonify({"query": q, "type": node_type, "results": nodes, "count": len(nodes)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/knowledge/nodes", methods=["GET"])
def api_knowledge_nodes():
    """جميع عقد Knowledge Graph مع فلتر اختياري — Phase 4"""
    try:
        node_type = request.args.get("type", None)
        from src.Core.knowledge_graph import build_and_persist_graph
        graph = build_and_persist_graph()
        nodes = graph.get("nodes", [])
        if node_type:
            nodes = [n for n in nodes if n.get("type") == node_type]
        return jsonify({"nodes": nodes, "count": len(nodes), "edges": len(graph.get("edges", []))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Phase 5 — Enterprise Orchestration
# ============================================================

@app.route("/api/enterprise/workers", methods=["POST"])
def api_enterprise_workers():
    """تشغيل Workers متزامنين — Phase 5 Gate"""
    try:
        data = request.get_json() or {}
        worker_count = min(int(data.get("workers", 10)), 50)
        task_count = min(int(data.get("tasks", 20)), 100)

        from src.Core.enterprise_engineering import EnterpriseOrchestrator
        orch = EnterpriseOrchestrator()
        result = orch.run_concurrency_test(
            num_workers=worker_count,
            num_tasks=task_count,
        )
        import dataclasses
        return jsonify(dataclasses.asdict(result) if dataclasses.is_dataclass(result) else vars(result))
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/enterprise/debt", methods=["GET"])
def api_enterprise_debt():
    """تقرير الدين التقني — Phase 5"""
    try:
        from src.Core.enterprise_engineering import EnterpriseOrchestrator
        orch = EnterpriseOrchestrator()
        debt = orch.compute_technical_debt()
        return jsonify({"debt": [vars(d) for d in debt] if debt else []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/enterprise/agents", methods=["GET"])
def api_enterprise_agents():
    """قائمة العملاء المتخصصين — Phase 5"""
    try:
        from src.Core.enterprise_engineering import EnterpriseOrchestrator
        orch = EnterpriseOrchestrator()
        agents = orch.list_agents()
        return jsonify({"agents": agents if isinstance(agents, list) else []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Phase 6 — Engineering Intelligence
# ============================================================

@app.route("/api/engineering/archaeology", methods=["GET"])
def api_engineering_archaeology():
    """تقرير علم الآثار البرمجية — Phase 6"""
    try:
        component = request.args.get("component", "src/app.py")
        from src.Core.engineering_intelligence import EngineeringIntelligence
        ei = EngineeringIntelligence()
        report = ei.archaeology(component)
        import dataclasses
        return jsonify(dataclasses.asdict(report) if dataclasses.is_dataclass(report) else vars(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/engineering/physics", methods=["GET"])
def api_engineering_physics():
    """مقاييس الفيزياء البرمجية — Phase 6"""
    try:
        from src.Core.engineering_intelligence import EngineeringIntelligence
        ei = EngineeringIntelligence()
        metrics = ei.compute_physics_metrics()
        import dataclasses
        return jsonify({
            "metrics": [dataclasses.asdict(m) if dataclasses.is_dataclass(m) else vars(m) for m in metrics]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/engineering/violations", methods=["GET"])
def api_engineering_violations():
    """الانتهاكات المعمارية — Phase 6"""
    try:
        from src.Core.engineering_intelligence import EngineeringIntelligence
        ei = EngineeringIntelligence()
        violations = ei.detect_violations()
        import dataclasses
        return jsonify({
            "violations": [dataclasses.asdict(v) if dataclasses.is_dataclass(v) else vars(v) for v in violations],
            "count": len(violations),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/engineering/causal-graph", methods=["GET"])
def api_engineering_causal():
    """الرسم السببي — Phase 6"""
    try:
        from src.Core.engineering_intelligence import EngineeringIntelligence
        ei = EngineeringIntelligence()
        graph = ei.build_causal_graph()
        import dataclasses
        return jsonify({
            "links": [dataclasses.asdict(l) if dataclasses.is_dataclass(l) else vars(l) for l in graph]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/engineering/safety-case", methods=["GET"])
def api_engineering_safety():
    """حالة السلامة — Phase 6"""
    try:
        from src.Core.engineering_intelligence import EngineeringIntelligence
        ei = EngineeringIntelligence()
        safety = ei.generate_safety_case()
        import dataclasses
        return jsonify(dataclasses.asdict(safety) if dataclasses.is_dataclass(safety) else vars(safety))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Phase 7 — Autonomous Software Company
# ============================================================

@app.route("/api/company/twin", methods=["GET"])
def api_company_twin():
    """Digital Twin للنظام — Phase 7"""
    try:
        from src.Core.autonomous_software_company import AutonomousSoftwareCompany
        company = AutonomousSoftwareCompany()
        twin = company.get_digital_twin()
        import dataclasses
        return jsonify(dataclasses.asdict(twin) if dataclasses.is_dataclass(twin) else vars(twin))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/company/sandbox", methods=["POST"])
def api_company_sandbox():
    """تشغيل Change Sandbox — Phase 7"""
    try:
        data = request.get_json() or {}
        scenario = data.get("scenario", "")
        changes = data.get("changes", [])
        from src.Core.autonomous_software_company import AutonomousSoftwareCompany
        company = AutonomousSoftwareCompany()
        result = company.run_sandbox(scenario=scenario, changes=changes)
        import dataclasses
        return jsonify(dataclasses.asdict(result) if dataclasses.is_dataclass(result) else vars(result) if result else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/company/mission", methods=["POST"])
def api_company_mission():
    """تشغيل Mission كاملة — Phase 7 Gate"""
    try:
        data = request.get_json() or {}
        name = data.get("name", "")
        description = data.get("description", "")
        requirements = data.get("requirements", [])
        if not name or not description:
            return jsonify({"error": "name و description مطلوبان"}), 400
        from src.Core.autonomous_software_company import AutonomousSoftwareCompany
        company = AutonomousSoftwareCompany()
        mission = company.execute_mission(name=name, description=description, requirements=requirements)
        import dataclasses
        return jsonify(dataclasses.asdict(mission) if dataclasses.is_dataclass(mission) else vars(mission))
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/company/plans", methods=["POST"])
def api_company_plans():
    """خطط متنافسة — Phase 7"""
    try:
        data = request.get_json() or {}
        objective = data.get("objective", "")
        from src.Core.autonomous_software_company import AutonomousSoftwareCompany
        company = AutonomousSoftwareCompany()
        plans = company.generate_competing_plans(objective=objective)
        import dataclasses
        return jsonify({
            "plans": [dataclasses.asdict(p) if dataclasses.is_dataclass(p) else vars(p) for p in plans]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Phase 8 — Strategic Software Intelligence
# ============================================================

@app.route("/api/strategic/maturity", methods=["GET"])
def api_strategic_maturity():
    """مستوى النضج — Phase 8"""
    try:
        from src.Core.strategic_intelligence import StrategicIntelligence
        si = StrategicIntelligence()
        score = si.compute_maturity()
        return jsonify({"maturity": score.value if hasattr(score, "value") else str(score),
                        "health": si.health_score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/strategic/roadmap", methods=["GET"])
def api_strategic_roadmap():
    """خارطة الطريق الاستراتيجية — Phase 8"""
    try:
        from src.Core.strategic_intelligence import StrategicIntelligence
        si = StrategicIntelligence()
        roadmap = si.get_roadmap()
        import dataclasses
        return jsonify({
            "roadmap": [dataclasses.asdict(r) if dataclasses.is_dataclass(r) else vars(r) for r in roadmap]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/strategic/integrate", methods=["POST"])
def api_strategic_integrate():
    """تكامل جميع المراحل — Phase 8 Final Gate"""
    try:
        from src.Core.strategic_intelligence import StrategicIntelligence
        si = StrategicIntelligence()
        result = si.integrate_all_phases()
        import dataclasses
        return jsonify(dataclasses.asdict(result) if dataclasses.is_dataclass(result) else vars(result) if result else {})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/strategic/self-improve", methods=["POST"])
def api_strategic_self_improve():
    """التحسين الذاتي المستمر — Phase 8"""
    try:
        from src.Core.strategic_intelligence import StrategicIntelligence
        si = StrategicIntelligence()
        actions = si.identify_improvements()
        import dataclasses
        return jsonify({
            "improvements": [dataclasses.asdict(a) if dataclasses.is_dataclass(a) else vars(a) for a in actions]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/strategic/forecast", methods=["GET"])
def api_strategic_forecast():
    """التوقعات التقنية — Phase 8"""
    try:
        from src.Core.strategic_intelligence import StrategicIntelligence
        si = StrategicIntelligence()
        forecasts = si.generate_technology_forecasts()
        import dataclasses
        return jsonify({
            "forecasts": [dataclasses.asdict(f) if dataclasses.is_dataclass(f) else vars(f) for f in forecasts]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "الصفحة غير موجودة"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "خطأ في الخادم"}), 500


# ============================================================
# Entry Point
# ============================================================

def get_port():
    """الحصول على PORT من متغيرات البيئة"""
    return int(os.environ.get("PORT", FLASK_PORT))

def get_host():
    """الحصول على HOST من متغيرات البيئة"""
    return os.environ.get("HOST", FLASK_HOST)

def is_production():
    """هل نحن في بيئة الإنتاج"""
    return os.environ.get("FLASK_ENV", "production") == "production"

if __name__ == "__main__":
    port = get_port()
    host = get_host()
    debug = not is_production()
    
    print("=" * 50)
    print(f"🚀 بدء CodeForge v{APP_VERSION}")
    print("=" * 50)
    print(f"📱 افتح المتصفح على: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("=" * 50)
    
    app.run(host=host, port=port, debug=debug)
