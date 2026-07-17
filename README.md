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

### المرحلة 1: الأساس ✅ (الحالية)
- [x] هيكل المشروع
- [x] التوثيق الأولي
- [x] تعريف الأدوار

### المرحلة 2: الوكلاء + CrewAI 📋
- [ ] دمج CrewAI
- [ ] بناء 4 وكلاء
- [ ] ربط Gemini API

### المرحلة 3: دورة العمل + الذاكرة 📋
- [ ] دورة عمل كاملة
- [ ] ChromaDB للذاكرة
- [ ] تكامل Git متقدم

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
│   └── adr/          # Architecture Decisions
├── agents/            # تعريف الوكلاء
│   ├── manager/       # Manager Agent
│   ├── architect/     # Architect Agent
│   ├── developer/     # Developer Agent
│   └── qa/           # QA Agent
├── memory/            # طبقة الذاكرة
├── src/               # الكود المصدري
├── tests/             # الاختبارات
└── workspace/         # مساحة العمل
```

---

## المتطلبات

- Python 3.11+
- Git

### للمرحلة 2+
- CrewAI
- Gemini API Key

### للمرحلة 3+
- OpenHands
- ChromaDB

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
