#!/usr/bin/env python3
"""
CodeForge CLI - Phase 8
=======================
طبقة CLI رقيقة جداً
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.codeforge import CodeForge


def main():
    print("""
╔══════════════════════════════════════════╗
║         🏗️  CodeForge v1.0              ║
║     منصة بناء المشاريع بالذكاء الاصطناعي    ║
╚══════════════════════════════════════════╝
    """)

    # قراءة الوصف من args أو stdin
    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
    else:
        description = input("📝 صف مشروعك:\n> ").strip()

    if not description:
        print("❌ يرجى كتابة وصف للمشروع")
        return

    cf = CodeForge()
    print(f"\n🚀 بناء: {description}\n")

    result = cf.build(description)

    if result.status == "success":
        print("📊 تقدم البناء:")
        for step in result.steps:
            icon = {"success": "✅", "failed": "❌", "running": "🔄", "skipped": "⏭️"}
            print(f"  [{step.step}/6] {icon.get(step.status, '⏳')} {step.name}")

        print(f"""
{"═" * 60}
✅ تم بناء المشروع بنجاح!


📁 المشروع: {result.project_name}
📍 المسار: {result.project_path}
📄 الملفات: {result.files_count} ملف
⏱️  المدة: {result.duration_seconds:.1f} ثانية


🚀 للتشغيل:
   cd {result.project_path}
   {result.run_command}


🌐 افتح: {result.url}


📊 التقارير:""")
        for report in result.reports:
            print(f"   - {report}")
        print("═" * 60)
    else:
        print(f"\n❌ فشل البناء: {result.error}")


if __name__ == "__main__":
    main()
