"""
CodeForge Policy Engine - Phase 2
==================================
Governs command execution, workspace access, and capability usage.
Every capability action passes through Policy Engine before execution.
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Any, Optional, Callable
from enum import Enum
import re
import os
from pathlib import Path


class PolicyDecision(str, Enum):
    """Policy decision"""
    ALLOW = "allow"
    DENY = "deny"
    BLOCK = "block"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class PolicyResult:
    """Result of a policy check"""
    decision: PolicyDecision
    reason: str
    allowed_commands: List[str] = field(default_factory=list)
    denied_reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommandPolicy:
    """
    Command execution policy with allowlist.
    Only commands in the allowlist can be executed.
    """
    
    # Default allowed commands (harmless, read-only or safe operations)
    DEFAULT_ALLOWED = {
        # File operations
        "ls", "ls -la", "ls -l", "ls -R",
        "cat", "head", "tail", "wc", "grep", "find", "stat",
        "md5sum", "sha256sum", "file",
        "pwd", "whoami", "date", "echo",
        
        # Git operations
        "git status", "git diff", "git log", "git show",
        "git branch", "git remote -v", "git rev-parse",
        
        # Python
        "python --version", "python3 --version",
        "pip list", "pip show",
        
        # Testing
        "pytest --version", "pytest --collect-only",
        
        # Network (read-only)
        "curl --version", "wget --version",
    }
    
    # Dangerous commands (always denied)
    DENIED_PATTERNS = {
        r"rm\s+-rf\s+/",  # Root deletion
        r"dd\s+if=",  # Direct disk write
        r":\(\)\{:\|:&\};:",  # Fork bomb
        r"mkfs",  # Filesystem creation
        r"fdisk",  # Disk partitioning
        r"parted",  # Partition editor
        r"chattr\s+-i",  # Immutable attribute removal
        r">\s*/dev/sd",  # Direct device write
        r"\|\s*sh",  # Pipe to shell
        r";\s*sh",  # Semicolon shell
        r"&\s*sh",  # Background shell
        r"eval\s+",  # Eval execution
        r"exec\s+",  # Direct exec
    }
    
    def __init__(
        self,
        allowed_commands: Set[str] = None,
        denied_patterns: List[str] = None,
        workspace_root: str = None,
    ):
        self.allowed_commands = allowed_commands or set(self.DEFAULT_ALLOWED)
        self.denied_patterns = denied_patterns or self.DENIED_PATTERNS
        self.workspace_root = workspace_root or os.getcwd()
        
        # Compile denial patterns
        self._denied_re = [re.compile(p) for p in self.denied_patterns]
    
    def check_command(self, command: str) -> PolicyResult:
        """
        Check if a command is allowed.
        
        Args:
            command: The command to check
            
        Returns:
            PolicyResult with decision and reason
        """
        if not command or not command.strip():
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="Empty command",
                denied_reason="Command cannot be empty"
            )
        
        # Check for dangerous patterns first (always deny)
        for pattern in self._denied_re:
            if pattern.search(command):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="Command matches denied pattern",
                    denied_reason=f"Command '{command}' matches dangerous pattern",
                    metadata={"pattern": pattern.pattern}
                )
        
        # Check if command is in allowlist (exact match)
        if command in self.allowed_commands:
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                reason="Command in allowlist",
                allowed_commands=[command]
            )
        
        # Check if base command is in allowlist
        base_command = command.split("|")[0].split(";")[0].split("&")[0].strip()
        base_parts = base_command.split()
        if base_parts and base_parts[0] in self.allowed_commands:
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                reason="Base command in allowlist",
                allowed_commands=[base_parts[0]]
            )
        
        # Check allowlist patterns (e.g., "git commit -m" pattern)
        for allowed in self.allowed_commands:
            if allowed.endswith("*"):
                prefix = allowed[:-1]
                if command.startswith(prefix):
                    return PolicyResult(
                        decision=PolicyDecision.ALLOW,
                        reason="Command matches allowed pattern",
                        allowed_commands=[allowed]
                    )
        
        # Command not in allowlist
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason="Command not in allowlist",
            denied_reason=f"Command '{command}' is not in the allowed commands list",
            allowed_commands=list(self.allowed_commands)
        )
    
    def add_allowed_command(self, command: str) -> None:
        """Add a command to the allowlist"""
        self.allowed_commands.add(command)
    
    def remove_allowed_command(self, command: str) -> None:
        """Remove a command from the allowlist"""
        self.allowed_commands.discard(command)
    
    def get_allowed_commands(self) -> Set[str]:
        """Get all allowed commands"""
        return set(self.allowed_commands)


class WorkspacePolicy:
    """
    Workspace access policy.
    Ensures all file operations stay within allowed workspace boundaries.
    """
    
    def __init__(
        self,
        workspace_root: str,
        allowed_paths: List[str] = None,
    ):
        self.workspace_root = Path(workspace_root).resolve()
        self.allowed_paths = set(allowed_paths or [])
        
        # Ensure workspace root is in allowed paths
        self.allowed_paths.add(str(self.workspace_root))
    
    def check_path(self, path: str, operation: str = "read") -> PolicyResult:
        """
        Check if a path access is allowed.
        
        Args:
            path: The path to check
            operation: "read", "write", "delete"
            
        Returns:
            PolicyResult with decision and reason
        """
        try:
            resolved_path = Path(path).resolve()
        except Exception as e:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="Invalid path",
                denied_reason=f"Path '{path}' is invalid: {e}"
            )
        
        # Check for path traversal attempts
        path_str = str(resolved_path)
        if "../" in path or path.startswith(".."):
            # This is allowed if it resolves within workspace
            pass
        else:
            # Direct path - check if within workspace
            try:
                resolved_path.relative_to(self.workspace_root)
            except ValueError:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="Path outside workspace",
                    denied_reason=f"Path '{path}' is outside workspace root '{self.workspace_root}'"
                )
        
        # Check if path is within any allowed path
        for allowed in self.allowed_paths:
            allowed_resolved = Path(allowed).resolve()
            try:
                resolved_path.relative_to(allowed_resolved)
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    reason=f"Path within allowed directory: {allowed}",
                    metadata={"allowed_path": allowed}
                )
            except ValueError:
                continue
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="Path within workspace",
            metadata={"workspace_root": str(self.workspace_root)}
        )
    
    def check_delete(self, path: str) -> PolicyResult:
        """
        Special check for delete operations (more restrictive).
        """
        result = self.check_path(path, "delete")
        
        if result.decision == PolicyDecision.ALLOW:
            # Additional checks for delete
            path_obj = Path(path)
            
            # Don't allow deleting workspace root
            if path_obj.resolve() == self.workspace_root:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="Cannot delete workspace root",
                    denied_reason="Deleting the workspace root is not allowed"
                )
            
            # Don't allow deleting protected directories
            protected = {".git", ".codeforge", ".config"}
            for part in path_obj.parts:
                if part in protected:
                    return PolicyResult(
                        decision=PolicyDecision.DENY,
                        reason=f"Cannot delete protected directory: {part}",
                        denied_reason=f"Directory '{part}' is protected"
                    )
        
        return result
    
    def is_within_workspace(self, path: str) -> bool:
        """Quick check if path is within workspace"""
        try:
            Path(path).resolve().relative_to(self.workspace_root)
            return True
        except ValueError:
            return False


class PolicyEngine:
    """
    Central policy engine that combines all policy checks.
    Single entry point for all policy decisions.
    """
    
    def __init__(
        self,
        workspace_root: str = None,
        allowed_commands: Set[str] = None,
    ):
        self.workspace_root = workspace_root or os.getcwd()
        self.command_policy = CommandPolicy(
            allowed_commands=allowed_commands,
            workspace_root=self.workspace_root
        )
        self.workspace_policy = WorkspacePolicy(
            workspace_root=self.workspace_root
        )
    
    def check_command(self, command: str) -> PolicyResult:
        """Check if a command is allowed"""
        return self.command_policy.check_command(command)
    
    def check_path(self, path: str, operation: str = "read") -> PolicyResult:
        """Check if a path access is allowed"""
        return self.workspace_policy.check_path(path, operation)
    
    def check_delete(self, path: str) -> PolicyResult:
        """Check if a delete operation is allowed"""
        return self.workspace_policy.check_delete(path)
    
    def check_execution(
        self,
        command: str = None,
        path: str = None,
        operation: str = "read"
    ) -> PolicyResult:
        """
        Combined check for command and path.
        If either check fails, execution is blocked.
        """
        if command:
            cmd_result = self.check_command(command)
            if cmd_result.decision != PolicyDecision.ALLOW:
                return cmd_result
        
        if path:
            path_result = self.check_path(path, operation)
            if path_result.decision != PolicyDecision.ALLOW:
                return path_result
        
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="All policy checks passed"
        )


# Global policy engine instance
_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get or create the global policy engine"""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine


def set_policy_engine(engine: PolicyEngine) -> None:
    """Set the global policy engine"""
    global _policy_engine
    _policy_engine = engine
