"""
Phase 3: Repository Intelligence Engine
========================================
Canonical Owner: Repository Intelligence Engine
Source: Filesystem + Dependency Index + Project Model
Target: M3

المكونات:
1. Project Onboarding Engine - Clone→Detect→Index→Understand→Build→Test→Run
2. Repository Discovery + Scale + Generated Artifacts
3. Incremental Indexing
4. Ownership Model (Evidence-based) + Project Health Model
5. Project Model + Dependency Graph + Impact (Repository-Level)

GATE: مشروع حقيقي - اكتشف الخدمات، ارسم dependency graph، حدد entry points،
      اعرف repository-level impact، اكتشف scale، أنتج Health Score + 
      Onboarding Report + Confidence %
"""

import ast
import os
import re
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict

from src.path_service import path_service


@dataclass
class FileNode:
    """ملف في المستودع"""
    path: str
    type: str  # source, generated, test, config, docs, build, dependency, temp
    language: Optional[str] = None
    lines: int = 0
    size: int = 0
    modified: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


@dataclass
class ServiceNode:
    """خدمة في المستودع"""
    name: str
    path: str
    files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)


@dataclass
class DependencyEdge:
    """تبعية بين ملفات/خدمات"""
    source: str
    target: str
    type: str  # import, call, inherits, uses, references
    line: Optional[int] = None


@dataclass
class ProjectHealth:
    """صحة المشروع"""
    overall: float = 0.0
    architecture: float = 0.0
    dependency: float = 0.0
    test: float = 0.0
    documentation: float = 0.0
    security: float = 0.0
    operational: float = 0.0


@dataclass
class OnboardingReport:
    """تقرير بدء المشروع"""
    project_path: str
    understanding_confidence: float = 0.0
    known_entry_points: List[str] = field(default_factory=list)
    unknown_modules: List[str] = field(default_factory=list)
    services_discovered: int = 0
    files_indexed: int = 0
    dependencies_found: int = 0
    scale_classification: str = "unknown"  # tiny, small, medium, large, monorepo
    health_score: Optional[ProjectHealth] = None
    generated_at: str = ""
    issues: List[str] = field(default_factory=list)


class RepositoryIntelligence:
    """
    محرك ذكاء المستودع
    """
    
    # أنماط الملفات حسب النوع
    SOURCE_PATTERNS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.go': 'go',
        '.java': 'java',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.rs': 'rust',
        '.php': 'php',
    }
    
    GENERATED_PATTERNS = {
        '__pycache__', '.pyc', '.pyo', 'node_modules',
        'dist', 'build', 'target', '.next', '.nuxt',
        'package-lock.json', 'yarn.lock', 'Pipfile.lock',
        '.tox', '.venv', 'venv', 'env',
    }
    
    TEST_PATTERNS = {
        'test_', '_test.', 'tests/', 'spec_', '_spec.',
        'Test.py', 'Tests.py',
    }
    
    CONFIG_PATTERNS = {
        'package.json', 'pyproject.toml', 'setup.py', 'setup.cfg',
        'requirements.txt', 'Gemfile', 'Cargo.toml', 'go.mod',
        '.gitignore', '.dockerignore', 'Dockerfile', 'docker-compose',
        '.env', '.env.example', 'config.py', 'settings.py',
    }
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or path_service.get_workspace_root()
        self.index: Dict[str, FileNode] = {}
        self.services: Dict[str, ServiceNode] = {}
        self.dependencies: List[DependencyEdge] = []
        self.ownership: Dict[str, str] = {}  # path -> owner
        self.last_index_time: Optional[str] = None
        
    def discover_repository(self, repo_path: Optional[str] = None) -> OnboardingReport:
        """
        اكتشاف المستودع وإنتاج تقرير البدء
        GATE: مشروع حقيقي - اكتشف الخدمات، dependency graph، entry points
        """
        repo_path = repo_path or self.workspace_root
        report = OnboardingReport(project_path=repo_path)
        report.generated_at = datetime.now(timezone.utc).isoformat()
        
        # 1. اكتشاف الهيكل
        files = self._discover_files(repo_path)
        report.files_indexed = len(files)
        
        # 2. تصنيف الملفات
        self._classify_files(files)
        
        # 3. استخراج التبعيات
        self._extract_dependencies(files)
        report.dependencies_found = len(self.dependencies)
        
        # 4. اكتشاف الخدمات
        self._discover_services()
        report.services_discovered = len(self.services)
        
        # 5. تحديد entry points
        self._identify_entry_points()
        
        # 6. حساب الصحة
        health = self._calculate_health()
        report.health_score = health
        
        # 7. تصنيف الحجم
        report.scale_classification = self._classify_scale(files)
        
        # 8. حساب الثقة
        report.understanding_confidence = self._calculate_confidence(report)
        
        # 9. تحديد unknown modules
        report.unknown_modules = self._find_unknown_modules()
        
        return report
    
    def _discover_files(self, repo_path: str) -> List[Path]:
        """اكتشاف جميع الملفات في المستودع"""
        files = []
        repo = Path(repo_path)
        
        for root, dirs, filenames in os.walk(repo):
            # تجاهل المجلدات المولدة
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            
            for filename in filenames:
                filepath = Path(root) / filename
                rel_path = str(filepath.relative_to(repo))
                files.append(filepath)
                
        return files
    
    def _classify_files(self, files: List[Path]) -> None:
        """تصنيف الملفات حسب النوع"""
        for filepath in files:
            rel_path = str(filepath.relative_to(self.workspace_root))
            
            # تحديد النوع
            file_type = self._determine_file_type(rel_path, filepath)
            
            # حساب الحجم والخطوط
            try:
                size = filepath.stat().st_size
                lines = len(filepath.read_text(errors='ignore').splitlines())
            except:
                size = 0
                lines = 0
            
            # استخراج imports
            imports = []
            if filepath.suffix == '.py':
                imports = self._extract_python_imports(filepath)
            
            node = FileNode(
                path=rel_path,
                type=file_type,
                language=self.SOURCE_PATTERNS.get(filepath.suffix),
                lines=lines,
                size=size,
                imports=imports
            )
            self.index[rel_path] = node
    
    def _determine_file_type(self, rel_path: str, filepath: Path) -> str:
        """تحديد نوع الملف"""
        name = filepath.name
        suffix = filepath.suffix
        
        # اختبار
        if any(p in name for p in self.TEST_PATTERNS):
            return 'test'
        
        # تكوين
        if name in self.CONFIG_PATTERNS or any(p in rel_path for p in ['config/', '.config']):
            return 'config'
        
        # مولد
        if any(p in rel_path for p in self.GENERATED_PATTERNS):
            return 'generated'
        
        # وثائق
        if suffix in ['.md', '.rst', '.txt', '.pdf', '.doc']:
            return 'docs'
        
        # بناء
        if suffix in ['.lock', '.json', '.yaml', '.yml'] and 'package' in name:
            return 'build'
        
        # مصدر
        if suffix in self.SOURCE_PATTERNS:
            return 'source'
        
        # مؤقت
        if name.startswith('.') or name.endswith('.tmp'):
            return 'temp'
        
        return 'unknown'
    
    def _extract_python_imports(self, filepath: Path) -> List[str]:
        """استخراج imports من ملف Python"""
        imports = []
        try:
            content = filepath.read_text(errors='ignore')
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return imports
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            pass
        return imports
    
    def _extract_dependencies(self, files: List[Path]) -> None:
        """استخراج التبعيات من الملفات"""
        for filepath in files:
            rel_path = str(filepath.relative_to(self.workspace_root))
            
            if filepath.suffix == '.py':
                try:
                    content = filepath.read_text(errors='ignore')
                    try:
                        tree = ast.parse(content)
                    except SyntaxError:
                        continue
                    
                    for node in ast.walk(tree):
                        # استيراد
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self.dependencies.append(DependencyEdge(
                                    source=rel_path,
                                    target=alias.name,
                                    type='import'
                                ))
                        
                        # استيراد من
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self.dependencies.append(DependencyEdge(
                                    source=rel_path,
                                    target=node.module,
                                    type='import_from'
                                ))
                except:
                    pass
    
    def _discover_services(self) -> None:
        """اكتشاف الخدمات في المستودع"""
        # تجميع الملفات حسب المجلد الجذر
        services_by_dir = defaultdict(list)
        
        for path, node in self.index.items():
            if node.type == 'source':
                parts = path.split('/')
                if len(parts) >= 2:
                    # افترض أن المجلد الأول هو اسم الخدمة
                    service_dir = parts[0]
                    if service_dir not in ['src', 'lib', 'app', 'core']:
                        services_by_dir[service_dir].append(path)
        
        # إذا لم نجد خدمات، استخدم src كخدمة واحدة
        if not services_by_dir:
            src_files = [p for p, n in self.index.items() 
                        if n.type == 'source' and p.startswith('src/')]
            if src_files:
                services_by_dir['src'] = src_files
        
        # إنشاء ServiceNodes
        for service_name, files in services_by_dir.items():
            service = ServiceNode(
                name=service_name,
                path=service_name,
                files=files
            )
            self.services[service_name] = service
    
    def _identify_entry_points(self) -> None:
        """تحديد نقاط الدخول"""
        for path, node in self.index.items():
            if node.type == 'source':
                # __main__.py
                if '__main__.py' in path:
                    self._add_entry_point(path)
                
                # app.py, main.py, server.py
                name = Path(path).stem.lower()
                if name in ['app', 'main', 'server', 'run', 'index']:
                    self._add_entry_point(path)
                
                # app/__init__.py أو routes
                if '__init__.py' in path and 'app' in path.lower():
                    self._add_entry_point(path)
    
    def _add_entry_point(self, path: str) -> None:
        """إضافة نقطة دخول"""
        for service in self.services.values():
            if any(path.startswith(f) for f in service.files):
                if path not in service.entry_points:
                    service.entry_points.append(path)
                break
    
    def _calculate_health(self) -> ProjectHealth:
        """حساب صحة المشروع"""
        health = ProjectHealth()
        
        # حساب كل قسم
        total_files = len([n for n in self.index.values() if n.type == 'source'])
        test_files = len([n for n in self.index.values() if n.type == 'test'])
        config_files = len([n for n in self.index.values() if n.type == 'config'])
        doc_files = len([n for n in self.index.values() if n.type == 'docs'])
        
        # صحة الاختبار
        if total_files > 0:
            health.test = min(test_files / total_files * 100, 100)
        else:
            health.test = 0
        
        # صحة التوثيق
        if total_files > 0:
            health.documentation = min(doc_files / total_files * 50, 100)
        else:
            health.documentation = 0
        
        # صحة التكوين
        health.operational = min(config_files * 20, 100) if config_files > 0 else 50
        
        # صحة الاعتماديات (تحقق من التبعيات المفقودة)
        internal_deps = len([d for d in self.dependencies if not d.target.startswith('.')])
        external_deps = len([d for d in self.dependencies if d.target.startswith('.')])
        health.dependency = 100 if internal_deps > 0 else 50
        
        # الصحة العامة
        health.overall = (
            health.test * 0.3 +
            health.documentation * 0.2 +
            health.operational * 0.2 +
            health.dependency * 0.3
        )
        
        return health
    
    def _classify_scale(self, files: List[Path]) -> str:
        """تصنيف حجم المشروع"""
        total_files = len(files)
        source_files = len([f for f in files if f.suffix in self.SOURCE_PATTERNS])
        
        if total_files > 10000 or source_files > 5000:
            return 'monorepo'
        elif total_files > 1000 or source_files > 500:
            return 'large'
        elif total_files > 100 or source_files > 50:
            return 'medium'
        elif total_files > 20 or source_files > 10:
            return 'small'
        else:
            return 'tiny'
    
    def _calculate_confidence(self, report: OnboardingReport) -> float:
        """حساب ثقة الفهم"""
        confidence = 0.0
        
        # نسبة الملفات المفهرسة
        if report.files_indexed > 0:
            confidence += 20
        
        # نسبة الخدمات المكتشفة
        if report.services_discovered > 0:
            confidence += 20
        
        # نسبة التبعيات
        if report.dependencies_found > 0:
            confidence += 20
        
        # صحة المشروع
        if report.health_score:
            confidence += report.health_score.overall * 0.4
        
        return min(confidence, 100)
    
    def _find_unknown_modules(self) -> List[str]:
        """العثور على الوحدات غير المعروفة"""
        unknown = []
        
        for path, node in self.index.items():
            if node.type == 'source' and not node.imports:
                unknown.append(path)
        
        return unknown[:10]  # الحد الأقصى 10
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """الحصول على رسم بياني للتبعيات"""
        graph = defaultdict(list)
        
        for edge in self.dependencies:
            if edge.target not in graph[edge.source]:
                graph[edge.source].append(edge.target)
        
        return dict(graph)
    
    def get_impact_analysis(self, file_path: str) -> Dict[str, Any]:
        """تحليل التأثير لملف معين"""
        impact = {
            'file': file_path,
            'affected_by': [],  # ملفات تستورد هذا الملف
            'affects': [],      # ملفات يستوردها هذا الملف
            'services': [],
            'tests': []
        }
        
        # الملفات المتأثرة (تستورد هذا الملف)
        for edge in self.dependencies:
            if edge.target == file_path:
                impact['affected_by'].append(edge.source)
        
        # الملفات المؤثرة (هذا الملف يستوردها)
        if file_path in self.index:
            node = self.index[file_path]
            impact['affects'] = node.imports
        
        # الخدمات المرتبطة
        for service in self.services.values():
            if file_path in service.files:
                impact['services'].append(service.name)
        
        # الاختبارات المرتبطة
        for path, node in self.index.items():
            if node.type == 'test' and file_path in node.imports:
                impact['tests'].append(path)
        
        return impact


# Singleton instance
_repository_intelligence: Optional[RepositoryIntelligence] = None


def get_repository_intelligence(workspace_root: Optional[str] = None) -> RepositoryIntelligence:
    """الحصول على مثيل singleton"""
    global _repository_intelligence
    if _repository_intelligence is None:
        _repository_intelligence = RepositoryIntelligence(workspace_root)
    return _repository_intelligence


def clear_repository_intelligence() -> None:
    """مسح المثيل"""
    global _repository_intelligence
    _repository_intelligence = None
