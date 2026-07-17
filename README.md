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

### المرحلة 3: دورة العمل + الذاكرة + Git ✅
- [x] دورة العمل الكاملة (Pipeline)
- [x] الذاكرة الذكية
- [x] إدارة Git
- [x] المهمة الأولى: إضافة زر التواصل

### المرحلة 4: واجهة الهاتف + أول مشروع ✅ (الحالية)
- [x] واجهة ويب Flask
- [x] API منفصل
- [x] لوحة تحكم
- [x] المشروع التجريبي: Todo App
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
│   │   ├── 003-pipeline-memory-git.md
│   │   └── 004-todo-app-project.md
│   └── reports/       # تقارير المهام
├── agents/            # تعريف الوكلاء
├── memory/            # طبقة الذاكرة
├── src/               # الكود المصدري
│   ├── agents.py     # فريق الوكلاء
│   ├── state.py      # نظام الحالة
│   ├── memory.py     # الذاكرة الذكية
│   ├── pipeline.py   # دورة العمل
│   ├── git_manager.py # إدارة Git
│   └── app.py        # Flask API (Phase 4)
├── templates/         # قوالب Flask
├── static/           # ملفات CSS/JS
├── workspace/         # مساحة العمل
│   ├── index.html    # صفحة الهبوط
│   └── projects/     # المشاريع
│       └── todo_app/ # المشروع التجريبي
└── tests/             # الاختبارات
```

---

## المتطلبات

- Python 3.11+
- Git

### Phase 4 (مُثبت)
- Flask >= 3.0
- CrewAI >= 1.15
- CrewAI Tools >= 1.15
- litellm >= 1.0
- Python Standard Library

---

## 🚀 التشغيل

### واجهة الويب (Flask)

```bash
cd /workspace/project/codeforge
pip install flask
python src/app.py
```

ثم افتح: http://localhost:5000

### واجهة سطر الأوامر

```bash
python src/agents.py "وصف المهمة"
```

### API

| المسار | الطريقة | الوصف |
|--------|--------|-------|
| `/api/health` | GET | فحص الصحة |
| `/api/state` | GET | حالة المنصة |
| `/api/projects` | GET/POST | إدارة المشاريع |
| `/api/projects/<name>/activate` | POST | تفعيل مشروع |
| `/api/projects/<name>/archive` | POST | أرشفة مشروع |
| `/api/projects/<name>` | DELETE | حذف مشروع |
| `/api/tasks` | GET/POST | المهام |
| `/api/events` | GET | سجل الأحداث |
| `/api/search` | GET | بحث في الذاكرة |
| `/api/adrs` | GET | قائمة ADRs |

---

## 🏗️ الهيكل (Phase 5)

```
codeforge/
├── config/           # إعدادات مركزية
│   ├── paths.py      # المسارات
│   ├── models.py    # النماذج
│   └── settings.py  # الإعدادات
├── src/             # الكود المصدري
│   ├── state.py      # الحالة
│   ├── memory.py     # الذاكرة
│   ├── pipeline.py   # دورة العمل
│   ├── project_manager.py # المشاريع
│   ├── health.py    # فحص الصحة
│   ├── event_logger.py  # سجل الأحداث
│   ├── storage/     # طبقة التخزين
│   └── app.py       # Flask API
├── projects/        # المشاريع
│   ├── todo_app/    # مثال
│   └── archive/     # مؤرشف
├── docs/
│   ├── projects/    # وثائق المشاريع
│   ├── adr/        # القرارات المعمارية
│   └── reports/    # تقارير المهام
├── logs/            # السجلات
│   └── events.log   # سجل الأحداث
└── workspace/       # العمل المؤقت

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
