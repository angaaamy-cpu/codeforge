# API.md — مرجع الواجهة البرمجية الفعلية (v1.0)

> يعكس هذا المستند فقط الـ routes الموجودة فعلياً في `src/app.py` (تتبُّع مباشر لـ `@app.route`)، لا نية أو خطة مستقبلية.

## المصادقة (إلزامية منذ Phase 1)

كل `/api/*` محمي بـ **Default Deny** عدا `GET /api/health`. أرسل الهيدر:

```
X-API-Key: <ADMIN_API_KEY>
```

بلا هيدر صحيح → `401 {"error": "unauthorized"}`. إن لم تضبط `ADMIN_API_KEY` كمتغيّر بيئة، راجع سجلات إقلاع السيرفر للمفتاح المؤقت المُولَّد (يتغيّر كل إعادة تشغيل).

## نقاط النهاية (Endpoints)

| Method | Path | الوصف | ملاحظات |
|---|---|---|---|
| GET | `/` | الواجهة (HTML) | عام - غير محمي بـ X-API-Key (ليس تحت `/api/`) |
| GET | `/api/health` | فحص صحة النظام + `ProviderMode` (Phase 4) | **عام - الوحيد المُستثنى من المصادقة** |
| GET | `/api/diagnostics` | تشخيص تفصيلي | يتطلب X-API-Key |
| GET | `/api/state` | حالة النظام | يتطلب X-API-Key |
| GET | `/api/summary` | ملخّص | يتطلب X-API-Key |
| GET | `/api/projects` | قائمة المشاريع | يتطلب X-API-Key |
| POST | `/api/projects` | إنشاء مشروع | يتطلب X-API-Key |
| POST | `/api/projects/<name>/activate` | تفعيل مشروع | يتطلب X-API-Key |
| POST | `/api/projects/<name>/archive` | أرشفة مشروع | يتطلب X-API-Key |
| DELETE | `/api/projects/<name>` | حذف مشروع (نهائي) | يتطلب X-API-Key - **إجراء تدميري، لا تراجع** |
| GET | `/api/active-project` | المشروع النشط حالياً | يتطلب X-API-Key |
| GET | `/api/tasks` | قائمة المهام | يتطلب X-API-Key |
| POST | `/api/tasks` | تنفيذ مهمة (عبر `pipeline.py`) | يتطلب X-API-Key |
| GET | `/api/history` | سجل تاريخي | يتطلب X-API-Key |
| GET | `/api/events` | أحداث حديثة | يتطلب X-API-Key |
| GET | `/api/search` | بحث في الذاكرة/التوثيق | يتطلب X-API-Key |
| GET | `/api/adrs` | قائمة القرارات المعمارية (**أُصلِحت في Phase 7** - كانت تُرجع فارغة دائماً) | يتطلب X-API-Key |
| POST | `/api/build` | بناء مشروع من وصف (المسار الفعلي: `codeforge.py`→`build_engine.py`) | يتطلب X-API-Key |

## `/api/health` - حقل `mode` (Phase 4)

القيمة أحد: `real` (مزوّد LLM حقيقي مُهيَّأ وسليم) | `mock` (نص مُولَّد بمطابقة أنماط - **ليس** استدلال نموذج حقيقي) | `unavailable` (لا مزوّد على الإطلاق). لا تُفترَض قيمة "real" ما لم يظهر ذلك صراحةً في الاستجابة.

## ملاحظات أمان
- `DELETE /api/projects/<name>` لا رجعة فيه - لا سلة مهملات.
- `POST /api/build`/`POST /api/tasks` يشغّلان أدوات فعلية (Phase 5: files/git عبر `CapabilityRegistry` إن استُخدِمت داخلياً) - راجع `docs/security/TERMINAL_CAPABILITY_SECURITY_REVIEW.md` لحدود ما هو مُفعَّل حالياً (لا Terminal، لا Browser).
