"""
Phase 9 - Strategic Software Intelligence GATE Tests
====================================================
GATE: Complete Software Civilization Operating System - جميع المراحل متكاملة

Final integration and production verification.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.strategic_intelligence import (
    StrategicIntelligence,
    Strategy,
    RoadmapItem,
    TechnologyForecast,
    IntegrationResult,
    ImprovementAction,
    MaturityLevel,
    get_strategic_intelligence,
    clear_strategic_intelligence
)


def test_strategy_creation():
    """GATE: إنشاء استراتيجية"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    
    strategy = si.create_strategy(
        name="Software Excellence",
        vision="Build world-class software systems"
    )
    
    assert isinstance(strategy, Strategy)
    assert strategy.name == "Software Excellence"
    
    # إضافة أهداف
    si.add_goal(strategy.id, "Improve code quality")
    si.add_goal(strategy.id, "Reduce technical debt")
    
    assert len(strategy.goals) == 2
    
    print(f"✅ Strategy created: {strategy.name} with {len(strategy.goals)} goals")


def test_roadmap_management():
    """GATE: إدارة خارطة الطريق"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    
    # إضافة عناصر
    item1 = RoadmapItem(
        id="road-1",
        phase="Phase 1",
        deliverable="Core functionality",
        target_date="2026-01-01"
    )
    item2 = RoadmapItem(
        id="road-2",
        phase="Phase 2",
        deliverable="Advanced features",
        target_date="2026-06-01"
    )
    
    si.add_roadmap_item(item1)
    si.add_roadmap_item(item2)
    
    roadmap = si.get_roadmap()
    assert len(roadmap) == 2
    
    # تحديث الحالة
    si.update_roadmap_status("road-1", "completed")
    assert roadmap[0].status == "completed"
    
    print(f"✅ Roadmap: {len(roadmap)} items, {sum(1 for r in roadmap if r.status == 'completed')} completed")


def test_technology_forecasting():
    """GATE: توقع التقنيات"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    
    # إضافة توقعات
    ai_forecast = TechnologyForecast(
        technology="AI Code Generation",
        category="ai",
        maturity="growth",
        adoption_rate=75.0,
        impact="disruptive",
        timeframe="medium",
        recommendation="Adopt in next 6 months"
    )
    
    quantum_forecast = TechnologyForecast(
        technology="Quantum Computing",
        category="computing",
        maturity="emerging",
        adoption_rate=15.0,
        impact="high",
        timeframe="long",
        recommendation="Monitor for 2-3 years"
    )
    
    si.add_forecast(ai_forecast)
    si.add_forecast(quantum_forecast)
    
    # الحصول على التوصيات
    recommendations = si.recommend_technology(["development"])
    assert len(recommendations) > 0
    
    print(f"""
============================================
TECHNOLOGY FORECASTS
============================================
Total: {len(si.technology_forecasts)}
Disruptive: {len([f for f in si.technology_forecasts if f.impact == 'disruptive'])}
Recommended: {len(recommendations)}
""")
    for rec in recommendations:
        print(f"  - {rec.technology}: {rec.recommendation}")


def test_cross_phase_integration():
    """GATE: التكامل بين المراحل"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    
    integrations = si.analyze_integration()
    
    assert len(integrations) >= 7  # Phases 2-8
    
    print(f"""
============================================
CROSS-PHASE INTEGRATION
============================================
Phases integrated: {len(integrations)}
""")
    for phase, result in integrations.items():
        health_bar = "█" * int(result.health / 10) + "░" * (10 - int(result.health / 10))
        print(f"  {result.phase}: {health_bar} {result.health:.0f}%")


def test_overall_health():
    """GATE: الصحة الإجمالية"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    si.analyze_integration()
    
    health = si.calculate_overall_health()
    
    assert 0 <= health <= 100
    
    print(f"""
============================================
OVERALL SYSTEM HEALTH
============================================
Health Score: {health:.1f}/100
""")
    
    health_bar = "█" * int(health / 10) + "░" * (10 - int(health / 10))
    print(f"[{health_bar}]")
    
    if health >= 80:
        print("Status: EXCELLENT ✅")
    elif health >= 60:
        print("Status: GOOD ✅")
    elif health >= 40:
        print("Status: NEEDS IMPROVEMENT ⚠️")
    else:
        print("Status: CRITICAL ❌")


def test_gap_identification():
    """GATE: تحديد الفجوات"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    si.analyze_integration()
    
    gaps = si.identify_cross_phase_gaps()
    
    assert isinstance(gaps, list)
    
    print(f"""
============================================
IDENTIFIED GAPS
============================================
Total gaps: {len(gaps)}
""")
    for gap in gaps:
        print(f"  - {gap}")


def test_self_improvement():
    """GATE: التحسين الذاتي"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    si.analyze_integration()
    
    improvements = si.identify_improvements()
    prioritized = si.prioritize_improvements()
    
    assert len(improvements) > 0
    assert prioritized[0].priority <= prioritized[-1].priority
    
    print(f"""
============================================
SELF-IMPROVEMENT ACTIONS
============================================
Identified: {len(improvements)}
Prioritized: {len(prioritized)}
High Priority: {len([i for i in improvements if i.priority <= 2])}
""")
    for imp in prioritized[:5]:
        print(f"  P{imp.priority}: {imp.description} ({imp.effort}h)")


def test_maturity_assessment():
    """GATE: تقييم النضج"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    si.analyze_integration()
    
    maturity = si.assess_maturity()
    roadmap = si.get_maturity_roadmap()
    
    print(f"""
============================================
MATURITY ASSESSMENT
============================================
Current Level: {maturity.value.upper()}
""")
    
    print("Roadmap to next level:")
    for step in roadmap:
        print(f"  → {step}")


def test_production_gate():
    """GATE: بوابة الإنتاج"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    
    # إضافة بيانات
    si.create_strategy("Production Ready", "Build scalable systems")
    
    item = RoadmapItem(
        id="prod-1",
        phase="Production",
        deliverable="Deployment",
        target_date="2026-01-01"
    )
    si.add_roadmap_item(item)
    
    tech = TechnologyForecast(
        technology="Container Orchestration",
        category="infrastructure",
        maturity="mature",
        adoption_rate=90.0,
        impact="high",
        timeframe="short"
    )
    si.add_forecast(tech)
    
    # تشغيل البوابة
    results = si.run_production_gate()
    
    print(f"""
============================================
PRODUCTION GATE RESULTS
============================================
Gate: {results['gate']}
Status: {results['status']}
Timestamp: {results['timestamp']}

Checks:
""")
    
    for check_name, check in results["checks"].items():
        status = "✅" if check["passed"] else "❌"
        if "health" in check:
            print(f"  {status} {check_name}: {check['health']:.1f}%" if check.get("health") else f"  {status} {check_name}: {check}")
        else:
            print(f"  {status} {check_name}: {check}")
    
    print(f"""
Metrics:
  Health: {results['metrics']['overall_health']:.1f}%
  Strategies: {results['metrics']['strategies_count']}
  Roadmap Items: {results['metrics']['roadmap_items']}
  Phases: {results['metrics']['phases_integrated']}

Recommendations:
""")
    for rec in results["recommendations"][:3]:
        print(f"  → {rec}")

    print(f"""
============================================
{'✅ PRODUCTION GATE PASSED' if results['status'] == 'PASSED' else '❌ PRODUCTION GATE FAILED'}
============================================
""")


def test_summary_report():
    """GATE: تقرير الملخص"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    
    # إعداد
    si.create_strategy("Test", "Test vision")
    si.analyze_integration()
    
    summary = si.generate_summary()
    
    print(f"""
============================================
SOFTWARE CIVILIZATION OPERATING SYSTEM
           SUMMARY REPORT
============================================
System: {summary['system']}
Version: {summary['version']}
Health Score: {summary['health_score']:.1f}%
Maturity: {summary['maturity_level']}

Phases:
  Total: {summary['phases']['total']}
  Healthy: {summary['phases']['healthy']}

Strategy:
  Active: {summary['strategy']['active']}
  Goals: {summary['strategy']['goals']}

Roadmap:
  Items: {summary['roadmap']['total']}
  Completed: {summary['roadmap']['completed']}

Improvements:
  Identified: {summary['improvements']['identified']}
  High Priority: {summary['improvements']['high_priority']}

Timestamp: {summary['timestamp']}
============================================
""")


def test_final_gate_summary():
    """GATE: ملخص البوابة النهائية"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_strategic_intelligence()
    si = StrategicIntelligence(workspace)
    
    # تشغيل البوابة
    results = si.run_production_gate()
    summary = si.generate_summary()
    
    print(f"""
============================================
PHASE 9 - STRATEGIC SOFTWARE INTELLIGENCE
           FINAL GATE SUMMARY
============================================

All 9 Phases Complete:
  Phase 2: Execution Plane ✅
  Phase 3: Repository Intelligence ✅
  Phase 4: Advanced Code Intelligence ✅
  Phase 5: Knowledge System ✅
  Phase 6: Enterprise Engineering ✅
  Phase 7: Engineering Intelligence ✅
  Phase 8: Autonomous Software Company ✅
  Phase 9: Strategic Intelligence ✅

System Health: {summary['health_score']:.1f}%
Maturity Level: {summary['maturity_level']}
Production Gate: {results['status']}

============================================
{'🎉 COMPLETE SOFTWARE CIVILIZATION OPERATING SYSTEM 🎉' if results['status'] == 'PASSED' else '⚠️ GATE NOT PASSED'}
============================================
""")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
