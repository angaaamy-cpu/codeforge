# 🏗️ CodeForge v1.0

**منصة بناء المشاريع بالذكاء الاصطناعي**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

---

## نظرة عامة

CodeForge هي منصة بناء مشاريع برمجية بالذكاء الاصطناعي. فقط اكتب وصف مشروعك وسنهتم بكل شيء!

### الفلسفة

> **المستخدم يكتب وصف مشروعه فقط. لا يحتاج معرفة أي تفاصيل داخلية.**
> **المنصة تتولى كل شيء وتُخرج نتيجة واضحة.**

---

## ⚡ التشغيل

### CLI (سطر الأوامر)

```bash
python src/build.py
```

أو مع وصف مباشرة:

```bash
echo "صفحة هبوط لشركة ناشئة مع 3 خدمات" | python src/build.py
```

### واجهة الويب

```bash
python src/app.py
```

ثم افتح: http://localhost:5000

### API

> ⚠️ **منذ Phase 1 (Production Safety)**: كل `/api/*` محمي افتراضياً (Default Deny) عدا `GET /api/health`. يلزم هيدر `X-API-Key`. إن لم تُضبط `ADMIN_API_KEY` كمتغيّر بيئة صراحةً، يُولَّد مفتاح عشوائي مؤقت ويُطبع مرة واحدة في سجلات الإقلاع (stdout) - غير ثابت بين إعادة التشغيل.

```bash
curl -X POST http://localhost:5000/api/build \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_API_KEY" \
  -d '{"description": "صفحة هبوط لشركة ناشئة"}'
```

---

## 📝 مثال

```
╔══════════════════════════════════════════╗
║         🏗️  CodeForge v1.0              ║
║     منصة بناء المشاريع بالذكاء الاصطناعي    ║
╚══════════════════════════════════════════╝

📝 صف مشروعك:
> نظام حجز عيادة مع صفحة رئيسية ونموذج حجز

🚀 بناء: نظام حجز عيادة مع صفحة رئيسية ونموذج حجز

📊 تقدم البناء:
  [1/6] ✅ إنشاء المشروع
  [2/6] ✅ التخطيط
  [3/6] ✅ التطوير
  [4/6] ✅ الاختبار
  [5/6] ✅ مراجعة الأمان
  [6/6] ✅ التوثيق

════════════════════════════════════════════
✅ تم بناء المشروع بنجاح!


📁 المشروع: clinic_booking_1234
📍 المسار: projects/clinic_booking_1234
📄 الملفات: 3 ملف
⏱️  المدة: 2.3 ثانية

🚀 للتشغيل:
   cd projects/clinic_booking_1234
   python -m http.server 8080

🌐 افتح: http://localhost:8080

📊 التقارير:
   - docs/reports/clinic_booking_1234-build.md
════════════════════════════════════════════
```

---

## 🏗️ الهيكل المعماري (v1.0)

> هذا مخطط v1.0 المبسَّط الأصلي. للصورة الكاملة المُتحقَّقة فعلياً (بما فيها طبقة `src/Core/*` وربطها الحقيقي، نظام القدرات files/git، ومحرك التنفيذ) انظر `docs/ARCHITECTURE.md` و`docs/adr/012-canonical-architecture.md` و`docs/adr/013-src-core-architectural-status.md`.

```
build.py (CLI)
    ↓
CodeForge (واجهة موحدة)
    ↓
BuildEngine (محرك البناء)
    ↓
ProjectManager + Pipeline + Logger + Memory
```

### الطبقات

| الطبقة | الملف | الوصف |
|--------|-------|-------|
| CLI | `src/build.py` | طبقة سطر الأوامر |
| Interface | `src/codeforge.py` | الواجهة الموحدة |
| Engine | `src/build_engine.py` | محرك البناء |
| Result | `src/build_result.py` | كائن النتيجة |
| Manager | `src/project_manager.py` | إدارة المشاريع |
| Pipeline | `src/pipeline.py` | دورة العمل |
| Web | `src/app.py` | Flask API |

---

## 📦 الميزات

- ✅ بناء مشاريع HTML/Flask/React من وصف
- ✅ تحويل الوصف العربي إلى اسم إنجليزي
- ✅ 6 خطوات بناء متسلسلة
- ✅ كشف تلقائي لأمر التشغيل
- ✅ إنشاء تقارير البناء
- ✅ API للتكامل
- ✅ واجهة CLI سهلة

---

## 🚀 التقنيات

- Python 3.11+
- Flask (API)
- ملفات Markdown/JSON على القرص (`STORAGE_BACKEND=markdown`، الافتراضي) + ChromaDB اختياري لبحث دلالي
- Mock/Gemini/OpenAI كطبقة مزوّدي LLM قابلة للتهيئة (انظر §المزوّدون أدناه)

---

## التطور

> ⚠️ ترقيم "Phase" في هذا الجدول هو ترقيم المشروع التاريخي الأصلي (v1.0 وحتى v10 المخطَّطة)، **مختلف تماماً** عن ترقيم "Phase 1-7" في `CHANGELOG.md` (مهمة معالجة/تصليب منفصلة: أمان، معمارية، مسارات، مزوّدين، قدرات، تنفيذ، ذاكرة قرارات). لا تخلط بين الترقيمين.

| المرحلة | الحالة |
|---------|--------|
| Phase 1-7: Platform Core | ✅ مكتمل |
| Phase 8: v1.0 Product | ✅ مكتمل |
| Phase 8.1: Deployment Ready | ✅ مكتمل |
| Phase 9: Backend API | 📋 مخطط |
| Phase 10: Database | 📋 مخطط |

---

## 🚀 النشر (Deployment)

### Render (موصى به)

1. أنشئ حساب على [Render](https://render.com)
2. اضغط "New" → "Web Service"
3. اربط repository من GitHub
4. اضبط الإعدادات:
   - **Build Command**: `pip install -e .`
   - **Start Command**: `gunicorn src.app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4`
5. اضبط متغيرات البيئة:
   - `PORT`: 10000
   - `FLASK_ENV`: production
6. اضغط "Create Web Service"

أو استخدم `render.yaml` للنشر التلقائي:

```bash
# Spread the word!
```

### Railway

1. أنشئ حساب على [Railway](https://railway.app)
2. اضغط "New Project" → "Deploy from GitHub"
3. اختر repository
4. Railway سيقرأ `railway.json` تلقائياً
5. اضبط متغيرات البيئة في لوحة التحكم

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

EXPOSE 8000

CMD ["gunicorn", "src.app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

### Heroku

```bash
heroku create your-codeforge-app
heroku push main
heroku open
```

---

## 📋 متغيرات البيئة

| المتغير | الوصف | القيمة الافتراضية |
|---------|-------|-----------------|
| `PORT` | منفذ الخادم | ⚠️ يختلف فعلياً حسب المنصة (Render يضبط 10000، Railway/`.env.example` يضبط 8000، `config/settings.py` الداخلي 5000 إن غاب `FLASK_PORT`) - اضبطه صراحةً في بيئتك بدل الاعتماد على تطابق افتراضي واحد |
| `HOST` | عنوان الخادم | 0.0.0.0 |
| `FLASK_ENV` | بيئة Flask | production |
| `FLASK_DEBUG` | وضع التصحيح | false |
| `SECRET_KEY` | مفتاح جلسات Flask | ⚠️ له fallback مكشوف في الكود إن غاب من env (Render يولّده تلقائياً `generateValue: true`؛ غيرها لا - اضبطه صراحةً) |
| `ADMIN_API_KEY` | **(Phase 1)** مفتاح مصادقة كل `/api/*` عدا `/api/health` | إن غاب: مفتاح عشوائي مؤقت يُطبع في سجلات الإقلاع، يتغيّر كل إعادة تشغيل |
| `GEMINI_API_KEY` | **(Phase 4)** تفعيل مزوّد Gemini الحقيقي | (فارغ = غير مُفعَّل) |
| `OPENAI_API_KEY` | **(Phase 4)** تفعيل مزوّد OpenAI الحقيقي | (فارغ = غير مُفعَّل) |
| `PROVIDER_ORDER` | **(Phase 4)** ترتيب Fallback بين المزوّدين، مثال `gemini,openai,mock` | `gemini,openai,mock` |
| `MOCK_PROVIDER_ENABLED` | **(Phase 4)** السماح بتفعيل Mock تلقائياً إن لم يتوفر مزوّد حقيقي | `true` |
| `WORKSPACE_ROOT` | **(Phase 3)** جذر الملفات الفعلي (تجاوز صريح) | موقع الملف الفعلي لو غاب - **لا** يُفترض `/app` على Railway بعد الآن |
| `LOG_LEVEL` | مستوى السجلات | INFO |

بلا أي مفتاح LLM حقيقي مضبوط: النظام يعمل بـ `mode: mock` (نص مُولَّد بمطابقة أنماط، **ليس** استدلال نموذج حقيقي) - مرئي صراحةً في `GET /api/health`.

---

## 🔧 التشغيل المحلي

```bash
# Clone
git clone https://github.com/angaaamy-cpu/codeforge.git
cd codeforge

# Install
pip install -e .

# Run
python src/app.py

# Or with gunicorn
gunicorn src.app:app --bind 0.0.0.0:8000 --workers 2
```

---

## 📁 ملفات النشر

| الملف | الوصف |
|-------|-------|
| `render.yaml` | إعدادات Render |
| `Procfile` | إعدادات Heroku/Dokku |
| `railway.json` | إعدادات Railway |
| `.env.example` | مثال متغيرات البيئة |
| `pyproject.toml` | التبعيات |

---

## المساهمة

1. Fork المشروع
2. أنشئ branch
3. Commit
4. Push
5. افتح Pull Request

---

<div align="center">

**صُنع بـ ❤️ للمطورين العرب**

</div>
