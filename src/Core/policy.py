"""
Policy Engine - Phase 2: Execution Engine Bridge
==============================================

Provides command allowlist policy and workspace isolation.
"""

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set


class PolicyDecision(Enum):
    """Policy decision outcomes"""
    ALLOW = "allow"
    DENY = "deny"
    BLOCK = "block"


@dataclass
class PolicyResult:
    """Result of a policy check"""
    decision: PolicyDecision
    reason: str = ""
    matched_rule: Optional[str] = None


class CommandPolicy:
    """
    Command policy with allowlist-based execution.
    
    Only commands in the allowlist can be executed.
    Dangerous patterns are always blocked.
    """
    
    # Default allowed commands
    DEFAULT_ALLOWED: Set[str] = {
        # File operations
        "ls", "cat", "echo", "mkdir", "touch", "cp", "mv", "rm", "chmod", "chown",
        # Git operations
        "git", "git-status", "git-commit", "git-push", "git-pull", "git-log", "git-diff",
        # Build tools
        "make", "npm", "pip", "python", "python3",
        # Text processing
        "grep", "sed", "awk", "find", "sort", "uniq",
        # System info
        "pwd", "whoami", "date", "uname", "hostname",
        # Network (read-only)
        "curl", "wget",
    }
    
    # Dangerous patterns - always blocked
    DANGEROUS_PATTERNS: List[str] = [
        r"rm\s+-rf\s+/",
        r"dd\s+if=.*of=/dev/",
        r"mkfs",
        r"fdisk",
        r":\(\)\{",  # Fork bomb
        r"curl.*\|.*sh",  # Pipe to shell
        r"wget.*\|.*sh",
        r">\s*/etc/passwd",
        r"chmod\s+777",
    ]
    
    def __init__(self, allowed_commands: Set[str] = None):
        self.allowed_commands = allowed_commands or self.DEFAULT_ALLOWED.copy()
        self.dangerous_patterns = [re.compile(p) for p in self.DANGEROUS_PATTERNS]
    
    def check_command(self, command: str) -> PolicyResult:
        """
        Check if a command is allowed.
        
        Args:
            command: The command string to check
            
        Returns:
            PolicyResult with decision and reason
        """
        command_lower = command.lower().strip()
        
        # Check for dangerous patterns first
        for pattern in self.dangerous_patterns:
            if pattern.search(command):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Dangerous pattern detected: {pattern.pattern}",
                    matched_rule=f"DANGEROUS_PATTERN:{pattern.pattern}"
                )
        
        # Extract the base command
        base_command = command_lower.split()[0] if command_lower.split() else ""
        
        # Check if base command is in allowlist
        if base_command in self.allowed_commands:
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                reason=f"Command '{base_command}' is in allowlist",
                matched_rule=f"ALLOWLIST:{base_command}"
            )
        
        # Check for common subcommands
        for allowed in self.allowed_commands:
            if base_command.startswith(allowed) or allowed.startswith(base_command):
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    reason=f"Command '{base_command}' matches allowed pattern",
                    matched_rule=f"PATTERN_MATCH:{allowed}"
                )
        
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason=f"Command '{base_command}' is not in allowlist",
            matched_rule=None
        )
    
    def add_allowed_command(self, command: str) -> None:
        """Add a command to the allowlist"""
        self.allowed_commands.add(command.lower().strip())


class WorkspacePolicy:
    """
    Workspace policy for path traversal prevention.
    
    Ensures all file operations stay within the workspace boundary.
    """
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
    
    def check_path(self, path: str, operation: str = "read") -> PolicyResult:
        """
        Check if a path is within the workspace.
        
        Args:
            path: The path to check
            operation: The operation being performed (read, write, delete)
            
        Returns:
            PolicyResult with decision and reason
        """
        # Resolve the path to absolute path
        try:
            abs_path = os.path.abspath(os.path.expanduser(path))
        except Exception as e:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Invalid path: {e}",
                matched_rule="PATH_VALIDATION"
            )
        
        # Resolve workspace root
        workspace_abs = os.path.abspath(os.path.expanduser(self.workspace_root))
        
        # Check if path is within workspace
        if not abs_path.startswith(workspace_abs + os.sep) and abs_path != workspace_abs:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Path outside workspace: {path}",
                matched_rule="WORKSPACE_BOUNDARY"
            )
        
        # Check for path traversal attempts
        if ".." in path:
            # Normalize and recheck
            normalized = os.path.normpath(path)
            if ".." in normalized:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Path traversal detected: {path}",
                    matched_rule="PATH_TRAVERSAL"
                )
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason=f"Path within workspace",
            matched_rule="WORKSPACE_BOUNDARY"
        )
    
    def set_workspace_root(self, path: str) -> None:
        """Set the workspace root directory"""
        self.workspace_root = path


class PolicyEngine:
    """
    Combined policy engine for execution.
    
    Combines command policy and workspace policy.
    """
    
    def __init__(self, workspace_root: str = None):
        self.command_policy = CommandPolicy()
        self.workspace_policy = WorkspacePolicy(workspace_root)
        self.workspace_root = workspace_root or os.getcwd()
    
    def check_execution(self, command: str, workspace_path: str = None) -> PolicyResult:
        """
        Check if command execution is allowed.
        
        Args:
            command: The command to execute
            workspace_path: Optional path context
            
        Returns:
            PolicyResult with decision
        """
        # Check command policy first
        cmd_result = self.command_policy.check_command(command)
        if cmd_result.decision != PolicyDecision.ALLOW:
            return cmd_result
        
        # Check workspace path if provided
        if workspace_path:
            path_result = self.workspace_policy.check_path(workspace_path)
            if path_result.decision != PolicyDecision.ALLOW:
                return path_result
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="All policy checks passed",
            matched_rule="COMBINED_PASS"
        )
    
    def check_path(self, path: str, operation: str = "read") -> PolicyResult:
        """Check if path operation is allowed"""
        return self.workspace_policy.check_path(path, operation)


# Global singleton
_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get singleton policy engine instance"""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine


def reset_policy_engine() -> None:
    """Reset the policy engine singleton"""
    global _policy_engine
    _policy_engine = None
