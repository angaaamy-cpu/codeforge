# 🏗️ CodeForge v1.0

**منصة بناء المشاريع بالذكاء الاصطناعي**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

---

## نظرة عامة

CodeForge هي منصة بناء مشاريع برمجية بالذكاء الاصطناعي. فقط اكتب وصف مشروعك وسنهتم بكل شيء!

### الفلسفة

> **المستخدم يكتب وصف مشروعه فقط. لا يحتاج معرفة أي تفاصيل داخلية.**
> **المنصة تتولى كل شيء وتُخرج نتيجة واضحة.**

---

## ⚡ التشغيل

### CLI (سطر الأوامر)

```bash
python src/build.py
```

أو مع وصف مباشرة:

```bash
echo "صفحة هبوط لشركة ناشئة مع 3 خدمات" | python src/build.py
```

### واجهة الويب

```bash
python src/app.py
```

ثم افتح: http://localhost:5000

### API

```bash
curl -X POST http://localhost:5000/api/build \
  -H "Content-Type: application/json" \
  -d '{"description": "صفحة هبوط لشركة ناشئة"}'
```

---

## 📝 مثال

```
╔══════════════════════════════════════════╗
║         🏗️  CodeForge v1.0              ║
║     منصة بناء المشاريع بالذكاء الاصطناعي    ║
╚══════════════════════════════════════════╝

📝 صف مشروعك:
> نظام حجز عيادة مع صفحة رئيسية ونموذج حجز

🚀 بناء: نظام حجز عيادة مع صفحة رئيسية ونموذج حجز

📊 تقدم البناء:
  [1/6] ✅ إنشاء المشروع
  [2/6] ✅ التخطيط
  [3/6] ✅ التطوير
  [4/6] ✅ الاختبار
  [5/6] ✅ مراجعة الأمان
  [6/6] ✅ التوثيق

════════════════════════════════════════════
✅ تم بناء المشروع بنجاح!


📁 المشروع: clinic_booking_1234
📍 المسار: projects/clinic_booking_1234
📄 الملفات: 3 ملف
⏱️  المدة: 2.3 ثانية

🚀 للتشغيل:
   cd projects/clinic_booking_1234
   python -m http.server 8080

🌐 افتح: http://localhost:8080

📊 التقارير:
   - docs/reports/clinic_booking_1234-build.md
════════════════════════════════════════════
```

---

## 🏗️ الهيكل المعماري (v1.0)

```
build.py (CLI)
    ↓
CodeForge (واجهة موحدة)
    ↓
BuildEngine (محرك البناء)
    ↓
ProjectManager + Pipeline + Logger + Memory
```

### الطبقات

| الطبقة | الملف | الوصف |
|--------|-------|-------|
| CLI | `src/build.py` | طبقة سطر الأوامر |
| Interface | `src/codeforge.py` | الواجهة الموحدة |
| Engine | `src/build_engine.py` | محرك البناء |
| Result | `src/build_result.py` | كائن النتيجة |
| Manager | `src/project_manager.py` | إدارة المشاريع |
| Pipeline | `src/pipeline.py` | دورة العمل |
| Web | `src/app.py` | Flask API |

---

## 📦 الميزات

- ✅ بناء مشاريع HTML/Flask/React من وصف
- ✅ تحويل الوصف العربي إلى اسم إنجليزي
- ✅ 6 خطوات بناء متسلسلة
- ✅ كشف تلقائي لأمر التشغيل
- ✅ إنشاء تقارير البناء
- ✅ API للتكامل
- ✅ واجهة CLI سهلة

---

## 🚀 التقنيات

- Python 3.11+
- Flask (API)
- localStorage (البيانات)
- Markdown (التقارير)

---

## التطور

| المرحلة | الحالة |
|---------|--------|
| Phase 1-7: Platform Core | ✅ مكتمل |
| Phase 8: v1.0 Product | ✅ مكتمل |
| Phase 9: Backend API | 📋 مخطط |
| Phase 10: Database | 📋 مخطط |

---

## المساهمة

1. Fork المشروع
2. أنشئ branch
3. Commit
4. Push
5. افتح Pull Request

---

<div align="center">

**صُنع بـ ❤️ للمطورين العرب**

</div>
