# CodeForge Model Provider - Agent OS
===================================

## نظرة عامة

نظام إدارة مزودي LLM لـ CodeForge Agent OS.

## المبدأ

```
بدون مفاتيح: المنصة تعمل 100%
مع مفاتيح: الذكاء يبدأ فوراً دون تعديل الكود
```

## المزودون المدعومون

| المزود | الحالة | API Key |
|--------|--------|---------|
| Mock | ✅ متاح | غير مطلوب |
| Gemini | 📋 مخطط | GEMINI_API_KEY |
| OpenAI | 📋 مخطط | OPENAI_API_KEY |
| Ollama | 📋 مخطط | غير مطلوب (local) |

## الاستخدام

```python
from src.model_provider import provider_registry, generate, has_llm_provider

# فحص المزودين
providers = provider_registry.list_all()
print(providers)

# هل هناك مزود LLM؟
if has_llm_provider():
    result = generate("اكتب Hello World")
else:
    print("لا يوجد مزود LLM - استخدم Mock")
```

## Mock Provider

Mock Provider يسمح باختبار المنصة بدون أي API Key.

```python
from src.model_provider import mock_provider

# إضافة استجابة مخصصة
mock_provider.add_response(
    pattern=r"custom.*pattern",
    response="Custom response"
)

# توليد
result = mock_provider.generate("custom pattern query")
```

## Capability Requirements

```python
from src.model_provider import capability_requirements

# فحص إذا كانت القدرة تحتاج LLM
req = capability_requirements.get("generate_code")
if req.requires_llm:
    print("تحتاج LLM")
else:
    print("تنفذ مباشرة")
```

## إضافة مزود جديد

```python
from src.model_provider import BaseProvider, provider_registry

class MyProvider(BaseProvider):
    @property
    def name(self):
        return "my-provider"
    
    @property
    def configured(self):
        return True  # أو تحقق من API key
    
    def generate(self, prompt, **kwargs):
        # تنفيذ API call
        return "response"

# تسجيل
provider_registry.register("my-provider", MyProvider())
```
