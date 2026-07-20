# ADR-012: المعمارية الرسمية (Canonical Architecture)

**الحالة**: مُعتمَد (Phase 2 - Architecture Consolidation)
**يُبطل**: التناقض الضمني بين ADR-001 (Flask v1.0)، ADR-011 (CodeForge-X Core)، ولا شيء يُبطلهما صراحة رغم التعارض — هذا ADR يحسم الأمر.
**السياق الكامل**: `AUDIT_REPORT.md` §1، `ARCHITECTURE_ASSESSMENT.md`، `CONTRADICTIONS.md` C1/C2.

## القرار

**Flask v1.0 (`src/app.py` + مسار `pipeline.py`/`build_engine.py`) هو المسار الإنتاجي الرسمي الوحيد (Production).**

السبب: هو المسار الوحيد الذي:
1. تُشغّله فعلياً ملفات النشر الثلاثة الموجودة (`Procfile`, `render.yaml`, `railway.json`).
2. يعمل فعلياً عند محاكاة تثبيت الإنتاج الحقيقي (مُتحقَّق: `import src.app` ينجح ببيئة flask+gunicorn فقط).
3. يملك أي تغطية اختبار حالية (وإن كانت جزئية).

## تصنيف كل مكوّن

| المكوّن | التصنيف | السبب |
|---|---|---|
| `src/app.py`, `src/pipeline.py`, `src/build_engine.py`, `src/state.py`, `src/project_manager.py`, `src/path_service.py`, `src/diagnostics.py`, `src/health.py`, `src/event_logger.py` | **Production** | مسار التشغيل الفعلي المنشور، مُتحقَّق بالاستيراد + الاختبارات |
| `src/model_provider/*` | **Production** (Mock نشط فعلياً، Gemini/OpenAI Development — انظر Phase 4) | مستورد فعلياً من build_engine |
| `src/Core/workspace.py`, `src/Core/capability.py` (تعريف العقود فقط) | **Development** | كود سليم بنيوياً، غير موصول بعد بالمسار الفعلي — مرشح للدمج التدريجي لا الحذف |
| `src/Core/execution.py`, `src/Core/deployment.py` | **Legacy / Placeholder** | موثَّقة ذاتياً في الكود كـ stub غير منفَّذ فعلياً؛ لا قيمة تشغيلية حالية |
| `src/Core/secrets.py`, `src/Core/event_bus.py`, `src/Core/plugin.py`, `src/Core/sdk.py`, `src/Core/memory.py` | **Experimental** | غير مستوردة من أي مسار منشور؛ تحتاج قرار منفصل: دمج أو أرشفة |
| `src/agents.py` (CrewAI) | **Legacy / Dead Code** | غير مستورد من `app.py`؛ hard-import لحزمة اختيارية غير مثبَّتة في أي بيئة نشر — خطر تعطّل مستقبلي عند أي استيراد غافل (انظر AUDIT F2/R6) |
| `web/` (React+Vite+Supabase) + `supabase/functions/codeforge-engine` | **Experimental / Unknown** | لا ملف نشر مقابل في المستودع (لا vercel.json/netlify.toml/supabase config)؛ حالة النشر الفعلية **UNKNOWN** (غير قابلة للتحقق من هذه البيئة) |

## القرارات التابعة (لا تُنفَّذ الآن، تحتاج قرارك)
- **`src/agents.py`**: يُقترَح حذفه أو نقله لمجلد `archive/` صراحة (ليس ضمن نطاق Phase 1-4 الحالي — يحتاج موافقتك صراحة لأنه "حذف" ممنوع بدون إذن).
- **`web/` + Supabase Edge Function**: يُقترَح توثيقه كمسار تجريبي منفصل رسمياً في README بدل تركه بلا تصنيف، أو حسم مستقبله (دمج/إيقاف) في ADR لاحق منفصل.
- **`src/Core/*` المتبقي**: مرشح لدمج تدريجي داخل `src/` الفعلي (لا كطبقة موازية) في Phase تالية، وليس ضمن هذا القرار.

## الأثر (Blast Radius) لو تجاهلنا هذا القرار
استمرار التطوير على أي من المسارات الثلاثة دون تصنيف واضح يعني تكرار العمل، وتوثيقاً مضللاً (كما وُثِّق في `CONTRADICTIONS.md`)، وخطر تراكمي على قابلية الصيانة.
