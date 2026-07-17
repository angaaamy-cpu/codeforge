"""
CodeForge Agent OS - Integration Tests
======================================
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPathService:
    """اختبارات Path Service"""
    
    def test_path_resolution(self):
        from src.path_service import PathService
        
        ps = PathService()
        
        # Check root
        assert ps.root.exists()
        
        # Resolve path
        resolved = ps.resolve("README.md")
        assert resolved.is_absolute()
    
    def test_read_write(self):
        from src.path_service import PathService
        
        ps = PathService()
        
        # Create temp file
        test_file = "test_integration.txt"
        content = "Hello, World!"
        
        # Write
        ps.write(test_file, content)
        
        # Read
        assert ps.exists(test_file)
        assert ps.read(test_file) == content
        
        # Clean up
        ps.delete(test_file)
    
    def test_is_within_root(self):
        from src.path_service import PathService
        
        ps = PathService()
        
        # Normal path should be within root
        assert ps.is_within_root("README.md")
        
        # Absolute path outside root should fail
        assert not ps.is_within_root("/etc/passwd")
    
    def test_directory_operations(self):
        from src.path_service import PathService
        
        ps = PathService()
        
        # Create directory
        test_dir = "test_dir_integration"
        ps.mkdir(test_dir)
        
        assert ps.is_dir(test_dir)
        
        # Create file in directory
        ps.write(f"{test_dir}/test.txt", "content")
        assert ps.exists(f"{test_dir}/test.txt")
        
        # Clean up
        ps.delete(test_dir)


class TestWorkspaceManager:
    """اختبارات Workspace Manager"""
    
    def test_create_workspace(self):
        from src.Core.workspace import WorkspaceManager
        
        # Create new manager
        wm = WorkspaceManager()
        
        # Create workspace
        meta = wm.create("test-workspace", "Test description")
        
        assert meta.name == "test-workspace"
        assert meta.description == "Test description"
        assert meta.status == "active"
        
        # Clean up
        wm.delete("test-workspace")
    
    def test_list_workspaces(self):
        from src.Core.workspace import WorkspaceManager
        
        wm = WorkspaceManager()
        
        # Create
        meta = wm.create("test-workspace-2")
        
        # List
        workspaces = wm.list_all()
        names = [w.name for w in workspaces]
        assert "test-workspace-2" in names
        
        # Clean up
        wm.delete("test-workspace-2")


class TestModelProvider:
    """اختبارات Model Provider"""
    
    def test_mock_provider(self):
        from src.model_provider import mock_provider
        
        # Should be configured
        assert mock_provider.configured
        
        # Generate response
        response = mock_provider.generate("Hello")
        assert len(response) > 0
        assert "Hello" in response or "I" in response
    
    def test_provider_registry(self):
        from src.model_provider import provider_registry
        
        # Should have mock
        providers = provider_registry.list_all()
        names = [p["name"] for p in providers]
        assert "mock" in names
        
        # Should have active provider
        assert provider_registry.has_provider()
    
    def test_mock_pattern_matching(self):
        from src.model_provider import mock_provider
        
        # Test pattern matching
        response = mock_provider.generate("create a file")
        assert "file" in response.lower()
        
        response = mock_provider.generate("show me HTML landing page")
        assert "html" in response.lower()


class TestCapabilityRequirements:
    """اختبارات Capability Requirements"""
    
    def test_direct_execution(self):
        from src.model_provider.capability_requirements import capability_requirements
        
        # create_file should not need LLM
        req = capability_requirements.get("create_file")
        assert req is not None
        assert not req.requires_llm
    
    def test_llm_required(self):
        from src.model_provider.capability_requirements import capability_requirements
        
        # generate_code needs LLM
        req = capability_requirements.get("generate_code")
        assert req is not None
        assert req.requires_llm
    
    def test_git_operations(self):
        from src.model_provider.capability_requirements import capability_requirements
        
        # git operations need git
        req = capability_requirements.get("git_commit")
        assert req is not None
        assert req.requires_git


class TestEventBus:
    """اختبارات Event Bus"""
    
    def test_emit_event(self):
        from src.Core.event_bus import EventBus, EventType
        
        eb = EventBus()
        
        received = []
        def handler(event):
            received.append(event)
        
        eb.subscribe(EventType.TASK_STARTED, handler)
        eb.emit(EventType.TASK_STARTED, {"task_id": "test"})
        
        assert len(received) == 1
        assert received[0].data["task_id"] == "test"


class TestDiagnostics:
    """اختبارات System Diagnostics"""
    
    def test_run_all(self):
        from src.diagnostics import run_diagnostics
        
        result = run_diagnostics()
        
        assert result["status"] in ["ok", "warning"]
        assert result["checks"] >= 8
        assert result["errors"] == 0


class TestProjectManager:
    """اختبارات Project Manager (بدون LLM)"""
    
    def test_create_project_direct(self):
        from src.project_manager import create_project, delete_project
        
        # Create
        result = create_project("test-direct-project", "Direct test")
        
        assert result["success"]
        assert result["project"]["name"] == "test-direct-project"
        
        # Clean up
        result = delete_project("test-direct-project")
        assert result["success"]


class TestSecretsManager:
    """اختبارات Secrets Manager"""
    
    def test_add_get_secret(self):
        from src.Core.secrets import SecretsManager
        
        sm = SecretsManager()
        
        # Add
        secret = sm.add("TEST_SECRET", "secret_value", "Test description")
        assert secret.name == "TEST_SECRET"
        
        # Get value
        value = sm.get_value("TEST_SECRET")
        assert value == "secret_value"
        
        # Clean up
        sm.remove("TEST_SECRET")
    
    def test_list_secrets(self):
        from src.Core.secrets import SecretsManager
        
        sm = SecretsManager()
        
        # Add
        sm.add("LIST_TEST", "value")
        
        # List
        metas = sm.list_all()
        names = [m.name for m in metas]
        assert "LIST_TEST" in names
        
        # Clean up
        sm.remove("LIST_TEST")


def test_no_llm_direct_execution():
    """مهمة بدون LLM = تنفيذ مباشر"""
    from src.model_provider.capability_requirements import capability_requirements
    
    # Check direct execution capabilities
    direct = capability_requirements.list_direct_execution()
    assert len(direct) > 0
    
    # These should work without LLM
    assert capability_requirements.get("create_file") is not None
    assert capability_requirements.get("list_projects") is not None


def test_mock_provider_full_cycle():
    """دورة كاملة مع Mock Provider"""
    from src.model_provider import mock_provider, provider_registry
    
    # Ensure mock is active
    provider_registry.set_active("mock")
    
    # Generate
    response = mock_provider.generate("create a Python function")
    assert "def" in response or "python" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
