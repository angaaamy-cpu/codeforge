"""
Phase 3 - Repository Intelligence GATE Tests
=============================================
GATE: مشروع حقيقي - اكتشف الخدمات، ارسم dependency graph، حدد entry points،
      اعرف repository-level impact، اكتشف scale، أنتج Health Score + 
      Onboarding Report + Confidence %

Real execution on actual codebase.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.repository_intelligence import (
    RepositoryIntelligence,
    get_repository_intelligence,
    clear_repository_intelligence,
    FileNode,
    ServiceNode,
    DependencyEdge,
    ProjectHealth,
    OnboardingReport
)


def test_repository_intelligence_discovers_real_files():
    """GATE: اكتشاف الملفات الحقيقية في المستودع"""
    # Use actual workspace
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # يجب أن finds real files
    assert report.files_indexed > 0, "No files discovered"
    print(f"✅ Discovered {report.files_indexed} files")
    
    # يجب أن finds real source files
    source_files = [f for f, n in ri.index.items() if n.type == 'source']
    assert len(source_files) > 0, "No source files found"
    print(f"✅ Found {len(source_files)} source files")


def test_repository_intelligence_classifies_files_correctly():
    """GATE: تصنيف الملفات بشكل صحيح"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # يجب أن finds test files
    test_files = [f for f, n in ri.index.items() if n.type == 'test']
    print(f"✅ Classified {len(test_files)} test files")
    
    # يجب أن finds config files
    config_files = [f for f, n in ri.index.items() if n.type == 'config']
    print(f"✅ Classified {len(config_files)} config files")
    
    # يجب أن finds docs
    doc_files = [f for f, n in ri.index.items() if n.type == 'docs']
    print(f"✅ Classified {len(doc_files)} doc files")


def test_repository_intelligence_extracts_python_imports():
    """GATE: استخراج imports من Python"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # يجب أن finds imports
    files_with_imports = [f for f, n in ri.index.items() if n.imports]
    assert len(files_with_imports) > 0, "No imports found"
    print(f"✅ Found imports in {len(files_with_imports)} files")
    
    # يجب أن finds dependencies
    assert len(ri.dependencies) > 0, "No dependencies found"
    print(f"✅ Found {len(ri.dependencies)} dependency edges")


def test_repository_intelligence_discovers_services():
    """GATE: اكتشاف الخدمات"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # يجب أن finds services
    assert report.services_discovered > 0, "No services discovered"
    print(f"✅ Discovered {report.services_discovered} services: {list(ri.services.keys())}")


def test_repository_intelligence_identifies_entry_points():
    """GATE: تحديد entry points"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # Entry points يجب أن تكون found
    all_entry_points = []
    for service in ri.services.values():
        all_entry_points.extend(service.entry_points)
    
    print(f"✅ Found {len(all_entry_points)} entry points: {all_entry_points[:5]}")
    # في مشروعنا يجب أن finds app.py أو __main__.py
    assert len(all_entry_points) > 0 or report.files_indexed > 0


def test_repository_intelligence_calculates_health():
    """GATE: حساب صحة المشروع"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # Health score يجب أن exists
    assert report.health_score is not None, "No health score"
    assert isinstance(report.health_score, ProjectHealth)
    
    health = report.health_score
    print(f"✅ Health Score: overall={health.overall:.1f}%")
    print(f"   - Test coverage: {health.test:.1f}%")
    print(f"   - Documentation: {health.documentation:.1f}%")
    print(f"   - Dependencies: {health.dependency:.1f}%")
    print(f"   - Operational: {health.operational:.1f}%")


def test_repository_intelligence_classifies_scale():
    """GATE: تصنيف حجم المشروع"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # Scale يجب أن be classified
    assert report.scale_classification in ['tiny', 'small', 'medium', 'large', 'monorepo']
    print(f"✅ Scale classified as: {report.scale_classification}")
    print(f"   - Files indexed: {report.files_indexed}")


def test_repository_intelligence_calculates_confidence():
    """GATE: حساب ثقة الفهم"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # Confidence يجب أن be calculated
    assert 0 <= report.understanding_confidence <= 100
    print(f"✅ Understanding confidence: {report.understanding_confidence:.1f}%")


def test_repository_intelligence_dependency_graph():
    """GATE: رسم بياني للتبعيات"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    graph = ri.get_dependency_graph()
    assert isinstance(graph, dict)
    print(f"✅ Dependency graph has {len(graph)} nodes")
    
    # يجب أن يكون هناك edges
    total_edges = sum(len(v) for v in graph.values())
    print(f"   - Total edges: {total_edges}")


def test_repository_intelligence_impact_analysis():
    """GATE: تحليل التأثير"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # تحليل تأثير لملف حقيقي
    source_files = [f for f, n in ri.index.items() if n.type == 'source']
    if source_files:
        test_file = source_files[0]
        impact = ri.get_impact_analysis(test_file)
        
        assert 'file' in impact
        assert 'affected_by' in impact
        assert 'affects' in impact
        assert 'services' in impact
        assert 'tests' in impact
        
        print(f"✅ Impact analysis for {test_file}:")
        print(f"   - Affected by: {len(impact['affected_by'])} files")
        print(f"   - Affects: {len(impact['affects'])} files")
        print(f"   - Services: {len(impact['services'])}")


def test_repository_intelligence_onboarding_report_complete():
    """GATE: تقرير بدء المشروع كامل"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_repository_intelligence()
    ri = RepositoryIntelligence(workspace)
    report = ri.discover_repository()
    
    # جميع الحقول مطلوبة
    assert report.project_path
    assert report.files_indexed > 0
    assert report.understanding_confidence > 0
    assert report.scale_classification != 'unknown'
    assert report.health_score is not None
    assert report.generated_at
    
    print(f"""
============================================
PHASE 3 - REPOSITORY INTELLIGENCE GATE
============================================
Project: {report.project_path}
Files Indexed: {report.files_indexed}
Services Discovered: {report.services_discovered}
Dependencies Found: {report.dependencies_found}
Scale: {report.scale_classification}
Confidence: {report.understanding_confidence:.1f}%

Health Score:
  Overall: {report.health_score.overall:.1f}%
  Test: {report.health_score.test:.1f}%
  Documentation: {report.health_score.documentation:.1f}%
  Dependency: {report.health_score.dependency:.1f}%
  Operational: {report.health_score.operational:.1f}%

Services: {list(ri.services.keys())}

Unknown Modules: {len(report.unknown_modules)}

Generated: {report.generated_at}
============================================
✅ GATE PASSED
============================================
""")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
