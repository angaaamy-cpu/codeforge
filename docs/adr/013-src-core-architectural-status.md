# ADR-013: الحالة المعمارية لـ `src/Core/*` (Architecture Safety Gate قبل Phase 5)

**ملاحظة ترقيم**: طُلِب إنشاء هذا الملف باسم `001-src-core-architectural-status.md`، لكن `docs/adr/001-initial-architecture.md` موجود فعلاً (قاعدة "لا حذف/لا إعادة تسمية لأي ملف موجود"). استُخدِم الرقم التالي المتاح فعلياً: **013**.

**الحالة**: مُعتمَد
**النطاق**: يُصحِّح وَيُدقِّق تصنيف `docs/adr/012-canonical-architecture.md` (انظر Errata في نهايته) بدليل تتبّع فعلي إضافي.

---

## 1. Runtime Reachability (بالدليل)

**FACT** (تتبُّع استيراد مباشر + تنفيذ فعلي في venv مطابق للإنتاج):

```
src/app.py:404-406  →  from src.codeforge import CodeForge; cf = CodeForge()
                        (داخل معالج /api/build، استيراد مؤجَّل عند كل طلب)
src/codeforge.py:13 →  from src.Core import (CapabilityRegistry, EventBus,
                        WorkspaceManager, ExecutionEngine, ProjectMemory,
                        PluginManager, DeploymentManager, SecretsManager)
                        (محاط بـ try/except ImportError)
```

**مُتحقَّق فعلياً**: في بيئة معزولة (`flask`+`gunicorn`+`requests` فقط، مطابقة لتثبيت الإنتاج الحقيقي عبر `pip install -e .`)، `CORE_AVAILABLE = True`، والاستيراد ينجح بالكامل بلا أي حزمة اختيارية إضافية.

**إذن**: `src/Core/*` **قابل للوصول فعلياً عبر API** (`/api/build`)، وأيضاً عبر `/api/health` و`/api/diagnostics` (`src/diagnostics.py` يستورد `src.Core.plugin.plugin_manager` و`src.Core.event_bus.event_bus` للفحص القرائي فقط). **لا وصول عبر CLI** (لا سكربت مستقل يستدعيه). **لا عملية خلفية/مجدولة** تستدعيه (لا cron/scheduler في المستودع).

هذا **يُصحِّح** الاستنتاج السابق في ADR-012 ("غير موصول بأي مسار منشور").

## 2. Dependency Analysis (بالدليل)

**من يستورد `src.Core`؟** (بحث شامل في كامل المستودع):
- `src/codeforge.py` (الاستدعاء الحقيقي الوحيد من مسار إنتاجي)
- `src/diagnostics.py` (قراءة حالة فقط، لا كتابة)
- `tests/test_agent_os.py` (اختبارات وحدة معزولة)

**ماذا يستورد `src/Core/*` داخلياً؟**
كل ملف في `src/Core/` (عدا `event_bus.py` نفسه) يستورد `src.Core.event_bus` لإطلاق الأحداث — لا تبعيات دائرية (event_bus هو الطبقة الأساس فقط، لا يستورد من أي أخ له).
استثناء مهم: **`src/Core/workspace.py` يستورد `src.path_service`** (الطبقة الإنتاجية الفعلية) — تكامل نظيف، **وليس تكراراً**؛ `WorkspaceManager` يبني فوق `PathService` بدل إعادة اختراعها.
`src/Core/sdk.py` يستورد كل الوحدات الأخرى (facade مقصودة) لكن **لا شيء يستورد `sdk.py` نفسه** — كود ميت 100% (تغطية اختبار = 0%، لا مستورد واحد في كامل المستودع).

**تكرار وظيفي مكتشَف**: `src/Core/memory.py::ProjectMemory` (تخزين JSON مستقل) **يُكرِّر** مفهوم `src/memory.py::` (نظام "الذاكرة الذكية" الفعلي المُستخدَم من `pipeline.py`) بلا أي مشاركة كود بينهما — مفهومان منفصلان لنفس الاسم "Memory"، أحدهما مُستخدَم فعلياً (`src/memory.py`) والآخر مبني فقط دون استدعاء (`src/Core/memory.py`).

## 3. Actual Current State (تصنيف كل ملف، بالدليل لا بالتخمين)

| الملف | الحالة | الدليل |
|---|---|---|
| `event_bus.py` | **Active** | يستقبل أحداثاً حقيقية (`capability:registered` × 9، `build:started/succeeded`) على كل استيراد لـ`src.Core` وكل نداء `codeforge.build()`؛ مُتحقَّق بتشغيل فعلي |
| `capability.py` (تسجيل) | **Active** (تسجيل ميتاداتا فقط) | `_register_builtin_capabilities()` يعمل تلقائياً عند الاستيراد، 9 قدرات مُسجَّلة فعلياً وقابلة للقراءة عبر `list_capabilities()` |
| `capability.py` (تنفيذ فعلي للقدرات) | **Placeholder** | كل القدرات المدمجة الـ9 (بما فيها **"terminal"**) لديها `tools: {}` فارغ — لا handler حقيقي واحد مربوط؛ **لا كود تنفيذ Shell حقيقي موجود في أي مكان قابل للوصول حالياً** |
| `workspace.py` (WorkspaceManager) | **Active** (للتهيئة) / **Experimental** (لبقية الواجهة) | يُنشئ فعلياً `workspaces/.workspaces.json` على القرص عند أول استدعاء (مُتحقَّق: هذا الملف ظهر فعلياً أثناء تشغيل الاختبارات)؛ لكن دوال CRUD الكاملة لا يستدعيها أي route |
| `execution.py` (ExecutionEngine) | **Placeholder** | يُبنى فقط (`self.execution` في `CodeForge.__init__`)؛ `_execute_step()` تعليق ذاتي "Placeholder"؛ غير مُستدعى بعد البناء |
| `deployment.py` (DeploymentManager) | **Placeholder** | يُبنى فقط؛ `deploy()` تعليق ذاتي "placeholder that documents the interface"؛ غير مُستدعى |
| `secrets.py` (SecretsManager) | **Placeholder / Experimental** | يُبنى فقط (`self.secrets`)؛ لا route في `app.py` يستدعيه (لوحة الأسرار الموجودة تخص تطبيق `web/` المنفصل تماماً) |
| `plugin.py` (PluginManager) | **Placeholder / Experimental** | يُبنى فقط (`self.plugins`)؛ لا استدعاء لاحق |
| `memory.py` (ProjectMemory) | **Experimental (مُكرِّر مفهومياً)** | يُبنى فقط (`self.memory`)؛ يُكرِّر `src/memory.py` الفعلي المُستخدَم بلا تشارك كود |
| `sdk.py` | **Dead / Unused** | لا مستورد واحد له في كامل المستودع؛ تغطية اختبار 0% |
| `__init__.py` | **Active** | نقطة الدخول الفعلية التي يمر عبرها `codeforge.py` |

## 4. Architectural Role

`src/Core/*` ليست "منصة مستقبلية مخطَّطة بالكامل" ولا "كود ميت بالكامل" — بل **بنية أساس جزئية حقيقية (Partial Foundation)**: طبقة الأحداث (`event_bus`) ونمط بناء `workspace.py` فوق `path_service.py` يُظهران قراراً معمارياً سليماً فعلاً ومُستخدَماً، بينما بقية الوحدات (execution/deployment/secrets/plugin/memory) هياكل صحيحة الشكل (dataclasses، singleton patterns متسقة) لكن **بلا منطق تنفيذي حقيقي بعد** — أقرب لـ"عقود واجهة مُعلَنة مسبقاً (interface contracts declared early)" منها لـ"كود ميت".

## 5. Strategic Future Fit لـ SCOS

| المكوّن | ملاءمته الحالية | الواقع الحالي مقابل الإمكانية المستقبلية |
|---|---|---|
| Orchestration/Events | مناسب جداً | **الواقع**: يعمل فعلياً اليوم بأحداث حقيقية. **الإمكانية**: يحتاج فقط توسيع أنواع الأحداث المُستمَع لها |
| Capability System | مناسب بنيوياً | **الواقع**: تسجيل ميتاداتا فقط اليوم. **الإمكانية**: ربط `tools` حقيقية لاحقاً (انظر §7 أدناه) |
| Execution Engine | يحتاج عملاً حقيقياً | **الواقع**: stub فارغ. **الإمكانية**: يمكن أن يصبح الجسر بين Capability وpipeline.py الفعلي - لكن هذا **قرار مستقبلي منفصل**، ليس اليوم |
| Memory Layer | يحتاج قراراً | **الواقع**: مُكرِّر لنظام موجود فعلاً (`src/memory.py`). **الإمكانية**: إما استبدال `src/memory.py` به مستقبلاً (قرار كبير) أو حذفه لصالح النظام الفعلي - **كلاهما خارج نطاق هذا الـ ADR** |
| Context Engine / Project Brain | غير موجود إطلاقاً بعد | لا FACT هنا سوى "غير موجود" - أي تقييم آخر Speculation بحت |

## 6. Strategic Analysis

| المعيار | التقييم |
|---|---|
| Migration value | متوسط-عالٍ لـ `event_bus`/`workspace` (تعملان فعلاً وتُبنيان بشكل نظيف فوق الطبقة الإنتاجية)؛ منخفض حالياً للباقي (لا منطق للترحيل منه) |
| Reuse value | عالٍ لبنية Singleton/dataclass المتسقة عبر كل الملفات - نمط جيد يستحق البقاء كقالب |
| Technical debt | متوسط: أسماء متطابقة مربكة (`memory.py` × 2)، تسمية `Core` بحرف كبير وسط `src/` بحروف صغيرة |
| Blast radius (الإبقاء كما هو) | منخفض - الملفات الخاملة (execution/deployment/secrets/plugin) لا تُنفِّذ شيئاً فعلياً حالياً، فلا خطر تشغيلي فوري من تركها |
| Blast radius (حذف/تجميد الآن) | **متوسط-عالٍ** - `event_bus.py` و`workspace.py` **يعملان فعلياً في الإنتاج**؛ حذفهما يكسر `/api/build` فوراً (استيراد فاشل في `codeforge.py` بلا حماية على مستوى الوحدة الفردية - الحماية فقط على `from src.Core import (...)` ككل) |
| Cost of keeping (كما هو) | منخفض - لا صيانة نشطة مطلوبة لكود لا يُستدعى |
| Cost of freezing | منخفض - نفس الشيء عملياً، مع توثيق أوضح لمنع تطوير عليه بلا وعي |
| Cost of deprecating | يحتاج خطة تعامل مع `event_bus`/`workspace` تحديداً (نشِطان)، لا يمكن التعامل مع `src/Core/*` ككتلة واحدة |
| Risk of building Phase 5+ *outside* it | **عالٍ** - يُنتِج معمارية رابعة تكرر الخطأ المُدقَّق أصلاً في `CONTRADICTIONS.md` C1 |
| Risk of building Phase 5+ *inside* it (كما هو، بلا تمييز) | **متوسط-عالٍ** - إضافة Terminal/Browser حقيقيين فوق `capability.py` الحالي يعني منح تنفيذ Shell حقيقي عبر مسار كان معروفاً بالتسجيل الميتاداتا فقط - يحتاج مراجعة أمنية منفصلة صريحة قبل أي ربط تنفيذي حقيقي |

## 7. القرار

**الحالة المُعتمَدة لـ `src/Core/*` ككل: `EXPERIMENTAL`** (وليس Canonical ولا Legacy ولا Frozen بالكامل — التصنيف الدقيق لكل ملف في الجدول §3 هو المرجع العملي، هذا التصنيف الإجمالي للتوثيق العلوي فقط).

**الأثر على Phase 5**:
1. **`src/Core/capability.py` هو المالك المعماري الوحيد (Canonical Owner) لأي نظام Capability مستقبلي.** لا يُنشأ نظام قدرات موازٍ جديد. أي عمل مستقبلي على القدرات = ربط `tools` حقيقية بالسجلات الـ9 الموجودة فعلاً (خصوصاً `files` و`git`، اللذين لديهما بالفعل نظائر إنتاجية جاهزة للربط: `path_service.py` و`git_manager.py` على التوالي) — **Adapter pattern، لا إعادة كتابة**.
2. **"Terminal" يبقى تسجيل ميتاداتا فقط بلا `tools` حقيقية حتى مراجعة أمنية منفصلة صريحة** (تحديد sandboxing، نموذج صلاحيات، تسجيل تدقيق) توافق عليها أنت تحديداً. هذا هو "الاهتمام الخاص بالسلامة" الذي طلبه توجيهكم بالحرف لـ Terminal تحديداً — والتنفيذ هنا هو: **عدم الربط إطلاقاً الآن**، لا "الربط بحذر".
3. **`event_bus.py` و`workspace.py`**: يبقيان كما هما (Active، نشطان فعلاً) - لا حاجة لأي قرار حذف/تجميد بشأنهما، فقط توثيق أنهما جزء من مسار الإنتاج الفعلي فعلياً (تحديث لـ `docs/ARCHITECTURE.md` مطلوب - انظر التالي).
4. **`sdk.py`**: مُرشَّح بقوة للحذف (Dead code مؤكَّد 100%، صفر مستوردين) - **لكن الحذف قرار مستقل يحتاج إذنك الصريح**، لا يُنفَّذ ضمن هذا الـ ADR.
5. **`memory.py` (Core) مقابل `src/memory.py` (الفعلي)**: يحتاج قرار توحيد مستقبلي منفصل (أيّهما يبقى) - **خارج نطاق Phase 5 الحالي**، يُسجَّل هنا كملاحظة استراتيجية فقط.

## Rejected Alternatives
- **Canonical فوراً لكل `src/Core/*`**: مرفوض - يتجاهل أن معظم الملفات (execution/deployment/secrets/plugin) placeholder فعلي بلا منطق حقيقي؛ تسميتها Canonical يخفي هذا الواقع بدل توثيقه.
- **Legacy/حذف فوراً لكل `src/Core/*`**: مرفوض - يتجاهل أن `event_bus.py`/`workspace.py` يعملان فعلياً في الإنتاج اليوم؛ حذفهما يكسر `/api/build`.
- **تجميد الكتلة كاملة (Frozen) دون تمييز داخلي**: مرفوض - يمنع الاستفادة من الجزء العامل فعلاً (event_bus/workspace) ويُبقي الالتباس قائماً.

## Migration Strategy
لا ترحيل مطلوب الآن. عند الحاجة مستقبلاً لتفعيل capability حقيقية: إضافة `tools` عبر `Capability.add_tool()` على السجل الموجود فعلاً (لا إنشاء `Capability` جديدة)، مع اختبار تكامل يُثبت الاستدعاء الفعلي من route حقيقي قبل اعتبارها "Active" بدل "Placeholder".

## Verification Criteria
- [x] تتبُّع استيراد فعلي مباشر لكل ملف (مكتمل أعلاه)
- [x] تشغيل فعلي في بيئة production-equivalent يثبت `CORE_AVAILABLE=True` والأحداث الحقيقية
- [ ] اختبار تكامل يغطي `src/codeforge.py` نفسه (غير موجود حالياً - **فجوة جديدة مكتشَفة**: `src/codeforge.py` بلا أي اختبار مباشر رغم كونه المسار الفعلي لـ `/api/build`)
