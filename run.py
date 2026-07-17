"""
CodeForge - Entry Point for Replit
===================================
نقطة الدخول الرئيسية للتشغيل على Replit
"""

import os
import sys

# Set WORKSPACE_ROOT so path_service resolves paths from the codeforge/ directory
os.environ.setdefault("WORKSPACE_ROOT", os.path.dirname(os.path.abspath(__file__)))

# Add project root to path so imports work (config, src)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from src.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    print("=" * 50)
    print("🚀 بدء CodeForge")
    print(f"📱 الرابط: http://localhost:{port}")
    print("=" * 50)

    app.run(host=host, port=port, debug=debug)
