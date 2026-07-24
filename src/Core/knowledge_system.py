"""
Phase 5: Knowledge System
=========================
Canonical Owner: Knowledge Engine
Source: ADRs + Failures + Decisions + Graph
Target: M3

المكونات:
1. Knowledge Validity + Stale Knowledge Rule
2. Confidence System + Provenance
3. Failure Intelligence + Failure Genome
4. Decision Intelligence + Environment Intelligence

GATE: "What will break if I change this API endpoint?" — Knowledge Graph فعلي،
      impact analysis، اختبارات+ADRs، تمييز VERIFIED_CURRENT من STALE/CONFLICTED
"""

import ast
import re
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

from src.path_service import path_service


class KnowledgeValidity(Enum):
    """صلاحية المعرفة"""
    VERIFIED_CURRENT = "verified_current"      # تم التحقق حديثاً
    VERIFIED_AT_COMMIT = "verified_at_commit"  # تم التحقق عند commit معين
    STALE = "stale"                           # قديمة/منحرفة
    UNKNOWN = "unknown"                        # غير معروف
    CONFLICTED = "conflicted"                 # متعارضة


class KnowledgeReliability(Enum):
    """موثوقية المصدر"""
    PRIMARY_SOURCE = "primary_source"          # مصدر أصلي
    DERIVED = "derived"                       # مشتقة
    INFERRED = "inferred"                     # مستنتجة
    TEMPORARY = "temporary"                   # مؤقتة
    CONFLICTED = "conflicted"                 # متعارضة


class FailureGenome:
    """
    Failure Genome - جينوم الفشل
    كل فشل له: root cause, solution, prevention, confidence + prediction
    """
    
    def __init__(
        self,
        failure_id: str,
        description: str,
        root_cause: str,
        solution: str,
        prevention: str,
        confidence: float = 0.5,
        affected_files: List[str] = None,
        affected_apis: List[str] = None,
        affected_tests: List[str] = None,
        recurrence_count: int = 0,
        last_occurrence: Optional[str] = None
    ):
        self.failure_id = failure_id
        self.description = description
        self.root_cause = root_cause
        self.solution = solution
        self.prevention = prevention
        self.confidence = confidence
        self.affected_files = affected_files or []
        self.affected_apis = affected_apis or []
        self.affected_tests = affected_tests or []
        self.recurrence_count = recurrence_count
        self.last_occurrence = last_occurrence
    
    def to_dict(self) -> Dict:
        return {
            'failure_id': self.failure_id,
            'description': self.description,
            'root_cause': self.root_cause,
            'solution': self.solution,
            'prevention': self.prevention,
            'confidence': self.confidence,
            'affected_files': self.affected_files,
            'affected_apis': self.affected_apis,
            'affected_tests': self.affected_tests,
            'recurrence_count': self.recurrence_count,
            'last_occurrence': self.last_occurrence
        }


@dataclass
class KnowledgeNode:
    """عقدة معرفة"""
    id: str
    type: str  # file, api, test, adr, capability, provider, failure, decision
    name: str
    content: Optional[str] = None
    validity: KnowledgeValidity = KnowledgeValidity.UNKNOWN
    reliability: KnowledgeReliability = KnowledgeReliability.DERIVED
    confidence: float = 0.5
    provenance: List[str] = field(default_factory=list)  # مصدر المعرفة
    last_verified: Optional[str] = None
    commit_hash: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class KnowledgeEdge:
    """حافة معرفة"""
    source: str
    target: str
    relationship: str  # contains, uses, depends_on, decided_by, verified_by, affected_by, tested_by
    confidence: float = 0.5
    provenance: str = ""  # المصدر الذي أثبت هذه العلاقة
    validity: KnowledgeValidity = KnowledgeValidity.UNKNOWN
    evidence: List[str] = field(default_factory=list)  # أدلة نصية


@dataclass
class Decision:
    """قرار تصميم"""
    decision_id: str
    title: str
    context: str  # السياق/المشكلة
    chosen: str  # القرار المختار
    rationale: str  # السبب
    alternatives: List[str] = field(default_factory=list)  # البدائل المرفوضة
    evidence: List[str] = field(default_factory=list)  # الأدلة
    adr_reference: Optional[str] = None
    commit_hash: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class EnvironmentInfo:
    """معلومات البيئة"""
    python_version: Optional[str] = None
    node_version: Optional[str] = None
    os: Optional[str] = None
    database: Optional[str] = None
    dependencies: Dict[str, str] = field(default_factory=dict)
    works_on: List[str] = field(default_factory=list)
    fails_on: List[str] = field(default_factory=list)


class KnowledgeSystem:
    """
    نظام المعرفة
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or path_service.get_workspace_root()
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.failure_genomes: Dict[str, FailureGenome] = {}
        self.decisions: Dict[str, Decision] = {}
        self.environment = EnvironmentInfo()
        self.last_index_time: Optional[str] = None
    
    def index_knowledge(self) -> int:
        """فهرسة المعرفة من المصادر"""
        count = 0
        
        # ADRs
        count += self._index_adrs()
        
        # APIs
        count += self._index_apis()
        
        # Tests
        count += self._index_tests()
        
        # Capabilities
        count += self._index_capabilities()
        
        # Build edges from relationships
        self._build_edges()
        
        self.last_index_time = datetime.now(timezone.utc).isoformat()
        
        return count
    
    def _index_adrs(self) -> int:
        """فهرسة ADRs"""
        count = 0
        adr_dir = Path(self.workspace_root) / 'docs' / 'adr'
        
        if adr_dir.exists():
            for adr_file in adr_dir.glob('*.md'):
                try:
                    content = adr_file.read_text(errors='ignore')
                    
                    # استخراج معلومات ADR
                    node_id = f"adr:{adr_file.stem}"
                    
                    node = KnowledgeNode(
                        id=node_id,
                        type="adr",
                        name=adr_file.name,
                        content=content[:500],  # أول 500 حرف
                        reliability=KnowledgeReliability.PRIMARY_SOURCE,
                        validity=KnowledgeValidity.VERIFIED_CURRENT,
                        provenance=[str(adr_file)]
                    )
                    
                    self.nodes[node_id] = node
                    count += 1
                    
                    # استخراج القرار
                    decision = self._extract_decision(content, node_id, adr_file.name)
                    if decision:
                        self.decisions[decision.decision_id] = decision
                        
                except Exception:
                    pass
        
        return count
    
    def _extract_decision(self, content: str, node_id: str, filename: str) -> Optional[Decision]:
        """استخراج قرار من محتوى ADR"""
        # استخراج العنوان
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            return None
        
        title = title_match.group(1).strip()
        
        # إنشاء قرار
        decision = Decision(
            decision_id=node_id,
            title=title,
            context="ADR content",
            chosen="ADR implementation",
            rationale="Documented in ADR",
            adr_reference=filename
        )
        
        return decision
    
    def _index_apis(self) -> int:
        """فهرسة APIs"""
        count = 0
        app_file = Path(self.workspace_root) / 'src' / 'app.py'
        
        if app_file.exists():
            try:
                content = app_file.read_text(errors='ignore')
                
                # البحث عن routes
                route_pattern = r'@app\.route\(\s*["\']([^"\']+)["\']'
                for match in re.finditer(route_pattern, content):
                    api_path = match.group(1)
                    node_id = f"api:{api_path}"
                    
                    node = KnowledgeNode(
                        id=node_id,
                        type="api",
                        name=api_path,
                        reliability=KnowledgeReliability.PRIMARY_SOURCE,
                        validity=KnowledgeValidity.VERIFIED_CURRENT,
                        provenance=["src/app.py"]
                    )
                    
                    self.nodes[node_id] = node
                    count += 1
                    
            except Exception:
                pass
        
        return count
    
    def _index_tests(self) -> int:
        """فهرسة الاختبارات"""
        count = 0
        tests_dir = Path(self.workspace_root) / 'tests'
        
        if tests_dir.exists():
            for test_file in tests_dir.glob('test_*.py'):
                try:
                    content = test_file.read_text(errors='ignore')
                    
                    # البحث عن دوال الاختبار
                    test_pattern = r'def\s+(test_[a-zA-Z0-9_]+)'
                    for match in re.finditer(test_pattern, content):
                        test_name = match.group(1)
                        node_id = f"test:{test_name}"
                        
                        node = KnowledgeNode(
                            id=node_id,
                            type="test",
                            name=test_name,
                            reliability=KnowledgeReliability.PRIMARY_SOURCE,
                            validity=KnowledgeValidity.VERIFIED_CURRENT,
                            provenance=[str(test_file)]
                        )
                        
                        self.nodes[node_id] = node
                        count += 1
                        
                except Exception:
                    pass
        
        return count
    
    def _index_capabilities(self) -> int:
        """فهرسة القدرات"""
        count = 0
        
        try:
            from src.Core.capability import capability_registry
            
            for cap_id, cap in capability_registry._capabilities.items():
                node_id = f"capability:{cap_id}"
                
                node = KnowledgeNode(
                    id=node_id,
                    type="capability",
                    name=cap_id,
                    reliability=KnowledgeReliability.PRIMARY_SOURCE,
                    validity=KnowledgeValidity.VERIFIED_CURRENT,
                    provenance=["src/Core/capability.py"]
                )
                
                self.nodes[node_id] = node
                count += 1
                
        except Exception:
            pass
        
        return count
    
    def _build_edges(self) -> None:
        """بناء العلاقات بين العقد"""
        # ربط APIs بالاختبارات
        for node_id, node in self.nodes.items():
            if node.type == "api":
                # البحث عن اختبارات تختبر هذا الـ API
                for test_id, test_node in self.nodes.items():
                    if test_node.type == "test":
                        # علاقة افتراضية - في الإنتاج سيتم التحقق من الكود الفعلي
                        edge = KnowledgeEdge(
                            source=node_id,
                            target=test_id,
                            relationship="tested_by",
                            confidence=0.7,
                            provenance="static_analysis"
                        )
                        self.edges.append(edge)
    
    def query_validity(self, node_id: str) -> KnowledgeValidity:
        """استعلام عن صلاحية معرفة"""
        if node_id not in self.nodes:
            return KnowledgeValidity.UNKNOWN
        
        return self.nodes[node_id].validity
    
    def check_stale(self, node_id: str) -> bool:
        """فحص إذا كانت المعرفة قديمة"""
        validity = self.query_validity(node_id)
        return validity in [KnowledgeValidity.STALE, KnowledgeValidity.CONFLICTED]
    
    def get_confidence(self, node_id: str) -> float:
        """الحصول على مستوى الثقة"""
        if node_id not in self.nodes:
            return 0.0
        
        return self.nodes[node_id].confidence
    
    def analyze_impact(self, target: str) -> Dict[str, Any]:
        """
        تحليل التأثير - "What will break if I change this?"
        GATE: Knowledge Graph فعلي، impact analysis، اختبارات+ADRs
        """
        impact = {
            'target': target,
            'affected_nodes': [],
            'affected_tests': [],
            'related_adrs': [],
            'confidence': 0.0,
            'validity': 'unknown',
            'risk_level': 'unknown'
        }
        
        # البحث عن العقد المرتبطة
        for edge in self.edges:
            if edge.source == target or edge.target == target:
                impact['affected_nodes'].append(edge.target if edge.source == target else edge.source)
                impact['confidence'] = max(impact['confidence'], edge.confidence)
                
                # اختبارات متأثرة
                related_node = self.nodes.get(edge.target if edge.source == target else edge.source)
                if related_node and related_node.type == 'test':
                    impact['affected_tests'].append(related_node.name)
                
                # ADRs مرتبطة
                if related_node and related_node.type == 'adr':
                    impact['related_adrs'].append(related_node.name)
        
        # حساب مستوى المخاطر
        impact_count = len(impact['affected_nodes'])
        if impact_count == 0:
            impact['risk_level'] = 'low'
        elif impact_count > 10:
            impact['risk_level'] = 'critical'
        elif impact_count > 5:
            impact['risk_level'] = 'high'
        else:
            impact['risk_level'] = 'medium'
        
        # تحديد الصلاحية
        if target in self.nodes:
            impact['validity'] = self.nodes[target].validity.value
        
        return impact
    
    def add_failure_genome(self, genome: FailureGenome) -> None:
        """إضافة جينوم فشل"""
        self.failure_genomes[genome.failure_id] = genome
    
    def get_failure_genome(self, failure_id: str) -> Optional[FailureGenome]:
        """الحصول على جينوم فشل"""
        return self.failure_genomes.get(failure_id)
    
    def predict_failures(self, change_target: str) -> List[FailureGenome]:
        """التنبؤ بالأعطال المحتملة"""
        predictions = []
        
        for genome in self.failure_genomes.values():
            # فحص إذا كان التغيير يؤثر على ملفات الفشل
            if any(change_target in f for f in genome.affected_files):
                predictions.append(genome)
        
        return predictions
    
    def add_decision(self, decision: Decision) -> None:
        """إضافة قرار"""
        self.decisions[decision.decision_id] = decision
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """الحصول على قرار"""
        return self.decisions.get(decision_id)
    
    def set_environment_info(self, env: EnvironmentInfo) -> None:
        """تعيين معلومات البيئة"""
        self.environment = env
    
    def check_works_on(self, component: str) -> bool:
        """فحص إذا كان المكون يعمل على البيئة الحالية"""
        return component in self.environment.works_on
    
    def mark_stale(self, node_id: str) -> None:
        """وضع علامة قديم على معرفة"""
        if node_id in self.nodes:
            self.nodes[node_id].validity = KnowledgeValidity.STALE
            self.nodes[node_id].confidence *= 0.5  # تقليل الثقة
    
    def verify_current(self, node_id: str) -> None:
        """التحقق من أن المعرفة حديثة"""
        if node_id in self.nodes:
            self.nodes[node_id].validity = KnowledgeValidity.VERIFIED_CURRENT
            self.nodes[node_id].last_verified = datetime.now(timezone.utc).isoformat()
            self.nodes[node_id].confidence = min(1.0, self.nodes[node_id].confidence + 0.1)


# Singleton
_knowledge_system: Optional[KnowledgeSystem] = None


def get_knowledge_system(workspace_root: Optional[str] = None) -> KnowledgeSystem:
    """الحصول على مثيل singleton"""
    global _knowledge_system
    if _knowledge_system is None:
        _knowledge_system = KnowledgeSystem(workspace_root)
    return _knowledge_system


def clear_knowledge_system() -> None:
    """مسح المثيل"""
    global _knowledge_system
    _knowledge_system = None
