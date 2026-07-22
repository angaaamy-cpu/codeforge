# KNOWLEDGE_GRAPH.md — Phase 8 (مهمة المعالجة/التصليب)

## 1. Knowledge Graph Audit (قبل أي تنفيذ)
بحث شامل في كامل المستودع (`grep -rl` لـ `knowledge.graph|KnowledgeGraph|graph_store|GraphNode|GraphEdge|networkx`، وفحص `src/app.py` لأي route باسم "knowledge"/"graph"): **لا شيء وُجِد إطلاقاً**. لا تنفيذ سابق، لا storage مخصَّص، لا endpoint، لا علاقات مسجَّلة مسبقاً. لا orphaned implementation ولا duplicate implementation - لأنه لا يوجد تنفيذ من الأساس.

## 2. ما أُعيد استخدامه / أُصلِح / أُنشِئ

| العنصر | الحالة |
|---|---|
| طبقة التخزين (`path_service.write`) | **أُعيد استخدامها** - لا قاعدة بيانات جديدة، لا مكتبة graph خارجية |
| `docs_storage.list_adrs()` (Phase 7) | **أُعيد استخدامها كمصدر Decision nodes** مباشرة |
| `CapabilityRegistry.list_all()` (Phase 5) | **أُعيد استخدامها كمصدر Capability nodes** مباشرة |
| `provider_registry.list_all()` (Phase 4) | **أُعيد استخدامها كمصدر Provider nodes** مباشرة |
| استخراج `@app.route` من `src/app.py` | **جديد** - regex على المصدر الفعلي، لا قائمة يدوية |
| تحليل AST لملفات `tests/*.py` | **جديد** - `ast.parse` حقيقي، لا قائمة مكتوبة يدوياً |
| `src/Core/knowledge_graph.py` | **جديد** (لا بديل موجود لإصلاحه) |
| `GET /api/knowledge/graph`, `GET /api/knowledge/impact/<node_id>` | **جديد** - محمي تلقائياً بطبقة Phase 1 (لا route عام جديد بلا مصادقة) |

## 3. أرقام حقيقية + دليل Provenance

آخر بناء حي (Reality Check أدناه): **162 عقدة، 303 علاقة**. كل عقدة تحمل `source_type`/`source_id`/`source_reference`/`provenance` صريحة (لا عقدة بلا مصدر). توزيع العقد:

| النوع | العدد | المصدر |
|---|---|---|
| test | ~65 | `ast.parse` لكل `tests/test_*.py` |
| file | ~44 | ملفات `src/**/*.py` الموجودة فعلياً |
| api | 20 | `@app.route` مُستخرَجة من `src/app.py` |
| decision | 10 | `docs_storage.list_adrs()` |
| capability | 9 | `CapabilityRegistry.list_all()` |
| deployment | 3 | وجود `Procfile`/`render.yaml`/`railway.json` فعلياً |
| provider | 1+ | `provider_registry.list_all()` (يزيد مع ضبط GEMINI_API_KEY/OPENAI_API_KEY) |
| project | 1 | عقدة تجميع اصطناعية واحدة، **مُعلَّم صراحة** أنها ليست مُشتقّة من بيانات |
| **failure** | **0** | **NOT_AVAILABLE صراحة** - لا نظام تتبع أعطال موجود، لم يُخترَع |

**علاقات غير مكتشَفة، مُسجَّلة صراحة في `not_available` بدل السكوت عنها**:
- `capability_depends_on_provider`: لا كود يربط أي capability (files/git/...) بأي provider LLM حالياً.
- `api_uses_capability`: لا route في `src/app.py` يستدعي `CapabilityRegistry` مباشرة (Phase 5/6 غير موصولين بـ`/api/build` الحي - موثَّق في ADR-013).

## 4. Impact Analysis - الدليل الحاسم (لا "nodes:100, edges:250, healthy")

**مشكلة حقيقية اكتُشِفت ثم أُصلِحت أثناء البناء**: التحليل الأول عبَر عقدة `project` المركزية (علاقات `contains`/`decided_by`/`deployed_as`)، فأعطى **نفس النتيجة (140 عقدة متأثرة) لـ ADR-013 ولـ ADR-007** - نتيجة مضلِّلة بالضبط كما حذَّر التوجيه. **الإصلاح**: تحليل الأثر يقتصر الآن على علاقات السببية الفعلية فقط (`mentions`/`exposes`/`verifies`/`runs`)، يستبعد علاقات العضوية التنظيمية.

**النتيجة بعد الإصلاح، مُتحقَّقة حياً عبر `/api/knowledge/impact/<node_id>`**:

| العقدة | العقد المتأثرة | لماذا |
|---|---|---|
| `decision:013` (ADR-013، يذكر عشرات مسارات src/*.py فعلياً) | **126** | مطابقة نصية حقيقية لمسارات مذكورة في نص الملف الكامل |
| `decision:007` (ADR-007، قرار عمل قديم لا يذكر أي مسار كود) | **0** | لا مطابقة نصية واحدة - **صفر حقيقي، لا اختراع** |
| عقدة غير موجودة (`decision:999`) | — | `404` صريح، لا نتيجة مُلفَّقة |

هذا الفرق (126 مقابل 0 لنفس نوع العقدة) هو الدليل أن التحليل حقيقي، لا عرض بيانات ثابتة.

## 5. حالة Execution Blockers الأربعة

| العائق | الحالة | الدليل |
|---|---|---|
| **Real Git** | ✅ متاح فعلياً وليس محاكاة | كل التزام (commit) في هذه المهمة (Phase 1 وحتى الآن) نُفِّذ عبر `git commit` حقيقي على مستودع حقيقي، ودُفِع (`git push`) لـ GitHub الفعلي، ومُتحقَّق لاحقاً عبر GitHub API (`branches/<name>` يُرجع commit SHA حقيقياً في كل مرة). لا محاكاة. |
| **Real Commands** | ✅ متاح فعلياً | كل اختبار Reality Check في هذه المهمة (curl مقابل سيرفر Flask حي، `pip install`، `pytest`) نُفِّذ عبر subprocess حقيقي في بيئة العمل، بأدلة stdout/stderr فعلية مُرفَقة في كل خطوة سابقة من هذه المهمة. |
| **Real Tests** | ✅ متاح فعلياً | 113 اختباراً حقيقياً يعمل عبر `pytest` الفعلي (ليس ادعاء نجاح) - النتيجة `113 passed` أعلاه تحديداً وليست افتراضاً. |
| **Real OS Filesystem** | ✅ متاح فعلياً | `path_service.write()`/`persist()` يكتبان فعلياً لملفات JSON على القرص - مُتحقَّق مباشرة في `test_graph_persists_to_real_file` (يقرأ الملف المكتوب فعلياً من القرص بعد الكتابة، لا يفترض نجاح الكتابة). |

**لا عائق حقيقي متبقٍ من هذه الأربعة داخل بيئة العمل المستخدَمة في هذه المهمة.** العائق الوحيد الباقي فعلياً (غير مذكور في هذه القائمة الأربعة تحديداً) يبقى: **لا وصول شبكي خارجي حقيقي** لـ Docker/Replit/Railway الفعلية (Deployment verification، Phase 11)، ولا لـ `generativelanguage.googleapis.com`/`api.openai.com` (اتصال LLM حي، Phase 4) - كلاهما موثَّق UNKNOWN صراحة منذ بداية هذه المهمة، وليس تراجعاً جديداً.
