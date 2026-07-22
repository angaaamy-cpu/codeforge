# ARCHITECTURE.md — الحالة الفعلية المُتحقَّقة (محدَّث حتى Phase 8)

> هذا المستند يعكس **ما يعمل فعلياً** بدليل مباشر (تتبع استيراد + اختبار تشغيل)، وليس النية الأصلية. للقرار الرسمي انظر `docs/adr/012-canonical-architecture.md`. للتفاصيل الجنائية الكاملة انظر `AUDIT_REPORT.md`. لسجل التغييرات الكامل انظر `CHANGELOG.md`.

## مخطط النظام (Production Path فقط)

```mermaid
flowchart TD
    subgraph Deploy["ملفات النشر"]
        PF[Procfile]
        RY[render.yaml]
        RJ[railway.json]
    end

    PF --> APP
    RY --> APP
    RJ --> APP

    APP["src/app.py (Flask)<br/>+ Phase1 Auth Middleware"] --> STATE[src/state.py]
    APP --> PM[src/project_manager.py]
    APP --> EL[src/event_logger.py]
    APP --> CF["src/codeforge.py"]
    CF --> BE[src/build_engine.py]
    CF -.->|"deferred import,<br/>try/except-guarded"| COREINIT["src/Core/__init__.py"]
    COREINIT --> EB["Core/event_bus.py ✅ Active<br/>(real events on every build)"]
    COREINIT --> WS["Core/workspace.py ✅ Active<br/>(writes workspaces/.workspaces.json)"]
    COREINIT --> CAP["Core/capability.py ✅ files/git wired (Phase 5)<br/>⚠️ terminal/http/etc still metadata-only"]
    COREINIT --> EXEC["Core/execution.py ✅ real capability execution + retry (Phase 6)<br/>⚠️ not wired into /api/build"]
    COREINIT -.->|"instantiated, never invoked"| INERT["Core/deployment.py, secrets.py,<br/>plugin.py, memory.py<br/>❌ still Placeholder"]
    BE --> PIPE[src/pipeline.py]
    PIPE --> PR[src/model_provider/registry.py]
    PR --> MOCK[MockProvider - active by default]
    PR --> GEM["GeminiProvider (Phase 4, real if healthy)"]
    PR --> OAI["OpenAIProvider (Phase 4, real if healthy)"]
    BE --> PS[src/path_service.py]
    APP --> GIT[src/git_manager.py]
    APP --> ADRAPI["GET /api/adrs -> docs_storage.list_adrs()<br/>✅ fixed in Phase 7 (was always empty)"]
    APP --> KGAPI["GET /api/knowledge/graph, /impact/&lt;id&gt;<br/>✅ Phase 8 - derived from real sources, see docs/KNOWLEDGE_GRAPH.md"]

    subgraph Disconnected["منفصل تماماً - لا استيراد من أي مسار منشور"]
        AGENTS["src/agents.py (CrewAI)<br/>❌ dead code"]
        SDK["src/Core/sdk.py<br/>❌ dead code (0 importers)"]
        WEB["web/ (React+Supabase)<br/>+ Edge Function<br/>❓ حالة نشر غير معروفة"]
    end

```

## تصنيف المكوّنات
انظر التصنيف الدقيق (لكل ملف على حدة، بالدليل) في `docs/adr/013-src-core-architectural-status.md`. القرار العلوي التلخيصي في `docs/adr/012-canonical-architecture.md` (مع تصحيح Errata في نهايته). **ملاحظة**: `capability.py` و`execution.py` تغيّر تصنيفهما جزئياً بعد Phase 5/6 (files/git أصبحا Active فعلياً) - الجدول في ADR-013 يعكس الحالة *قبل* Phase 5؛ `CHANGELOG.md` يوثّق كل تغيير لاحق بدليله.

## حقيقة المزوّدين (Providers) حالياً
- **Mock**: نشط افتراضياً ما لم يُضبَط مزوّد حقيقي وسليم.
- **Gemini / OpenAI**: مُنفَّذان فعلياً (Phase 4) - انظر `CHANGELOG.md` §Phase 4 وقيد الاتصال الحي الصادق المذكور فيه.

## حقيقة الأمان
طبقة Default-Deny على `/api/*` (باستثناء `GET /api/health`) — التفاصيل الكاملة في `docs/API.md`، والتحقق في `tests/test_security.py`.

## ما لا يعكسه هذا المخطط (قصداً)
- `web/` غير مرسومة كمسار تشغيل حقيقي لأن **حالة نشرها الفعلية غير قابلة للتحقق من هذه البيئة (UNKNOWN)** — رسمها كمسار "يعمل" سيكون ادعاءً غير موثَّق.
- بيئات Replit/Docker/Railway الفعلية: لا يوجد تحقق تشغيلي حي منها من بيئة العمل المستخدَمة طوال هذه المهمة (UNKNOWN بصراحة، غير مُدَّعاة أبداً كـ PASS).
