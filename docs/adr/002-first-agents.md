# ADR-002: تنفيذ الوكلاء الأربعة + Gemini Integration

## الحالة
**مقبول** - 2026-07-17

---

## المشكلة

نحتاج لتفعيل Phase 2: بناء فريق الوكلاء الأربعة وتشغيل أول مهمة حقيقية.

---

## السياق

CodeForge Phase 2 تتضمن:
- تثبيت CrewAI
- بناء 4 وكلاء (Manager, Architect, Developer, QA)
- ربط Gemini API
- تشغيل المهمة الأولى: صفحة هبوط

### المهمة الأولى
إنشاء صفحة هبوط لشركة "CodeForge AI":
- عنوان رئيسي: 'ابنِ تطبيقاتك بالذكاء الاصطناعي'
- عنوان فرعي: 'منصة تطوير متعددة الوكلاء تعمل من هاتفك'
- زر دعوة للإجراء: 'ابدأ الآن'
- تصميم داكن بسيط

---

## القرارات

### 1. اختيار CrewAI كإطار تنسيق
- **القرار**: CrewAI v1.15+
- **السبب**: جاهز، مختبر، دعم Agents + Tasks + Crew
- **التثبيت**: `pip install crewai crewai-tools`

### 2. استخدام Gemini كـ LLM
- **القرار**: Gemini 2.0 Flash
- **السبب**: سريع، رخيص، جيد للكود
- **التكوين**: `GEMINI_API_KEY` environment variable
- **Fallback**: GPT-4 إذا لم يتوفر Gemini

### 3. هيكل الكود
```
src/
├── agents.py      # تعريف الوكلاء والمهام
└── __init__.py
```

### 4. الأدوات (Tools)
| الوكيل | الأدوات |
|--------|---------|
| Manager | FileReadTool, FileWriteTool (docs/progress.md) |
| Architect | FileWriteTool (docs/adr/) |
| Developer | FileWriteTool (workspace/index.html) |
| QA | FileWriteTool (docs/qa_report.md) |

### 5. تصميم صفحة الهبوط
- **HTML5 Semantic**: استخدام عناصر HTML5 الصحيحة
- **CSS inline**: CSS مدمج في الملف الواحد
- **تصميم داكن**: خلفية #0a0a0f، ألوان مضيئة
- **متجاوب**: يعمل على الهاتف والكمبيوتر

---

## دورة العمل (Workflow)

```
1. Manager
   └── يبدأ المهمة
   └── يسجل في progress.md
   
2. Architect
   └── يحلل المتطلبات
   └── ينشئ ADR-002
   
3. Developer
   └── يكتب index.html
   └── يتبع التصميم
   
4. QA
   └── يختبر الصفحة
   └── يكتب تقرير
   
5. Manager
   └── يسجل النتيجة
```

---

## النتائج

### ✅ مكتسبات
- فريق عمل كامل من الوكلاء
- CrewAI مُدمج ويعمل
- مهمة أولى منجزة
- توثيق كامل في ADR

### ⚠️ مخاطر
| المخاطر | التخفيف |
|---------|---------|
| تكلفة Gemini API | monitoring + استخدام Flash |
| فشل API | retry logic + fallback |
| جودة الكود | QA يختبر قبل الدمج |

---

## التنفيذ

### الملفات الجديدة
- `src/agents.py` - تعريف الوكلاء
- `workspace/index.html` - صفحة الهبوط
- `docs/adr/002-first-agents.md` - هذا ADR
- `docs/qa_report.md` - تقرير الاختبار

### التبعيات
```txt
crewai>=1.15.0
crewai-tools>=1.15.0
litellm>=1.0.0
```

### متغيرات البيئة
```bash
export GEMINI_API_KEY="your-key-here"
```

---

## ملاحظات

- هذا ADR يمهد لـ Phase 3 (دورة العمل الكاملة)
- OpenHands سيُستخدم لاحقاً للتنفيذ الفعلي
- ChromaDB للذاكرة في Phase 3
