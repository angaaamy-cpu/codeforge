# ARCHITECTURE.md — الحالة الفعلية المُتحقَّقة (Phase 2)

> هذا المستند يعكس **ما يعمل فعلياً** بدليل مباشر (تتبع استيراد + اختبار تشغيل)، وليس النية الأصلية. للقرار الرسمي انظر `docs/adr/012-canonical-architecture.md`. للتفاصيل الجنائية الكاملة انظر `AUDIT_REPORT.md`.

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
    COREINIT --> CAP["Core/capability.py ⚠️ metadata-only<br/>(9 built-ins registered, 0 real tools)"]
    COREINIT -.->|"instantiated, never invoked"| INERT["Core/execution.py, deployment.py,<br/>secrets.py, plugin.py, memory.py<br/>❌ Placeholder"]
    BE --> PIPE[src/pipeline.py]
    PIPE --> PR[src/model_provider/registry.py]
    PR --> MOCK[MockProvider - active by default]
    PR --> GEM["GeminiProvider (Phase 4, real if healthy)"]
    PR --> OAI["OpenAIProvider (Phase 4, real if healthy)"]
    BE --> PS[src/path_service.py]
    APP --> GIT[src/git_manager.py]

    subgraph Disconnected["منفصل تماماً - لا استيراد من أي مسار منشور"]
        AGENTS["src/agents.py (CrewAI)<br/>❌ dead code"]
        SDK["src/Core/sdk.py<br/>❌ dead code (0 importers)"]
        WEB["web/ (React+Supabase)<br/>+ Edge Function<br/>❓ حالة نشر غير معروفة"]
    end

```

## تصنيف المكوّنات
انظر التصنيف الدقيق (لكل ملف على حدة، بالدليل) في `docs/adr/013-src-core-architectural-status.md`. القرار العلوي التلخيصي في `docs/adr/012-canonical-architecture.md` (مع تصحيح Errata في نهايته).

## حقيقة المزوّدين (Providers) حالياً
- **Mock**: الوحيد النشط فعلياً في أي بيئة نشر حالية بلا تدخل إضافي.
- **Gemini / OpenAI**: طبقة الواجهة (`registry.py`) موجودة، **لكن ملفات التنفيذ الفعلية أُضيفت في Phase 4** (انظر `PHASE4_PROVIDERS.md`).

## حقيقة الأمان
طبقة Default-Deny على `/api/*` (باستثناء `GET /api/health`) — انظر `docs/adr/` والكود في `src/app.py`. التفاصيل والتحقق في `tests/test_security.py` و`FINAL_VERIFICATION.md`.

## ما لا يعكسه هذا المخطط (قصداً)
- `web/` غير مرسومة كمسار تشغيل حقيقي لأن **حالة نشرها الفعلية غير قابلة للتحقق من هذه البيئة (UNKNOWN)** — رسمها كمسار "يعمل" سيكون ادعاءً غير موثَّق.
- بيئات Replit/Docker/Railway الفعلية: حالة كل منها موثقة في `FINAL_VERIFICATION.md` (§Environment Matrix) وليس هنا، لأن هذا الملف عن البنية لا عن حالة التشغيل الخارجي.
