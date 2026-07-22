# قواعد الترميز (Coding Rules)

## المبادئ العامة

1. **الوضوح قبل الاختصار**: الكود الواضح أفضل من الكود الذكي
2. **البساطة**: الحل الأبسط هو الأفضل دائماً
3. **الاتساق**: اتبع الأنماط الموجودة

---

## Python

### PEP 8 Compliance
جميع الكود يجب أن يتبع [PEP 8](https://pep8.org/)

### تنسيق الكود
```python
# ✅ صحيح
def calculate_total(items: list[int]) -> int:
    return sum(items)

# ❌ خطأ
def calculate_total(items:list[int])->int:
    return sum(items)
```

### أسماء المتغيرات والدوال
```python
# ✅ أسماء واضحة ومعبرة
user_profile = get_user_profile(user_id)
total_amount = calculate_total(items)

# ❌ أسماء غامضة
up = get_up(uid)
ta = calc(its)
```

### docstrings
```python
def fetch_user(user_id: str) -> dict:
    """
    جلب بيانات المستخدم من قاعدة البيانات.

    Args:
        user_id: المعرف الفريد للمستخدم

    Returns:
        قاموس يحتوي على بيانات المستخدم

    Raises:
        UserNotFoundError: إذا لم يتم العثور على المستخدم
    """
```

### Type Hints
```python
# ✅ استخدام Type Hints
def process_data(data: list[dict]) -> dict[str, int]:
    ...

# ✅ Union Types
from typing import Optional
def get_optional(value: Optional[str] = None) -> str:
    ...
```

### Imports
```python
# ✅ ترتيب Imports
# 1. مكتبات النظام
import os
import sys

# 2. مكتبات خارجية
from typing import Optional

# 3. مكتبات المشروع
from src.models import User
```

---

## Git Commits

### صيغة Commit Messages
```
<type>: <description>

[optional body]
```

### Types
- `feat`: ميزة جديدة
- `fix`: إصلاح bug
- `docs`: توثيق
- `refactor`: إعادة هيكلة
- `test`: اختبارات
- `chore`: مهام صيانة

### أمثلة
```
feat: add user authentication

-implements JWT based auth
-adds login/logout endpoints
```

---

## الاختبارات

### قبل الدمج (Merge)
كل طلب سحب يجب أن:
- ✅ يجتاز جميع الاختبارات الحالية
- ✅ يضيف اختبارات للم-features الجديدة
- ✅ يحقق 80%+ coverage
- ✅ لا يوجد linting errors

### هيكل الاختبارات
```python
# tests/test_feature.py
class TestFeature:
    def test_success_case(self):
        ...

    def test_error_case(self):
        ...

    def test_edge_case(self):
        ...
```

---

## Code Review

### ما يجب مراجعته
- [ ] المنطق صحيح
- [ ] معالجة الأخطاء كافية
- [ ] الأداء مقبول
- [ ] الأمان محسّن
- [ ] التوثيق محدث

### وقت المراجعة
- مراجعة أولى: خلال 24 ساعة
- مراجعة ثانية: خلال 48 ساعة

---

## متغيرات البيئة

```python
# ✅ تحميل من Environment
import os
API_KEY = os.getenv("API_KEY")

# ❌ قيم ثابتة
API_KEY = "hardcoded-key-123"
```

---

## معالجة الأخطاء

```python
# ✅ استخدام exceptions مناسبة
class ValidationError(Exception):
    pass

def validate_input(data):
    if not data:
        raise ValidationError("Data cannot be empty")
```

---

## الأمان

- لا تخزن secrets في الكود
- تحقق من المدخلات دائماً
- استخدم parameterized queries
- حدّث المكتبات دورياً
