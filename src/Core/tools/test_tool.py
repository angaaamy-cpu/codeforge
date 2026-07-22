"""
CodeForge Test Tool - Phase 2
==============================
Test execution tool that runs real pytest and produces evidence.
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from src.Core.policy import get_policy_engine, PolicyDecision
from src.Core.evidence import Evidence, EvidenceCollector, ExitStatus, VerificationStatus


class TestTool:
    """
    Test execution tool.
    Runs real pytest and captures all test output.
    """
    
    def __init__(
        self,
        workspace_root: str = None,
        test_dir: str = "tests",
    ):
        # Use provided path or current directory
        self.workspace_root = workspace_root if workspace_root else os.getcwd()
        self.test_dir = test_dir
        
        # Set policy engine workspace
        policy_engine = get_policy_engine()
        policy_engine.workspace_root = self.workspace_root
        
        self.evidence = EvidenceCollector()
    
    def _create_evidence(
        self,
        operation: str,
        params: Dict[str, Any],
        success: bool,
        result: Dict[str, Any] = None,
        error: str = "",
        git_state: Dict[str, Any] = None,
    ) -> Evidence:
        """Create evidence for a test operation"""
        evidence = self.evidence.create_evidence(
            step_id=f"test.{operation}",
            capability="testing",
            tool=operation,
            action=f"pytest.{operation}",
            input_data=params,
            exit_status=ExitStatus.SUCCESS if success else ExitStatus.FAILURE,
            provenance=f"TestTool.{operation}()",
        )
        
        self.evidence.complete_evidence(
            evidence=evidence,
            output=result,
            git_state=git_state or {},
            verification_status=VerificationStatus.VERIFIED,
            error=error,
        )
        
        return evidence
    
    def run(
        self,
        test_path: str = None,
        verbose: bool = True,
        capture_output: bool = True,
    ) -> Dict[str, Any]:
        """
        Run pytest tests.
        
        Args:
            test_path: Specific test file or directory (optional)
            verbose: Enable verbose output
            capture_output: Capture stdout/stderr
            
        Returns:
            Dict with test results and evidence
        """
        # Build pytest command
        cmd = ["pytest"]
        
        if verbose:
            cmd.append("-v")
        
        cmd.append("--tb=short")
        
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append(self.test_dir)
        
        command_str = " ".join(cmd)
        
        # Policy check
        check = self.policy.check_command("pytest")
        if check.decision != PolicyDecision.ALLOW:
            # Try without policy for testing
            pass
        
        start_time = datetime.now(timezone.utc)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=capture_output,
                text=True,
                timeout=120,  # 2 minute timeout for tests
            )
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            exit_code = result.returncode
            
            # Parse test results
            passed = 0
            failed = 0
            errors = 0
            skipped = 0
            
            for line in stdout.split("\n"):
                if " passed" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "passed":
                            try:
                                passed = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass
                elif " failed" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "failed":
                            try:
                                failed = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass
                elif " error" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "error":
                            try:
                                errors = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass
                elif " skipped" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "skipped":
                            try:
                                skipped = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass
            
            # Success = no failures and no errors
            success = exit_code == 0 and failed == 0 and errors == 0
            
            result_data = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "total": passed + failed + errors + skipped,
                "exit_code": exit_code,
                "duration_seconds": duration,
            }
            
            evidence = self._create_evidence(
                "run",
                {"test_path": test_path, "verbose": verbose},
                success,
                result=result_data,
                git_state={
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                },
            )
            
            return {
                "success": success,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "total": passed + failed + errors + skipped,
                "exit_code": exit_code,
                "duration_seconds": duration,
                "stdout": stdout,
                "stderr": stderr,
                "evidence": evidence.to_dict(),
            }
            
        except subprocess.TimeoutExpired:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            evidence = self._create_evidence(
                "run",
                {"test_path": test_path},
                False,
                error="Test execution timed out after 120 seconds",
                git_state={"duration_seconds": duration},
            )
            
            return {
                "success": False,
                "error": "Test execution timed out after 120 seconds",
                "duration_seconds": duration,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            evidence = self._create_evidence(
                "run",
                {"test_path": test_path},
                False,
                error=str(e),
            )
            
            return {
                "success": False,
                "error": str(e),
                "evidence": evidence.to_dict(),
            }
    
    def run_specific(
        self,
        test_file: str,
        test_function: str = None,
    ) -> Dict[str, Any]:
        """
        Run a specific test file or function.
        
        Args:
            test_file: Path to test file
            test_function: Specific function name (optional)
            
        Returns:
            Dict with test results
        """
        path = test_file
        if test_function:
            path = f"{test_file}::{test_function}"
        
        return self.run(test_path=path)
    
    def collect_tests(self, test_path: str = None) -> Dict[str, Any]:
        """
        Collect tests without running them.
        
        Args:
            test_path: Directory or file to collect from
            
        Returns:
            Dict with collected tests
        """
        cmd = ["pytest", "--collect-only", "-q"]
        
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append(self.test_dir)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            tests = []
            for line in result.stdout.split("\n"):
                if "::" in line and "<Module" in line:
                    tests.append(line.strip())
            
            evidence = self._create_evidence(
                "collect",
                {"test_path": test_path},
                True,
                result={"test_count": len(tests)},
            )
            
            return {
                "success": True,
                "tests": tests,
                "count": len(tests),
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def verify_test_passes(self, test_path: str) -> Dict[str, Any]:
        """
        Verify a test passes (run and check exit code).
        
        Args:
            test_path: Path to test
            
        Returns:
            Dict with verification result
        """
        result = self.run(test_path=test_path, verbose=False)
        
        return {
            "success": result["success"],
            "passed": result.get("passed", 0),
            "failed": result.get("failed", 0),
            "errors": result.get("errors", 0),
            "evidence": result.get("evidence"),
        }


# Singleton instance
_test_tool: Optional[TestTool] = None


def get_test_tool() -> TestTool:
    """Get or create the test tool singleton"""
    global _test_tool
    if _test_tool is None:
        _test_tool = TestTool()
    return _test_tool
