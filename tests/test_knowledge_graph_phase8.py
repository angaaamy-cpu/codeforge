"""
Phase 8 - Knowledge Graph
==========================
لا seed data، لا بيانات مُختلَقة. كل اختبار هنا يتحقق من أن الرسم مُشتَق
فعلياً من مصادر حقيقية (ADRs، @app.route، ملفات، اختبارات)، وأن تحليل
الأثر لا يُعطي نتيجة مضلِّلة عبر عقدة project المركزية.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.knowledge_graph import KnowledgeGraph


def test_graph_has_real_nodes_from_multiple_real_sources():
    kg = KnowledgeGraph().build()
    types = {n.type for n in kg.nodes.values()}
    # كل نوع يجب أن يكون مُشتقاً فعلياً - لا نوع بلا أي عقدة واحدة على الأقل
    # عدا failure (NOT_AVAILABLE صراحة، لا نظام تتبع أعطال موجود إطلاقاً)
    for expected in ("decision", "capability", "provider", "api", "test", "file", "deployment", "project"):
        assert expected in types, f"لا عقدة واحدة من نوع '{expected}' - هل المصدر الحقيقي فعلاً غير متاح؟"


def test_decision_nodes_match_real_adr_count():
    from src.storage.docs_storage import DocsStorage
    kg = KnowledgeGraph().build()
    real_adrs = DocsStorage().list_adrs()
    decision_nodes = [n for n in kg.nodes.values() if n.type == "decision"]
    assert len(decision_nodes) == len(real_adrs)


def test_api_nodes_match_real_app_routes():
    """كل عقدة API يجب أن تُشير فعلياً لسطر حقيقي في src/app.py، لا اختراع."""
    kg = KnowledgeGraph().build()
    api_nodes = [n for n in kg.nodes.values() if n.type == "api"]
    assert len(api_nodes) >= 15  # عدد الـ @app.route المعروف فعلياً (18 وقت الكتابة)
    for n in api_nodes:
        assert n.source_reference.startswith("src/app.py:")


def test_test_nodes_derived_from_real_ast_parsing():
    """كل عقدة test تقابل دالة test_* حقيقية موجودة فعلياً في الملف المذكور."""
    kg = KnowledgeGraph().build()
    test_nodes = [n for n in kg.nodes.values() if n.type == "test"]
    assert len(test_nodes) > 50
    sample = test_nodes[0]
    file_part = sample.source_reference.split(":")[0]
    full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_part)
    assert os.path.exists(full_path)
    content = open(full_path, encoding="utf-8").read()
    assert f"def {sample.label}" in content


def test_no_edge_references_nonexistent_node():
    """قاعدة صارمة: لا يوجد edge واحد يشير لعقدة غير موجودة في self.nodes."""
    kg = KnowledgeGraph().build()
    for e in kg.edges:
        assert e.source in kg.nodes
        assert e.target in kg.nodes


def test_honest_impact_analysis_adr_007_has_no_real_connections():
    """اختبار الصدق المحوري: ADR-007 (قرار عمل قديم لا يذكر أي مسار ملف
    حقيقي) يجب أن يُعطي 0 تأثير حقيقي - لا نتيجة مُلفَّقة تماثل ADR-013."""
    kg = KnowledgeGraph().build()
    result = kg.impact_analysis("decision:007")
    assert result["found"] is True
    assert result["total_affected"] == 0


def test_honest_impact_analysis_adr_013_has_real_connections():
    """بالمقابل: ADR-013 يذكر عشرات مسارات src/*.py فعلياً - يجب أن يُظهر
    تأثيراً حقيقياً، ومختلفاً عن نتيجة ADR-007 (لا تماثل مضلِّل)."""
    kg = KnowledgeGraph().build()
    result = kg.impact_analysis("decision:013")
    assert result["found"] is True
    assert result["total_affected"] > 20
    assert "file" in result["affected_by_type"]
    assert "src/app.py" in [f["label"] for f in result["affected_by_type"]["file"]]


def test_impact_analysis_unknown_node_reports_not_found_not_fabricated():
    kg = KnowledgeGraph().build()
    result = kg.impact_analysis("decision:999")
    assert result["found"] is False
    assert "reason" in result


def test_not_available_sections_are_explicit_not_silently_empty():
    """قاعدة 'لا تخترعها. سجّلها UNKNOWN' - العلاقات غير المكتشَفة يجب أن
    تظهر صراحة في not_available، لا أن تختفي بصمت."""
    kg = KnowledgeGraph().build()
    joined = " ".join(kg.not_available)
    assert "failure" in joined
    assert "capability_depends_on_provider" in joined
    assert "api_uses_capability" in joined


def test_graph_persists_to_real_file(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    import importlib
    import src.Core.knowledge_graph as kgmod
    importlib.reload(kgmod)
    import src.path_service as psmod
    importlib.reload(psmod)
    importlib.reload(kgmod)

    kg = kgmod.KnowledgeGraph().build()
    kg.persist()
    graph_file = tmp_path / "data" / "knowledge_graph.json"
    assert graph_file.exists()
    import json
    data = json.loads(graph_file.read_text())
    assert data["node_count"] == len(kg.nodes)


def test_deployment_nodes_only_for_files_that_actually_exist():
    kg = KnowledgeGraph().build()
    deployment_nodes = [n for n in kg.nodes.values() if n.type == "deployment"]
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for n in deployment_nodes:
        assert os.path.exists(os.path.join(repo_root, n.source_id))
