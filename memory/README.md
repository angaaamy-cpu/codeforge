# طبقة الذاكرة (Memory Layer)

## الغرض

طبقة الذاكرة مسؤولة عن:
- **حفظ السياق**: الاحتفاظ بمعلومات المحادثات والمهام
- **استرجاع القرارات**: الوصول السريع للـ ADRs والقرارات السابقة
- **منع النسيان**: ضمان استمرارية المشروع عبر الجلسات

---

## الهيكل الحالي (المرحلة 1)

```
memory/
├── README.md          # هذا الملف
├── context/           # سياق المشاريع النشطة
│   └── active.md
├── decisions/         # القرارات المعمارية
│   └── index.md
└── knowledge/         # المعرفة العامة
    └── patterns.md
```

### context/
يحفظ حالة المشاريع والمهام الحالية.

```markdown
# Current Context

## Active Project: CodeForge
- Phase: 1 (Foundation)
- Current Task: Documentation
- Blockers: None

## Recent Changes
- 2026-07-17: Initial structure created
```

### decisions/
فهرس لكل القرارات المعمارية.

```markdown
# Architecture Decisions

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| 001 | CrewAI Selection | Accepted | 2026-07-17 |

See: docs/adr/
```

### knowledge/
معرفة عامة ومعلومات مرجعية.

```markdown
# Project Knowledge

## Design Patterns Used
- Repository Pattern
- Factory Pattern

## Key Technologies
- CrewAI (Phase 2)
- OpenHands (Phase 3)
```

---

## الانتقال لـ ChromaDB (المرحلة 3)

### لماذا ChromaDB؟
- **Vector Search**: بحث ذكي حسب المعنى
- **Semantic Retrieval**: استرجاع القرارات المشابهة
- **Contextual**: فهم السياق

### العملية
```
User Query → Embedding → ChromaDB → Relevant Docs → Response
```

### ADR المطلوب
قبل الانتقال، يجب كتابة ADR جديد يغطي:
- Migration strategy
- Schema design
- Backup policy

---

## نموذج البيانات

### Document Schema
```json
{
  "id": "unique-id",
  "text": "المحتوى الكامل",
  "metadata": {
    "type": "adr|context|knowledge",
    "project": "codeforge",
    "created_at": "2026-07-17",
    "tags": ["architecture", "crewai"]
  },
  "embedding": [0.1, 0.2, ...]
}
```

### Query Types
1. **Semantic Search**: "ما القرارات المتعلقة بـ authentication؟"
2. **Similarity**: "ما похожее على هذا القرار؟"
3. **Filter**: "جلب كل الـ ADRs المقبولة"

---

## الوكلاء والذاكرة

### Manager Agent
- يحفظ حالة المهام
- يسترجع التقدم السابق
- يتتبع الـ blockers

### Architect Agent
- يسترجع الـ ADRs السابقة
- يحفظ القرارات الجديدة
- يحلل السياق

### Developer Agent
- يسترجع المعايير
- يحفظ أنماط الحل
- يتعلم من الأخطاء

### QA Agent
- يحفظ أنماط الـ bugs
- يسترجع الـ test patterns
- يتتبع quality metrics

---

## أفضل الممارسات

### كتابة الذاكرة
1. **واضح ومختصر**: كل document له عنوان واضح
2. **meta-data**: أضف tags وtimestamps
3. **مرتبط**: اربط بالـ issues والـ PRs

### استرجاع الذاكرة
1. **استخدم الكلمات المفتاحية**: للبحث الدقيق
2. **استخدم الدلالات**: للبحث الذكي
3. **فلتر**: قلل النتائج

---

## Migration Checklist (Phase 3)

- [ ] تقييم ChromaDB vs alternatives
- [ ] كتابة ADR-002
- [ ] تصميم Schema
- [ ] كتابة migration script
- [ ] اختبار search quality
- [ ] تدريب الوكلاء على الاستخدام
- [ ] backup strategy
- [ ] decommission old structure

---

## ملاحظات

### المرحلة 1
- الذاكرة = ملفات Markdown منظمة
- الموقع: `docs/` و `memory/`
- سهل الفهم والصيانة

### المرحلة 3+
- الذاكرة = ChromaDB vector store
- الموقع: `.chroma/`
- بحث ذكي وسريع
