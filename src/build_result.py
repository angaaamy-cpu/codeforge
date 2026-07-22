"""
CodeForge Build Result - Phase 8
=================================
كائنات نتيجة البناء
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime


@dataclass
class BuildStep:
    """خطوة في عملية البناء"""
    step: int
    name: str
    status: str  # success / failed / running / skipped
    error: Optional[str] = None
    duration_seconds: float = 0.0
    details: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BuildResult:
    """نتيجة البناء الكاملة"""
    status: str  # success / failed
    project_name: str
    project_path: str
    files: List[str] = field(default_factory=list)
    files_count: int = 0
    run_command: str = ""
    url: str = ""
    reports: List[str] = field(default_factory=list)
    steps: List[BuildStep] = field(default_factory=list)
    duration_seconds: float = 0.0
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """تحويل إلى dictionary"""
        data = asdict(self)
        data['steps'] = [s.to_dict() for s in self.steps]
        return data
    
    def display(self):
        """يعرض الملخص النهائي للمستخدم"""
        print(f"""
╔══════════════════════════════════════════════════════════╗
║                     ✅ تم بناء المشروع                     ║
╚══════════════════════════════════════════════════════════╝

📁 المشروع: {self.project_name}
📍 المسار: {self.project_path}
📄 الملفات: {self.files_count} ملف
⏱️  المدة: {self.duration_seconds:.1f} ثانية

🚀 للتشغيل:
   cd {self.project_path}
   {self.run_command}

🌐 افتح: {self.url}

📊 التقارير:""")
        for report in self.reports:
            print(f"   - {report}")
        
        print("═" * 60)
    
    @staticmethod
    def from_dict(data: dict) -> 'BuildResult':
        """إنشاء من dictionary"""
        steps = [BuildStep(**s) for s in data.get('steps', [])]
        return BuildResult(
            **data,
            steps=steps
        )
