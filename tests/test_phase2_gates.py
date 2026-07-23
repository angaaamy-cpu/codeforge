"""
Phase 2 Gate Tests - Execution Engine Bridge Verification
======================================================

This test suite verifies the Phase 2 Execution Engine Bridge implementation.
All gates must pass with REAL execution evidence.
"""

import os
import sys
import time
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.tools.files import FilesTool
from src.Core.tools.git_tool import GitTool
from src.Core.tools.terminal import TerminalTool
from src.Core.tools.test_tool import TestTool


def get_test_workspace():
    """Get a temporary workspace for testing"""
    workspace = tempfile.mkdtemp(prefix="codeforge_phase2_test_")
    
    # Configure git for the workspace
    subprocess.run(["git", "init"], cwd=workspace, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@codeforge.dev"], cwd=workspace, capture_output=True)
    subprocess.run(["git", "config", "user.name", "CodeForge Test"], cwd=workspace, capture_output=True)
    
    # Clear evidence collector to avoid stale evidence
    from src.Core.evidence import evidence_collector
    evidence_collector.clear_evidence()
    
    return workspace


def test_gate_a_hello_world():
    """GATE A: Real Hello World - File → Disk → Git → Commit → Verify"""
    print("\n" + "=" * 60)
    print("GATE A: Hello World Test")
    print("=" * 60)
    
    workspace = get_test_workspace()
    print(f"Workspace: {workspace}")
    
    try:
        files_tool = FilesTool(workspace)
        git_tool = GitTool(workspace)
        
        # Create file on disk
        test_file = Path(workspace) / "hello_world.txt"
        content = "Hello World from Phase 2 Gate A!\n"
        content += f"Timestamp: {time.time()}\n"
        
        result = files_tool.write(str(test_file), content)
        assert result["success"], f"Failed to write file: {result.get('error')}"
        assert result["verified"], "File write not verified"
        print(f"   ✅ File created: {result['path']}")
        
        # Verify file exists
        exists_result = files_tool.exists(str(test_file))
        assert exists_result["exists"], "File does not exist"
        print(f"   ✅ File exists verified")
        
        # Read file content
        read_result = files_tool.read(str(test_file))
        assert read_result["success"], f"Failed to read file"
        assert read_result["content"] == content, "Content mismatch"
        print(f"   ✅ Content verified: {len(read_result['content'])} bytes")
        
        # Git commit
        commit_result = git_tool.commit("Phase 2 GATE A: Hello World test")
        assert commit_result["success"], f"Git commit failed: {commit_result.get('error')}"
        print(f"   ✅ Commit created: {commit_result['commit_hash']}")
        
        # Verify commit
        verify_result = git_tool.verify_commit_exists(commit_result["commit_hash"])
        assert verify_result["exists"], "Commit not found"
        print(f"   ✅ Commit verified in git")
        
        print("\n" + "=" * 60)
        print("GATE A: ✅ PASSED")
        print("=" * 60)
        return True
        
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_gate_c_command_execution():
    """GATE C: Real Command Execution"""
    print("\n" + "=" * 60)
    print("GATE C: Command Execution Test")
    print("=" * 60)
    
    workspace = get_test_workspace()
    
    try:
        terminal = TerminalTool(workspace)
        
        # Test allowed commands
        allowed_commands = [
            "echo 'Hello from Gate C'",
            "pwd",
            "whoami",
            "date",
        ]
        
        for cmd in allowed_commands:
            result = terminal.execute(cmd)
            assert result["success"], f"Command failed: {cmd}"
            assert result["exit_code"] == 0, f"Non-zero exit code: {result['exit_code']}"
            print(f"   ✅ Executed: {cmd[:30]}... -> exit_code={result['exit_code']}")
        
        # Test policy rejection
        forbidden_commands = [
            "rm -rf /",
            "dd if=/dev/zero of=/dev/sda",
        ]
        
        for cmd in forbidden_commands:
            result = terminal.execute(cmd)
            assert not result["success"], f"Forbidden command should be blocked: {cmd}"
            print(f"   ✅ Correctly rejected: {cmd[:30]}...")
        
        print("\n" + "=" * 60)
        print("GATE C: ✅ PASSED")
        print("=" * 60)
        return True
        
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_gate_d_failure_detection():
    """GATE D: Real Failure Detection and Recovery"""
    print("\n" + "=" * 60)
    print("GATE D: Failure Detection Test")
    print("=" * 60)
    
    workspace = get_test_workspace()
    
    try:
        files_tool = FilesTool(workspace)
        
        # Attempt to read non-existent file
        read_result = files_tool.read(f"{workspace}/nonexistent_file.txt")
        assert not read_result["success"], "Should have failed"
        print(f"   ✅ Failure detected: {read_result.get('error')}")
        
        # Verify failure is recorded in evidence
        evidence = read_result.get("evidence", {})
        exit_status = evidence.get("exit_status")
        if hasattr(exit_status, 'value'):
            exit_status = exit_status.value
        assert exit_status == "failure", f"Exit status not failure: {exit_status}"
        print(f"   ✅ Failure recorded in evidence")
        
        # Test recovery
        valid_result = files_tool.write(
            f"{workspace}/recovered_file.txt",
            "Recovery successful"
        )
        assert valid_result["success"], "Recovery failed"
        print(f"   ✅ Recovery successful")
        
        print("\n" + "=" * 60)
        print("GATE D: ✅ PASSED")
        print("=" * 60)
        return True
        
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_gate_e_git_lifecycle():
    """GATE E: Git Change Lifecycle"""
    print("\n" + "=" * 60)
    print("GATE E: Git Lifecycle Test")
    print("=" * 60)
    
    workspace = get_test_workspace()
    
    try:
        git_tool = GitTool(workspace)
        files_tool = FilesTool(workspace)
        
        # Create file change
        test_file = Path(workspace) / "git_lifecycle.txt"
        write_result = files_tool.write(str(test_file), "Git lifecycle test content\n")
        assert write_result["success"], "Failed to write file"
        print(f"   ✅ File created")
        
        # Check git status
        status_result = git_tool.status()
        assert status_result["has_changes"], "No changes detected"
        print(f"   ✅ Git status shows changes")
        
        # Git commit
        commit_result = git_tool.commit("GATE E: Git lifecycle test")
        assert commit_result["success"], f"Commit failed: {commit_result.get('error')}"
        print(f"   ✅ Commit created: {commit_result['commit_hash']}")
        
        # Verify commit hash
        log_result = git_tool.log(limit=1)
        assert log_result["success"], "Failed to get log"
        latest_commit = log_result["commits"][0]
        assert latest_commit["hash"].startswith(commit_result["commit_hash"])
        print(f"   ✅ Commit verified")
        
        print("\n" + "=" * 60)
        print("GATE E: ✅ PASSED")
        print("=" * 60)
        return True
        
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main():
    """Run all Phase 2 gate tests"""
    print("=" * 60)
    print("PHASE 2 GATE TESTS - STARTING")
    print("=" * 60)
    
    results = []
    
    # GATE A: Hello World
    try:
        results.append(("GATE A", test_gate_a_hello_world()))
    except Exception as e:
        print(f"❌ GATE A failed: {e}")
        results.append(("GATE A", False))
    
    # GATE C: Command Execution
    try:
        results.append(("GATE C", test_gate_c_command_execution()))
    except Exception as e:
        print(f"❌ GATE C failed: {e}")
        results.append(("GATE C", False))
    
    # GATE D: Failure Detection
    try:
        results.append(("GATE D", test_gate_d_failure_detection()))
    except Exception as e:
        print(f"❌ GATE D failed: {e}")
        results.append(("GATE D", False))
    
    # GATE E: Git Lifecycle
    try:
        results.append(("GATE E", test_gate_e_git_lifecycle()))
    except Exception as e:
        print(f"❌ GATE E failed: {e}")
        results.append(("GATE E", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("PHASE 2 GATE TESTS - SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 ALL PHASE 2 GATES PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total - passed} GATE(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
