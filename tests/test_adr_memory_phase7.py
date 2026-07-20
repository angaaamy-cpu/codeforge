"""
Phase 7 - Organizational Memory (نطاق ضيّق: إصلاح ذاكرة قرارات ADR الموجودة)
=============================================================================
اكتشاف أثناء العمل: docs_storage.list_adrs() (وبالتالي /api/adrs، endpoint
منشور فعلياً) كانت تبحث عن نمط "ADR-*.md"، بينما كل ملف ADR حقيقي في
المستودع مُسمّى "NNN-slug.md" بلا تلك البادئة - فتُرجع فارغة دائماً.
هذا الاختبار يثبت الإصلاح، لا يفترضه.

ملاحظة: DocsStorage ليست singleton (لا نمط _instance) - تُبنى مباشرة بلا
حاجة لأي حيلة إعادة استيراد للوحدة (module reload)، وهذا مقصود: محاولة
سابقة استخدمت del sys.modules['src.storage.docs_storage'] واكتشفت خللاً
حقيقياً في پايثون نفسه (submodule import يُعيد ربط اسم docs_storage على
حزمة src.storage للوحدة (module) بدل الـ instance الذي يُصدّره
__init__.py عمداً) - أُزيلت تلك الحيلة هنا لتفادي تلويث بيئة الاختبار.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.docs_storage import DocsStorage


def test_list_adrs_finds_real_repo_adrs():
    """يثبت مباشرة على ملفات ADR الحقيقية في هذا المستودع (001-013، بلا
    ملفات ADR-*.md على الإطلاق) أن list_adrs() لا تُرجع صفراً بعد الآن."""
    ds = DocsStorage()
    result = ds.list_adrs()
    assert len(result) >= 10  # 001-007, 011, 012, 013 معروفة على الأقل
    numbers = {a.number for a in result}
    assert 12 in numbers
    assert 13 in numbers


def test_list_adrs_with_real_naming_convention(tmp_path):
    """اختبار معزول: ملف بنمط NNN-slug.md (الفعلي) يُكتشَف."""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "042-test-decision.md").write_text(
        "# قرار اختباري\n\n**الحالة**: مُعتمَد\n\nمحتوى.\n", encoding="utf-8"
    )
    ds = DocsStorage(docs_dir=str(tmp_path / "docs"))
    result = ds.list_adrs()
    assert len(result) == 1
    assert result[0].number == 42
    assert "قرار اختباري" in result[0].title


def test_list_adrs_still_supports_adr_prefixed_naming(tmp_path):
    """توافق خلفي: لو ظهر ملف مستقبلي بنمط ADR-NNN-slug.md (النمط
    الأصلي الذي افترضه الكود قبل الإصلاح) يبقى يعمل أيضاً."""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "ADR-007-legacy-style.md").write_text(
        "# ADR-007: قرار بالنمط القديم\n\n**الحالة**: مُعتمَد\n", encoding="utf-8"
    )
    ds = DocsStorage(docs_dir=str(tmp_path / "docs"))
    result = ds.list_adrs()
    assert len(result) == 1
    assert result[0].number == 7


def test_adr_exists_matches_real_naming(tmp_path):
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "005-something.md").write_text("# شيء\n", encoding="utf-8")
    ds = DocsStorage(docs_dir=str(tmp_path / "docs"))
    assert ds.adr_exists(5) is True
    assert ds.adr_exists(999) is False


def test_no_duplicate_if_file_matches_both_patterns_conceptually(tmp_path):
    """لا يُعَدّ الملف مرتين حتى لو تشابهت الأنماط."""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "009-only-once.md").write_text("# مرة واحدة فقط\n", encoding="utf-8")
    ds = DocsStorage(docs_dir=str(tmp_path / "docs"))
    result = ds.list_adrs()
    assert len(result) == 1
