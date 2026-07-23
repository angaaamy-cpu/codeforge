"""
Terminal Tool - Phase 2: Execution Engine Bridge
===============================================

Real subprocess execution with policy enforcement and evidence collection.
"""

import os
import subprocess
import time
from typing import Any, Dict, List, Optional

from src.Core.evidence import Evidence, EvidenceCollector, ExitStatus, VerificationStatus
from src.Core.policy import get_policy_engine, PolicyDecision


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
        """
        Initialize TerminalTool.
        
        Args:
            workspace_root: Root directory for command execution.
            timeout: Default timeout for commands in seconds.
        """
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
        success: bool,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        duration: float = 0.0,
        error: str = "",
    ) -> Evidence:
        """Create evidence for a command execution"""
        evidence = self.evidence.create_evidence(
            step_id="terminal.execute",
            capability="terminal",
            tool="execute",
            action="terminal.execute",
            input_data={"command": command, "workspace": self.workspace_root},
            exit_status=ExitStatus.SUCCESS if success else ExitStatus.FAILURE,
            provenance="TerminalTool.execute()",
        )
        
        self.evidence.complete_evidence(
            evidence=evidence,
            output={
                "exit_code": exit_code,
                "stdout_length": len(stdout),
                "stderr_length": len(stderr),
                "duration_seconds": duration,
            },
            verification_status=VerificationStatus.VERIFIED if success else VerificationStatus.FAILED,
            error=error or stderr,
            duration_seconds=duration,
        )
        
        return evidence
    
    def execute(self, command: str, timeout: int = None) -> Dict[str, Any]:
        """
        Execute a command with policy enforcement.
        
        Args:
            command: The command to execute
            timeout: Optional timeout override
            
        Returns:
            Dict with success, exit_code, stdout, stderr, duration, evidence
        """
        timeout = timeout or self.default_timeout
        
        # Check command policy only (terminal doesn't have path context)
        policy_result = self.policy.command_policy.check_command(command)
        if policy_result.decision != PolicyDecision.ALLOW:
            evidence = self._create_evidence(
                command=command,
                success=False,
                exit_code=-1,
                error=f"Policy denied: {policy_result.reason}",
            )
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Policy Decision: {policy_result.decision.value}",
                "policy_decision": policy_result.decision.value,
                "policy_reason": policy_result.reason,
                "duration": 0.0,
                "evidence": evidence.to_dict(),
            }
        
        # Execute command
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            evidence = self._create_evidence(
                command=command,
                success=success,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration,
            )
            
            return {
                "success": success,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "evidence": evidence.to_dict(),
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            evidence = self._create_evidence(
                command=command,
                success=False,
                exit_code=-1,
                error=f"Command timed out after {timeout} seconds",
                duration=duration,
            )
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "duration": duration,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            duration = time.time() - start_time
            evidence = self._create_evidence(
                command=command,
                success=False,
                exit_code=-1,
                error=str(e),
                duration=duration,
            )
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": duration,
                "evidence": evidence.to_dict(),
            }
    
    def execute_batch(self, commands: List[str]) -> List[Dict[str, Any]]:
        """
        Execute multiple commands.
        
        Args:
            commands: List of commands to execute
            
        Returns:
            List of results
        """
        results = []
        for command in commands:
            results.append(self.execute(command))
        return results
