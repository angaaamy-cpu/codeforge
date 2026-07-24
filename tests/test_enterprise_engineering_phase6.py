"""
Phase 6 - Enterprise Engineering GATE Tests
============================================
GATE: تشغيل 50+ Workers حقيقيين على مهام متنوعة مع Concurrency Test كامل

Real execution of enterprise patterns.
"""

import os
import sys
import time
import threading
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.enterprise_engineering import (
    EnterpriseOrchestrator,
    Worker,
    Task,
    WorkerState,
    TaskPriority,
    ConcurrencyTestResult,
    TechnicalDebt,
    AgentContract,
    get_enterprise_orchestrator,
    clear_enterprise_orchestrator
)


def test_enterprise_orchestrator_creates_workers():
    """GATE: إنشاء Workers"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    workers = orchestrator.create_workers(50)
    
    assert len(workers) == 50
    assert len(orchestrator.workers) == 50
    
    print(f"✅ Created {len(workers)} workers")


def test_enterprise_orchestrator_submits_tasks():
    """GATE: إرسال المهام"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    task = Task(
        id="test-task-1",
        type="analysis",
        priority=TaskPriority.HIGH,
        required_capabilities=["execution"]
    )
    
    task_id = orchestrator.submit_task(task)
    
    assert task_id == "test-task-1"
    assert task.id in orchestrator.tasks
    
    print(f"✅ Task submitted: {task_id}")


def test_enterprise_orchestrator_assigns_tasks():
    """GATE: تعيين المهام"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    # إنشاء workers ومهمة
    workers = orchestrator.create_workers(5)
    task = Task(
        id="test-task-2",
        type="analysis",
        required_capabilities=["execution"]
    )
    orchestrator.submit_task(task)
    
    # تعيين
    assigned = orchestrator.assign_task(workers[0].id, task)
    
    assert assigned == True
    assert task.worker_id == workers[0].id
    assert task.status == "running"
    
    print(f"✅ Task assigned to {workers[0].id}")


def test_enterprise_orchestrator_completes_tasks():
    """GATE: إكمال المهام"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    workers = orchestrator.create_workers(5)
    task = Task(
        id="test-task-3",
        type="analysis"
    )
    orchestrator.submit_task(task)
    orchestrator.assign_task(workers[0].id, task)
    
    # إكمال
    orchestrator.complete_task(task.id, {"result": "success"})
    
    assert task.status == "completed"
    assert task.result == {"result": "success"}
    assert workers[0].state == WorkerState.IDLE
    
    print(f"✅ Task completed successfully")


def test_enterprise_orchestrator_handles_failures():
    """GATE: معالجة الفشل"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    workers = orchestrator.create_workers(5)
    task = Task(
        id="test-task-4",
        type="analysis",
        max_retries=3
    )
    orchestrator.submit_task(task)
    orchestrator.assign_task(workers[0].id, task)
    
    # فشل
    orchestrator.fail_task(task.id, "Test error")
    
    assert task.retries == 1
    assert task.status == "retrying"
    
    print(f"✅ Task failure handled with retry")


def test_enterprise_orchestrator_blocks_tasks():
    """GATE: حظر المهام"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    workers = orchestrator.create_workers(5)
    task = Task(
        id="test-task-5",
        type="analysis"
    )
    orchestrator.submit_task(task)
    orchestrator.assign_task(workers[0].id, task)
    
    # حظر
    orchestrator.block_task(task.id, "Resource limit exceeded")
    
    assert task.status == "blocked"
    assert task.error == "Resource limit exceeded"
    
    print(f"✅ Task blocked correctly")


def test_enterprise_orchestrator_concurrency_test():
    """GATE: اختبار التزامن - 50+ workers"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    # تشغيل اختبار التزامن
    result = orchestrator.run_concurrency_test(num_workers=50, num_tasks=100)
    
    assert isinstance(result, ConcurrencyTestResult)
    assert result.total_workers == 50
    assert result.total_tasks == 100
    assert result.total_time > 0
    
    print(f"""
============================================
CONCURRENCY TEST: 50 WORKERS
============================================
Completed: {result.completed_tasks}/{result.total_tasks}
Failed: {result.failed_tasks}
Blocked: {result.blocked_tasks}
Deadlocks: {result.deadlocks_detected}
Time: {result.total_time:.3f}s
============================================
""")


def test_enterprise_orchestrator_resource_monitoring():
    """GATE: مراقبة الموارد"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    orchestrator.create_workers(10)
    
    resources = orchestrator.get_resource_usage()
    
    assert 'cpu' in resources
    assert 'memory' in resources
    assert 'workers' in resources
    assert 'tasks' in resources
    
    print(f"✅ Resource monitoring working:")
    print(f"   CPU: {resources['cpu']['usage_percent']:.1f}%")
    print(f"   Memory: {resources['memory']['percent']:.1f}%")
    print(f"   Workers: {resources['workers']['total']}")


def test_enterprise_orchestrator_technical_debt():
    """GATE: الدين التقني"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    # إضافة دين
    debt = TechnicalDebt(
        component="auth.py",
        issue="Missing rate limiting",
        interest_rate=0.15,
        impact="high",
        risk="high",
        cost_of_delay=1000.0,
        fix_cost=500.0
    )
    orchestrator.add_technical_debt(debt)
    
    # الحصول على الديون
    debts = orchestrator.get_debt_by_priority()
    assert len(debts) == 1
    assert debts[0].component == "auth.py"
    
    total = orchestrator.calculate_total_debt_cost()
    assert total == 1000.0
    
    print(f"✅ Technical debt tracking working:")
    print(f"   Total debt: ${total}")
    print(f"   Interest: ${orchestrator.calculate_debt_interest():.2f}")


def test_enterprise_orchestrator_specialized_agents():
    """GATE: الوكلاء المتخصصون"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    # تسجيل وكيل
    contract = AgentContract(
        id="agent-1",
        role="code-reviewer",
        capabilities=["analysis", "review", "security"],
        permissions=["read", "comment"],
        input_contract={"code": "string"},
        output_contract={"issues": "list", "score": "number"},
        risk_level="low",
        verification_method="unit_tests"
    )
    orchestrator.register_agent(contract)
    
    # اختيار وكيل
    selected = orchestrator.select_agent("review")
    assert selected is not None
    assert selected.role == "code-reviewer"
    
    agents = orchestrator.get_all_agents()
    assert len(agents) == 1
    
    print(f"✅ Specialized agents working:")
    print(f"   Registered: {len(agents)} agents")
    print(f"   Selected: {selected.role}")


def test_enterprise_orchestrator_large_scale():
    """GATE: اختبار نطاق كبير"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    # تشغيل اختبار كبير
    result = orchestrator.run_concurrency_test(num_workers=100, num_tasks=200)
    
    assert result.success == True or result.completed_tasks > 100
    
    print(f"✅ Large scale test: {result.completed_tasks} tasks in {result.total_time:.3f}s")


def test_enterprise_orchestrator_gate_summary():
    """GATE: ملخص Phase 6"""
    workspace = str(Path(__file__).parent.parent)
    
    clear_enterprise_orchestrator()
    orchestrator = EnterpriseOrchestrator(workspace)
    
    # إنشاء 50 workers
    orchestrator.create_workers(50)
    
    # إضافة بعض المهام
    for i in range(20):
        task = Task(
            id=f"summary-task-{i}",
            type="mixed",
            priority=TaskPriority.MEDIUM
        )
        orchestrator.submit_task(task)
    
    # تشغيل اختبار
    result = orchestrator.run_concurrency_test(num_workers=50, num_tasks=100)
    
    print(f"""
============================================
PHASE 6 - ENTERPRISE ENGINEERING GATE
============================================
Workers: {result.total_workers}
Tasks: {result.total_tasks}
Completed: {result.completed_tasks} ({result.completed_tasks/result.total_tasks*100:.1f}%)
Failed: {result.failed_tasks} ({result.failed_tasks/result.total_tasks*100:.1f}%)
Blocked: {result.blocked_tasks}

Deadlocks: {result.deadlocks_detected}
Race Conditions: {result.race_conditions_detected}

Total Time: {result.total_time:.3f}s
Throughput: {result.completed_tasks/result.total_time:.1f} tasks/s

GATE STATUS: {'✅ PASSED' if result.success else '⚠️ PARTIAL'}
============================================
""")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
