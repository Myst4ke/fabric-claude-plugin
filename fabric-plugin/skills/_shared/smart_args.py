#!/usr/bin/env python3
"""
Smart Arguments Module

Provides automatic name-to-ID resolution for skill arguments.
Skills can import this module to accept both names and GUIDs.

Usage:
    from smart_args import SmartResolver

    resolver = SmartResolver()
    workspace_id = resolver.workspace(sys.argv[1])
    notebook_id = resolver.notebook(sys.argv[2], workspace_id)
"""

import os
import sys
from typing import Optional, Tuple

# Add current directory for fabric_resolver import
sys.path.insert(0, os.path.dirname(__file__))

from fabric_resolver import (
    is_guid,
    load_token,
    FabricCache,
    resolve_workspace,
    resolve_item,
    resolve_table,
    AuthenticationError,
    NotFoundError,
    AmbiguousMatchError,
    ResolverError
)


class SmartResolver:
    """
    Smart argument resolver that handles both names and GUIDs.

    Usage:
        resolver = SmartResolver()
        workspace_id = resolver.workspace("My Workspace")
        notebook_id = resolver.notebook("Sales Analysis", workspace_id)
    """

    def __init__(self, token: Optional[str] = None, cache: Optional[FabricCache] = None):
        """
        Initialize resolver.

        Args:
            token: Access token (loaded automatically if not provided)
            cache: Cache instance (created automatically if not provided)
        """
        self._token = token
        self._cache = cache
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of token and cache."""
        if not self._initialized:
            if self._token is None:
                self._token = load_token()
            if self._cache is None:
                self._cache = FabricCache()
            self._initialized = True

    def workspace(self, name_or_id: str) -> str:
        """
        Resolve workspace name to ID.

        Args:
            name_or_id: Workspace name or GUID

        Returns:
            Workspace GUID
        """
        if is_guid(name_or_id):
            return name_or_id

        self._ensure_initialized()
        result = resolve_workspace(name_or_id, self._token, self._cache)
        return result['id']

    def notebook(self, name_or_id: str, workspace_id: str) -> str:
        """
        Resolve notebook name to ID.

        Args:
            name_or_id: Notebook name or GUID
            workspace_id: Workspace GUID (must already be resolved)

        Returns:
            Notebook GUID
        """
        if is_guid(name_or_id):
            return name_or_id

        self._ensure_initialized()
        result = resolve_item(name_or_id, workspace_id, 'notebook', self._token, self._cache)
        return result['id']

    def pipeline(self, name_or_id: str, workspace_id: str) -> str:
        """
        Resolve pipeline name to ID.

        Args:
            name_or_id: Pipeline name or GUID
            workspace_id: Workspace GUID

        Returns:
            Pipeline GUID
        """
        if is_guid(name_or_id):
            return name_or_id

        self._ensure_initialized()
        result = resolve_item(name_or_id, workspace_id, 'pipeline', self._token, self._cache)
        return result['id']

    def lakehouse(self, name_or_id: str, workspace_id: str) -> str:
        """
        Resolve lakehouse name to ID.

        Args:
            name_or_id: Lakehouse name or GUID
            workspace_id: Workspace GUID

        Returns:
            Lakehouse GUID
        """
        if is_guid(name_or_id):
            return name_or_id

        self._ensure_initialized()
        result = resolve_item(name_or_id, workspace_id, 'lakehouse', self._token, self._cache)
        return result['id']

    def table(self, name: str, workspace_id: str, lakehouse_id: str) -> str:
        """
        Resolve table name (tables don't have GUIDs, returns name).

        Args:
            name: Table name
            workspace_id: Workspace GUID
            lakehouse_id: Lakehouse GUID

        Returns:
            Table name (verified to exist)
        """
        self._ensure_initialized()
        result = resolve_table(name, workspace_id, lakehouse_id, self._token, self._cache)
        return result.get('name', name)

    def item(self, name_or_id: str, workspace_id: str, item_type: str) -> str:
        """
        Resolve any item type by name.

        Args:
            name_or_id: Item name or GUID
            workspace_id: Workspace GUID
            item_type: Type of item (notebook, pipeline, lakehouse, etc.)

        Returns:
            Item GUID
        """
        if is_guid(name_or_id):
            return name_or_id

        self._ensure_initialized()
        result = resolve_item(name_or_id, workspace_id, item_type, self._token, self._cache)
        return result['id']


def resolve_workspace_and_item(workspace_arg: str, item_arg: str,
                               item_type: str) -> Tuple[str, str]:
    """
    Convenience function to resolve both workspace and item in one call.

    Args:
        workspace_arg: Workspace name or GUID
        item_arg: Item name or GUID
        item_type: Type of item (notebook, pipeline, lakehouse)

    Returns:
        Tuple of (workspace_id, item_id)

    Example:
        workspace_id, notebook_id = resolve_workspace_and_item(
            sys.argv[1], sys.argv[2], 'notebook'
        )
    """
    resolver = SmartResolver()
    workspace_id = resolver.workspace(workspace_arg)
    item_id = resolver.item(item_arg, workspace_id, item_type)
    return workspace_id, item_id


def resolve_workspace_lakehouse_table(workspace_arg: str, lakehouse_arg: str,
                                      table_arg: str) -> Tuple[str, str, str]:
    """
    Convenience function to resolve workspace, lakehouse, and table.

    Args:
        workspace_arg: Workspace name or GUID
        lakehouse_arg: Lakehouse name or GUID
        table_arg: Table name

    Returns:
        Tuple of (workspace_id, lakehouse_id, table_name)
    """
    resolver = SmartResolver()
    workspace_id = resolver.workspace(workspace_arg)
    lakehouse_id = resolver.lakehouse(lakehouse_arg, workspace_id)
    table_name = resolver.table(table_arg, workspace_id, lakehouse_id)
    return workspace_id, lakehouse_id, table_name


# Error handling helpers
def handle_resolution_error(error: Exception, quiet: bool = False) -> int:
    """
    Handle resolution errors with appropriate messages and exit codes.

    Args:
        error: The exception that was raised
        quiet: If True, suppress output

    Returns:
        Exit code (1=not found, 2=ambiguous, 3=auth, 4=other)
    """
    if isinstance(error, AuthenticationError):
        if not quiet:
            print(f"[AUTH ERROR] {error}")
        return 3
    elif isinstance(error, NotFoundError):
        if not quiet:
            print(f"[NOT FOUND] {error}")
        return 1
    elif isinstance(error, AmbiguousMatchError):
        if not quiet:
            print(f"[AMBIGUOUS] {error}")
            print("\nMultiple matches found:")
            for m in error.matches:
                name = m.get('name') or m.get('displayName', 'Unknown')
                print(f"  - {name} (score: {m['score']:.2f})")
            print("\nUse a more specific name or the full GUID.")
        return 2
    elif isinstance(error, ResolverError):
        if not quiet:
            print(f"[ERROR] {error}")
        return 4
    else:
        if not quiet:
            print(f"[ERROR] Unexpected error: {error}")
        return 4


# Convenience decorator for skills that use workspace + item pattern
def with_name_resolution(item_type: str):
    """
    Decorator to add name resolution to skill main functions.

    Usage:
        @with_name_resolution('notebook')
        def run_notebook(workspace_id: str, notebook_id: str):
            # workspace_id and notebook_id are guaranteed to be GUIDs
            ...
    """
    def decorator(func):
        def wrapper(workspace_arg: str, item_arg: str, *args, **kwargs):
            try:
                resolver = SmartResolver()
                workspace_id = resolver.workspace(workspace_arg)
                item_id = resolver.item(item_arg, workspace_id, item_type)
                return func(workspace_id, item_id, *args, **kwargs)
            except (AuthenticationError, NotFoundError, AmbiguousMatchError, ResolverError) as e:
                return handle_resolution_error(e)
        return wrapper
    return decorator
