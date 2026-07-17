# ADR-006: جاهزية الإنتاج (Phase 6A)

## الحالة
**مقبول** - 2026-07-17

---

## المشكلة

تحويل CodeForge من نموذج أولي إلى منصة جاهزة للإنتاج.

---

## السياق

المراحل السابقة (1-5) أنشأت الأساس. الآن نحتاج:
- نظام تسجيل متقدم
- موجه نماذج ذكي
- وكلاء أمان وتوثيق
- ملخصات أسبوعية
- ChromaDB كطبقة اختيارية
- إدارة إصدارات

---

## القرارات

### 1. نظام التسجيل (src/logger.py)

**3 ملفات سجل:**
- `logs/events.log` - جميع الأحداث
- `logs/errors.log` - الأخطاء فقط
- `logs/agent.log` - نشاط كل وكيل

**Format:**
```
YYYY-MM-DD HH:MM:SS | LEVEL | Agent | Action | Details
```

**السبب**: تتبع مركزي لكل العمليات مع فئات مختلفة.

### 2. Model Router (src/model_router.py)

**الأدوار:**
```python
MODEL_ROLES = {
    "planning": {"primary": "gemini-flash", "fallback": "gemini-pro"},
    "coding": {"primary": "gemini-pro", "fallback": "gpt-4-turbo"},
    "review": {"primary": "gemini-flash", "fallback": "gemini-pro"},
    "documentation": {"primary": "gemini-flash", "fallback": "gemini-pro"},
    "security": {"primary": "gemini-pro", "fallback": "gpt-4"},
    "creative": {"primary": "gemini-flash", "fallback": "gpt-4-turbo"},
}
```

**Fallback Strategy:**
1. Try primary model
2. If error → try fallback
3. If error → try any available model
4. If nothing → return error

**السبب**: اختيار النموذج المناسب لكل مهمة مع fallback تلقائي.

### 3. Security Agent

**الفحوصات:**
- API keys/secrets مكشوفة
- innerHTML غير آمن (XSS)
- eval(), exec() (code injection)
- os.system(), shell=True (command injection)
- SQL injection patterns

**التقرير:** `docs/reports/security-report.md`

**السبب**: أمان الكود جزء أساسي من الإنتاج.

### 4. Documentation Agent

**المسؤوليات:**
- تحديث progress.md بعد كل مهمة
- تحديث README.md إذا تأثر
- إنشاء ADR جديد عند الحاجة
- إنشاء تقارير المهام

**السبب**: توثيق تلقائي ومتسق.

### 5. Weekly Summarizer (src/summarizer.py)

**المحتوى:**
- المشاريع النشطة
- المهام (مكتملة/فاشلة)
- الأخطاء
- نشاط الوكلاء
- ADRs
- التوصيات

**التقرير:** `docs/reports/weekly-summary-YYYY-Wxx.md`

**السبب**: رؤية أسبوعية للتقدم والأخطاء.

### 6. ChromaDB Layer

**البنية:**
```
Markdown (source of truth) ← Always used
ChromaDB (retrieval layer) ← Optional
```

**Storage Router:**
- `search()` - بحث Markdown
- `search_hybrid()` - بحث Markdown + ChromaDB
- `get_storage_stats()` - إحصائيات

**السبب**: Vector search اختياري بدون التأثير على استقرار Markdown.

### 7. Version System (src/version.py)

```python
VERSION = "1.0.0"
PHASE = "6A"
BUILD_NUMBER = 6
```

**السبب**: تتبع الإصدارات بشكل واضح.

---

## الملفات الجديدة

| الملف | الوصف |
|-------|-------|
| src/logger.py | نظام التسجيل المتقدم |
| src/model_router.py | موجه النماذج |
| src/summarizer.py | الملخصات الأسبوعية |
| src/version.py | إدارة الإصدارات |
| src/storage/chroma_storage.py | ChromaDB layer |
| src/storage/storage_router.py | Hybrid storage router |
| src/agents.py (محدث) | Security + Documentation agents |

---

## التوافق

- **Backward Compatibility**: جميع الملفات السابقة تعمل
- **ChromaDB**: اختياري، Markdown يبقى المصدر
- **Agents**: إضافات فقط، لا تغييرات جوهرية

---

## الإصدار

**CodeForge v1.0.0 (Phase 6A)**
