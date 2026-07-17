# ADR-005: منصة متعددة المشاريع

## الحالة
**مقبول** - 2026-07-17

---

## المشكلة

تحويل CodeForge من نموذج أولي إلى منصة إنتاج متعددة المشاريع.

---

## السياق

Phase 4 أنشأت واجهة ويب بسيطة ومشروع تجريبي واحد. الآن نحتاج:
- دعم مشاريع متعددة
- نظام إعدادات موحد
- مدير مشاريع حقيقي
- طبقة تخزين مجردة
- سجل أحداث مركزي
- لوحة تحكم فعلية

---

## القرارات

### 1. هيكل المشاريع

```
projects/
├── todo_app/       # مشروع نشط
├── landing_page/   # مشروع نشط
├── dashboard/      # مشروع مخطط
└── archive/        # المشاريع المؤرشفة
```

**السبب**: فصل واضح بين المشاريع النشطة والمؤرشفة

### 2. نظام الإعدادات (config/)

```
config/
├── __init__.py
├── paths.py       # جميع المسارات
├── models.py      # إعدادات النماذج
└── settings.py    # الإعدادات المركزية
```

**السبب**: مركزية الإعدادات، سهولة التعديل

### 3. مدير المشاريع (project_manager.py)

```python
class ProjectManager:
    def create_project(name, description)
    def delete_project(name)
    def archive_project(name)
    def switch_project(name)
    def list_projects()
    def get_project_status(name)
```

**السبب**: واجهة موحدة لإدارة المشاريع

### 4. طبقة التخزين (src/storage/)

```
src/storage/
├── __init__.py
├── storage.py      # واجهة مجردة
└── docs_storage.py # تطبيق Markdown
```

**السبب**: 
- إمكانية التبديل بين Markdown و ChromaDB
- فصل المنطق عن التنفيذ

### 5. سجل الأحداث (logs/events.log)

```
YYYY-MM-DD HH:MM Agent Action Details
2026-07-17 14:10 Manager Created Project: todo_app
```

**السبب**: تتبع مركزي لكل العمليات

### 6. لوحة التحكم

- قائمة المشاريع مع أزرار
- حالة الوكلاء
- آخر commit
- معلومات health
- سجل الأحداث

---

## الملفات الجديدة

| الملف | الوصف |
|-------|-------|
| config/__init__.py | إعدادات مركزية |
| config/paths.py | المسارات |
| config/models.py | النماذج |
| config/settings.py | الإعدادات |
| src/project_manager.py | مدير المشاريع |
| src/storage/__init__.py | واجهة التخزين |
| src/storage/storage.py | كيانات التخزين |
| src/storage/docs_storage.py | تطبيق Markdown |
| src/event_logger.py | سجل الأحداث |
| src/health.py | فحص الصحة |
| logs/events.log | ملف الأحداث |

---

## التوافق

- **Backward Compatibility**: جميع الملفات السابقة تعمل
- **Config Fallback**: إذا لم يوجد config/ يُستخدم القيم القديمة
