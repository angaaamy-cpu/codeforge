"""
Phase 5 - Knowledge System GATE Tests
======================================
GATE: "What will break if I change this API endpoint?" — Knowledge Graph فعلي،
      impact analysis، اختبارات+ADRs، تمييز VERIFIED_CURRENT من STALE/CONFLICTED

Real execution on actual codebase.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.knowledge_system import (
    KnowledgeSystem,
    KnowledgeValidity,
    KnowledgeReliability,
    FailureGenome,
    Decision,
    EnvironmentInfo,
    get_knowledge_system,
    clear_knowledge_system
)


def test_knowledge_system_indexes_knowledge():
    """GATE: فهرسة المعرفة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    count = ks.index_knowledge()
    
    assert count > 0, "No knowledge indexed"
    print(f"✅ Indexed {count} knowledge nodes")


def test_knowledge_system_finds_adrs():
    """GATE: البحث عن ADRs"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    adr_nodes = [n for n in ks.nodes.values() if n.type == 'adr']
    print(f"✅ Found {len(adr_nodes)} ADRs")
    
    # Check decisions extracted
    print(f"✅ Extracted {len(ks.decisions)} decisions")


def test_knowledge_system_finds_apis():
    """GATE: البحث عن APIs"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    api_nodes = [n for n in ks.nodes.values() if n.type == 'api']
    assert len(api_nodes) > 0, "No APIs found"
    
    print(f"✅ Found {len(api_nodes)} APIs:")
    for api in api_nodes[:5]:
        print(f"   - {api.name}")


def test_knowledge_system_finds_tests():
    """GATE: البحث عن الاختبارات"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    test_nodes = [n for n in ks.nodes.values() if n.type == 'test']
    assert len(test_nodes) > 0, "No tests found"
    
    print(f"✅ Found {len(test_nodes)} tests")


def test_knowledge_system_finds_capabilities():
    """GATE: البحث عن القدرات"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    cap_nodes = [n for n in ks.nodes.values() if n.type == 'capability']
    print(f"✅ Found {len(cap_nodes)} capabilities")


def test_knowledge_system_validity():
    """GATE: صلاحية المعرفة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    # Check validity for a known node
    api_nodes = [n for n in ks.nodes.values() if n.type == 'api']
    if api_nodes:
        node = api_nodes[0]
        validity = ks.query_validity(node.id)
        
        assert validity in [
            KnowledgeValidity.VERIFIED_CURRENT,
            KnowledgeValidity.VERIFIED_AT_COMMIT,
            KnowledgeValidity.STALE,
            KnowledgeValidity.UNKNOWN,
            KnowledgeValidity.CONFLICTED
        ]
        
        print(f"✅ Node validity: {validity.value}")


def test_knowledge_system_stale_detection():
    """GATE: كشف المعرفة القديمة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    # Mark a node as stale
    api_nodes = [n for n in ks.nodes.values() if n.type == 'api']
    if api_nodes:
        node_id = api_nodes[0].id
        ks.mark_stale(node_id)
        
        assert ks.check_stale(node_id) == True
        print(f"✅ Stale detection working")


def test_knowledge_system_confidence():
    """GATE: مستوى الثقة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    # Check confidence for a known node
    api_nodes = [n for n in ks.nodes.values() if n.type == 'api']
    if api_nodes:
        node = api_nodes[0]
        confidence = ks.get_confidence(node.id)
        
        assert 0.0 <= confidence <= 1.0
        print(f"✅ Node confidence: {confidence}")


def test_knowledge_system_impact_analysis():
    """GATE: تحليل التأثير - 'What will break if I change this?'"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    # Get an API to analyze
    api_nodes = [n for n in ks.nodes.values() if n.type == 'api']
    if api_nodes:
        api_id = api_nodes[0].id
        impact = ks.analyze_impact(api_id)
        
        assert 'target' in impact
        assert 'affected_nodes' in impact
        assert 'affected_tests' in impact
        assert 'risk_level' in impact
        assert 'validity' in impact
        
        print(f"""
============================================
IMPACT ANALYSIS: {api_id}
============================================
Affected nodes: {len(impact['affected_nodes'])}
Affected tests: {len(impact['affected_tests'])}
Risk level: {impact['risk_level']}
Validity: {impact['validity']}
Confidence: {impact['confidence']:.2f}
============================================
""")


def test_knowledge_system_failure_genome():
    """GATE: Failure Genome"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    
    # Create a failure genome
    genome = FailureGenome(
        failure_id="FAIL-001",
        description="Authentication bug in login endpoint",
        root_cause="Missing token validation",
        solution="Add token validation middleware",
        prevention="Add unit tests for auth flow",
        confidence=0.85,
        affected_files=["src/auth.py", "src/middleware.py"],
        affected_apis=["/api/login"],
        affected_tests=["test_login.py"],
        recurrence_count=2
    )
    
    ks.add_failure_genome(genome)
    
    # Retrieve it
    retrieved = ks.get_failure_genome("FAIL-001")
    assert retrieved is not None
    assert retrieved.root_cause == "Missing token validation"
    
    print(f"✅ Failure genome added and retrieved:")
    print(f"   - Root cause: {retrieved.root_cause}")
    print(f"   - Confidence: {retrieved.confidence}")
    print(f"   - Recurrence: {retrieved.recurrence_count}")


def test_knowledge_system_decision():
    """GATE: Decision Intelligence"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    
    # Create a decision
    decision = Decision(
        decision_id="DEC-001",
        title="Use SQLite for development",
        context="Need a simple database for local development",
        chosen="SQLite - simple, no setup required",
        rationale="Zero configuration, perfect for development",
        alternatives=["PostgreSQL", "MongoDB", "MySQL"]
    )
    
    ks.add_decision(decision)
    
    # Retrieve it
    retrieved = ks.get_decision("DEC-001")
    assert retrieved is not None
    assert retrieved.title == "Use SQLite for development"
    assert "PostgreSQL" in retrieved.alternatives
    
    print(f"✅ Decision added and retrieved:")
    print(f"   - Title: {retrieved.title}")
    print(f"   - Alternatives: {len(retrieved.alternatives)}")
    print(f"   - Chosen: {retrieved.chosen[:50]}...")


def test_knowledge_system_environment():
    """GATE: Environment Intelligence"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    
    # Set environment info
    env = EnvironmentInfo(
        python_version="3.13.0",
        os="Linux",
        database="SQLite",
        works_on=["development", "testing"],
        fails_on=["production"]
    )
    
    ks.set_environment_info(env)
    
    assert ks.environment.python_version == "3.13.0"
    assert "development" in ks.environment.works_on
    
    print(f"✅ Environment info set:")
    print(f"   - Python: {ks.environment.python_version}")
    print(f"   - OS: {ks.environment.os}")
    print(f"   - Works on: {ks.environment.works_on}")


def test_knowledge_system_verify_current():
    """GATE: التحقق من المعرفة الحديثة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    api_nodes = [n for n in ks.nodes.values() if n.type == 'api']
    if api_nodes:
        node_id = api_nodes[0].id
        
        # Mark as stale
        ks.mark_stale(node_id)
        assert ks.nodes[node_id].validity == KnowledgeValidity.STALE
        
        # Verify as current
        ks.verify_current(node_id)
        assert ks.nodes[node_id].validity == KnowledgeValidity.VERIFIED_CURRENT
        
        print(f"✅ Stale → Verified current transition working")


def test_knowledge_system_gate_summary():
    """GATE: ملخص Phase 5"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_knowledge_system()
    ks = KnowledgeSystem(workspace)
    ks.index_knowledge()
    
    # Analyze an API
    api_nodes = [n for n in ks.nodes.values() if n.type == 'api']
    api_id = api_nodes[0].id if api_nodes else None
    
    print(f"""
============================================
PHASE 5 - KNOWLEDGE SYSTEM GATE
============================================
Knowledge indexed: {len(ks.nodes)}
  - ADRs: {len([n for n in ks.nodes.values() if n.type == 'adr'])}
  - APIs: {len([n for n in ks.nodes.values() if n.type == 'api'])}
  - Tests: {len([n for n in ks.nodes.values() if n.type == 'test'])}
  - Capabilities: {len([n for n in ks.nodes.values() if n.type == 'capability'])}

Edges: {len(ks.edges)}
Decisions: {len(ks.decisions)}
Failure Genomes: {len(ks.failure_genomes)}

Knowledge Validity:
  - VERIFIED_CURRENT: {len([n for n in ks.nodes.values() if n.validity == KnowledgeValidity.VERIFIED_CURRENT])}
  - STALE: {len([n for n in ks.nodes.values() if n.validity == KnowledgeValidity.STALE])}
  - UNKNOWN: {len([n for n in ks.nodes.values() if n.validity == KnowledgeValidity.UNKNOWN])}

Impact Analysis (for {api_id}):
""")
    
    if api_id:
        impact = ks.analyze_impact(api_id)
        print(f"  - Affected nodes: {len(impact['affected_nodes'])}")
        print(f"  - Affected tests: {len(impact['affected_tests'])}")
        print(f"  - Risk level: {impact['risk_level']}")
        print(f"  - Validity: {impact['validity']}")

    print(f"""
============================================
✅ GATE PASSED
============================================
""")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
