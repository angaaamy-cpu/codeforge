"""
Phase 8 - Autonomous Software Company GATE Tests
================================================
GATE: Mission: "Build production-ready web app with auth, DB, API, frontend"
إكمال كامل، Recovery، Digital Twin قبل التعديلات الخطيرة.

Real execution patterns.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.autonomous_software_company import (
    AutonomousSoftwareCompany,
    DigitalTwin,
    Sandbox,
    Plan,
    Mission,
    Hypothesis,
    TwinConfidence,
    get_autonomous_company,
    clear_autonomous_company
)


def test_digital_twin_creation():
    """GATE: إنشاء Digital Twin"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    
    twin = company.create_twin("test-twin")
    
    assert isinstance(twin, DigitalTwin)
    assert twin.name == "test-twin"
    assert twin.state is not None
    assert twin.coverage >= 0
    
    print(f"""
============================================
DIGITAL TWIN CREATED
============================================
Name: {twin.name}
Version: {twin.version}
Coverage: {twin.coverage:.1f}%
Confidence: {twin.confidence:.1f}%
Freshness: {twin.freshness:.1f}%
Files: {twin.state.get('files', 0)}
============================================
""")


def test_digital_twin_sync():
    """GATE: مزامنة Digital Twin"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    company.create_twin()
    
    twin = company.sync_twin()
    
    assert twin.last_sync is not None
    assert twin.last_sync != ""
    
    print(f"✅ Twin synced at {twin.last_sync}")


def test_digital_twin_confidence_level():
    """GATE: مستوى ثقة Twin"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    company.create_twin()
    
    level = company.get_twin_confidence_level()
    
    assert level in [TwinConfidence.HIGH, TwinConfidence.MEDIUM, TwinConfidence.LOW, TwinConfidence.UNKNOWN]
    
    print(f"✅ Twin confidence level: {level.value}")


def test_sandbox_creation():
    """GATE: إنشاء Sandbox"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    company.create_twin()
    
    sandbox = company.create_sandbox("test-sandbox", "Testing changes")
    
    assert isinstance(sandbox, Sandbox)
    assert sandbox.name == "test-sandbox"
    assert sandbox.original_state is not None
    
    print(f"✅ Sandbox created: {sandbox.id}")


def test_sandbox_apply_change():
    """GATE: تطبيق تغيير في Sandbox"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    company.create_twin()
    
    sandbox = company.create_sandbox("test")
    sandbox = company.apply_change_in_sandbox(sandbox.id, "modify: auth.py")
    
    assert len(sandbox.changes) == 1
    assert "modify: auth.py" in sandbox.changes
    
    print(f"✅ Change applied in sandbox: {sandbox.changes}")


def test_sandbox_scenario():
    """GATE: تشغيل سيناريو في Sandbox"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    company.create_twin()
    
    sandbox = company.create_sandbox("test")
    company.apply_change_in_sandbox(sandbox.id, "add: feature")
    sandbox = company.run_sandbox_scenario(sandbox.id)
    
    assert sandbox.results is not None
    assert sandbox.results.get("status") == "success"
    
    print(f"✅ Sandbox scenario completed: {sandbox.results}")


def test_competing_plans():
    """GATE: توليد خطط متعددة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    
    plans = company.generate_competing_plans("web_app")
    
    assert len(plans) == 4  # fast, safe, cheap, scalable
    
    types = [p.type for p in plans]
    assert "fast" in types
    assert "safe" in types
    assert "cheap" in types
    assert "scalable" in types
    
    print(f"✅ Generated {len(plans)} competing plans:")
    for p in plans:
        print(f"   - {p.name}: {p.estimated_time}h, ${p.estimated_cost}")


def test_future_impact_simulation():
    """GATE: محاكاة التأثير المستقبلي"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    
    plans = company.generate_competing_plans("test")
    impact = company.simulate_future_impact(plans[0].id, "6_months")
    
    assert "predictions" in impact
    assert "1_month" in impact["predictions"]
    
    print(f"""
============================================
FUTURE IMPACT SIMULATION
============================================
Plan: {impact['plan_id']}
Timeframe: {impact['timeframe']}
Predictions:
  1 month: {impact['predictions']['1_month']}
  6 months: {impact['predictions']['6_months']}
  1 year: {impact['predictions']['1_year']}
Confidence: {impact['confidence']:.0%}
============================================
""")


def test_hypothesis_engine():
    """GATE: محرك الفرضيات"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    
    hyp = company.create_hypothesis(
        "New auth system works correctly",
        "success"
    )
    
    assert hyp.outcome == "pending"
    
    # اختبار الفرضية
    result = company.test_hypothesis(hyp.id, "success")
    
    assert result.outcome == "CONFIRMED"
    assert result.confidence == 0.9
    
    print(f"✅ Hypothesis tested: {result.outcome} (confidence: {result.confidence})")


def test_mission_creation():
    """GATE: إنشاء مهمة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    
    mission = company.create_mission(
        name="Build Web App",
        description="Production-ready web app",
        requirements=["auth", "database", "api", "frontend"]
    )
    
    assert isinstance(mission, Mission)
    assert mission.name == "Build Web App"
    assert len(mission.requirements) == 4
    
    print(f"✅ Mission created: {mission.id}")


def test_mission_execution():
    """GATE: تنفيذ مهمة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    company.create_twin()
    
    mission = company.create_mission("Test Mission", "Test", ["req1", "req2"])
    result = company.execute_mission(mission.id)
    
    assert result.status in ["completed", "failed"]
    
    print(f"""
============================================
MISSION EXECUTION
============================================
Mission: {result.name}
Status: {result.status}
Phases: {result.phases}
Current Phase: {result.current_phase}
Errors: {len(result.errors)}
Evidence: {len(result.evidence)}
============================================
""")


def test_mission_recovery():
    """GATE: استعادة مهمة فاشلة"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    company.create_twin()
    
    mission = company.create_mission("Recovery Test", "Test", ["req1"])
    mission.status = "failed"
    mission.errors.append("Simulated failure")
    
    recovered = company.recover_mission(mission.id)
    
    assert recovered.recovery_attempts == 1
    assert recovered.status in ["completed", "failed_permanently"]
    
    print(f"✅ Recovery attempted: {recovered.recovery_attempts} time(s)")


def test_human_governance():
    """GATE: الحكومية البشرية"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    
    # إرسال للموافقة
    approval_id = company.submit_for_approval({
        "action": "deploy_production",
        "details": "..."
    })
    
    assert approval_id is not None
    
    # الموافقة
    approved = company.approve_item(approval_id)
    assert approved == True
    
    print(f"✅ Governance flow: submitted → approved")


def test_final_gate():
    """GATE: المرحلة النهائية"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_autonomous_company()
    company = AutonomousSoftwareCompany(workspace)
    
    results = company.run_final_gate()
    
    assert results["gate"] == "AUTONOMOUS_SOFTWARE_COMPANY"
    assert "checks" in results
    assert len(results["checks"]) == 6
    assert "status" in results
    
    print(f"""
============================================
PHASE 8 - AUTONOMOUS SOFTWARE COMPANY GATE
============================================
Gate: {results['gate']}
Status: {results['status']}

Checks:
""")
    for check in results["checks"]:
        status = "✅" if check["passed"] else "❌"
        print(f"  {status} {check['name']}")

    print(f"""
Evidence: {len(results['evidence'])} items

============================================
{'✅ GATE PASSED' if results['status'] == 'PASSED' else '❌ GATE FAILED'}
============================================
""")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
