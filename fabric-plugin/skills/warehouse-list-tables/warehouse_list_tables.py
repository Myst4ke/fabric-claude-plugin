#!/usr/bin/env python3
"""
Skill: warehouse-list-tables
Description: List all tables and views in a SQL warehouse using INFORMATION_SCHEMA

Tries the warehouse executeQuery API first, then falls back to a direct
pyodbc connection to the SQL endpoint (silent token auth).
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request_json,
                         connect_sql_endpoint, handle_http_error)

# SQL query to list all tables
LIST_TABLES_SQL = """
SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
ORDER BY TABLE_SCHEMA, TABLE_NAME
"""


def get_warehouse_connection(workspace_id, warehouse_id):
    """Get warehouse connection string from properties."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/warehouses/{warehouse_id}"
    try:
        data = fabric_request_json(url)
        return data.get('properties', {}).get('connectionString', '')
    except Exception:
        return None


def list_tables_via_pyodbc(connection_string):
    """List tables using pyodbc connection (silent token auth, no login prompt)."""
    try:
        import pyodbc  # noqa: F401 - availability check before connecting
    except ImportError:
        print("[WARN] pyodbc is not installed - SQL fallback unavailable. "
              "Install it with: pip install pyodbc (plus the Microsoft ODBC "
              "Driver 17/18 for SQL Server).", file=sys.stderr)
        return None

    try:
        # Fabric API tokens are NOT valid for the TDS endpoint;
        # connect_sql_endpoint mints a database.windows.net token silently.
        conn = connect_sql_endpoint(connection_string, 'master')
        cursor = conn.cursor()
        cursor.execute(LIST_TABLES_SQL.strip())

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"[WARN] pyodbc query failed: {e}")
        return None


def list_tables_via_api(workspace_id, warehouse_id):
    """List tables using warehouse executeQuery API."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/warehouses/{warehouse_id}/executeQuery"
    body = {'query': LIST_TABLES_SQL.strip(), 'maxRows': 5000}

    try:
        data = fabric_request_json(url, method='POST', data=body)

        results = data.get('results', [])
        if not results:
            return []

        result = results[0]
        columns = [col.get('columnName', f'col_{i}') for i, col in enumerate(result.get('columns', []))]
        rows = result.get('rows', [])

        return [dict(zip(columns, row)) for row in rows]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("[WARN] executeQuery endpoint not available. Trying pyodbc...")
            return None
        raise


def list_tables(workspace_id, warehouse_id):
    """List tables in warehouse."""
    tables = None

    # Try API first
    try:
        tables = list_tables_via_api(workspace_id, warehouse_id)
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Warehouse")
    except Exception:
        pass

    # Fallback to pyodbc
    if tables is None:
        conn_str = get_warehouse_connection(workspace_id, warehouse_id)
        if conn_str:
            tables = list_tables_via_pyodbc(conn_str)

    if tables is None:
        print("[ERROR] Could not retrieve table list. Both API and pyodbc methods failed.")
        print("\nAlternative: query directly with:")
        print(f"  fabric-plugin:warehouse-query {workspace_id} {warehouse_id} \\")
        print('    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES"')
        return 2

    display_tables(tables, workspace_id, warehouse_id)
    return 0


def display_tables(tables, workspace_id, warehouse_id):
    """Display tables in formatted output."""
    count = len(tables)
    print(f"\nFound {count} table(s)/view(s) in warehouse:\n")

    if count == 0:
        print("No tables or views found in this warehouse.")
        return

    print(f"{'Schema':<20} {'Table Name':<35} {'Type':<15}")
    print(f"{'-'*20} {'-'*35} {'-'*15}")

    for t in tables:
        schema = str(t.get('TABLE_SCHEMA', 'N/A'))[:20]
        name = str(t.get('TABLE_NAME', 'N/A'))[:35]
        ttype = str(t.get('TABLE_TYPE', 'N/A'))[:15]

        print(f"{schema:<20} {name:<35} {ttype:<15}")

    print(f"\nNext steps:")
    print(f"  - Query:  fabric-plugin:warehouse-query {workspace_id} {warehouse_id} \"SELECT TOP 10 * FROM dbo.<table>\"")


def main():
    cli = SkillCLI('warehouse_list_tables.py',
                   'List all tables and views in a SQL warehouse')
    cli.workspace()
    cli.item('warehouse')
    args = cli.parse()

    sys.exit(list_tables(args.workspace_id, args.warehouse_id))


if __name__ == "__main__":
    main()
