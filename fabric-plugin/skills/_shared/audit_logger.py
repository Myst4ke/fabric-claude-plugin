#!/usr/bin/env python3
"""
Audit Logger - Track all Fabric operations for compliance and security.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional


class AuditLogger:
    """Logs all Fabric operations to audit trail."""

    def __init__(self, log_file: Optional[str] = None):
        """Initialize audit logger."""
        if log_file is None:
            try:
                from token_manager import CACHE_DIR as cache_dir
            except ImportError:
                cache_dir = os.getenv("TEMP", "/tmp")
            log_file = f"{cache_dir}/fabric-plugin-audit.jsonl"

        self.log_file = log_file
        self.enabled = True
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Create log file if it doesn't exist."""
        try:
            if not os.path.exists(self.log_file):
                os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
                with open(self.log_file, 'w') as f:
                    pass  # Create empty file
        except Exception as e:
            print(f"[WARN] Failed to create audit log file: {e}", file=sys.stderr)
            self.enabled = False

    def log_operation(
        self,
        operation: str,
        workspace_id: str,
        success: bool,
        **kwargs
    ):
        """
        Log an operation to audit trail.

        Args:
            operation: Operation name (e.g., "warehouse:query")
            workspace_id: Target workspace GUID
            success: Whether operation succeeded
            **kwargs: Additional context (environment, item_id, error, etc.)
        """
        if not self.enabled:
            return

        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'operation': operation,
            'workspace_id': workspace_id,
            'success': success,
            'user': os.getenv('USERNAME', os.getenv('USER', 'unknown')),
            'hostname': os.getenv('COMPUTERNAME', os.getenv('HOSTNAME', 'unknown')),
            **kwargs
        }

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            # Never fail the operation due to audit logging
            print(f"[WARN] Failed to write audit log: {e}", file=sys.stderr)


# Singleton instance
_logger = None


def get_logger() -> AuditLogger:
    """Get singleton audit logger instance."""
    global _logger
    if _logger is None:
        _logger = AuditLogger()
    return _logger


def log_operation(operation: str, workspace_id: str, success: bool, **kwargs):
    """Convenience function to log operation."""
    get_logger().log_operation(operation, workspace_id, success, **kwargs)


def log_query(operation: str, workspace_id: str, query: str, success: bool, **kwargs):
    """Log a SQL/KQL query operation."""
    # Truncate query if very long
    query_truncated = query if len(query) < 500 else query[:497] + '...'

    get_logger().log_operation(
        operation=operation,
        workspace_id=workspace_id,
        success=success,
        query=query_truncated,
        **kwargs
    )
