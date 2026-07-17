"""
CodeForge Agent Team - Phase 2, 3 & 6A
==================================
فريق الوكلاء: Manager, Architect, Developer, QA, Security, Documentation
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from crewai import Agent, Task, Crew, Process
try:
    from crewai_tools import FileReadTool, FileWriterTool as FileWriteTool
except ImportError:
    try:
        from crewai_tools import FileReadTool, FileWriteTool
    except ImportError:
        FileReadTool = None
        FileWriteTool = None

# ============================================================
# Phase 3 & 6A Modules
# ============================================================

try:
    from src.state import get_state, record_agent_decision, get_task_id
    from src.memory import record_decision as memory_record_decision, update_progress
    from src.git_manager import auto_commit, auto_push, has_uncommitted_changes
    from src.logger import logger, log_event, log_error
    from src.model_router import get_model_for_task, get_llm_config
    PHASE3_ENABLED = True
except ImportError:
    PHASE3_ENABLED = False
    log_event = lambda *a, **k: None
    log_error = lambda *a, **k: None

# ============================================================
# الأدوات (Tools)
# ============================================================

progress_reader = FileReadTool(file_path="docs/progress.md")
progress_writer = FileWriteTool(file_path="docs/progress.md")
adr_writer = FileWriteTool(file_path="docs/adr/")
html_writer = FileWriteTool(file_path="workspace/index.html")
qa_writer = FileWriteTool(file_path="docs/qa_report.md")


def record_agent_decision_safe(agent: str, content: str, impact: str):
    """تسجيل قرار بطريقة آمنة (مع fallback)"""
    if PHASE3_ENABLED:
        try:
            memory_record_decision(agent, content, impact)
        except Exception:
            pass  # Phase 3 غير مهيأ


def update_progress_safe(task: str, status: str, notes: str = ""):
    """تحديث التقدم بطريقة آمنة"""
    if PHASE3_ENABLED:
        try:
            update_progress(task, status, notes)
        except Exception:
            pass


def auto_commit_safe(message: str = None):
    """Commit بطريقة آمنة"""
    if PHASE3_ENABLED:
        try:
            return auto_commit(message)
        except Exception:
            return False, "Phase 3 غير مهيأ"
    return False, "Phase 3 غير مهيأ"


def auto_push_safe():
    """Push بطريقة آمنة"""
    if PHASE3_ENABLED:
        try:
            return auto_push()
        except Exception:
            return False, "Phase 3 غير مهيأ"
    return False, "Phase 3 غير مهيأ"


# ============================================================
# إعدادات النموذج اللغوي
# ============================================================

def get_llm():
    """الحصول على نموذج Gemini عبر litellm."""
    import litellm
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        return "gemini/gemini-2.0-flash"
    return "gpt-4"


# ============================================================
# الوكيل 1: Manager Agent
# ============================================================

manager_agent = Agent(
    role="مدير المشروع (Manager)",
    goal="تنسيق المهام وتتبع التقدم وإدارة دورة العمل كاملة",
    backstory="""
أنت مدير المشروع في CodeForge. دورك هو:
1. تنسيق المهام بين الوكلاء
2. تتبع التقدم وتحديث docs/progress.md
3. إدارة دورة العمل: Plan → Execute → Test → Fix
4. ضمان التواصل الفعال بين الوكلاء
5. تسجيل القرارات في memory (Phase 3)

أنت تعمل عن كثب مع Architect لتحليل المتطلبات،
ومع Developer لتنفيذ المهام،
ومع QA للتحقق من الجودة.
""",
    verbose=True,
    allow_delegation=True,
    tools=[progress_reader, progress_writer],
)

# ============================================================
# الوكيل 2: Architect Agent
# ============================================================

architect_agent = Agent(
    role="المعماري (Architect)",
    goal="تحليل المتطلبات وتصميم الحل وإخراج خطة واضحة قبل أي كود",
    backstory="""
أنت المعماري في CodeForge. دورك هو:
1. تحليل المتطلبات بدقة
2. تصميم المعمارية والحل التقني
3. كتابة ADR لكل قرار معماري مهم
4. التأكد من أن التصميم قابل للتطبيق

أنت تعمل مع Manager لفهم المتطلبات،
ومع Developer لتوضيح التصميم.
""",
    verbose=True,
    tools=[adr_writer],
)

# ============================================================
# الوكيل 3: Developer Agent
# ============================================================

developer_agent = Agent(
    role="المطور (Developer)",
    goal="كتابة الكود الفعلي وإنتاج كود نظيف وعملي",
    backstory="""
أنت المطور في CodeForge. دورك هو:
1. تنفيذ المهام حسب المواصفات
2. كتابة كود نظيف ومُعلق
3. اتباع معايير الترميز (PEP 8)
4. كتابة اختبارات بسيطة

أنت تعمل بناءً على تصميم Architect،
وتقدم العمل لـ QA للمراجعة.
""",
    verbose=True,
    tools=[html_writer],
)

# ============================================================
# الوكيل 4: QA Agent
# ============================================================

qa_agent = Agent(
    role="ضمان الجودة (QA)",
    goal="اختبار الكود واكتشاف الأخطاء والتحقق من الجودة",
    backstory="""
أنت مسؤول ضمان الجودة في CodeForge. دورك هو:
1. اختبار الكود بشكل شامل
2. اكتشاف الأخطاء والمشاكل
3. التحقق من جودة الكود
4. كتابة تقارير الاختبار

أنت تعمل على مراجعة عمل Developer،
وتقديم التغذية الراجعة لـ Manager.
""",
    verbose=True,
    tools=[qa_writer],
)

# ============================================================
# المهام (Tasks)
# ============================================================

# مهمة المدير: بدء المهمة وتتبعها
manager_task = Task(
    description="""
1. سجل المهمة الجديدة في docs/progress.md
2. وزّع المهام على الوكلاء:
   - Architect: تحليل المتطلبات
   - Developer: تنفيذ الكود
   - QA: اختبار الكود
3. تابع التقدم وحدّث docs/progress.md
4. أبلغ بالنتيجة النهائية
""",
    agent=manager_agent,
    expected_output="تقرير تقدم محدث في docs/progress.md",
)

# مهمة المعماري: تحليل وتصميم
architect_task = Task(
    description="""
تحليل متطلبات صفحة الهبوط لشركة CodeForge AI:
- عنوان رئيسي: 'ابنِ تطبيقاتك بالذكاء الاصطناعي'
- عنوان فرعي: 'منصة تطوير متعددة الوكلاء تعمل من هاتفك'
- زر دعوة للإجراء: 'ابدأ الآن'
- تصميم داكن بسيط

أنشئ ADR في docs/adr/002-first-agents.md يوثق:
1. قرار التصميم (HTML/CSS)
2. قرار اللون (داكن)
3. قرار البساطة
""",
    agent=architect_agent,
    expected_output="ADR في docs/adr/002-first-agents.md",
)

# مهمة المطور: إنشاء صفحة الهبوط
developer_task = Task(
    description="""
أنشئ صفحة هبوط (index.html) في workspace/ تتضمن:
- HTML5 semantic
- CSS inline (تصميم داكن)
- العنوان الرئيسي: 'ابنِ تطبيقاتك بالذكاء الاصطناعي'
- العنوان الفرعي: 'منصة تطوير متعددة الوكلاء تعمل من هاتفك'
- زر: 'ابدأ الآن'
- تصميم بسيط وأنيق
""",
    agent=developer_agent,
    expected_output="ملف workspace/index.html",
)

# مهمة QA: اختبار الصفحة
qa_task = Task(
    description="""
راجع صفحة الهبوط في workspace/index.html:
1. تحقق من وجود جميع العناصر المطلوبة
2. تحقق من صحة HTML
3. تحقق من التصميم الداكن
4. اكتب تقرير اختبار في docs/qa_report.md
""",
    agent=qa_agent,
    expected_output="تقرير اختبار في docs/qa_report.md",
)

# ============================================================
# Phase 3: Pipeline Integration
# ============================================================

def run_pipeline_task(task_description: str):
    """تشغيل مهمة عبر Pipeline (Phase 3)"""
    try:
        from src.pipeline import execute_task
        return execute_task(task_description)
    except ImportError:
        print("⚠️ Phase 3 Pipeline غير متوفر")
        return None


# ============================================================
# فريق العمل (Crew)
# ============================================================

def create_crew():
    """إنشاء فريق العمل مع CrewAI."""
    crew = Crew(
        agents=[manager_agent, architect_agent, developer_agent, qa_agent],
        tasks=[manager_task, architect_task, developer_task, qa_task],
        process=Process.sequential,
        verbose=True,
    )
    return crew


def run_landing_page_task():
    """تشغيل المهمة الأولى: إنشاء صفحة هبوط."""
    print("🚀 بدء فريق CodeForge - المهمة: صفحة الهبوط")
    print("=" * 60)
    
    crew = create_crew()
    result = crew.kickoff()
    
    print("\n" + "=" * 60)
    print("✅ اكتملت المهمة!")
    print("=" * 60)
    
    return result


# ============================================================
# Phase 6A: Security Agent
# ============================================================

class SecurityAgent:
    """وكيل الأمان"""

    def __init__(self):
        self.name = "Security"
        self.issues_found: List[Dict] = []

    def scan_file(self, file_path: str) -> Dict:
        """فحص ملف واحد للأمان"""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
            
            # Check for API keys/secrets
            secret_patterns = [
                (r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "API Key exposed"),
                (r'secret["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "Secret exposed"),
                (r'password["\']?\s*[:=]\s*["\']?[^"\'\s]{8,}', "Password in code"),
                (r'token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}', "Token in code"),
                (r'ghp_[a-zA-Z0-9]{36}', "GitHub token"),
                (r'AKIA[0-9A-Z]{16}', "AWS access key"),
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern, issue_type in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            "file": file_path,
                            "line": i,
                            "type": issue_type,
                            "severity": "critical",
                            "content": line.strip()[:100],
                        })
            
            # Check for unsafe patterns
            unsafe_patterns = [
                (r'innerHTML\s*=', "innerHTML - XSS risk"),
                (r'\.innerHTML\s*=', "innerHTML assignment - XSS risk"),
                (r'document\.write\s*\(', "document.write - XSS risk"),
                (r'eval\s*\(', "eval() - code injection risk"),
                (r'exec\s*\(', "exec() - code injection risk"),
                (r'os\.system\s*\(', "os.system() - command injection"),
                (r'subprocess\.\w+\s*\(\s*shell\s*=\s*True', "shell=True - command injection"),
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern, issue_type in unsafe_patterns:
                    if re.search(pattern, line):
                        issues.append({
                            "file": file_path,
                            "line": i,
                            "type": issue_type,
                            "severity": "high",
                            "content": line.strip()[:100],
                        })
            
            # Check for SQL injection patterns
            sql_patterns = [
                (r'execute\s*\(\s*f["\']', "SQL with f-string - injection risk"),
                (r'cursor\.execute\s*\(.*\%s', "SQL with %s - check for proper escaping"),
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern, issue_type in sql_patterns:
                    if re.search(pattern, line):
                        issues.append({
                            "file": file_path,
                            "line": i,
                            "type": issue_type,
                            "severity": "medium",
                            "content": line.strip()[:100],
                        })
            
        except Exception as e:
            issues.append({
                "file": file_path,
                "line": 0,
                "type": "scan_error",
                "severity": "info",
                "content": str(e),
            })
        
        return {
            "file": file_path,
            "issues": issues,
            "issue_count": len(issues),
        }

    def scan_project(self, root_dir: str = ".") -> Dict:
        """فحص المشروع كامل"""
        results = {
            "files_scanned": 0,
            "total_issues": 0,
            "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            "issues": [],
            "scanned_files": [],
        }
        
        # Code files to scan
        extensions = [".py", ".js", ".html", ".ts", ".jsx", ".tsx"]
        
        for ext in extensions:
            for file_path in Path(root_dir).rglob(f"*{ext}"):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ["node_modules", ".git", "__pycache__", "venv", ".venv"]):
                    continue
                
                result = self.scan_file(str(file_path))
                results["scanned_files"].append(str(file_path))
                results["files_scanned"] += 1
                results["total_issues"] += result["issue_count"]
                
                for issue in result["issues"]:
                    results["by_severity"][issue["severity"]] += 1
                    results["issues"].append(issue)
        
        return results

    def generate_report(self, results: Dict) -> str:
        """إنشاء تقرير الأمان"""
        report = f"""# تقرير الأمان - CodeForge
=========================

تاريخ الفحص: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ملخص

| المقياس | القيمة |
|---------|--------|
| الملفات المفحوصة | {results['files_scanned']} |
| إجمالي المشاكل | {results['total_issues']} |
| حرجة | {results['by_severity']['critical']} |
| عالية | {results['by_severity']['high']} |
| متوسطة | {results['by_severity']['medium']} |
| منخفضة | {results['by_severity']['low']} |
| معلومات | {results['by_severity']['info']} |

"""
        
        if results["issues"]:
            report += "## المشاكل المكتشفة\n\n"
            
            # Sort by severity
            severity_order = ["critical", "high", "medium", "low", "info"]
            for severity in severity_order:
                severity_issues = [i for i in results["issues"] if i["severity"] == severity]
                if severity_issues:
                    report += f"### {severity.upper()}\n\n"
                    for issue in severity_issues:
                        report += f"- **{issue['type']}** in `{issue['file']}` line {issue['line']}\n"
                        report += f"  ```\n  {issue['content']}\n  ```\n\n"
        
        report += "\n## التوصيات\n\n"
        if results["by_severity"]["critical"] > 0 or results["by_severity"]["high"] > 0:
            report += "⚠️ **تحتاج اهتمام فوري!** يرجى إصلاح المشاكل الحرجة والعالية أولاً.\n\n"
        else:
            report += "✅ لا توجد مشاكل حرجة أو عالية.\n\n"
        
        report += "### أفضل الممارسات:\n"
        report += "1. استخدم متغيرات البيئة للمفاتيح السرية\n"
        report += "2. تجنب innerHTML - استخدم textContent\n"
        report += "3. لا تستخدم eval() أو exec()\n"
        report += "4. استخدم استعلامات parameterized للـ SQL\n"
        report += "5. تحقق من المدخلات دائماً\n"
        
        return report

    def save_report(self, results: Dict, report_path: str = "docs/reports/security-report.md"):
        """حفظ التقرير"""
        report = self.generate_report(results)
        
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        return report_path


# ============================================================
# Phase 6A: Documentation Agent
# ============================================================

class DocumentationAgent:
    """وكيل التوثيق"""

    def __init__(self):
        self.name = "Documentation"
        self.changes_made: List[str] = []

    def update_progress(self, task_id: str, task_name: str, status: str, notes: str = ""):
        """تحديث progress.md"""
        try:
            progress_file = Path("docs/progress.md")
            if not progress_file.exists():
                return False
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            status_icon = {
                "completed": "✅",
                "in_progress": "🔄",
                "failed": "❌",
                "blocked": "⏸️",
            }.get(status, "📋")
            
            entry = f"\n| {task_id} | {task_name} | {timestamp} | {status_icon} {status} | {notes} |"
            
            with open(progress_file, "a", encoding="utf-8") as f:
                f.write(entry)
            
            self.changes_made.append(f"Updated progress.md: {task_id}")
            return True
        except Exception as e:
            log_error("Documentation", f"Failed to update progress: {e}")
            return False

    def update_readme(self, section: str, content: str):
        """تحديث README.md"""
        try:
            readme_file = Path("README.md")
            if not readme_file.exists():
                return False
            
            # Read current content
            with open(readme_file, "r", encoding="utf-8") as f:
                content_current = f.read()
            
            # Simple section update
            if f"## {section}" in content_current:
                # Find section and replace
                pattern = rf"(## {section}.*?)(?=\n## |\Z)"
                new_content = rf"\1\n\n{content}\n"
                updated = re.sub(pattern, new_content, content_current, flags=re.DOTALL)
            else:
                # Append at end
                updated = content_current + f"\n\n## {section}\n\n{content}\n"
            
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(updated)
            
            self.changes_made.append(f"Updated README.md: {section}")
            return True
        except Exception as e:
            log_error("Documentation", f"Failed to update README: {e}")
            return False

    def create_adr(self, number: int, title: str, content: str, agent: str = "Documentation") -> str:
        """إنشاء ADR جديد"""
        try:
            adr_file = Path(f"docs/adr/ADR-{number:03d}-{agent.lower()}.md")
            adr_file.parent.mkdir(parents=True, exist_ok=True)
            
            adr_content = f"""# ADR-{number:03d}: {title}

## الحالة
**مقبول** - {datetime.now().strftime('%Y-%m-%d')}

---

## القرار

**الوكيل**: {agent}

{content}

---

## السبب

[يُضاف لاحقاً]

---

## النتائج

### إيجابية
- 

### سلبية
- 

---

## ملاحظات

- تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
            
            with open(adr_file, "w", encoding="utf-8") as f:
                f.write(adr_content)
            
            self.changes_made.append(f"Created ADR-{number:03d}: {title}")
            return str(adr_file)
        except Exception as e:
            log_error("Documentation", f"Failed to create ADR: {e}")
            return ""

    def create_task_report(self, task_id: str, description: str, status: str,
                          plan: List[str] = None, files: List[str] = None,
                          errors: List[str] = None) -> str:
        """إنشاء تقرير مهمة"""
        try:
            report_file = Path(f"docs/reports/{task_id}.md")
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            status_icon = {
                "completed": "✅",
                "in_progress": "🔄",
                "failed": "❌",
            }.get(status, "📋")
            
            report = f"""# تقرير المهمة: {task_id}

## معلومات عامة

| الحقل | القيمة |
|-------|--------|
| **المعرف** | {task_id} |
| **الوصف** | {description} |
| **الحالة** | {status_icon} {status} |
| **تاريخ البدء** | {datetime.now().strftime('%Y-%m-%d')} |

---

## الخطة

"""
            if plan:
                for i, step in enumerate(plan, 1):
                    report += f"{i}. {step}\n"
            else:
                report += "_لا توجد خطة مسجلة_\n"
            
            report += "\n## الملفات المعدلة\n\n"
            if files:
                for f in files:
                    report += f"- `{f}`\n"
            else:
                report += "_لا توجد ملفات معدلة_\n"
            
            report += "\n## الأخطاء\n\n"
            if errors:
                for err in errors:
                    report += f"- ❌ {err}\n"
            else:
                report += "✅ لا توجد أخطاء\n"
            
            report += "\n---\n\n_تقرير مُنشأ بواسطة CodeForge Documentation Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}_"
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            self.changes_made.append(f"Created report: {task_id}")
            return str(report_file)
        except Exception as e:
            log_error("Documentation", f"Failed to create report: {e}")
            return ""

    def get_changes(self) -> List[str]:
        """الحصول على التغييرات"""
        return self.changes_made.copy()

    def clear_changes(self):
        """مسح سجل التغييرات"""
        self.changes_made = []


# ============================================================
# Global Instances
# ============================================================

security_agent = SecurityAgent()
documentation_agent = DocumentationAgent()


# ============================================================
# نقطة الدخول
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Phase 3+: استخدام Pipeline
        task_description = sys.argv[1]
        print(f"🎯 تشغيل Pipeline للمهمة: {task_description}")
        result = run_pipeline_task(task_description)
        if result:
            print(f"\n📊 النتيجة: {result.status}")
    else:
        # Phase 2: المهمة الأولى
        result = run_landing_page_task()
        print(f"\nالنتيجة:\n{result}")
