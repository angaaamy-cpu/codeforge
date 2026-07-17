# ADR-003: دورة العمل + الذاكرة الذكية + تكامل Git

## الحالة
**مقبول** - 2026-07-17

---

## المشكلة

نحتاج لإكمال Phase 3: بناء دورة عمل كاملة مع ذاكرة ذكية وتكامل Git.

---

## السياق

Phase 2 أنشأت 4 وكلاء لكن بدون دورة عمل منظمة:
- لا يوجد نظام حالة مركزي
- لا يوجد نظام ذاكرة ذكي
- لا يوجد تكامل Git منظم
- كل وكيل يعمل بشكل مستقل

### المتطلبات
- نظام حالة للمشروع
- ذاكرة تقرأ فقط الملفات المرتبطة
- قرار معماري → ADR
- قرار تشغيلي → progress.md
- commit بعد كل مهمة
- push فقط بعد نجاح الاختبارات

---

## القرارات

### 1. نظام الحالة (src/state.py)

```python
@dataclass
class ProjectState:
    current_task: Optional[str]
    active_agent: Optional[AgentType]
    attempts: dict  # لكل وكيل
    last_decision: Optional[Decision]
    last_commit: Optional[str]
```

**السبب**: مركزية المعلومات ومنع فقدان السياق

### 2. الذاكرة الذكية (src/memory.py)

```python
class SmartMemory:
    def read_context(task_description):
        # يقرأ الملفات المرتبطة فقط
        # لا يقرأ كل docs/
    
    def record_decision(agent, content, impact):
        if impact == "architectural":
            # → ADR جديد
        else:
            # → progress.md
```

**السبب**: 
- كفاءة (لا قراءة ملفات غير مطلوبة)
- تنظيم (معماري ≠ تشغيلي)
- لا decisions.md أبداً

### 3. دورة العمل (src/pipeline.py)

```
Task → Planner → Executor → Reviewer → Recorder
```

**الطبقات**:
| الطبقة | الوكيل | الوظيفة |
|--------|-------|---------|
| Planner | Architect | تحليل + تخطيط |
| Executor | Developer | تنفيذ الكود |
| Reviewer | QA | اختبار + مراجعة |
| Recorder | Manager | توثيق + commit |

**السبب**: فصل واضح للمسؤوليات

### 4. قاعدة الـ 3 محاولات

```python
if attempts >= 3:
    stop_and_document()  # إنشاء ADR للفشل
```

**السبب**: منع الدوران في حلقة فشل

### 5. إدارة Git (src/git_manager.py)

```python
auto_commit()  # بعد كل مهمة
auto_push()    # فقط بعد نجاح QA
```

**السبب**: 
- commit متكرر للتتبع
- push انتقائي للأمان

---

## التقارير (docs/reports/)

كل مهمة تُنشئ تقرير:
```
docs/reports/task-NNN.md
```

المحتوى:
- وصف المهمة
- الخطة
- الملفات المعدلة
- نتائج الاختبار
- القرارات
- الأخطاء

---

## النتائج

### ✅ مكتسبات
- دورة عمل كاملة ومنظمة
- ذاكرة ذكية تقرأ فقط اللازم
- نظام حالة مركزي
- تكامل Git منظم
- تقارير تلقائية

### ⚠️ مخاطر
| المخاطر | التخفيف |
|---------|---------|
| تعقيد النظام | توثيق + ADR |
| فقدان البيانات | commit متكرر |
| فشل متكرر | قاعدة 3 محاولات |

---

## التنفيذ

### الملفات الجديدة
```
src/state.py         # نظام الحالة
src/memory.py        # الذاكرة الذكية
src/pipeline.py      # دورة العمل
src/git_manager.py   # إدارة Git
docs/reports/        # التقارير
```

### المهمة الأولى
"أضف زر تواصـل معنا":
- ✅ Planner: خطة جاهزة
- ✅ Executor: الزر مُضاف
- ✅ Reviewer: الاختبارات تمر
- ✅ Recorder: التقرير + commit

---

## ملاحظات

- **Backwards Compatibility**: agents.py يتوافق مع Phase 2 و Phase 3
- **لا decisions.md**: القرارات تُسجل في ADR أو progress.md
- **Phase 4**: واجهة الهاتف + ChromaDB
