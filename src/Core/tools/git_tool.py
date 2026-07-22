"""
CodeForge Git Tool - Phase 2
=============================
Git operations as a capability tool.
Wraps git_manager and produces real evidence.
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from src.Core.policy import get_policy_engine, PolicyDecision
from src.Core.evidence import Evidence, EvidenceCollector, ExitStatus, VerificationStatus


class GitTool:
    """
    Git operations tool.
    All operations are verified against real Git state.
    """
    
    def __init__(self, repo_path: str = None):
        # Use provided path or current directory
        self.repo_path = repo_path if repo_path else os.getcwd()
        
        # Set policy engine workspace
        policy_engine = get_policy_engine()
        policy_engine.workspace_root = self.repo_path
        
        self.evidence = EvidenceCollector()
    
    def _run_git(self, args: List[str], check: bool = True) -> Dict[str, Any]:
        """Run a git command and return result"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Git command timed out",
                "exit_code": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
            }
    
    def _create_evidence(
        self,
        operation: str,
        params: Dict[str, Any],
        success: bool,
        result: Dict[str, Any] = None,
        error: str = "",
        git_state: Dict[str, Any] = None,
    ) -> Evidence:
        """Create evidence for a git operation"""
        evidence = self.evidence.create_evidence(
            step_id=f"git.{operation}",
            capability="git",
            tool=operation,
            action=f"git.{operation}",
            input_data=params,
            exit_status=ExitStatus.SUCCESS if success else ExitStatus.FAILURE,
            provenance=f"GitTool.{operation}()",
        )
        
        self.evidence.complete_evidence(
            evidence=evidence,
            output=result,
            git_state=git_state or {},
            verification_status=VerificationStatus.VERIFIED if success else VerificationStatus.FAILED,
            error=error,
        )
        
        return evidence
    
    def status(self) -> Dict[str, Any]:
        """
        Get git status.
        
        Returns:
            Dict with status information
        """
        result = self._run_git(["status", "--porcelain"])
        
        files = []
        has_changes = False
        
        if result["success"] and result["stdout"]:
            for line in result["stdout"].strip().split("\n"):
                if line:
                    status = line[:2].strip()
                    filename = line[3:]
                    files.append({"status": status, "file": filename})
                    # Untracked files (??) or modified files indicate changes
                    if status in ["??", "M", "A", "D", "R"] or status.strip():
                        has_changes = True
        
        evidence = self._create_evidence(
            "status",
            {},
            result["success"],
            result={"changed_files": len(files)},
            git_state={"files": files, "exit_code": result["exit_code"]},
        )
        
        return {
            "success": result["success"],
            "files": files,
            "has_changes": has_changes or len(files) > 0,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "evidence": evidence.to_dict(),
        }
    
    def diff(self, file: str = None) -> Dict[str, Any]:
        """
        Get git diff.
        
        Args:
            file: Specific file to diff (optional)
            
        Returns:
            Dict with diff output
        """
        args = ["diff"]
        if file:
            args.append("--")
            args.append(file)
        
        result = self._run_git(args)
        
        evidence = self._create_evidence(
            "diff",
            {"file": file},
            result["success"],
            result={"output_length": len(result["stdout"])},
            git_state={"exit_code": result["exit_code"]},
        )
        
        return {
            "success": result["success"],
            "diff": result["stdout"],
            "stderr": result["stderr"],
            "has_changes": bool(result["stdout"].strip()),
            "evidence": evidence.to_dict(),
        }
    
    def log(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get git log.
        
        Args:
            limit: Number of commits to show
            
        Returns:
            Dict with commit history
        """
        result = self._run_git([
            "log",
            f"-{limit}",
            "--format=%H|%s|%an|%ad",
            "--date=iso"
        ])
        
        commits = []
        if result["success"] and result["stdout"]:
            for line in result["stdout"].strip().split("\n"):
                if line:
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                        })
        
        evidence = self._create_evidence(
            "log",
            {"limit": limit},
            result["success"],
            result={"commits": len(commits)},
            git_state={"commits": commits},
        )
        
        return {
            "success": result["success"],
            "commits": commits,
            "stderr": result["stderr"],
            "evidence": evidence.to_dict(),
        }
    
    def commit(self, message: str) -> Dict[str, Any]:
        """
        Create a git commit.
        
        Args:
            message: Commit message
            
        Returns:
            Dict with commit result
        """
        # First check for changes
        status_result = self.status()
        if not status_result["has_changes"]:
            evidence = self._create_evidence(
                "commit",
                {"message": message},
                False,
                error="No changes to commit",
            )
            return {
                "success": False,
                "error": "No changes to commit",
                "evidence": evidence.to_dict(),
            }
        
        # git add .
        add_result = self._run_git(["add", "."])
        if not add_result["success"]:
            evidence = self._create_evidence(
                "commit",
                {"message": message},
                False,
                error=f"git add failed: {add_result['stderr']}",
            )
            return {
                "success": False,
                "error": f"git add failed: {add_result['stderr']}",
                "evidence": evidence.to_dict(),
            }
        
        # git commit
        result = self._run_git(["commit", "-m", message])
        
        # Get commit hash if successful
        commit_hash = ""
        if result["success"]:
            hash_result = self._run_git(["rev-parse", "--short", "HEAD"])
            if hash_result["success"]:
                commit_hash = hash_result["stdout"].strip()
        
        evidence = self._create_evidence(
            "commit",
            {"message": message},
            result["success"],
            result={
                "commit_hash": commit_hash,
                "message": message,
            },
            error="" if result["success"] else result["stderr"],
            git_state={
                "exit_code": result["exit_code"],
                "commit_hash": commit_hash,
                "stdout": result["stdout"],
            },
        )
        
        return {
            "success": result["success"],
            "commit_hash": commit_hash,
            "message": message,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "evidence": evidence.to_dict(),
        }
    
    def get_commit(self, ref: str = "HEAD") -> Dict[str, Any]:
        """
        Get details of a specific commit.
        
        Args:
            ref: Commit reference (hash, branch, HEAD, etc.)
            
        Returns:
            Dict with commit details
        """
        # Get commit info
        result = self._run_git([
            "log", "-1",
            "--format=%H|%s|%an|%ae|%ad",
            "--date=iso",
            ref
        ])
        
        if not result["success"] or not result["stdout"].strip():
            evidence = self._create_evidence(
                "get_commit",
                {"ref": ref},
                False,
                error=f"Commit not found: {ref}",
            )
            return {
                "success": False,
                "error": f"Commit not found: {ref}",
                "evidence": evidence.to_dict(),
            }
        
        parts = result["stdout"].strip().split("|")
        if len(parts) < 5:
            evidence = self._create_evidence(
                "get_commit",
                {"ref": ref},
                False,
                error="Invalid commit format",
            )
            return {
                "success": False,
                "error": "Invalid commit format",
                "evidence": evidence.to_dict(),
            }
        
        commit = {
            "hash": parts[0],
            "message": parts[1],
            "author": parts[2],
            "email": parts[3],
            "date": parts[4],
        }
        
        evidence = self._create_evidence(
            "get_commit",
            {"ref": ref},
            True,
            result=commit,
            git_state={"commit": commit},
        )
        
        return {
            "success": True,
            "commit": commit,
            "evidence": evidence.to_dict(),
        }
    
    def branch(self) -> Dict[str, Any]:
        """
        Get current branch and all branches.
        
        Returns:
            Dict with branch information
        """
        # Current branch
        current_result = self._run_git(["branch", "--show-current"])
        current = current_result["stdout"].strip() if current_result["success"] else ""
        
        # All branches
        all_result = self._run_git(["branch", "-a"])
        branches = []
        if all_result["success"] and all_result["stdout"]:
            for line in all_result["stdout"].strip().split("\n"):
                if line:
                    branch = line.strip().replace("* ", "")
                    branches.append({
                        "name": branch,
                        "current": "*" in line,
                    })
        
        evidence = self._create_evidence(
            "branch",
            {},
            True,
            result={"current": current, "count": len(branches)},
            git_state={"current": current, "branches": branches},
        )
        
        return {
            "success": True,
            "current": current,
            "branches": branches,
            "evidence": evidence.to_dict(),
        }
    
    def remote(self) -> Dict[str, Any]:
        """
        Get remote information.
        
        Returns:
            Dict with remote information
        """
        result = self._run_git(["remote", "-v"])
        
        remotes = []
        if result["success"] and result["stdout"]:
            for line in result["stdout"].strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes.append({
                            "name": parts[0],
                            "url": parts[1],
                        })
        
        evidence = self._create_evidence(
            "remote",
            {},
            True,
            result={"remotes": len(remotes)},
            git_state={"remotes": remotes},
        )
        
        return {
            "success": True,
            "remotes": remotes,
            "evidence": evidence.to_dict(),
        }
    
    def verify_commit_exists(self, commit_hash: str) -> Dict[str, Any]:
        """
        Verify a commit exists by checking its hash.
        
        Args:
            commit_hash: Full or partial commit hash
            
        Returns:
            Dict with verification result
        """
        result = self._run_git(["cat-file", "-t", commit_hash])
        
        exists = result["success"] and "commit" in result["stdout"]
        
        evidence = self._create_evidence(
            "verify_commit",
            {"commit_hash": commit_hash},
            True,
            result={"exists": exists, "type": result["stdout"].strip() if exists else None},
            git_state={"exists": exists},
        )
        
        return {
            "success": True,
            "exists": exists,
            "commit_hash": commit_hash,
            "evidence": evidence.to_dict(),
        }


# Singleton instance
_git_tool: Optional[GitTool] = None


def get_git_tool() -> GitTool:
    """Get or create the git tool singleton"""
    global _git_tool
    if _git_tool is None:
        _git_tool = GitTool()
    return _git_tool
