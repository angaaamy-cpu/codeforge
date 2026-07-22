"""
CodeForge Terminal Tool - Phase 2
=================================
Real subprocess execution with policy enforcement.
Every command produces evidence with stdout, stderr, exit code.
"""

import subprocess
import os
import signal
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from src.Core.policy import get_policy_engine, PolicyDecision
from src.Core.evidence import Evidence, EvidenceCollector, ExitStatus, VerificationStatus


class TerminalTool:
    """
    Real subprocess execution tool.
    All commands pass through policy engine and produce real evidence.
    """
    
    def __init__(
        self,
        workspace_root: str = None,
        timeout: int = 30,
    ):
        # If workspace_root is provided, use it; otherwise use current directory
        self.workspace_root = workspace_root if workspace_root else os.getcwd()
        self.default_timeout = timeout
        
        # Set policy engine workspace
        policy_engine = get_policy_engine()
        policy_engine.workspace_root = self.workspace_root
        self.policy = policy_engine
        
        self.evidence = EvidenceCollector()
        self._running_processes: Dict[int, subprocess.Popen] = {}
    
    def _create_evidence(
        self,
        command: str,
        params: Dict[str, Any],
        success: bool,
        result: Dict[str, Any] = None,
        error: str = "",
        stdout: str = "",
        stderr: str = "",
        exit_code: int = -1,
    ) -> Evidence:
        """Create evidence for a command execution"""
        evidence = self.evidence.create_evidence(
            step_id=f"terminal.execute",
            capability="terminal",
            tool="execute",
            action=f"subprocess.run({command})",
            input_data=params,
            exit_status=ExitStatus.SUCCESS if success else ExitStatus.FAILURE,
            provenance=f"TerminalTool.execute({command})",
        )
        
        self.evidence.complete_evidence(
            evidence=evidence,
            output=result,
            verification_status=VerificationStatus.VERIFIED,
            error=error,
        )
        
        evidence.output = result
        evidence.git_state = {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
        }
        
        return evidence
    
    def execute(
        self,
        command: str,
        timeout: int = None,
        cwd: str = None,
        capture_output: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a command with real subprocess.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds (default: 30)
            cwd: Working directory (default: workspace_root)
            capture_output: Capture stdout/stderr
            
        Returns:
            Dict with stdout, stderr, exit_code, and evidence
        """
        # Policy check - this is the critical security gate
        check = self.policy.check_command(command)
        if check.decision != PolicyDecision.ALLOW:
            evidence = self._create_evidence(
                command,
                {"timeout": timeout, "cwd": cwd},
                False,
                error=f"REJECTED_BY_POLICY: {check.denied_reason}",
            )
            return {
                "success": False,
                "error": f"REJECTED_BY_POLICY: {check.denied_reason}",
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "evidence": evidence.to_dict(),
                "policy_decision": check.decision,
            }
        
        # Set defaults
        timeout = timeout or self.default_timeout
        cwd = cwd or self.workspace_root
        
        # Resolve working directory
        work_dir = Path(cwd)
        if not work_dir.is_absolute():
            work_dir = Path(self.workspace_root) / work_dir
        
        # Verify working directory is within workspace
        try:
            work_dir.resolve().relative_to(Path(self.workspace_root).resolve())
        except ValueError:
            evidence = self._create_evidence(
                command,
                {"timeout": timeout, "cwd": cwd},
                False,
                error=f"Working directory outside workspace: {work_dir}",
            )
            return {
                "success": False,
                "error": f"Working directory outside workspace: {work_dir}",
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "evidence": evidence.to_dict(),
            }
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Execute real subprocess
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(work_dir),
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                env={**os.environ, "HOME": os.environ.get("HOME", "/root")},
            )
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            # Extract output
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            exit_code = result.returncode
            
            # Determine success
            success = exit_code == 0
            
            result_data = {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "duration_seconds": duration,
                "timed_out": False,
            }
            
            evidence = self._create_evidence(
                command,
                {"timeout": timeout, "cwd": str(work_dir)},
                success,
                result=result_data,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
            )
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "duration_seconds": duration,
                "timed_out": False,
                "evidence": evidence.to_dict(),
            }
            
        except subprocess.TimeoutExpired as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            # Get partial output if available
            stdout = ""
            stderr = f"Command timed out after {timeout} seconds"
            if e.stdout:
                stdout = e.stdout.decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else str(e.stdout)
            if e.stderr:
                stderr = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else str(e.stderr)
            
            evidence = self._create_evidence(
                command,
                {"timeout": timeout, "cwd": str(work_dir)},
                False,
                error=f"Timeout after {timeout} seconds",
                stdout=stdout,
                stderr=stderr,
                exit_code=-1,
            )
            
            return {
                "success": False,
                "error": f"Timeout after {timeout} seconds",
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": -1,
                "duration_seconds": duration,
                "timed_out": True,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            evidence = self._create_evidence(
                command,
                {"timeout": timeout, "cwd": str(work_dir)},
                False,
                error=str(e),
            )
            
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "duration_seconds": duration,
                "timed_out": False,
                "evidence": evidence.to_dict(),
            }
    
    def execute_with_input(
        self,
        command: str,
        input_data: str = None,
        timeout: int = None,
        cwd: str = None,
    ) -> Dict[str, Any]:
        """
        Execute a command with stdin input.
        
        Args:
            command: Command to execute
            input_data: Data to send to stdin
            timeout: Timeout in seconds
            cwd: Working directory
            
        Returns:
            Dict with results and evidence
        """
        # Policy check
        check = self.policy.check_command(command)
        if check.decision != PolicyDecision.ALLOW:
            return {
                "success": False,
                "error": f"REJECTED_BY_POLICY: {check.denied_reason}",
                "evidence": None,
            }
        
        timeout = timeout or self.default_timeout
        cwd = cwd or self.workspace_root
        
        work_dir = Path(cwd)
        if not work_dir.is_absolute():
            work_dir = Path(self.workspace_root) / work_dir
        
        start_time = datetime.now(timezone.utc)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(work_dir),
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            exit_code = result.returncode
            success = exit_code == 0
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "duration_seconds": duration,
                "evidence": self._create_evidence(
                    command,
                    {"timeout": timeout, "cwd": str(work_dir), "has_input": True},
                    success,
                    result={"exit_code": exit_code, "duration": duration},
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                ).to_dict(),
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Timeout after {timeout} seconds",
                "evidence": None,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "evidence": None,
            }
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get list of currently tracked processes"""
        return [
            {
                "pid": pid,
                "command": proc.args if hasattr(proc, 'args') else str(proc),
            }
            for pid, proc in self._running_processes.items()
        ]
    
    def terminate_process(self, pid: int) -> Dict[str, Any]:
        """Terminate a running process"""
        if pid not in self._running_processes:
            return {
                "success": False,
                "error": f"Process {pid} not found",
            }
        
        try:
            proc = self._running_processes[pid]
            os.kill(pid, signal.SIGTERM)
            del self._running_processes[pid]
            return {
                "success": True,
                "message": f"Process {pid} terminated",
            }
        except ProcessLookupError:
            return {
                "success": True,
                "message": f"Process {pid} already terminated",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


# Singleton instance
_terminal_tool: Optional[TerminalTool] = None


def get_terminal_tool() -> TerminalTool:
    """Get or create the terminal tool singleton"""
    global _terminal_tool
    if _terminal_tool is None:
        _terminal_tool = TerminalTool()
    return _terminal_tool
