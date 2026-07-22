"""
CodeForge - Phase 8: Knowledge Graph
======================================
Audit أُجرِي أولاً (per التوجيه): بحث شامل في كامل المستودع عن أي تنفيذ
سابق لـ Knowledge Graph، أي graph storage، أي /api/knowledge - **لا شيء
وُجِد إطلاقاً**. لا نظام معزول موجود لإصلاحه أو إعادة استخدامه لهذا
الغرض تحديداً - لذا هذا تنفيذ جديد، لكن:
- يُعاد استخدام طبقة التخزين الموجودة فعلياً (`src.path_service`) - لا
  قاعدة بيانات جديدة، لا مكتبة graph خارجية.
- كل Node يُشتَق مباشرة من مصدر حقيقي موجود فعلاً (لا Seed Data):
    Decision  <- docs_storage.list_adrs()          (Phase 7، حقيقي فعلاً)
    Capability<- CapabilityRegistry.list_capabilities() (Phase 5، حقيقي)
    Provider  <- provider_registry.list_all()       (Phase 4، حقيقي)
    API       <- استخراج @app.route(...) من src/app.py مباشرة (regex على المصدر الفعلي)
    Test      <- تحليل AST حقيقي لملفات tests/*.py (أسماء دوال test_* فعلية)
    File      <- ملفات src/**/*.py الموجودة فعلياً على القرص
    Deployment<- Procfile/render.yaml/railway.json الموجودة فعلياً
    Failure   <- **NOT_AVAILABLE** - لا نظام تتبع أعطال موجود؛ لا يُخترَع
- كل Edge مُشتَق من دليل نصي فعلي (استخراج مسارات ملفات مذكورة داخل نص
  ADR، مطابقة سلاسل مسارات API داخل ملفات الاختبار، إلخ) - لا علاقة
  "افتراضية" أو seed. إن لم يوجد دليل، لا تُنشَأ علاقة (يُسجَّل NOT_AVAILABLE
  عند الطلب، لا يُترَك فارغاً بصمت وكأنه "لا شيء للربط").

Persistence: يُعاد بناء الرسم بالكامل من المصادر عند كل استدعاء (لا cache
قد ينحرف عن الحقيقة - نفس مبدأ Phase 7)، ثم يُكتَب لملف JSON عبر
path_service (تحقيق شرط "persistent" الفعلي دون المخاطرة بانجراف الحالة).
"""

import ast
import re
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict

from src.path_service import path_service

GRAPH_FILE = "data/knowledge_graph.json"

# API path literal pattern used both to find routes in app.py and to find
# references to those routes inside test files.
_API_PATH_RE = re.compile(r"/api/[A-Za-z0-9_\-/<>]*")
_ROUTE_DECORATOR_RE = re.compile(
    r'@app\.route\(\s*["\'](?P<path>/[^"\']*)["\']\s*(?:,\s*methods\s*=\s*\[(?P<methods>[^\]]*)\])?\s*\)'
)
_FILE_MENTION_RE = re.compile(r"\bsrc/[\w\-/]+\.py\b")


@dataclass
class Node:
    id: str
    type: str  # decision | capability | provider | api | test | file | deployment | project | failure
    label: str
    source_type: str
    source_id: str
    source_reference: str
    provenance: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Edge:
    source: str
    target: str
    relationship: str
    provenance: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.not_available: List[str] = []

    # ------------------------------------------------------------------
    # Node/edge helpers
    # ------------------------------------------------------------------
    def _add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def _add_edge(self, source: str, target: str, relationship: str, provenance: str) -> None:
        if source not in self.nodes or target not in self.nodes:
            return  # لا نُنشئ علاقة لعقدة غير موجودة فعلياً - لا تخمين
        self.edges.append(Edge(source=source, target=target, relationship=relationship, provenance=provenance))

    # ------------------------------------------------------------------
    # Source extraction (كل دالة هنا تشتق من مصدر حقيقي واحد فقط)
    # ------------------------------------------------------------------
    def _extract_decisions(self) -> None:
        from src.storage.docs_storage import DocsStorage
        ds = DocsStorage()
        for adr in ds.list_adrs():
            padded = f"{adr.number:03d}"
            node_id = f"decision:{padded}"
            self._add_node(Node(
                id=node_id, type="decision", label=adr.title,
                source_type="adr_file", source_id=padded,
                source_reference=f"docs/adr/{padded}-*.md",
                provenance="docs_storage.list_adrs()",
            ))

    def _extract_capabilities(self) -> None:
        from src.Core.capability import CapabilityRegistry
        for cap in CapabilityRegistry().list_all():
            node_id = f"capability:{cap.name}"
            self._add_node(Node(
                id=node_id, type="capability", label=cap.name,
                source_type="capability_registry", source_id=cap.name,
                source_reference="src/Core/capability.py",
                provenance="CapabilityRegistry.list_all()",
            ))

    def _extract_providers(self) -> None:
        from src.model_provider.registry import provider_registry
        for p in provider_registry.list_all():
            node_id = f"provider:{p['name']}"
            self._add_node(Node(
                id=node_id, type="provider", label=p["name"],
                source_type="provider_registry", source_id=p["name"],
                source_reference="src/model_provider/registry.py",
                provenance="provider_registry.list_all()",
            ))

    def _extract_apis(self) -> List[Tuple[str, str]]:
        """يُرجع [(path, node_id), ...] من src/app.py الفعلي مباشرة (regex على المصدر)."""
        app_py = path_service.root / "src" / "app.py"
        results = []
        if not app_py.exists():
            self.not_available.append("api: src/app.py غير موجود")
            return results
        text = app_py.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), start=1):
            m = _ROUTE_DECORATOR_RE.search(line)
            if m:
                path = m.group("path")
                methods_raw = (m.group("methods") or '"GET"').replace('"', '').replace("'", '').strip()
                node_id = f"api:{methods_raw}:{path}"
                self._add_node(Node(
                    id=node_id, type="api", label=f"{methods_raw} {path}",
                    source_type="flask_route", source_id=path,
                    source_reference=f"src/app.py:{i}",
                    provenance=f"@app.route extracted from src/app.py line {i}",
                ))
                results.append((path, node_id))
        return results

    def _extract_tests(self) -> List[Tuple[str, str]]:
        """يُرجع [(file_text, node_id), ...] عبر تحليل AST حقيقي لكل def test_*."""
        tests_dir = path_service.root / "tests"
        results = []
        if not tests_dir.exists():
            self.not_available.append("test: مجلد tests/ غير موجود")
            return results
        for f in sorted(tests_dir.glob("test_*.py")):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(text, filename=str(f))
            except (SyntaxError, OSError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    node_id = f"test:{f.name}:{node.name}"
                    self._add_node(Node(
                        id=node_id, type="test", label=node.name,
                        source_type="ast_function_def", source_id=node.name,
                        source_reference=f"tests/{f.name}:{node.lineno}",
                        provenance=f"ast.parse(tests/{f.name}) FunctionDef line {node.lineno}",
                    ))
                    results.append((text, node_id))
        return results

    def _extract_files(self) -> Set[str]:
        """ملفات src/**/*.py الفعلية الموجودة على القرص - نطاق محدود ومباشر."""
        src_dir = path_service.root / "src"
        found = set()
        if not src_dir.exists():
            self.not_available.append("file: مجلد src/ غير موجود")
            return found
        for f in src_dir.rglob("*.py"):
            rel = str(f.relative_to(path_service.root))
            node_id = f"file:{rel}"
            self._add_node(Node(
                id=node_id, type="file", label=rel,
                source_type="filesystem", source_id=rel,
                source_reference=rel,
                provenance="path_service.root/src rglob('*.py') - موجود فعلياً على القرص",
            ))
            found.add(rel)
        return found

    def _extract_deployments(self) -> None:
        candidates = {
            "Procfile": "heroku_dokku",
            "render.yaml": "render",
            "railway.json": "railway",
        }
        for filename, platform in candidates.items():
            f = path_service.root / filename
            if f.exists():
                node_id = f"deployment:{platform}"
                self._add_node(Node(
                    id=node_id, type="deployment", label=platform,
                    source_type="deployment_config_file", source_id=filename,
                    source_reference=filename,
                    provenance=f"{filename} موجود فعلياً في جذر المستودع",
                ))

    def _extract_project_root(self) -> str:
        """عقدة جذر واحدة تمثّل المستودع نفسه - مذكورة صراحة كعقدة تجميع
        اصطناعية (provenance تقول ذلك بوضوح)، لا كبيانات "مُكتشَفة"."""
        node_id = "project:codeforge"
        self._add_node(Node(
            id=node_id, type="project", label="codeforge (repository root)",
            source_type="synthetic_anchor", source_id="codeforge",
            source_reference=".",
            provenance="عقدة تجميع اصطناعية تمثّل جذر المستودع - وليست مُشتقّة من مصدر بيانات، مذكور صراحة",
        ))
        return node_id

    # ------------------------------------------------------------------
    # Edge derivation (كل علاقة من دليل نصي فعلي فقط)
    # ------------------------------------------------------------------
    def _derive_edges(self, project_id: str, api_results, test_results, real_files: Set[str]) -> None:
        # File -> exposes -> API: كل API node مُستخرَج من src/app.py حصراً
        app_file_id = "file:src/app.py"
        for _, api_id in api_results:
            self._add_edge(app_file_id, api_id, "exposes", "كل API node مُستخرَج حصرياً من src/app.py")

        # Test -> verifies -> API: مطابقة نصية فعلية لمسار API داخل نص ملف الاختبار
        for path, api_id in api_results:
            for test_text, test_id in test_results:
                if path in test_text:
                    self._add_edge(test_id, api_id, "verifies",
                                   f"السلسلة '{path}' موجودة فعلياً في نص ملف الاختبار")

        # Decision -> mentions -> File: مطابقة نصية فعلية لمسار src/*.py داخل
        # النص الكامل لملف ADR (وليس adr.content المقتطَع لـ500 حرف فقط في
        # list_adrs() - القراءة هنا مباشرة من الملف نفسه لتفادي فقدان مراجع حقيقية)
        adr_dir = path_service.root / "docs" / "adr"
        for node_id, node in list(self.nodes.items()):
            if node.type != "decision":
                continue
            matches = list(adr_dir.glob(f"{node.source_id}-*.md")) or list(adr_dir.glob(f"ADR-{node.source_id}-*.md"))
            if not matches:
                continue
            full_text = matches[0].read_text(encoding="utf-8", errors="replace")
            mentioned = set(_FILE_MENTION_RE.findall(full_text))
            for path in mentioned:
                file_id = f"file:{path}"
                if file_id in self.nodes:
                    self._add_edge(node_id, file_id, "mentions",
                                   f"المسار '{path}' مذكور حرفياً في النص الكامل لملف {matches[0].name}")

        # Deployment -> runs -> File: مطابقة نصية فعلية لمرجع src.app:app / src/app.py
        for filename, platform in [("Procfile", "heroku_dokku"), ("render.yaml", "render"), ("railway.json", "railway")]:
            f = path_service.root / filename
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            if "src.app" in text or "src/app.py" in text:
                self._add_edge(f"deployment:{platform}", app_file_id, "runs",
                               f"'{filename}' يذكر src.app:app نصياً")

        # Project -> contains -> File (لكل ملف حقيقي مُكتشَف)
        for rel in real_files:
            self._add_edge(project_id, f"file:{rel}", "contains", "ملف موجود فعلياً تحت src/")

        # Project -> decided_by -> Decision (كل ADR يخص المستودع كوحدة واحدة)
        for node_id, node in list(self.nodes.items()):
            if node.type == "decision":
                self._add_edge(project_id, node_id, "decided_by", "كل ADR في docs/adr/ يخص هذا المستودع")

        # Project -> deployed_as -> Deployment
        for node_id, node in list(self.nodes.items()):
            if node.type == "deployment":
                self._add_edge(project_id, node_id, "deployed_as", f"ملف {node.source_id} موجود في جذر المستودع")

        # Capability -> depends_on -> Provider: لا علاقة حقيقية مكتشَفة حالياً
        # (لا كود يربط capability files/git بأي provider LLM فعلياً) - نُسجِّل
        # هذا صراحة بدل السكوت.
        self.not_available.append(
            "capability_depends_on_provider: لا استدعاء حقيقي بين أي capability "
            "مسجَّلة (files/git/terminal/...) وأي provider LLM موجود في الكود حالياً"
        )

        # API -> uses -> Capability: لا استدعاء حقيقي حالياً (routes لا تستدعي
        # CapabilityRegistry مباشرة بعد) - يُسجَّل صراحة، لا يُخترَع
        self.not_available.append(
            "api_uses_capability: لا route في src/app.py يستدعي CapabilityRegistry "
            "مباشرة حالياً - Phase 5/6 لم يُوصَلا بمسار /api/build الحي (موثَّق في ADR-013 وCHANGELOG.md)"
        )

        # Failure nodes: لا نظام تتبع أعطال موجود إطلاقاً
        self.not_available.append("failure: لا نظام تتبع أعطال (Failure Memory) موجود في المستودع حالياً")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build(self) -> "KnowledgeGraph":
        self.nodes = {}
        self.edges = []
        self.not_available = []

        project_id = self._extract_project_root()
        self._extract_decisions()
        self._extract_capabilities()
        self._extract_providers()
        api_results = self._extract_apis()
        test_results = self._extract_tests()
        real_files = self._extract_files()
        self._extract_deployments()

        self._derive_edges(project_id, api_results, test_results, real_files)
        return self

    def to_dict(self) -> Dict:
        return {
            "nodes": {nid: asdict(n) for nid, n in self.nodes.items()},
            "edges": [asdict(e) for e in self.edges],
            "not_available": self.not_available,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
        }

    def persist(self) -> None:
        path_service.write(GRAPH_FILE, json.dumps(self.to_dict(), ensure_ascii=False, indent=2))

    # علاقات "عضوية/تنظيمية" (project hub) تُستبعَد من تحليل الأثر عمداً:
    # كل ADR وكل ملف متصل بعقدة project الواحدة، فلو دخلت ضمن BFS يصبح كل
    # شيء "متأثراً" بكل شيء خلال قفزتين - نتيجة مضلِّلة بالضبط كما حذّر
    # التوجيه. علاقات الأثر الحقيقي فقط: mentions/exposes/verifies/runs.
    _IMPACT_RELEVANT_RELATIONSHIPS = {"mentions", "exposes", "verifies", "runs"}

    def impact_analysis(self, node_id: str, max_depth: int = 4) -> Dict:
        """يتتبّع فقط العلاقات ذات الدلالة السببية (mentions/exposes/verifies/
        runs) - لا يعبر عقدة project المركزية (عضوية تنظيمية، لا تأثير سببي)،
        لتفادي نتيجة "كل شيء يؤثر في كل شيء" غير الحقيقية."""
        if node_id not in self.nodes:
            return {"node_id": node_id, "found": False, "reason": "لا توجد عقدة بهذا المعرّف في الرسم الحالي"}

        relevant_edges = [e for e in self.edges if e.relationship in self._IMPACT_RELEVANT_RELATIONSHIPS]

        visited = {node_id}
        frontier = {node_id}
        by_type: Dict[str, List[Dict]] = {}
        edges_used: List[Dict] = []

        for _ in range(max_depth):
            next_frontier = set()
            for e in relevant_edges:
                if e.source in frontier and e.target not in visited:
                    next_frontier.add(e.target)
                    edges_used.append(asdict(e))
                elif e.target in frontier and e.source not in visited:
                    next_frontier.add(e.source)
                    edges_used.append(asdict(e))
            if not next_frontier:
                break
            visited |= next_frontier
            frontier = next_frontier

        visited.discard(node_id)
        for nid in visited:
            n = self.nodes[nid]
            by_type.setdefault(n.type, []).append(asdict(n))

        return {
            "node_id": node_id,
            "found": True,
            "root": asdict(self.nodes[node_id]),
            "affected_by_type": by_type,
            "total_affected": len(visited),
            "edges_used": edges_used,
        }


def build_and_persist_graph() -> Dict:
    kg = KnowledgeGraph().build()
    kg.persist()
    return kg.to_dict()


def get_impact_analysis(node_id: str) -> Dict:
    kg = KnowledgeGraph().build()
    return kg.impact_analysis(node_id)
