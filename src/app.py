"""
CodeForge Web Interface - Phase 5
==================================
لوحة التحكم الكاملة
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
        health = check_health()
        return jsonify(health)
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

if __name__ == "__main__":
    print("=" * 50)
    print(f"🚀 بدء CodeForge v{APP_VERSION} ({CURRENT_PHASE})")
    print("=" * 50)
    print("📱 افتح المتصفح على: http://localhost:5000")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
