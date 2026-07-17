# Migration Guide: v1.0 → CodeForge X
==========================================

**من**: CodeForge v1.0
**إلى**: CodeForge X (Autonomous Software Factory)

---

## نظرة عامة

CodeForge X يبني على v1.0 مع إضافة:
- Event Bus للـ loose coupling
- Capability System للتوسعة
- Plugin System للإضافات
- Workspace Manager لإدارة المشاريع
- Secrets Manager للأسرار
- Deployment Manager للنشر

---

## التغييرات الرئيسية

### 1. CodeForge Instance

**قبل (v1.0)**:
```python
from src.codeforge import CodeForge

cf = CodeForge()
result = cf.build("صفحة هبوط")
```

**بعد (CodeForge X)**:
```python
from src.codeforge import CodeForge

cf = CodeForge()
result = cf.build("صفحة هبوط")

# الجديد: X features
print(cf.x_enabled)  # True
print(cf.list_capabilities())  # قائمة القدرات
```

---

### 2. Event Bus

**قبل (v1.0)**:
```python
from src.event_logger import log_event

log_event("system", "task_completed", {})
```

**بعد (CodeForge X)**:
```python
from src.Core.event_bus import EventBus, EventType, emit

# إصدار حدث
emit(EventType.TASK_COMPLETED, {"task_id": "123"})

# الاشتراك
def handler(event):
    print(f"Received: {event.type}")

event_bus.subscribe(EventType.TASK_COMPLETED, handler)
```

---

### 3. Capabilities

**قبل (v1.0)**:
```python
# Directly call functions
from src.pipeline import execute_task

result = execute_task("description")
```

**بعد (CodeForge X)**:
```python
# Call via Capability
from src.Core.capability import get_capability

cap = get_capability("files")
tool = cap.get_tool("read_file")
result = tool.execute(path="README.md")
```

---

### 4. Python SDK

**قبل (v1.0)**: لا يوجد SDK

**بعد (CodeForge X)**:
```python
from src.Core.sdk import CodeForge, Project

# SDK كامل
cf = CodeForge()
project = cf.create_project("my-app")
result = project.build("أضف صفحة تسجيل")
project.deploy("railway")
```

---

## Backward Compatibility

### v1 API يعمل تماماً

```python
# هذا الكود لا يزال يعمل
from src.codeforge import codeforge

result = codeforge.build("صفحة هبوط")
print(result.status)
```

### Zero Breaking Changes

- جميع دوال v1 API سليمة
- لا تغيير في التوقيعات
- Core اختياري (try/except)

---

## خطوات Migration

### للمطورين

1. **لا تغيير مطلوب** - الكود الحالي يعمل
2. **لاستخدام X features**:
   ```python
   if cf.x_enabled:
       caps = cf.list_capabilities()
   ```

### للمستخدمين

1. **لا تغيير مطلوب** - CLI و Web UI يعملان
2. **للتوسع**:
   ```bash
   # Plugins directory
   mkdir -p plugins/my-plugin
   ```

---

## Plugin Development

### هيكل Plugin

```
plugins/my-plugin/
├── manifest.json
├── __init__.py
└── capabilities/
```

### manifest.json

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My custom plugin",
  "capabilities": ["custom-tool"],
  "permissions": ["read"]
}
```

### __init__.py

```python
from src.Core.plugin import BasePlugin
from src.Core.capability import Capability

class Plugin(BasePlugin):
    def on_load(self):
        # Register capabilities
        pass
    
    def on_unload(self):
        # Cleanup
        pass
```

---

## ملاحظات

- **Performance**: Core له overhead بسيط جداً
- **Dependencies**: Core يستخدم stdlib فقط
- **Storage**: Secrets لا تُحفظ أبداً في Git

---

_هذا الدليل مُنشأ بواسطة CodeForge X Migration - 2026-07-17_
