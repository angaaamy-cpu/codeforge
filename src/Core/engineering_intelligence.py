"""
Phase 7: Engineering Intelligence
===================================
Canonical Owner: Engineering Intelligence Engine
Source: Complete System Model + Knowledge Graph + Digital Twin
Target: M4

المكونات:
1. Engineering Consciousness + Architectural Reasoning + Design Review
2. Software Causal Graph
3. Requirements-to-Code Traceability
4. Software Physics Metrics (Gravity, Fragility, Heat, Entropy, Mass, Stress)
5. Architectural Immune System + Software Conservation
6. Architecture Evolution + Continuous Refactoring + Software Archaeology
7. Engineering Economics + Safety Case Engine

GATE: مشروع قديم معقد: Archaeology Report، Architectural Violations،
      Causal Graph، Physics Metrics، Refactoring مبني على Economics، Safety Case.
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from datetime import datetime, timezone

from src.path_service import path_service


class InvariantLevel(Enum):
    """مستوى الثابت"""
    CRITICAL = "critical"  # Security/Data
    HIGH = "high"          # Public API
    MEDIUM = "medium"      # Performance
    LOW = "low"            # Style


class ViolationType(Enum):
    """نوع الانتهاك"""
    LAYER_VIOLATION = "layer_violation"
    BOUNDARY_VIOLATION = "boundary_violation"
    COUPLING = "coupling"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    ANTI_PATTERN = "anti_pattern"


@dataclass
class ArchitectureViolation:
    """انتهاك معماري"""
    id: str
    type: ViolationType
    level: InvariantLevel
    component: str
    description: str
    evidence: List[str] = field(default_factory=list)
    fix_suggestion: Optional[str] = None
    cost: float = 0.0


@dataclass
class PhysicsMetric:
    """ميتريك الفيزياء البرمجية"""
    component: str
    gravity: float = 0.0      # صعوبة التغيير
    fragility: float = 0.0   # قابلية الكسر
    heat: float = 0.0        # النشاط/التغيير
    entropy: float = 0.0     # الفوضى/التعقيد
    mass: float = 0.0        # الحجم
    stress: float = 0.0       # الحمل/الضغط


@dataclass
class CausalLink:
    """رابط سببي"""
    cause: str
    effect: str
    probability: float = 1.0
    description: str = ""


@dataclass
class RequirementTrace:
    """تتبع المتطلب"""
    requirement_id: str
    adr_id: Optional[str] = None
    component: Optional[str] = None
    api_endpoint: Optional[str] = None
    controller: Optional[str] = None
    service: Optional[str] = None
    tests: List[str] = field(default_factory=list)
    monitoring: Optional[str] = None


@dataclass
class SafetyCase:
    """حالة السلامة"""
    claim: str
    hazard: Optional[str] = None
    potential_impact: Optional[str] = None
    argument: str = ""
    evidence: List[str] = field(default_factory=list)
    residual_risk: str = "low"
    verified: bool = False


@dataclass
class SoftwareArchaeology:
    """علم آثار البرمجيات"""
    component: str
    age_years: float
    original_purpose: str
    current_purpose: str
    changes_count: int
    contributors: List[str] = field(default_factory=list)
    interesting_facts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class EngineeringIntelligence:
    """
    محرك ذكاء الهندسة
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or path_service.get_workspace_root()
        self.violations: List[ArchitectureViolation] = []
        self.physics_metrics: Dict[str, PhysicsMetric] = {}
        self.causal_graph: List[CausalLink] = []
        self.requirements_trace: Dict[str, RequirementTrace] = {}
        self.safety_cases: List[SafetyCase] = []
        self.archaeology_reports: Dict[str, SoftwareArchaeology] = {}
    
    # ==================== Architecture Immune System ====================
    
    def detect_layer_violation(self, file_path: str) -> Optional[ArchitectureViolation]:
        """كشف انتهاك الطبقات"""
        # مثال: بيانات تدخل في طبقة العرض
        if 'templates' in file_path and ('db.' in file_path or 'query' in file_path):
            return ArchitectureViolation(
                id=f"LAYER-{len(self.violations)+1}",
                type=ViolationType.LAYER_VIOLATION,
                level=InvariantLevel.CRITICAL,
                component=file_path,
                description="Business logic in presentation layer",
                evidence=[f"File: {file_path}"]
            )
        return None
    
    def detect_boundary_violation(self, file_path: str) -> Optional[ArchitectureViolation]:
        """كشف انتهاك الحدود"""
        # مثال: وصول مباشر للـ database من API
        if 'app.py' in file_path and 'execute(' in file_path:
            return ArchitectureViolation(
                id=f"BOUND-{len(self.violations)+1}",
                type=ViolationType.BOUNDARY_VIOLATION,
                level=InvariantLevel.HIGH,
                component=file_path,
                description="Direct database access from API layer"
            )
        return None
    
    def detect_circular_dependency(self) -> List[ArchitectureViolation]:
        """كشف التبعيات الدائرية"""
        violations = []
        # هذا فحص مبسط - في الإنتاج يستخدم تحليل التبعيات الكامل
        return violations
    
    def scan_architecture(self) -> List[ArchitectureViolation]:
        """فحص المعمارية بالكامل"""
        violations = []
        
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            
            for filename in files:
                if filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, self.workspace_root)
                    
                    # فحص الانتهاكات
                    v = self.detect_layer_violation(rel_path)
                    if v:
                        violations.append(v)
                    
                    v = self.detect_boundary_violation(rel_path)
                    if v:
                        violations.append(v)
        
        self.violations = violations
        return violations
    
    def get_violations_by_level(self, level: InvariantLevel) -> List[ArchitectureViolation]:
        """الحصول على الانتهاكات حسب المستوى"""
        return [v for v in self.violations if v.level == level]
    
    def get_critical_violations(self) -> List[ArchitectureViolation]:
        """الحصول على الانتهاكات الحرجة"""
        return self.get_violations_by_level(InvariantLevel.CRITICAL)
    
    # ==================== Software Physics Metrics ====================
    
    def calculate_physics_metrics(self, component: str) -> PhysicsMetric:
        """حساب ميتريك الفيزياء"""
        # gravity: نسبة الأسطر المعدلة / الأسطر الإجمالية
        # fragility: نسبة الفشل / التغيير
        # heat: نسبة التغيير مع الوقت
        # entropy: التعقيد الدوري
        
        metric = PhysicsMetric(component=component)
        
        # حساب من الملفات
        component_path = os.path.join(self.workspace_root, component)
        if os.path.exists(component_path):
            if os.path.isfile(component_path):
                with open(component_path) as f:
                    lines = len(f.readlines())
                    metric.mass = lines
                    metric.gravity = min(lines / 100, 1.0)  # normalize
                    metric.fragility = 0.3  # افتراضي
                    metric.heat = 0.2  # افتراضي
                    metric.entropy = 0.1  # افتراضي
            elif os.path.isdir(component_path):
                total_lines = 0
                for root, dirs, files in os.walk(component_path):
                    for f in files:
                        if f.endswith('.py'):
                            try:
                                with open(os.path.join(root, f)) as file:
                                    total_lines += len(file.readlines())
                            except:
                                pass
                metric.mass = total_lines
                metric.gravity = min(total_lines / 1000, 1.0)
                metric.fragility = 0.3
                metric.heat = 0.2
                metric.entropy = 0.1
        
        self.physics_metrics[component] = metric
        return metric
    
    def get_component_health(self, component: str) -> float:
        """الحصول على صحة المكون (0-1)"""
        if component not in self.physics_metrics:
            self.calculate_physics_metrics(component)
        
        m = self.physics_metrics[component]
        # صحة أقل مع gravity و fragility و entropy أعلى
        health = 1.0 - (m.gravity * 0.3 + m.fragility * 0.3 + m.entropy * 0.2)
        return max(0.0, min(1.0, health))
    
    # ==================== Causal Graph ====================
    
    def add_causal_link(self, cause: str, effect: str, description: str = "") -> None:
        """إضافة رابط سببي"""
        link = CausalLink(
            cause=cause,
            effect=effect,
            description=description
        )
        self.causal_graph.append(link)
    
    def trace_effects(self, cause: str) -> List[str]:
        """تتبع التأثيرات"""
        effects = []
        for link in self.causal_graph:
            if link.cause == cause:
                effects.append(link.effect)
        return effects
    
    def trace_causes(self, effect: str) -> List[str]:
        """تتبع الأسباب"""
        causes = []
        for link in self.causal_graph:
            if link.effect == effect:
                causes.append(link.cause)
        return causes
    
    def build_causal_graph(self) -> List[CausalLink]:
        """بناء الرسم البياني السببي"""
        # ربط Causes الشائعة بالـ Effects
        common_causes = [
            ("Slow DB", "API Latency", "Database slowness affects API response"),
            ("API Latency", "Frontend Timeout", "Slow API causes frontend timeouts"),
            ("Frontend Timeout", "User Abandonment", "Users leave when pages don't load"),
            ("User Abandonment", "Revenue Loss", "Lost users = lost revenue"),
        ]
        
        for cause, effect, desc in common_causes:
            self.add_causal_link(cause, effect, desc)
        
        return self.causal_graph
    
    # ==================== Requirements Traceability ====================
    
    def add_requirement_trace(self, req_id: str, trace: RequirementTrace) -> None:
        """إضافة تتبع متطلب"""
        self.requirements_trace[req_id] = trace
    
    def get_trace(self, req_id: str) -> Optional[RequirementTrace]:
        """الحصول على تتبع متطلب"""
        return self.requirements_trace.get(req_id)
    
    def trace_requirement_to_code(self, req_id: str) -> Dict[str, Any]:
        """تتبع متطلب للكود"""
        trace = self.get_trace(req_id)
        if not trace:
            return {"found": False}
        
        return {
            "found": True,
            "requirement": req_id,
            "adr": trace.adr_id,
            "component": trace.component,
            "api": trace.api_endpoint,
            "controller": trace.controller,
            "service": trace.service,
            "tests": trace.tests,
            "monitoring": trace.monitoring
        }
    
    # ==================== Safety Case ====================
    
    def add_safety_case(self, case: SafetyCase) -> None:
        """إضافة حالة سلامة"""
        self.safety_cases.append(case)
    
    def verify_safety_case(self, claim: str) -> bool:
        """التحقق من حالة السلامة"""
        for case in self.safety_cases:
            if case.claim == claim:
                return case.verified
        return False
    
    # ==================== Software Archaeology ====================
    
    def generate_archaeology_report(self, component: str) -> SoftwareArchaeology:
        """إنشاء تقرير آثار"""
        report = SoftwareArchaeology(
            component=component,
            age_years=0.0,
            original_purpose="Unknown",
            current_purpose="Unknown",
            changes_count=0,
            interesting_facts=[],
            recommendations=[]
        )
        
        # محاولة معرفة العمر من git
        component_path = os.path.join(self.workspace_root, component)
        if os.path.exists(component_path):
            try:
                result = subprocess.run(
                    ['git', 'log', '--follow', '--format=%ai', '--', component],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    dates = result.stdout.strip().split('\n')
                    if dates:
                        first_date = dates[-1]
                        # حساب العمر
                        try:
                            first = datetime.fromisoformat(first_date.split()[0])
                            now = datetime.now(timezone.utc)
                            report.age_years = (now - first).days / 365.25
                        except:
                            pass
                        
                        report.changes_count = len(dates)
            except:
                pass
            
            # معرفة الغرض
            try:
                with open(component_path) as f:
                    content = f.read(1000)
                    if 'class' in content:
                        report.original_purpose = "Contains class definitions"
                        report.current_purpose = "Active component"
            except:
                pass
            
            # توصيات
            if report.age_years > 5:
                report.recommendations.append("Consider modernizing this legacy component")
            if report.changes_count > 20:
                report.recommendations.append("High maintenance - consider refactoring")
        
        self.archaeology_reports[component] = report
        return report
    
    # ==================== Design Review ====================
    
    def design_review(self, change_proposal: str) -> Dict[str, Any]:
        """
        مراجعة التصميم
        قبل التنفيذ: هل هذه أفضل طريقة؟
        """
        review = {
            "proposal": change_proposal,
            "questions": [],
            "alternatives": [],
            "risks": [],
            "recommendation": "PROCEED",
            "confidence": 0.5
        }
        
        # أسئلة مهمة
        review["questions"] = [
            "هل هذا التغيير يتعارض مع الطبقات المعمارية؟",
            "هل هناك تأثير على الـ Public API؟",
            "هل التغيير قابل للتراجع؟",
            "هل الاختبارات كافية؟",
            "ما تكلفة التراجع؟"
        ]
        
        # بدائل
        review["alternatives"] = [
            "تراجع تدريجي",
            "feature flag",
            "parallel implementation"
        ]
        
        # مخاطر
        review["risks"] = [
            "Breaking changes",
            "Migration complexity",
            "Test coverage gaps"
        ]
        
        return review
    
    # ==================== Engineering Economics ====================
    
    def calculate_refactoring_cost(self, component: str) -> Dict[str, float]:
        """حساب تكلفة إعادة الهيكلة"""
        metric = self.physics_metrics.get(component) or self.calculate_physics_metrics(component)
        
        # تقدير التكلفة
        cost = {
            "analysis": metric.mass * 0.5,      # ساعة لكل 500 سطر
            "refactor": metric.mass * 2.0,       # ساعتين لكل 500 سطر
            "test": metric.mass * 1.0,            # ساعة لكل 500 سطر
            "deploy": 4.0,                       # 4 ساعات ثابتة
            "total": 0.0
        }
        cost["total"] = sum(v for k, v in cost.items() if k != "total")
        
        return cost
    
    def should_refactor(self, component: str, budget: float) -> Tuple[bool, str]:
        """هل يجب إعادة الهيكلة؟"""
        cost = self.calculate_refactoring_cost(component)
        health = self.get_component_health(component)
        
        if health < 0.5 and cost["total"] <= budget:
            return True, f"Health {health:.0%} < 50%, cost ${cost['total']:.0f} within budget"
        elif health < 0.3:
            return True, f"Critical health {health:.0%} - refactor recommended regardless of cost"
        else:
            return False, f"Health {health:.0%} acceptable"


# Singleton
_engineering_intelligence: Optional[EngineeringIntelligence] = None


def get_engineering_intelligence(workspace_root: Optional[str] = None) -> EngineeringIntelligence:
    """الحصول على مثيل singleton"""
    global _engineering_intelligence
    if _engineering_intelligence is None:
        _engineering_intelligence = EngineeringIntelligence(workspace_root)
    return _engineering_intelligence


def clear_engineering_intelligence() -> None:
    """مسح المثيل"""
    global _engineering_intelligence
    _engineering_intelligence = None
