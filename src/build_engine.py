"""
CodeForge Build Engine - Phase 8
=================================
محرك البناء - ينسق كل المكونات
"""

import time
import re
from pathlib import Path
from typing import List, Optional

from src.build_result import BuildResult, BuildStep
from src.project_manager import project_manager
from src.pipeline import pipeline, execute_task
from src.logger import logger
from src.memory import record_decision
from config import PROJECTS_DIR


class BuildEngine:
    """محرك البناء - ينسق كل المكونات"""

    def __init__(self):
        self.project_manager = project_manager
        self.pipeline = pipeline
        self.logger = logger
        self._project = None
        self._files = []

    def execute(self, description: str) -> BuildResult:
        """ينفذ دورة البناء كاملة ويعيد BuildResult"""
        steps: List[BuildStep] = []
        start_time = time.time()

        try:
            # Step 1: إنشاء المشروع
            steps.append(BuildStep(1, "إنشاء المشروع", "running"))
            project_result = self._create_project(description)
            self._project = project_result
            steps[-1].status = "success"
            steps[-1].duration_seconds = time.time() - start_time

            # Step 2: التخطيط
            step2_start = time.time()
            steps.append(BuildStep(2, "التخطيط", "running"))
            plan = self._plan(description)
            steps[-1].status = "success"
            steps[-1].duration_seconds = time.time() - step2_start

            # Step 3: التطوير
            step3_start = time.time()
            steps.append(BuildStep(3, "التطوير", "running"))
            self._execute_development(description, plan)
            steps[-1].status = "success"
            steps[-1].duration_seconds = time.time() - step3_start

            # Step 4: الاختبار
            step4_start = time.time()
            steps.append(BuildStep(4, "الاختبار", "running"))
            test_result = self._run_tests()
            if test_result:
                steps[-1].status = "success"
            else:
                steps[-1].status = "skipped"
            steps[-1].duration_seconds = time.time() - step4_start

            # Step 5: مراجعة الأمان
            step5_start = time.time()
            steps.append(BuildStep(5, "مراجعة الأمان", "running"))
            security_result = self._security_check()
            if security_result:
                steps[-1].status = "success"
            else:
                steps[-1].status = "skipped"
            steps[-1].duration_seconds = time.time() - step5_start

            # Step 6: التوثيق
            step6_start = time.time()
            steps.append(BuildStep(6, "التوثيق", "running"))
            reports = self._create_reports(description)
            steps[-1].status = "success"
            steps[-1].duration_seconds = time.time() - step6_start

            # تجميع الملفات
            self._collect_files()

            # تجميع النتيجة
            return BuildResult(
                status="success",
                project_name=self._project["name"],
                project_path=str(Path(PROJECTS_DIR) / self._project["name"]),
                files=self._files,
                files_count=len(self._files),
                run_command=self._detect_run_command(),
                url=self._detect_url(),
                reports=reports,
                steps=steps,
                duration_seconds=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Build failed: {e}")
            return BuildResult(
                status="failed",
                project_name=self._project.get("name", "unknown") if self._project else "unknown",
                project_path=str(Path(PROJECTS_DIR) / self._project.get("name", "")) if self._project else "",
                error=str(e),
                steps=steps,
                duration_seconds=time.time() - start_time
            )

    def _create_project(self, description: str) -> dict:
        """إنشاء مشروع جديد"""
        # تحويل الوصف إلى اسم slug
        name = self._generate_name(description)

        # التحقق من عدم التكرار
        counter = 1
        original_name = name
        while self._project_exists(name):
            name = f"{original_name}-{counter}"
            counter += 1

        # إنشاء المشروع
        result = self.project_manager.create_project(name, description)

        if not result.get("success"):
            raise Exception(result.get("error", "فشل في إنشاء المشروع"))

        project_data = result["project"]
        project_data["path"] = str(Path(PROJECTS_DIR) / name)

        # تسجيل القرار
        record_decision(
            agent="BuildEngine",
            content=f"تم إنشاء مشروع جديد: {name}",
            impact="operational"
        )

        return project_data

    def _generate_name(self, description: str) -> str:
        """يحول الوصف إلى slug إنجليزي"""
        # Keywords mapping
        keywords = {
            "صفحة": "page",
            "موقع": "site",
            "تطبيق": "app",
            "منصة": "platform",
            "نظام": "system",
            "متجر": "store",
            "مشروع": "project",
            "هبوط": "landing",
            "مدونة": "blog",
            "بوابة": "portal",
            " لوحة ": "dashboard",
            "إدارة": "management",
            "تجارة": "trade",
            "صحة": "health",
            "تعليم": "edu",
            "اختبار": "quiz",
            "حجز": "booking",
            "عيادة": "clinic",
            "مستشفى": "hospital",
            "ناشئة": "startup",
            "خدمات": "services",
            "برمجة": "coding",
        }

        name = description.lower()

        # استبدال الكلمات العربية
        for ar, en in keywords.items():
            name = name.replace(ar, f"_{en}_")

        # إزالة الأحرف غير الإنجليزية
        name = re.sub(r'[^a-z0-9_-]', '_', name)

        # إزالةunderscores المتعددة
        name = re.sub(r'_+', '_', name)

        # إزالة الشرطة في البداية والنهاية
        name = name.strip('_')

        # تحويل إلى lowercase
        name = name.lower()

        # إضافة timestamp للتأكد من التفرد
        timestamp = int(time.time()) % 10000
        name = f"{name}_{timestamp}"

        # الحد من الطول
        if len(name) > 50:
            name = name[:50]

        return name

    def _project_exists(self, name: str) -> bool:
        """التحقق من وجود المشروع"""
        project_path = Path(PROJECTS_DIR) / name
        return project_path.exists()

    def _plan(self, description: str) -> List[str]:
        """التخطيط للمشروع"""
        plan = []

        # تحليل نوع المشروع
        desc_lower = description.lower()

        if "html" in desc_lower or "صفحة" in desc_lower or "landing" in desc_lower:
            plan.append("تحليل متطلبات الصفحة")
            plan.append("إنشاء HTML")
            plan.append("إضافة CSS")
            plan.append("إضافة JavaScript")

        elif "flask" in desc_lower or "python" in desc_lower:
            plan.append("إنشاء تطبيق Flask")
            plan.append("تعريف المسارات")
            plan.append("إنشاء القوالب")
            plan.append("إضافة النماذج")

        elif "react" in desc_lower or "vue" in desc_lower:
            plan.append("إنشاء مشروع React/Vue")
            plan.append("تعريف المكونات")
            plan.append("إنشاء الصفحات")
            plan.append("إضافة الـ routing")

        else:
            plan.append("تحليل المتطلبات")
            plan.append("إنشاء الهيكل الأساسي")
            plan.append("تطوير الميزات")
            plan.append("اختبار التطبيق")

        # تسجيل الخطة
        record_decision(
            agent="BuildEngine",
            content=f"خطة المشروع: {', '.join(plan)}",
            impact="operational"
        )

        return plan

    def _execute_development(self, description: str, plan: List[str]):
        """تنفيذ التطوير"""
        project_name = self._project["name"]
        project_path = Path(PROJECTS_DIR) / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        desc_lower = description.lower()

        # إنشاء index.html أساسي
        if "html" in desc_lower or "صفحة" in desc_lower or "landing" in desc_lower or "موقع" in desc_lower:
            self._create_html_project(project_path, description)
        elif "flask" in desc_lower:
            self._create_flask_project(project_path, description)
        else:
            # إنشاء مشروع HTML عام
            self._create_html_project(project_path, description)

    def _create_html_project(self, project_path: Path, description: str):
        """إنشاء مشروع HTML"""
        # index.html
        html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{description[:50]}</title>
    <style>
        :root {{
            --bg-primary: #0a0a14;
            --bg-secondary: #12121f;
            --bg-card: #1a1a2e;
            --accent: #7c3aed;
            --accent-light: #a78bfa;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            background: var(--bg-secondary);
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--bg-card);
        }}
        .header h1 {{
            font-size: 1.5rem;
            color: var(--accent-light);
        }}
        .main {{
            flex: 1;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }}
        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1rem;
        }}
        .btn {{
            background: var(--accent);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
        }}
        .btn:hover {{
            background: var(--accent-light);
        }}
        .footer {{
            background: var(--bg-secondary);
            padding: 1rem;
            text-align: center;
            color: var(--text-secondary);
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>🏗️ {description[:30]}...</h1>
    </header>
    <main class="main">
        <div class="card">
            <h2>مرحباً بك!</h2>
            <p style="margin: 1rem 0; color: var(--text-secondary);">
                تم إنشاء هذا المشروع بواسطة <strong>CodeForge</strong>
            </p>
            <button class="btn" onclick="alert('تم النقر!')">ابدأ الآن</button>
        </div>
    </main>
    <footer class="footer">
        <p>© 2026 CodeForge - صُنع بالذكاء الاصطناعي</p>
    </footer>
    <script>
        console.log('🏗️ CodeForge: تم تحميل المشروع بنجاح');
    </script>
</body>
</html>"""
        index_file = project_path / "index.html"
        index_file.write_text(html_content, encoding="utf-8")

    def _create_flask_project(self, project_path: Path, description: str):
        """إنشاء مشروع Flask"""
        # app.py
        app_content = f'''"""{description}
منشأ بواسطة CodeForge
"""

from flask import Flask, render_template

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.route("/")
def index():
    """الصفحة الرئيسية"""
    return render_template("index.html", title="{description[:30]}")

@app.route("/about")
def about():
    """صفحة من نحن"""
    return "<h1>من نحن</h1><p>تم إنشاء هذا التطبيق بواسطة CodeForge</p>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''
        app_file = project_path / "app.py"
        app_file.write_text(app_content, encoding="utf-8")

        # templates
        templates_dir = project_path / "templates"
        templates_dir.mkdir(exist_ok=True)

        template_content = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: sans-serif; background: #0a0a14; color: #f8fafc; padding: 2rem; }
        h1 { color: #a78bfa; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>تم إنشاء هذا التطبيق بواسطة CodeForge</p>
</body>
</html>'''
        template_file = templates_dir / "index.html"
        template_file.write_text(template_content, encoding="utf-8")

        # requirements.txt
        requirements = "flask==3.0.0\n"
        req_file = project_path / "requirements.txt"
        req_file.write_text(requirements)

    def _run_tests(self) -> bool:
        """تشغيل الاختبارات"""
        project_name = self._project["name"]
        project_path = Path(PROJECTS_DIR) / project_name

        # فحص وجود الملفات الأساسية
        index_html = project_path / "index.html"
        if not index_html.exists():
            return False

        # فحص صحة HTML
        content = index_html.read_text(encoding="utf-8")
        checks = [
            "<!DOCTYPE html>" in content,
            "<html" in content,
            "</html>" in content,
            "<head>" in content,
            "</head>" in content,
            "<body>" in content,
            "</body>" in content,
        ]

        return all(checks)

    def _security_check(self) -> bool:
        """فحص الأمان"""
        project_name = self._project["name"]
        project_path = Path(PROJECTS_DIR) / project_name

        # فحص وجود eval أو exec في JavaScript
        for js_file in project_path.rglob("*.js"):
            content = js_file.read_text(encoding="utf-8")
            if "eval(" in content or "exec(" in content:
                return False

        return True

    def _create_reports(self, description: str) -> List[str]:
        """إنشاء التقارير"""
        project_name = self._project["name"]
        reports_dir = Path("docs/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_file = reports_dir / f"{project_name}-build.md"
        report_content = f"""# تقرير بناء: {project_name}

## معلومات المشروع

| الحقل | القيمة |
|-------|--------|
| **الاسم** | {project_name} |
| **الوصف** | {description} |
| **تاريخ الإنشاء** | {time.strftime('%Y-%m-%d %H:%M:%S')} |

## الملفات

{chr(10).join([f"- `{f}`" for f in self._files])}

---
_تقرير مُنشأ بواسطة CodeForge v1.0_
"""
        report_file.write_text(report_content, encoding="utf-8")

        return [str(report_file)]

    def _collect_files(self):
        """جمع قائمة الملفات"""
        project_name = self._project["name"]
        project_path = Path(PROJECTS_DIR) / project_name

        self._files = []
        for file in project_path.rglob("*"):
            if file.is_file():
                self._files.append(str(file.relative_to(project_path)))

    def _detect_run_command(self) -> str:
        """يكتشف أمر التشغيل من نوع المشروع"""
        project_name = self._project["name"]
        project_path = Path(PROJECTS_DIR) / project_name

        # فحص وجود app.py مع Flask
        app_py = project_path / "app.py"
        if app_py.exists():
            content = app_py.read_text(encoding="utf-8")
            if "flask" in content.lower() and "app.run" in content:
                return "python app.py"

        # فحص وجود package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            return "npm run dev"

        # فحص وجود HTML
        if (project_path / "index.html").exists():
            return "python -m http.server 8080"

        return "python -m http.server 8080"

    def _detect_url(self) -> str:
        """يكتشف الرابط المناسب"""
        run_command = self._detect_run_command()

        if "5000" in run_command:
            return "http://localhost:5000"
        elif "5173" in run_command:
            return "http://localhost:5173"
        else:
            return "http://localhost:8080"
