"""
CodeForge Web Interface - Phase 4
==================================
واجهة التحكم من الهاتف
"""

import os
import sys
import traceback
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["JSON_AS_ASCII"] = False

# ============================================================
# Imports من Phase 3
# ============================================================

try:
    from src.state import (
        get_state_dict,
        get_state_summary,
        state_manager,
        add_history,
        increment_completed
    )
    from src.pipeline import execute_task
    from src.memory import update_progress
    STATE_OK = True
except ImportError as e:
    STATE_OK = False
    print(f"⚠️ خطأ في تحميل state: {e}")


# ============================================================
# Routes - الواجهة
# ============================================================

@app.route("/")
def index():
    """الصفحة الرئيسية"""
    return render_template("index.html")


# ============================================================
# API Routes
# ============================================================

@app.route("/api/state", methods=["GET"])
def api_get_state():
    """الحصول على حالة المنصة"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        state = get_state_dict()
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def api_get_history():
    """الحصول على سجل التنفيذ"""
    if not STATE_OK:
        return jsonify({"error": "النظام غير جاهز"}), 500
    
    try:
        state = get_state_dict()
        return jsonify({
            "history": state.get("execution_history", []),
            "total_tasks": state.get("task_count", 0),
            "completed_tasks": state.get("completed_tasks", 0)
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
        
        # تحديث الحالة
        task_num = state_manager.state.task_count + 1
        task_id = f"task-{task_num:03d}"
        state_manager.state.start_task(description)
        state_manager.save()
        
        # إضافة للسجل
        add_history(task_id, description, "قيد التنفيذ")
        
        # تنفيذ المهمة
        try:
            result = execute_task(description)
            
            # تحديث السجل
            add_history(task_id, description, result.status)
            
            if result.status == "completed":
                increment_completed()
            
            return jsonify({
                "success": True,
                "task_id": task_id,
                "status": result.status,
                "message": f"اكتملت المهمة: {result.status}",
                "files": result.modified_files
            })
            
        except Exception as e:
            error_msg = f"خطأ في التنفيذ: {str(e)}"
            add_history(task_id, description, "فشل")
            traceback.print_exc()
            
            return jsonify({
                "success": False,
                "task_id": task_id,
                "status": "failed",
                "error": error_msg
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def api_health():
    """فحص حالة النظام"""
    return jsonify({
        "status": "ok",
        "phase": "phase4",
        "timestamp": datetime.now().isoformat(),
        "state_ready": STATE_OK
    })


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
# نقطة الدخول
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 بدء واجهة CodeForge")
    print("=" * 50)
    print("📱 افتح المتصفح على: http://localhost:5000")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
