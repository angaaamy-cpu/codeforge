# CodeForge X.1 - Regression Tests
==================================

**Date**: 2026-07-17
**Tests**: 19 tests

---

## Overview

This document describes the regression tests for CodeForge X.1. These tests ensure that critical functionality continues to work after changes.

---

## Running Tests

### Run All Tests
```bash
cd /workspace/project/codeforge
python -m pytest tests/test_agent_os.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_agent_os.py::TestPathService -v
```

### Run Single Test
```bash
python -m pytest tests/test_agent_os.py::TestPathService::test_read_write -v
```

### With Coverage
```bash
python -m pytest tests/test_agent_os.py --cov=src --cov-report=term-missing
```

---

## Test Categories

### 1. PathService Tests (4 tests)

Tests for `src/path_service.py`

| Test | Description |
|------|-------------|
| test_path_resolution | Path resolution works correctly |
| test_read_write | File read/write operations |
| test_is_within_root | Security check for paths |
| test_directory_operations | Directory creation and deletion |

### 2. WorkspaceManager Tests (2 tests)

Tests for `src/Core/workspace.py`

| Test | Description |
|------|-------------|
| test_create_workspace | Workspace creation |
| test_list_workspaces | Workspace listing |

### 3. ModelProvider Tests (3 tests)

Tests for `src/model_provider/`

| Test | Description |
|------|-------------|
| test_mock_provider | Mock provider basic functionality |
| test_provider_registry | Provider registration and selection |
| test_pattern_matching | Pattern-based response matching |

### 4. CapabilityRequirements Tests (3 tests)

Tests for `src/model_provider/capability_requirements.py`

| Test | Description |
|------|-------------|
| test_direct_execution | Direct execution capabilities |
| test_llm_required | LLM-dependent capabilities |
| test_git_operations | Git operation requirements |

### 5. EventBus Tests (1 test)

Tests for `src/Core/event_bus.py`

| Test | Description |
|------|-------------|
| test_emit_event | Event emission and handling |

### 6. Diagnostics Tests (1 test)

Tests for `src/diagnostics.py`

| Test | Description |
|------|-------------|
| test_run_all | All diagnostic checks pass |

### 7. ProjectManager Tests (1 test)

Tests for `src/project_manager.py`

| Test | Description |
|------|-------------|
| test_create_project_direct | Project creation without LLM |

### 8. SecretsManager Tests (2 tests)

Tests for `src/Core/secrets.py`

| Test | Description |
|------|-------------|
| test_add_get_secret | Adding and retrieving secrets |
| test_list_secrets | Listing secrets |

### 9. Integration Tests (2 tests)

Full workflow tests

| Test | Description |
|------|-------------|
| test_no_llm_direct_execution | Tasks without LLM work directly |
| test_mock_provider_full_cycle | Full cycle with Mock Provider |

---

## Test Execution Order

Tests are independent and can run in any order. Each test:
1. Sets up its required state
2. Executes the test
3. Verifies the result
4. Cleans up (where applicable)

---

## Expected Results

### Success Criteria
```
19 passed ✅
```

### Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| ModuleNotFoundError | Missing dependency | pip install -r requirements.txt |
| FileNotFoundError | Path resolution issue | Check WORKSPACE_ROOT |
| AssertionError | Logic error | Review test and code |

---

## Adding New Tests

### Template
```python
class TestNewFeature:
    def test_feature_name(self):
        """Description of what is tested"""
        # Arrange
        ...
        
        # Act
        result = do_something()
        
        # Assert
        assert result == expected
```

### Guidelines
1. One test class per module
2. One test method per function/feature
3. Use descriptive names
4. Include docstrings
5. Clean up after tests

---

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run tests
  run: python -m pytest tests/test_agent_os.py -v
```

### Pre-commit Hook
```bash
#!/bin/bash
python -m pytest tests/test_agent_os.py -q || exit 1
```

---

## Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| src/path_service.py | 100% | 100% |
| src/project_manager.py | 80% | 90% |
| src/model_provider/ | 90% | 95% |
| src/Core/ | 70% | 85% |

---

_Last updated: 2026-07-17_
