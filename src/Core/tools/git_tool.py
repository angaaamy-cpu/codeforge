"""
Git Tool - Phase 2: Execution Engine Bridge
===========================================

Real git operations with evidence collection.
"""

import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.Core.evidence import Evidence, EvidenceCollector, ExitStatus, VerificationStatus


class GitTool:
    """
    Real git operations tool.
    
    All operations produce real evidence against the actual git repository.
    """
    
    def __init__(self, workspace_root: str = None):
        """
        Initialize GitTool.
        
        Args:
            workspace_root: Root directory for git operations.
        """
        self.workspace_root = workspace_root or os.getcwd()
        self.evidence = EvidenceCollector()
    
    def _run_git(self, args: List[str]) -> Dict[str, Any]:
        """Run a git command"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.workspace_root,
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
                "stderr": "Command timed out",
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
        action: str,
        params: Dict[str, Any],
        success: bool,
        result: Dict[str, Any] = None,
        git_state: Dict[str, Any] = None,
    ) -> Evidence:
        """Create evidence for a git operation"""
        evidence = self.evidence.create_evidence(
            step_id=f"git.{action}",
            capability="git",
            tool=action,
            action=f"git.{action}",
            input_data=params,
            exit_status=ExitStatus.SUCCESS if success else ExitStatus.FAILURE,
            provenance=f"GitTool.{action}()",
        )
        
        self.evidence.complete_evidence(
            evidence=evidence,
            output=result,
            git_state=git_state or {},
            verification_status=VerificationStatus.VERIFIED if success else VerificationStatus.FAILED,
            error=result.get("stderr", "") if result else "",
        )
        
        return evidence
    
    def status(self) -> Dict[str, Any]:
        """Get git status"""
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
        """Get git diff"""
        args = ["diff"]
        if file:
            args.append(file)
        
        result = self._run_git(args)
        
        evidence = self._create_evidence(
            "diff",
            {"file": file} if file else {},
            result["success"],
            result={"output_length": len(result["stdout"])},
            git_state={"exit_code": result["exit_code"]},
        )
        
        return {
            "success": result["success"],
            "diff": result["stdout"],
            "has_changes": bool(result["stdout"].strip()),
            "stderr": result["stderr"],
            "evidence": evidence.to_dict(),
        }
    
    def log(self, limit: int = 10) -> Dict[str, Any]:
        """Get git log"""
        result = self._run_git(["log", f"--max-count={limit}", "--format=%H|%s|%an|%ad|%ai", "--date=iso"])
        
        commits = []
        if result["success"] and result["stdout"]:
            for line in result["stdout"].strip().split("\n"):
                if line and "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                            "full_date": parts[4],
                        })
        
        evidence = self._create_evidence(
            "log",
            {"limit": limit},
            result["success"],
            result={"commits": len(commits)},
            git_state={"commits": commits, "exit_code": result["exit_code"]},
        )
        
        return {
            "success": result["success"],
            "commits": commits,
            "stderr": result["stderr"],
            "evidence": evidence.to_dict(),
        }
    
    def commit(self, message: str) -> Dict[str, Any]:
        """Create a git commit"""
        # First check for changes
        status = self.status()
        if not status["has_changes"]:
            evidence = self._create_evidence(
                "commit",
                {"message": message},
                success=False,
                result=None,
                git_state={},
            )
            return {
                "success": False,
                "error": "No changes to commit",
                "evidence": evidence.to_dict(),
            }
        
        # Stage all changes
        add_result = self._run_git(["add", "-A"])
        
        # Commit
        result = self._run_git(["commit", "-m", message])
        
        commit_hash = None
        if result["success"]:
            # Extract commit hash from output
            for line in result["stdout"].split("\n"):
                if "root-commit" in line or "commit" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "commit" or "root-commit" in part:
                            if i + 1 < len(parts):
                                commit_hash = parts[i + 1].rstrip(']')
                            break
                    if not commit_hash:
                        commit_hash = line.split()[-1][:7].rstrip(']')
        
        evidence = self._create_evidence(
            "commit",
            {"message": message},
            result["success"],
            result={"commit_hash": commit_hash, "message": message},
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
    
    def get_commit(self, commit_hash: str) -> Dict[str, Any]:
        """Get commit details"""
        result = self._run_git(["show", "--format=%H|%an|%ae|%ad|%s", "-s", commit_hash])
        
        commit_info = {}
        if result["success"] and result["stdout"]:
            parts = result["stdout"].strip().split("|")
            if len(parts) >= 5:
                commit_info = {
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4],
                }
        
        evidence = self._create_evidence(
            "get_commit",
            {"commit_hash": commit_hash},
            result["success"],
            result=commit_info,
            git_state={"commit": commit_info, "exit_code": result["exit_code"]},
        )
        
        return {
            "success": result["success"],
            "commit": commit_info,
            "stderr": result["stderr"],
            "evidence": evidence.to_dict(),
        }
    
    def verify_commit_exists(self, commit_hash: str) -> Dict[str, Any]:
        """Verify a commit exists"""
        result = self._run_git(["cat-file", "-t", commit_hash])
        
        exists = result["success"] and result["stdout"].strip() == "commit"
        
        evidence = self._create_evidence(
            "verify_commit",
            {"commit_hash": commit_hash},
            exists,
            result={"exists": exists},
            git_state={"exit_code": result["exit_code"]},
        )
        
        return {
            "exists": exists,
            "evidence": evidence.to_dict(),
        }
