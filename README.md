# CodeForge 🔨

**منصة تطوير متعددة الوكلاء تعمل من الهاتف**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

---

## نظرة عامة

CodeForge هي منصة تطوير برمجيات متقدمة تستخدم الذكاء الاصطناعي لتنسيق فريق من الوكلاء (Agents) المتخصصين:

- **Manager** - تنسيق المهام وتتبع التقدم
- **Architect** - تحليل المتطلبات وتصميم المعمارية
- **Developer** - كتابة الكود وتنفيذ المهام
- **QA** - اختبار الكود وضمان الجودة

---

## المعمارية

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│    Phone    │────▶│   GitHub    │────▶│  Codespaces  │
└─────────────┘     └─────────────┘     └──────────────┘
                                                 │
                                                 ▼
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│     Git     │◀────│ Orchestration   │◀────│  Workspace   │
└─────────────┘     │    Layer        │     └──────────────┘
                    └─────────────────┘
```

### الطبقات الرئيسية

| الطبقة | التقنية | الحالة |
|--------|---------|--------|
| Orchestration | **CrewAI** | مخطط (Phase 2) |
| Execution | **OpenHands** | مخطط (Phase 3) |
| Memory | docs/ → **ChromaDB** | جاري (Phase 3) |

---

## مراحل التطوير

### المرحلة 1: الأساس ✅
- [x] هيكل المشروع
- [x] التوثيق الأولي
- [x] تعريف الأدوار

### المرحلة 2: الوكلاء + CrewAI ✅
- [x] دمج CrewAI
- [x] بناء 4 وكلاء
- [x] ربط Gemini API
- [x] صفحة هبوط CodeForge AI

### المرحلة 3: دورة العمل + الذاكرة + Git ✅ (الحالية)
- [x] دورة العمل الكاملة (Pipeline)
- [x] الذاكرة الذكية
- [x] إدارة Git
- [x] المهمة الأولى: إضافة زر التواصل

### المرحلة 4: واجهة الهاتف + الإنتاج 📋
- [ ] تطبيق هاتف
- [ ] أول مشروع حقيقي
- [ ] دعم production

---

## هيكل المشروع

```
codeforge/
├── docs/               # التوثيق
│   ├── vision.md      # الرؤية
│   ├── architecture.md # المعمارية
│   ├── roadmap.md     # خارطة الطريق
│   ├── progress.md    # سجل التقدم
│   ├── coding_rules.md # قواعد الترميز
│   ├── project_conventions.md # اتفاقيات
│   ├── qa_report.md   # تقرير الاختبار
│   ├── adr/          # Architecture Decisions
│   │   ├── 001-initial-architecture.md
│   │   ├── 002-first-agents.md
│   │   └── 003-pipeline-memory-git.md
│   └── reports/       # تقارير المهام
├── agents/            # تعريف الوكلاء
│   ├── manager/       # Manager Agent
│   ├── architect/     # Architect Agent
│   ├── developer/     # Developer Agent
│   └── qa/           # QA Agent
├── memory/            # طبقة الذاكرة
├── src/               # الكود المصدري
│   ├── agents.py     # فريق الوكلاء (Phase 2)
│   ├── state.py      # نظام الحالة (Phase 3)
│   ├── memory.py     # الذاكرة الذكية (Phase 3)
│   ├── pipeline.py   # دورة العمل (Phase 3)
│   └── git_manager.py # إدارة Git (Phase 3)
├── tests/             # الاختبارات
└── workspace/         # مساحة العمل
    └── index.html    # صفحة الهبوط
```

---

## المتطلبات

- Python 3.11+
- Git

### للمرحلة 2+ (مُثبت)
- CrewAI >= 1.15
- CrewAI Tools >= 1.15
- litellm >= 1.0
- Gemini API Key (GEMINI_API_KEY)

### للمرحلة 3+ (مُثبت Phase 3)
- Python Standard Library (state, memory, pipeline, git_manager)
- ChromaDB (مخطط لـ Phase 4)
- OpenHands (مخطط لـ Phase 4)

---

## البدء

### استنساخ المشروع
```bash
git clone https://github.com/codeforge/codeforge.git
cd codeforge
```

### إعداد البيئة
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
.\venv\Scripts\activate  # Windows
```

### التثبيت (المرحلة 2+)
```bash
pip install -e .
```

---

## التوثيق

| الملف | الوصف |
|-------|-------|
| `docs/vision.md` | رؤية المشروع وأهدافه |
| `docs/architecture.md` | المعمارية التقنية |
| `docs/roadmap.md` | خطة التطوير |
| `docs/progress.md` | سجل التقدم |
| `docs/coding_rules.md` | قواعد الترميز |
| `docs/project_conventions.md` | اتفاقيات المشروع |

---

## المساهمة

1. Fork المشروع
2. أنشئ branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'feat: إضافة ميزة'`)
4. Push (`git push origin feature/amazing-feature`)
5. افتح Pull Request

---

## الرخصة

هذا المشروع مرخص تحت [MIT License](LICENSE).

---

## الفريق

- **CodeForge Team** - فريق التطوير

---

<div align="center">

**صُنع بـ ❤️ للمطورين العرب**

</div>
