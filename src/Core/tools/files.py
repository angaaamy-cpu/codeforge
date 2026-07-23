"""
Files Tool - Phase 2: Execution Engine Bridge
============================================

Real file operations with workspace isolation and evidence collection.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.Core.evidence import Evidence, EvidenceCollector, ExitStatus, VerificationStatus
from src.Core.policy import get_policy_engine, PolicyDecision


class FilesTool:
    """
    Real file operations tool.
    
    All operations produce real evidence and respect workspace boundaries.
    """
    
    def __init__(self, workspace_root: str = None):
        """
        Initialize FilesTool.
        
        Args:
            workspace_root: Root directory for file operations. 
                          All paths will be checked against this boundary.
        """
        self.workspace_root = os.path.abspath(workspace_root) if workspace_root else os.getcwd()
        self.policy = get_policy_engine()
        self.policy.workspace_root = self.workspace_root
        self.evidence = EvidenceCollector()
    
    def _check_path(self, path: str, operation: str = "read") -> bool:
        """Check if path is within workspace"""
        # Don't check paths that are being created - they will be resolved
        abs_path = os.path.abspath(path)
        workspace_abs = os.path.abspath(self.workspace_root)
        
        # Allow paths within workspace
        if abs_path.startswith(workspace_abs + os.sep) or abs_path == workspace_abs:
            return True
        
        # For new files, also check if parent directory is within workspace
        parent = os.path.dirname(abs_path)
        if parent.startswith(workspace_abs + os.sep) or parent == workspace_abs:
            return True
        
        return False
    
    def _create_evidence(
        self,
        action: str,
        params: Dict[str, Any],
        success: bool,
        output: Any = None,
        error: str = "",
    ) -> Evidence:
        """Create evidence for an operation"""
        evidence = self.evidence.create_evidence(
            step_id=f"files.{action}",
            capability="files",
            tool=action,
            action=f"filesystem.{action}",
            input_data=params,
            exit_status=ExitStatus.SUCCESS if success else ExitStatus.FAILURE,
            provenance=f"FilesTool.{action}()",
        )
        
        self.evidence.complete_evidence(
            evidence=evidence,
            output=output,
            verification_status=VerificationStatus.VERIFIED if success else VerificationStatus.FAILED,
            error=error,
        )
        
        return evidence
    
    def write(self, path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            path: File path to write to
            content: Content to write
            
        Returns:
            Dict with success, path, bytes_written, verified, evidence
        """
        try:
            # Check workspace boundary
            if not self._check_path(path, "write"):
                evidence = self._create_evidence(
                    "write", {"path": path, "content_length": len(content)},
                    success=False, error="Path outside workspace"
                )
                return {
                    "success": False,
                    "error": "Path outside workspace",
                    "evidence": evidence.to_dict(),
                }
            
            # Ensure parent directory exists
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            
            # Write file
            start_time = os.times().elapsed if hasattr(os.times(), 'elapsed') else 0
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Verify write
            bytes_written = len(content.encode('utf-8'))
            with open(path, 'r', encoding='utf-8') as f:
                verified_content = f.read()
            
            verified = verified_content == content
            
            evidence = self._create_evidence(
                "write",
                {"path": path, "content_length": len(content)},
                success=True,
                output={"bytes_written": bytes_written, "verified": verified},
            )
            
            return {
                "success": True,
                "path": path,
                "bytes_written": bytes_written,
                "verified": verified,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            evidence = self._create_evidence(
                "write", {"path": path, "content_length": len(content)},
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": str(e),
                "evidence": evidence.to_dict(),
            }
    
    def read(self, path: str) -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            path: File path to read
            
        Returns:
            Dict with success, content, bytes_read, evidence
        """
        try:
            # Check workspace boundary
            if not self._check_path(path, "read"):
                evidence = self._create_evidence(
                    "read", {"path": path},
                    success=False, error="Path outside workspace"
                )
                return {
                    "success": False,
                    "error": "Path outside workspace",
                    "evidence": evidence.to_dict(),
                }
            
            # Check file exists
            if not os.path.exists(path):
                evidence = self._create_evidence(
                    "read", {"path": path},
                    success=False, error=f"File not found: {path}"
                )
                return {
                    "success": False,
                    "error": f"File not found: {path}",
                    "evidence": evidence.to_dict(),
                }
            
            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            bytes_read = len(content.encode('utf-8'))
            
            evidence = self._create_evidence(
                "read",
                {"path": path},
                success=True,
                output={"bytes_read": bytes_read, "content_length": len(content)},
            )
            
            return {
                "success": True,
                "content": content,
                "bytes_read": bytes_read,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            evidence = self._create_evidence(
                "read", {"path": path},
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": str(e),
                "evidence": evidence.to_dict(),
            }
    
    def delete(self, path: str) -> Dict[str, Any]:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            
        Returns:
            Dict with success, evidence
        """
        try:
            # Check workspace boundary
            if not self._check_path(path, "delete"):
                evidence = self._create_evidence(
                    "delete", {"path": path},
                    success=False, error="Path outside workspace"
                )
                return {
                    "success": False,
                    "error": "Path outside workspace",
                    "evidence": evidence.to_dict(),
                }
            
            # Check exists
            if not os.path.exists(path):
                evidence = self._create_evidence(
                    "delete", {"path": path},
                    success=False, error=f"Path not found: {path}"
                )
                return {
                    "success": False,
                    "error": f"Path not found: {path}",
                    "evidence": evidence.to_dict(),
                }
            
            # Delete
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            
            evidence = self._create_evidence(
                "delete",
                {"path": path},
                success=True,
                output={"deleted": True},
            )
            
            return {
                "success": True,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            evidence = self._create_evidence(
                "delete", {"path": path},
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": str(e),
                "evidence": evidence.to_dict(),
            }
    
    def list(self, path: str = None) -> Dict[str, Any]:
        """
        List directory contents.
        
        Args:
            path: Directory path to list (defaults to workspace root)
            
        Returns:
            Dict with success, files, evidence
        """
        try:
            path = path or self.workspace_root
            
            # Check workspace boundary
            if not self._check_path(path, "read"):
                evidence = self._create_evidence(
                    "list", {"path": path},
                    success=False, error="Path outside workspace"
                )
                return {
                    "success": False,
                    "error": "Path outside workspace",
                    "evidence": evidence.to_dict(),
                }
            
            if not os.path.isdir(path):
                evidence = self._create_evidence(
                    "list", {"path": path},
                    success=False, error=f"Not a directory: {path}"
                )
                return {
                    "success": False,
                    "error": f"Not a directory: {path}",
                    "evidence": evidence.to_dict(),
                }
            
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                files.append({
                    "name": item,
                    "path": item_path,
                    "is_file": os.path.isfile(item_path),
                    "is_dir": os.path.isdir(item_path),
                })
            
            evidence = self._create_evidence(
                "list",
                {"path": path},
                success=True,
                output={"file_count": len(files)},
            )
            
            return {
                "success": True,
                "path": path,
                "files": files,
                "count": len(files),
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            evidence = self._create_evidence(
                "list", {"path": path},
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": str(e),
                "evidence": evidence.to_dict(),
            }
    
    def exists(self, path: str) -> Dict[str, Any]:
        """
        Check if path exists.
        
        Args:
            path: Path to check
            
        Returns:
            Dict with success, exists, is_file, is_dir, evidence
        """
        try:
            exists = os.path.exists(path)
            is_file = os.path.isfile(path) if exists else False
            is_dir = os.path.isdir(path) if exists else False
            
            evidence = self._create_evidence(
                "exists",
                {"path": path},
                success=True,
                output={"exists": exists, "is_file": is_file, "is_dir": is_dir},
            )
            
            return {
                "success": True,
                "exists": exists,
                "is_file": is_file,
                "is_dir": is_dir,
                "evidence": evidence.to_dict(),
            }
            
        except Exception as e:
            evidence = self._create_evidence(
                "exists", {"path": path},
                success=False, error=str(e)
            )
            return {
                "success": False,
                "error": str(e),
                "evidence": evidence.to_dict(),
            }
