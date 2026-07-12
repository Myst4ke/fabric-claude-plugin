#!/usr/bin/env python3
"""
Skill: warehouse-query
Description: Execute read-only SQL query on a Microsoft Fabric warehouse

Security features:
- Read-only mode (SELECT only)
- SQL injection validation
- Row limit enforcement
- Audit logging
"""

import sys
import os
import re
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error
from security_guard import (check_permission, require_confirmation,
                            validate_sql_safe, SecurityGuard, SecurityViolation)
from audit_logger import log_query


def execute_query(workspace_id, warehouse_id, query, limit=None):
    """Execute SQL query on warehouse."""

    # 1. Check permission
    try:
        check_permission(workspace_id, "warehouse:query")
    except SecurityViolation as e:
        print(str(e))
        log_query("warehouse:query", workspace_id, query, False, error="Permission denied")
        return 1

    # 2. Validate SQL is read-only
    try:
        validate_sql_safe(query)
    except SecurityViolation as e:
        print(str(e))
        log_query("warehouse:query", workspace_id, query, False, error="SQL validation failed")
        return 1

    # 3. Get row limit from security policy (apply most restrictive limit)
    guard = SecurityGuard()
    policy_limit = guard.get_max_query_rows(workspace_id)
    if policy_limit is not None:
        if limit is None or limit > policy_limit:
            print(f"[INFO] Applying security policy limit: {policy_limit} rows")
            limit = policy_limit

    # 4. Request confirmation if needed
    env_name = guard.get_environment_name(workspace_id)
    if not require_confirmation(
        workspace_id,
        "warehouse:query",
        f"Execute SQL query on warehouse in {env_name or 'this environment'}"
    ):
        print("[INFO] Operation cancelled by user")
        log_query("warehouse:query", workspace_id, query, False, error="Cancelled by user")
        return 1

    # Add TOP clause if a limit is set and the query has none (case-insensitive)
    query_upper = query.upper().strip()
    if limit and 'LIMIT' not in query_upper and 'TOP' not in query_upper:
        new_query, n = re.subn(r'(?i)^\s*SELECT\b', f'SELECT TOP {limit}',
                               query, count=1)
        if n:
            query = new_query
        else:
            print(f"[WARN] Cannot apply LIMIT to non-SELECT query")

    # Fabric Warehouse uses SQL Analytics Endpoint
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/warehouses/{warehouse_id}/executeQuery"

    try:
        print(f"[INFO] Executing query on warehouse...")
        print(f"[DEBUG] Query: {query[:200]}{'...' if len(query) > 200 else ''}")
        print()

        result = fabric_request_json(url, method='POST', data={'query': query})

        rows = result.get('rows', [])
        columns = result.get('columns', [])

        # Apply row limit if needed
        if limit and len(rows) > limit:
            rows = rows[:limit]
            print(f"[INFO] Results truncated to {limit} rows")

        log_query("warehouse:query", workspace_id, query, True,
                  warehouse_id=warehouse_id, rows_returned=len(rows),
                  columns=len(columns))

        display_results(rows, columns, warehouse_id, query)
        return 0

    except urllib.error.HTTPError as e:
        code = handle_http_error(e, "Warehouse")
        log_query("warehouse:query", workspace_id, query, False,
                  error=f"HTTP {e.code}", http_code=e.code, warehouse_id=warehouse_id)
        return code

    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        log_query("warehouse:query", workspace_id, query, False,
                  error=str(e), warehouse_id=warehouse_id)
        return 2


def display_results(rows, columns, warehouse_id, query):
    """Display query results in formatted output."""
    row_count = len(rows)
    col_count = len(columns)

    print()
    print("=" * 100)
    print(f"  Query Results - Warehouse: {warehouse_id}")
    print("=" * 100)
    print()
    print(f"Rows: {row_count} | Columns: {col_count}")
    print()

    if row_count == 0:
        print("(No results)")
        return

    # Get column names
    col_names = [col.get('name', f'col_{i}') for i, col in enumerate(columns)]

    # Format rows
    print("  ".join([f"{name:<20}" for name in col_names]))
    print("  ".join(["-" * 20 for _ in col_names]))

    for row in rows[:100]:  # Max 100 rows displayed
        values = []
        for val in row:
            if val is None:
                values.append("NULL")
            elif isinstance(val, str) and len(val) > 20:
                values.append(val[:17] + "...")
            else:
                values.append(str(val))
        print("  ".join([f"{val:<20}" for val in values]))

    if row_count > 100:
        print()
        print(f"[INFO] Showing first 100 rows of {row_count} total")

    print()


def main():
    cli = SkillCLI('warehouse_query.py',
                   'Execute read-only SQL query on a Microsoft Fabric warehouse')
    cli.workspace()
    cli.item('warehouse')
    cli.positional('query', help='SQL query (SELECT only)')
    cli.opt('--limit', type=int, help='Maximum rows to return')
    args = cli.parse()

    sys.exit(execute_query(args.workspace_id, args.warehouse_id,
                           args.query, args.limit))


if __name__ == "__main__":
    main()
