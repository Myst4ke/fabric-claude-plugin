#!/usr/bin/env python3
"""
Security Guard - Access control and validation for Fabric operations.
"""

import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


class SecurityViolation(Exception):
    """Raised when a security policy is violated."""
    pass


class SecurityGuard:
    """Enforces security policies for Fabric operations."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize security guard with configuration."""
        if config_path is None:
            # Default: look for config/security.json relative to this file
            config_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                '..',
                'config',
                'security.json'
            )

        self.config = self._load_config(config_path)
        self.default_policy = self.config.get('default_policy', 'read-only')

    def _load_config(self, path: str) -> Dict:
        """Load security configuration."""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                # Replace $TEMP in paths (resolves to the plugin cache dir)
                try:
                    from token_manager import CACHE_DIR as temp_dir
                except ImportError:
                    temp_dir = os.getenv("TEMP", "/tmp")
                if 'audit' in config and 'log_file' in config['audit']:
                    config['audit']['log_file'] = config['audit']['log_file'].replace('$TEMP', temp_dir)
                return config
        except FileNotFoundError:
            # Opt-in security model: with no config file the plugin runs
            # unrestricted. Copy config/security.json.example to
            # config/security.json to enable per-environment guardrails.
            print(f"[INFO] No security config at {path} - running unrestricted "
                  f"(opt-in mode). Copy config/security.json.example to enable guardrails.")
            return {
                'default_policy': 'allow',
                'environments': {},
                'audit': {'enabled': True}
            }
        except Exception as e:
            print(f"[ERROR] Failed to load security config: {e}")
            sys.exit(1)

    def check_operation(
        self,
        workspace_id: str,
        operation: str,
        **kwargs
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if operation is allowed.

        Returns:
            (allowed: bool, reason: Optional[str])
        """
        # 1. Identify environment
        env = self._identify_environment(workspace_id)

        if env is None:
            # Opt-in model: workspaces not listed in security.json are unmanaged
            # and allowed (check_permission surfaces a warning).
            return True, f"Workspace {workspace_id} not in security.json - allowed (opt-in, unmanaged)"

        # 2. Check if operation is allowed
        env_config = self.config['environments'][env]

        # Check denied operations first (explicit deny wins)
        denied = env_config.get('denied_operations', [])
        if operation in denied:
            return False, f"Operation '{operation}' is explicitly denied in {env.upper()} environment"

        # Check operation category (e.g., "notebook:run" → check "notebook:*")
        if ':' in operation:
            category = operation.split(':')[0]
            if f"{category}:*" in denied or category in denied:
                return False, f"All '{category}' operations are denied in {env.upper()} environment"

        # Check allowed operations
        allowed = env_config.get('allowed_operations', [])

        # Wildcard: allow all
        if '*' in allowed:
            return True, None

        # Exact match
        if operation in allowed:
            return True, None

        # Category match (e.g., "notebook:*")
        if ':' in operation:
            category = operation.split(':')[0]
            if f"{category}:*" in allowed:
                return True, None

        # Default deny
        return False, f"Operation '{operation}' not in allowed list for {env.upper()} environment"

    def _identify_environment(self, workspace_id: str) -> Optional[str]:
        """Identify environment (prod/uat/dev) from workspace ID."""
        for env_name, env_config in self.config['environments'].items():
            if workspace_id in env_config.get('workspaces', []):
                return env_name
        return None

    def get_environment_name(self, workspace_id: str) -> Optional[str]:
        """Get environment name for workspace."""
        env = self._identify_environment(workspace_id)
        if env:
            return self.config['environments'][env].get('display_name', env.upper())
        return None

    def requires_confirmation(self, workspace_id: str, operation: str) -> bool:
        """Check if operation requires user confirmation."""
        env = self._identify_environment(workspace_id)
        if env is None:
            return False  # Opt-in: unmanaged workspace, no confirmation gate

        env_config = self.config['environments'][env]
        return env_config.get('require_confirmation', False)

    def get_max_query_rows(self, workspace_id: str) -> Optional[int]:
        """Get maximum allowed query result rows for environment."""
        env = self._identify_environment(workspace_id)
        if env is None:
            return 1000  # Safe default

        env_config = self.config['environments'][env]
        return env_config.get('max_query_rows')

    def validate_sql_query(self, query: str, allow_write: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safety.

        Args:
            query: SQL query to validate
            allow_write: If False (default), deny write operations

        Returns:
            (is_safe: bool, reason: Optional[str])
        """
        query_upper = query.upper().strip()

        # Check for write operations if not allowed
        if not allow_write:
            write_keywords = [
                'DELETE ', 'DROP ', 'TRUNCATE ', 'ALTER ',
                'CREATE ', 'INSERT ', 'UPDATE ', 'MERGE '
            ]

            for keyword in write_keywords:
                if keyword in query_upper:
                    return False, f"Query contains write operation: {keyword.strip()} (read-only mode)"

        # Check for SQL injection patterns
        suspicious_patterns = [
            ('--', 'SQL comment'),
            ('/*', 'Multi-line comment'),
            ('*/', 'Multi-line comment'),
            ('EXEC ', 'Dynamic execution'),
            ('EXECUTE ', 'Dynamic execution'),
            ('xp_', 'System procedure'),
            ('sp_', 'System procedure'),
            (';--', 'Comment injection'),
            ("';", 'Quote injection'),
            ('";', 'Quote injection'),
            (' OR 1=1', 'Boolean injection'),
            (' OR \'1\'=\'1', 'Boolean injection')
        ]

        for pattern, description in suspicious_patterns:
            if pattern.upper() in query_upper:
                return False, f"Query contains suspicious pattern: {description}"

        return True, None


def check_permission(workspace_id: str, operation: str) -> bool:
    """
    Convenience function to check permission.
    Raises SecurityViolation if denied.
    """
    guard = SecurityGuard()
    allowed, reason = guard.check_operation(workspace_id, operation)

    if not allowed:
        raise SecurityViolation(f"\n[SECURITY DENIED] {reason}")

    # Allowed but with a reason set = opt-in/unmanaged workspace: surface a warning.
    if reason:
        print(f"[SECURITY] {reason}")

    return True


def require_confirmation(workspace_id: str, operation: str, message: str) -> bool:
    """
    Ask user for confirmation if required by policy.
    """
    guard = SecurityGuard()

    if not guard.requires_confirmation(workspace_id, operation):
        return True  # No confirmation needed

    env_name = guard.get_environment_name(workspace_id)

    print()
    print("=" * 60)
    print("[SECURITY] User confirmation required")
    print("=" * 60)
    print(f"  Environment: {env_name or 'UNKNOWN'}")
    print(f"  Operation:   {operation}")
    print(f"  Message:     {message}")
    print("=" * 60)
    print()

    try:
        response = input("Continue with this operation? [y/N]: ").strip().lower()
        return response in ['y', 'yes']
    except (KeyboardInterrupt, EOFError):
        print("\n[SECURITY] Operation cancelled by user")
        return False


def validate_sql_safe(query: str) -> bool:
    """
    Validate SQL query is safe (read-only).
    Raises SecurityViolation if dangerous.
    """
    guard = SecurityGuard()
    is_safe, reason = guard.validate_sql_query(query, allow_write=False)

    if not is_safe:
        raise SecurityViolation(f"\n[SECURITY DENIED] {reason}")

    return True
