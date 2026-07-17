"""
CodeForge Agent Team - Phase 2
===============================
فريق الوكلاء الأربعة: Manager, Architect, Developer, QA
"""

import os
import json
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, FileWriteTool

# ============================================================
# الأدوات (Tools)
# ============================================================

progress_reader = FileReadTool(file_path="docs/progress.md")
progress_writer = FileWriteTool(file_path="docs/progress.md")
adr_writer = FileWriteTool(file_path="docs/adr/")
html_writer = FileWriteTool(file_path="workspace/index.html")
qa_writer = FileWriteTool(file_path="docs/qa_report.md")

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
# نقطة الدخول
# ============================================================

if __name__ == "__main__":
    result = run_landing_page_task()
    print(f"\nالنتيجة:\n{result}")
