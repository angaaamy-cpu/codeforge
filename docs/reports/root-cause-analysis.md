# CodeForge X.1 - Root Cause Analysis
=====================================

**Date**: 2026-07-17
**Author**: CTO
**Version**: CodeForge X.1

---

## Executive Summary

This document analyzes all production issues in CodeForge that could cause failures, exceptions, or unexpected behavior. The goal is to make CodeForge work 100% without any LLM API keys.

---

## Issues Found

### 1. Flask Dependency Missing
**Severity**: Critical
**Location**: `src/app.py`

**Problem**: 
```
ModuleNotFoundError: No module named 'flask'
```

**Root Cause**: Flask is not listed in dependencies or not installed.

**Fix**: Already fixed - Flask installed.

---

### 2. Path Handling - Relative Paths in Multiple Locations
**Severity**: High
**Locations**: 
- `src/build_engine.py` line 91, 106, 131, 200, 402, etc.
- `src/pipeline.py` line 378, 420
- `src/storage/docs_storage.py` line 20-26

**Problem**:
```python
# These use relative paths without considering WORKSPACE_ROOT
project_path = Path(PROJECTS_DIR) / name
reports_dir = Path("docs/reports")
```

**Root Cause**: Assumes `cwd` is always the project root. On Railway, the working directory might be different.

**Fix Status**: PathService exists but not consistently used. Need to ensure all modules use the central PathService.

---

### 3. Config Paths Hardcoded
**Severity**: Medium
**Location**: `config/paths.py`

**Problem**:
```python
ROOT_DIR = Path(__file__).parent.parent.absolute()
```

**Root Cause**: This is actually correct, but it's duplicated in PathService.

**Fix Status**: Need to consolidate into single path management.

---

### 4. Storage Uses Relative Paths
**Severity**: High
**Location**: `src/storage/docs_storage.py`

**Problem**:
```python
def __init__(self, docs_dir: str = "docs", projects_dir: str = "projects"):
    self.docs_dir = Path(docs_dir)  # Relative to cwd!
```

**Root Cause**: Default arguments are relative paths.

**Fix Status**: Need to use absolute paths based on ROOT_DIR.

---

### 5. Pipeline Report Creation
**Severity**: Medium
**Location**: `src/pipeline.py` line 378

**Problem**:
```python
reports_dir = Path("docs/reports")
reports_dir.mkdir(exist_ok=True)
```

**Root Cause**: Uses relative path without considering workspace root.

**Fix Status**: Need to use PathService.

---

### 6. Git Manager Hardcoded Paths
**Severity**: Low
**Location**: `src/git_manager.py`

**Problem**: Uses relative paths for git operations.

**Root Cause**: Assumes cwd is project root.

**Fix Status**: Need to use PathService.

---

### 7. Model Provider Not Integrated
**Severity**: High
**Location**: `src/pipeline.py`, `src/build_engine.py`

**Problem**:
- MockProvider exists in `src/model_provider/`
- Not integrated with Pipeline or BuildEngine
- No graceful fallback when LLM unavailable

**Root Cause**: Mock provider was created but not wired into the system.

**Fix Status**: Need to integrate MockProvider into pipeline.

---

### 8. Workspace Directory Confusion
**Severity**: Medium
**Locations**: 
- `config/paths.py` - `WORKSPACE_DIR = ROOT_DIR / "workspace"`
- `src/Core/workspace.py` - uses `workspaces` directory
- `src/storage/docs_storage.py` - uses `projects` directory

**Problem**: Three different "workspace" concepts:
1. `/workspace` - main directory
2. `workspace/` - subdirectory
3. `workspaces/` - for WorkspaceManager

**Root Cause**: Historical naming confusion.

**Fix Status**: Need to clarify and standardize.

---

## Analysis of Path Usage

### Files Using relative_to(), Path.relative_to(), os.path.relpath()

| File | Line | Usage | Risk |
|------|------|-------|------|
| src/build_engine.py | 91, 106, 131, 200, 402, 467, 477, 480 | `Path(PROJECTS_DIR) / name` | High |
| src/build_engine.py | 472 | `file.relative_to(project_path)` | Medium |
| src/pipeline.py | 378 | `Path("docs/reports")` | High |
| src/storage/docs_storage.py | 20-26 | Default args | High |
| src/storage/docs_storage.py | 30-33 | `mkdir` on relative paths | High |

### No Issues Found In:
- `config/paths.py` - Uses `__file__` correctly
- `src/path_service.py` - Well implemented
- `src/diagnostics.py` - Uses PathService

---

## Environment Variables

### Current Usage
```python
# config/settings.py
FLASK_HOST = os.environ.get("HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("PORT", 5000))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
```

### Missing Environment Variables
- `WORKSPACE_ROOT` - Should be used but isn't consistently
- `RAILWAY_ENVIRONMENT` - Should be detected for Railway deployment

---

## Railway Deployment Issues

### Identified Problems

1. **Working Directory**: On Railway, the working directory might not be the project root.

2. **Static Files**: Flask's `static_folder` and `template_folder` use relative paths.

3. **Port**: Already fixed with `os.environ.get("PORT", 5000)`.

---

## Mock Provider Integration Issues

### Current State
```python
# src/model_provider/mock_provider.py - Exists
# src/model_provider/registry.py - Exists
# src/model_provider/__init__.py - Exists
```

### Not Integrated In
- `src/pipeline.py` - Uses agents directly
- `src/build_engine.py` - No AI content generation
- `src/summarizer.py` - Probably requires LLM

---

## Recommendations

### Priority 1: Fix Path Handling
1. Create centralized path configuration
2. Use `WORKSPACE_ROOT` environment variable
3. Ensure all modules use PathService
4. Test on both local and Railway environments

### Priority 2: Integrate Mock Provider
1. Wire MockProvider into Pipeline
2. Create fallback mechanism
3. Add clear error messages when LLM unavailable

### Priority 3: UI Fixes
1. Ensure dashboard shows clear status
2. Add file explorer
3. Add system diagnostics display

### Priority 4: Testing
1. Create regression tests
2. Test on Railway-like environment
3. Test with different working directories

---

## Summary

| Issue | Severity | Status |
|-------|----------|--------|
| Flask dependency | Critical | ✅ Fixed |
| Path handling | High | 🔧 In Progress |
| Storage paths | High | 🔧 In Progress |
| Pipeline paths | Medium | 🔧 In Progress |
| Mock provider integration | High | 🔧 In Progress |
| Workspace confusion | Medium | 📋 Planned |
| Git manager paths | Low | 📋 Planned |

---

## Conclusion

The codebase has a good foundation with PathService already implemented. The main issues are:

1. **Inconsistent path usage** - Not all modules use PathService
2. **Mock provider not integrated** - Exists but not wired in
3. **Environment variable usage** - `WORKSPACE_ROOT` not consistently used

All issues are fixable without modifying the core logic.

---

_Last updated: 2026-07-17_
