#!/usr/bin/env python3
"""
Fabric Base - Standard bootstrap for all fabric-plugin skills.

Provides unified access to:
- Token management (auto-refresh)
- Retry logic (exponential backoff on 429/500/503)
- Security checks (warning-only mode)
- Audit logging
- Standardized API requests

Usage:
    # Minimal: just replace load_token()
    from fabric_base import get_token
    token = get_token()

    # Full: use fabric_request() for automatic retry + refresh
    from fabric_base import fabric_request
    status, data, headers = fabric_request(url)

    # Security check (warning only)
    from fabric_base import check_security
    check_security(workspace_id, "notebook:run")
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

# Ensure _shared modules are importable
_shared_dir = os.path.dirname(os.path.abspath(__file__))
if _shared_dir not in sys.path:
    sys.path.insert(0, _shared_dir)

from token_manager import (
    get_fabric_token, get_sql_token, get_storage_token,
    get_graph_token, get_kusto_token, TokenManager,
)
from token_manager import get_token as get_token_for_audience
from retry_handler import RetryHandler

FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"

# SQL_COPT_SS_ACCESS_TOKEN connection attribute (msodbcsql driver)
SQL_COPT_SS_ACCESS_TOKEN = 1256


# =============================================================================
# Token Management
# =============================================================================

def get_token(force_refresh=False, audience='fabric'):
    """
    Get a valid access token with automatic silent refresh.

    Replaces the legacy load_token() pattern. Audiences: fabric (default),
    sql, storage, graph, kusto.

    Returns:
        str: Valid access token

    Raises:
        SystemExit(3): If authentication fails entirely
    """
    return get_token_for_audience(audience, force_refresh=force_refresh)


# =============================================================================
# SQL Analytics Endpoint Connections (pyodbc, token-based - NO interactive prompt)
# =============================================================================

def pick_odbc_driver():
    """
    Pick the best available SQL Server ODBC driver (18 preferred, then 17).

    Returns:
        str: Driver name, e.g. "ODBC Driver 18 for SQL Server"

    Raises:
        RuntimeError: If no suitable driver is installed
    """
    import pyodbc
    available = pyodbc.drivers()
    for candidate in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"):
        if candidate in available:
            return candidate
    raise RuntimeError(
        "No SQL Server ODBC driver found (need ODBC Driver 17 or 18). "
        f"Installed drivers: {available}"
    )


def sql_token_struct(token):
    """
    Pack an access token into the SQL_COPT_SS_ACCESS_TOKEN structure
    expected by the msodbcsql driver: <length:uint32-le><token:utf-16-le>.
    """
    import struct
    token_bytes = token.encode('utf-16-le')
    return struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)


def connect_sql_endpoint(server, database, timeout=30):
    """
    Open a pyodbc connection to a Fabric SQL analytics endpoint using the
    cached delegated credentials - silently, with NO interactive login window.

    Uses a database.windows.net-audience token minted from the cached refresh
    token (Fabric API tokens are rejected by the TDS endpoint).

    Args:
        server: SQL endpoint host (lakehouse sqlEndpointProperties.connectionString
                or warehouse properties.connectionString)
        database: Database name (lakehouse or warehouse display name)
        timeout: Login timeout in seconds

    Returns:
        pyodbc.Connection
    """
    import pyodbc

    driver = pick_odbc_driver()
    token = get_sql_token()

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )

    return pyodbc.connect(
        conn_str,
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: sql_token_struct(token)},
        timeout=timeout,
    )


# =============================================================================
# API Requests with Retry + Auto-Refresh
# =============================================================================

def fabric_request(url, method='GET', data=None, headers=None, timeout=30):
    """
    Make a Fabric API request with automatic retry and token refresh.

    Features:
    - Auto-refreshing token (handles 401 transparently)
    - Retry on transient errors: 429, 500, 502, 503, 504
    - Exponential backoff with Retry-After header support
    - Timeout protection

    Args:
        url: Full API URL
        method: HTTP method (GET, POST, PATCH, DELETE)
        data: Request body (dict or bytes). Dicts are JSON-encoded.
        headers: Additional headers (Authorization is added automatically)
        timeout: Request timeout in seconds

    Returns:
        urllib.response object (call .read(), .status, .headers on it)

    Raises:
        urllib.error.HTTPError: On non-retryable HTTP errors
        SystemExit(3): On authentication failure
    """
    token = get_token()

    if headers is None:
        headers = {}
    headers['Authorization'] = f'Bearer {token}'
    headers.setdefault('Content-Type', 'application/json')

    req_data = None
    if data is not None:
        if isinstance(data, dict):
            req_data = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            req_data = data.encode('utf-8')
        else:
            req_data = data

    retry = RetryHandler(max_retries=3)
    _refreshed = [False]  # use list for nonlocal mutation in nested func

    def _do_request():
        nonlocal token
        headers['Authorization'] = f'Bearer {token}'

        request = urllib.request.Request(
            url, data=req_data, headers=headers, method=method
        )

        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code == 401 and not _refreshed[0]:
                # Token expired mid-request, refresh once and retry
                _refreshed[0] = True
                token = get_token(force_refresh=True)
                headers['Authorization'] = f'Bearer {token}'
                request = urllib.request.Request(
                    url, data=req_data, headers=headers, method=method
                )
                return urllib.request.urlopen(request, timeout=timeout)
            raise

    return retry.execute_with_retry(_do_request)


def fabric_request_json(url, method='GET', data=None, headers=None, timeout=30):
    """fabric_request + JSON decode of the body. Returns a dict (or {})."""
    response = fabric_request(url, method=method, data=data,
                              headers=headers, timeout=timeout)
    body = response.read().decode('utf-8')
    return json.loads(body) if body else {}


def fabric_list(url, limit=None, item_key='value'):
    """
    Fetch ALL items from a paginated Fabric list endpoint.

    Handles continuationToken transparently (URL-encoded), with the same
    retry/refresh guarantees as fabric_request(). Stops early when `limit`
    is reached.

    Args:
        url: Full list endpoint URL (without continuation params)
        limit: Optional max number of items to return
        item_key: Key of the items array in the response (default 'value')

    Returns:
        list: All items across pages (truncated to limit if given)
    """
    import urllib.parse as _parse

    items = []
    continuation = None
    while True:
        page_url = url
        if continuation:
            sep = '&' if '?' in url else '?'
            page_url = f"{url}{sep}continuationToken={_parse.quote(continuation, safe='')}"

        data = fabric_request_json(page_url)
        items.extend(data.get(item_key, []))

        if limit is not None and len(items) >= limit:
            return items[:limit]

        continuation = data.get('continuationToken')
        if not continuation:
            return items


# =============================================================================
# Security (Warning-Only Mode)
# =============================================================================

def check_security(workspace_id, operation):
    """
    Check security policy and print warning if operation is restricted.

    WARNING-ONLY mode: never blocks execution, only warns.
    This allows operations to proceed while informing the user
    about policy violations.

    Args:
        workspace_id: Target workspace GUID
        operation: Operation name (e.g., "notebook:run", "lakehouse:delete")
    """
    try:
        from security_guard import SecurityGuard
        guard = SecurityGuard()
        allowed, reason = guard.check_operation(workspace_id, operation)

        if not allowed:
            env_name = guard.get_environment_name(workspace_id) or "UNKNOWN"
            print(f"\n[SECURITY WARNING] {reason}")
            print(f"  Environment: {env_name}")
            print(f"  Operation:   {operation}")
            print(f"  Status:      Proceeding (warning-only mode)\n")

    except ImportError:
        pass  # security_guard not available, skip silently
    except Exception:
        pass  # never block execution due to security check failures


# =============================================================================
# Audit Logging
# =============================================================================

def log_audit(operation, workspace_id, success, **kwargs):
    """
    Log operation to audit trail (fire-and-forget).

    Never raises exceptions or blocks execution.

    Args:
        operation: Operation name (e.g., "notebook:run")
        workspace_id: Target workspace GUID
        success: Whether operation succeeded
        **kwargs: Additional context
    """
    try:
        from audit_logger import log_operation
        log_operation(operation, workspace_id, success, **kwargs)
    except ImportError:
        pass  # audit_logger not available
    except Exception:
        pass  # never fail due to audit logging


# =============================================================================
# Standardized Error Handling
# =============================================================================

def handle_http_error(error, resource_type="Resource"):
    """
    Standardized HTTP error handling with proper exit codes.

    Args:
        error: urllib.error.HTTPError
        resource_type: Name for error messages (e.g., "Notebook", "Pipeline")

    Returns:
        int: Exit code (1=permanent, 2=retryable, 3=auth)
    """
    if error.code == 401:
        print("[ERROR] Unauthorized. Token expired.")
        print("Run: /fabric-plugin:setup:login")
        return 3
    elif error.code == 403:
        print(f"[ERROR] Forbidden. Check workspace permissions for this {resource_type.lower()}.")
        return 1
    elif error.code == 404:
        print(f"[ERROR] {resource_type} not found. Verify the ID is correct.")
        return 1
    elif error.code == 429:
        retry_after = error.headers.get('Retry-After', '?')
        print(f"[ERROR] Rate limited. Retry after {retry_after}s.")
        return 2
    elif error.code in [500, 502, 503, 504]:
        print(f"[ERROR] Server error ({error.code}). This is usually transient, retry shortly.")
        return 2
    else:
        try:
            error_body = error.read().decode('utf-8')
            print(f"[ERROR] HTTP {error.code}: {error.reason}")
            if error_body:
                # Try to parse as JSON for cleaner output
                try:
                    err_json = json.loads(error_body)
                    msg = err_json.get('error', {}).get('message', error_body[:500])
                    print(f"Details: {msg}")
                except json.JSONDecodeError:
                    print(f"Details: {error_body[:500]}")
        except Exception:
            print(f"[ERROR] HTTP {error.code}: {error.reason}")
        return 2
