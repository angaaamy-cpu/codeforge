"""
Test Tool - Phase 2: Execution Engine Bridge
============================================

Real pytest execution with detailed reporting.
"""

import os
import subprocess
import time
import json
from typing import Any, Dict, List, Optional

from src.Core.evidence import Evidence, EvidenceCollector, ExitStatus, VerificationStatus


class TestTool:
    """
    Real pytest execution tool.
    
    Executes tests with detailed evidence collection.
    """
    
    def __init__(self, workspace_root: str = None):
        """
        Initialize TestTool.
        
        Args:
            workspace_root: Root directory for test execution.
        """
        self.workspace_root = workspace_root or os.getcwd()
        self.evidence = EvidenceCollector()
    
    def _create_evidence(
        self,
        command: str,
        success: bool,
        exit_code: int,
        output: Dict[str, Any] = None,
        error: str = "",
        duration: float = 0.0,
    ) -> Evidence:
        """Create evidence for test execution"""
        evidence = self.evidence.create_evidence(
            step_id="test.execute",
            capability="test",
            tool="execute",
            action="test.execute",
            input_data={"command": command, "workspace": self.workspace_root},
            exit_status=ExitStatus.SUCCESS if success else ExitStatus.FAILURE,
            provenance="TestTool.execute()",
        )
        
        self.evidence.complete_evidence(
            evidence=evidence,
            output=output or {},
            verification_status=VerificationStatus.VERIFIED,
            error=error,
            duration_seconds=duration,
        )
        
        return evidence
    
    def run_pytest(
        self,
        test_path: str = None,
        verbose: bool = True,
        capture: str = "no",
        timeout: int = 120,
    ) -> Dict[str, Any]:
        """
        Run pytest tests.
        
        Args:
            test_path: Path to test file or directory
            verbose: Enable verbose output
            capture: Capture mode (no, yes, log)
            timeout: Timeout in seconds
            
        Returns:
            Dict with success, exit_code, output, tests_run, tests_failed, tests_passed, evidence
        """
        test_path = test_path or self.workspace_root
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        if verbose:
            cmd.append("-v")
        
        if capture == "no":
            cmd.append("-s")
        
        cmd.append("--tb=short")
        cmd.append("--json-report")
        cmd.append("--json-report-file=/tmp/pytest_report.json")
        
        cmd.append(test_path)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                " ".join(cmd),
                shell=True,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Parse output for test results
            output_lines = result.stdout.split("\n")
            tests_run = 0
            tests_passed = 0
            tests_failed = 0
            
            for line in output_lines:
                if "passed" in line:
                    # Extract numbers from pytest output like "5 passed"
                    import re
                    match = re.search(r"(\d+)\s+passed", line)
                    if match:
                        tests_passed = int(match.group(1))
                        tests_run += tests_passed
                elif "failed" in line:
                    match = re.search(r"(\d+)\s+failed", line)
                    if match:
                        tests_failed = int(match.group(1))
                        tests_run += tests_failed
                elif "passed" in line and "failed" not in line:
                    match = re.search(r"(\d+)\s+passed", line)
                    if match:
                        tests_passed = int(match.group(1))
                        tests_run = tests_passed
            
            output = {
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "exit_code": result.returncode,
                "duration_seconds": duration,
            }
            
            evidence = self._create_evidence(
                command=" ".join(cmd),
                success=success,
                exit_code=result.returncode,
                output=output,
                error=result.stderr if not success else "",
                duration=duration,
            )
            
            return {
                "success": success,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "duration": duration,
                "evidence": evidence.to_dict(),
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            evidence = self._create_evidence(
                command=" ".join(cmd),
                success=False,
                exit_code=-1,
                output={"timeout": timeout},
                error=f"Tests timed out after {timeout} seconds",
                duration=duration,
            )
            
            return {
                "success": False,
                "exit_code": -1,
                "output": "",
                "errors": f"Tests timed out after {timeout} seconds",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "duration": duration,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            duration = time.time() - start_time
            evidence = self._create_evidence(
                command=" ".join(cmd),
                success=False,
                exit_code=-1,
                error=str(e),
                duration=duration,
            )
            
            return {
                "success": False,
                "exit_code": -1,
                "output": "",
                "errors": str(e),
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "duration": duration,
                "evidence": evidence.to_dict(),
            }
