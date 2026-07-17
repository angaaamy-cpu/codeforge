# ADR-004: المشروع التجريبي - Todo App

## الحالة
**مقبول** - 2026-07-17

---

## المشكلة

اختبار قدرات منصة CodeForge Phase 4 بمشروع حقيقي متكامل.

---

## السياق

المشروع الأول كاختبار end-to-end:
- HTML/CSS/JS بدون frameworks
- localStorage للحفظ
- تصميم mobile-first
- دورة عمل كاملة (Pipeline)

### المتطلبات
1. index.html: عنوان 'مهامي'، حقل إدخال، زر 'أضف مهمة'، قائمة مهام
2. style.css: تصميم داكن أنيق
3. script.js: إضافة مهمة، حذف مهمة، حفظ في localStorage

---

## القرارات

### 1. البنية
```
workspace/projects/todo_app/
├── index.html    # الهيكل + المحتوى
├── style.css     # التصميم
└── script.js     # المنطق
```

### 2. التصميم
- **لون أساسي**: #0a0a0f (داكن)
- **لون التمييز**: #00d4ff (سماوي)
- **البطاقات**: #16213e
- **التدرجات**: سماوي ↔ بنفسجي

### 3. localStorage
```javascript
{
    "todos": [
        {"id": 1, "text": "...", "done": false}
    ]
}
```

### 4. الميزات
- إضافة مهمة جديدة
- حذف مهمة
- وضع علامة "تم"
- الحفظ التلقائي
- عرض العدد

---

## دورة العمل

```
1. Planner: تحليل المتطلبات
2. Executor: كتابة index.html + style.css + script.js
3. Reviewer: اختبار كل وظيفة
4. Recorder: إنشاء التقرير + commit
```

---

## النتائج المتوقعة

- 3 ملفات: HTML, CSS, JS
- جميع الوظائف تعمل
- تقرير في docs/reports/task-003.md
