# CONTRIBUTING.md

## قبل أي تغيير معماري
اقرأ `docs/adr/012-canonical-architecture.md` (المعمارية الرسمية) و`docs/adr/013-src-core-architectural-status.md` (تصنيف `src/Core/*`). أي قرار معماري جديد يستحق ADR جديداً برقم تسلسلي تالٍ لآخر ملف في `docs/adr/` - **لا تُعِد استخدام رقم ADR موجود**.

## اتفاقية تسمية ADR
`docs/adr/NNN-slug-وصفي.md` (بدون بادئة `ADR-`) - هذا هو النمط الفعلي المُستخدَم في كل ملف من 001 حتى 013. `docs_storage.list_adrs()` (Phase 7) تدعم أيضاً `ADR-NNN-slug.md` للتوافق، لكن الاتفاقية القياسية هي بلا بادئة.

## قبل لمس `src/Core/*`
`src/Core/capability.py` هو المالك الوحيد لأي نظام قدرات (Capability System) - لا تُنشئ نظاماً موازياً. لا تربط أدوات حقيقية لقدرة `terminal` بدون مراجعة أمنية منفصلة صريحة (انظر `docs/security/TERMINAL_CAPABILITY_SECURITY_REVIEW.md`).

## الاختبارات
قبل أي Pull Request:
```bash
python3 -m pytest tests/ -q
```
كل الاختبارات الحالية (96+) يجب أن تنجح. أضف اختباراً لأي سلوك جديد - لا "سأختبر لاحقاً".

## قاعدة عدم الادعاء الزائف
لا تصف شيئاً بأنه "يعمل" أو "✅ مكتمل" في التوثيق بدون دليل تشغيل فعلي (اختبار ناجح أو استدعاء API حي مُتحقَّق). "غير مُتحقَّق من هذه البيئة" أو "UNKNOWN" أفضل من ادعاء غير مُثبَت.

## مصدر آخر للاتفاقيات
`docs/project_conventions.md` و`docs/coding_rules.md` يحتويان تفاصيل إضافية سبقت هذا الملف - راجعهما أيضاً.
