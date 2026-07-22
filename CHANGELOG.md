# CHANGELOG.md — مهمة المعالجة/التصليب (Production Safety & Consolidation)

> ⚠️ الترقيم هنا (Phase 1-7) خاص **بمهمة معالجة منفصلة** بدأت بتدقيق فني جنائي كامل (`AUDIT_REPORT.md`) ثم أصلحت المشاكل المكتشَفة تدريجياً - **ليس** ترقيم مراحل المشروع التاريخي الأصلي الوارد في `README.md` (v1.0 حتى v10). كل بند أدناه مبني على دليل مباشر (كود/اختبار/تشغيل فعلي)، لا افتراض.

## Phase 1 — Production Safety
- **المشكلة**: كل `/api/*` كان بلا أي مصادقة - أي زائر يقدر يحذف مشاريع أو يشغّل بناء.
- **الحل**: Default-Deny middleware، `GET /api/health` وحده مُستثنى علناً. `ADMIN_API_KEY` بلا fallback ثابت (مفتاح عشوائي مؤقت إن غاب، يُطبع في السجلات مرة واحدة).
- **التحقق**: 46 اختبار أمان + Reality Check حي (curl مقابل سيرفر فعلي).

## Phase 2 — Architecture Consolidation
- **المشكلة**: 3 معماريات متوازية موثَّقة بتناقض في `docs/architecture.md` مقابل `README.md` مقابل `docs/adr/011-*.md`.
- **الحل**: `docs/adr/012-canonical-architecture.md` - Flask v1.0 (`src/app.py`+`pipeline.py`+`build_engine.py`) هو المسار الإنتاجي الرسمي الوحيد؛ تصنيف كل مكوّن آخر (Development/Legacy/Experimental).

## Phase 3 — Runtime Stability
- **المشكلة**: `path_service.py` كان يفترض `Path("/app")` ثابتاً على Railway، بصرف النظر عن كون هذا المسار الفعلي أو قابلاً للكتابة.
- **اكتشاف إضافي أثناء الإصلاح**: `is_within_root()` كانت تُحلّل المسارات النسبية حسب CWD الحالي للعملية لا حسب جذر العمل - يكسر كل كتابة ملف متى اختلف CWD عن `WORKSPACE_ROOT` (بالضبط الحالة التي صُمِّم المتغيّر لدعمها).
- **الحل**: الاعتماد على موقع الملف الفعلي (`__file__`) بدل افتراض مسار نشر مُعيَّن، وإصلاح `is_within_root` لتستخدم نفس منطق `resolve()`.
- **التحقق**: Reality Check حي (كتابة ملف فعلي بجذر مختلف تماماً عن CWD).

## Phase 4 — Provider Layer
- **المشكلة**: `registry.py` كان يستورد `gemini_provider.py`/`openai_provider.py` - **ملفان غير موجودين إطلاقاً** رغم ادعاء `roadmap.md` أن Gemini "✅ مربوط".
- **الحل**: تنفيذ الملفين فعلياً (طلبات HTTP مباشرة، لا SDK ثقيل)، + `ProviderMode` صريح (`real`/`mock`/`unavailable`) مرئي في `/api/health`، + `PROVIDER_ORDER` قابل للتهيئة، + قاعدة أمان: فشل health check لمزود حقيقي لا يُخفى أبداً كـ "يعمل".
- **قيد صادق**: الاتصال الحي الفعلي بـ Gemini/OpenAI **UNKNOWN** من بيئة CI/التطوير هذه (egress محدود) - منطق المزوّدين مُختبَر عبر HTTP محاكى.

## Phase 5 — Capability System (نطاق files/git فقط)
- **قرار سابق (Architecture Safety Gate، ADR-013)**: `src/Core/capability.py` كان يُسجِّل 9 "قدرات" (منها `terminal`) كميتاداتا فقط، بلا أي أداة حقيقية.
- **مراجعة أمان منفصلة** (`docs/security/TERMINAL_CAPABILITY_SECURITY_REVIEW.md`): Terminal **لا يُربَط إطلاقاً** - أي تنفيذ Shell حقيقي يتجاوز حدود `PathService` بالكامل ويعمل في نفس عملية `SecretsManager`.
- **الحل**: `src/Core/builtin_tools.py` - أدابتر يربط أدوات حقيقية لـ `files` (عبر `path_service.py`) و`git` (عبر `git_manager.py`) فقط. لا أداة `push` مربوطة عمداً.

## Phase 6 — Execution Engine
- **المشكلة**: `ExecutionEngine._execute_step` كان يُرجع نجاحاً وهمياً دائماً (`{"status": "success"}` بلا أي عمل فعلي)؛ `self._max_retries` مُعرَّف بلا استخدام إطلاقاً.
- **الحل**: تنفيذ حقيقي عبر أدوات Phase 5 عند تحديد `capability`+`tool`؛ حالة `BLOCKED` جديدة منفصلة عن `FAILED` (قدرة غير موجودة = يستحيل المحاولة، لا فشل بعد محاولة حقيقية)؛ `_max_retries` مُطبَّق فعلياً.
- **حد نطاق متعمَّد**: لم يُوصَل بمسار `/api/build` الحقيقي - يبقى ذلك قراراً منفصلاً لاحقاً.

## Phase 7 — Organizational Memory (نطاق ضيّق: ذاكرة قرارات ADR)
- **اكتشاف**: `docs_storage.list_adrs()` - التي تُغذّي `GET /api/adrs` المنشور فعلياً - كانت تبحث عن ملفات بنمط `ADR-*.md`، بينما كل ملف ADR حقيقي في المستودع (001-013) مُسمّى `NNN-slug.md` بلا تلك البادئة. **النتيجة: كان هذا الـ endpoint يُرجع قائمة فارغة دائماً**.
- **الحل**: مطابقة النمط الفعلي المُستخدَم، مع بقاء التوافق مع النمط القديم لو ظهر مستقبلاً.
- **التحقق**: Reality Check حي - `/api/adrs` يُرجع الآن 10 قرارات حقيقية بدل الصفر.

## غير مُنفَّذ (بقرار صريح، لا إغفال)
- **Phase 8 (Knowledge Graph)**: تُخُطِّي بقرار صريح - نظام R&D كبير بلا مستهلك حالي.
- **الاتصال الحي بـ Docker/Replit/Railway الحقيقية**: **UNKNOWN** من بيئة العمل هذه طوال المهمة - غير مُدَّعى أبداً كـ PASS.
