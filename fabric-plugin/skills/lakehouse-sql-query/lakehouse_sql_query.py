#!/usr/bin/env python3
"""
Skill: lakehouse-sql-query
Description: Execute SQL queries on lakehouse via SQL Analytics Endpoint

Uses SQL Analytics Endpoint (T-SQL) for full SQL support including:
- JOIN operations, GROUP BY / aggregations
- Complex WHERE clauses, subqueries, CTEs

Authentication is silent (cached token) - no browser prompt.
Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request_json,
                         handle_http_error, connect_sql_endpoint)


def get_lakehouse_properties(workspace_id, lakehouse_id):
    """Get lakehouse properties including SQL endpoint connection string."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
    try:
        return fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Lakehouse"))
    except Exception as e:
        print(f"[ERROR] Failed to get lakehouse properties: {e}")
        sys.exit(2)


def execute_sql_query(workspace_id, lakehouse_id, query, limit=None, verbose=False):
    """Execute SQL query via SQL Analytics Endpoint using pyodbc."""

    # Check if pyodbc is available
    try:
        import pyodbc
    except ImportError:
        print("[ERROR] pyodbc is not installed")
        print("\nThis skill requires pyodbc to connect to SQL Analytics Endpoint.")
        print("\nInstall with:")
        print("  pip install pyodbc")
        print("\nAlso ensure ODBC Driver 17 or 18 for SQL Server is installed:")
        print("  Windows: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        print("  Linux: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server")
        print("  Mac: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos")
        return 1

    # Get lakehouse properties
    print("[INFO] Retrieving lakehouse properties...")
    lakehouse = get_lakehouse_properties(workspace_id, lakehouse_id)

    # Extract SQL endpoint info
    lakehouse_name = lakehouse.get('displayName', 'unknown')
    sql_properties = lakehouse.get('properties', {}).get('sqlEndpointProperties', {})
    connection_string_host = sql_properties.get('connectionString')
    sql_endpoint_id = sql_properties.get('id')
    provisioning_status = sql_properties.get('provisioningStatus')

    if verbose:
        print(f"[DEBUG] Lakehouse: {lakehouse_name}")
        print(f"[DEBUG] SQL Endpoint ID: {sql_endpoint_id}")
        print(f"[DEBUG] Provisioning Status: {provisioning_status}")

    if not connection_string_host:
        print("[ERROR] No SQL Analytics Endpoint found for this lakehouse")
        print("SQL Analytics Endpoint is automatically created for lakehouses.")
        print("If this is a new lakehouse, wait a few moments and try again.")
        return 1

    if provisioning_status != "Success":
        print(f"[ERROR] SQL Analytics Endpoint not ready (status: {provisioning_status})")
        print("Wait for provisioning to complete and try again.")
        return 1

    # Apply LIMIT if specified
    query_upper = query.strip().upper()
    if limit and 'LIMIT' not in query_upper and 'TOP' not in query_upper:
        if query_upper.startswith('SELECT'):
            # T-SQL uses TOP, not LIMIT
            query = query.replace('SELECT', f'SELECT TOP {limit}', 1)
        else:
            print(f"[WARN] Cannot apply LIMIT to non-SELECT query")

    try:
        print(f"[INFO] Connecting to SQL Analytics Endpoint...")
        print(f"[INFO] Server: {connection_string_host}")
        print(f"[INFO] Database: {lakehouse_name}")
        print()

        # Connect with cached delegated token (database.windows.net audience).
        # Silent - never opens an interactive login window.
        connection = connect_sql_endpoint(connection_string_host, lakehouse_name)
        cursor = connection.cursor()

        print(f"[INFO] Executing query...")
        if verbose:
            print(f"[DEBUG] Query: {query[:200]}{'...' if len(query) > 200 else ''}")
        print()

        # Execute query
        cursor.execute(query)

        # Fetch results
        columns = [column[0] for column in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        # Close connection
        cursor.close()
        connection.close()

        # Display results
        display_results(rows, columns, lakehouse_name, query)

        return 0

    except pyodbc.Error as e:
        print(f"[ERROR] SQL execution failed")
        print(f"Error: {e}")

        # Provide helpful hints based on error
        error_str = str(e).lower()
        if 'login failed' in error_str or 'authentication' in error_str or 'token' in error_str:
            print("\nAuthentication failed. Please ensure:")
            print("  1. You have access to the workspace")
            print("  2. Your session is valid - re-run /fabric-plugin:setup:login if needed")
        elif 'invalid object name' in error_str:
            print("\nTable not found. Please ensure:")
            print("  1. Table name is correct (case-sensitive)")
            print("  2. Schema prefix is included (e.g., 'dbo.tablename')")
            print("  3. Table exists in the lakehouse")
        elif 'syntax error' in error_str:
            print("\nSQL syntax error. Please check:")
            print("  1. Query uses T-SQL syntax (SQL Server compatible)")
            print("  2. All table and column names are correct")
            print("  3. Proper use of quotes (single quotes for strings)")

        return 1

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 2


def display_results(rows, columns, lakehouse_name, query):
    """Display query results in formatted output."""
    row_count = len(rows)
    col_count = len(columns)

    print()
    print("=" * 120)
    print(f"  SQL Query Results - Lakehouse: {lakehouse_name}")
    print("=" * 120)
    print()
    print(f"Rows: {row_count} | Columns: {col_count}")
    print()

    if row_count == 0:
        print("(No results)")
        print()
        return

    # Calculate column widths
    col_widths = [len(col) for col in columns]

    for row in rows[:100]:  # Sample first 100 rows for width calculation
        for i, val in enumerate(row):
            if i < len(col_widths):
                val_str = str(val) if val is not None else "NULL"
                col_widths[i] = max(col_widths[i], min(len(val_str), 30))

    # Display header
    header = "  ".join([f"{col:<{col_widths[i]}}" for i, col in enumerate(columns)])
    print(header)
    print("  ".join(["-" * col_widths[i] for i in range(len(columns))]))

    # Display rows (max 100)
    for row in rows[:100]:
        values = []
        for i, val in enumerate(row):
            if i < len(col_widths):
                if val is None:
                    val_str = "NULL"
                else:
                    val_str = str(val)
                    if len(val_str) > 30:
                        val_str = val_str[:27] + "..."
                values.append(f"{val_str:<{col_widths[i]}}")
        print("  ".join(values))

    if row_count > 100:
        print()
        print(f"[INFO] Showing first 100 rows of {row_count} total")

    print()


def main():
    cli = SkillCLI('lakehouse_sql_query.py',
                   'Execute SQL query on lakehouse via SQL Analytics Endpoint (T-SQL)')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('query', help='SQL query (T-SQL syntax, e.g. "SELECT TOP 10 * FROM dbo.customers")')
    cli.opt('--limit', type=int, help='Maximum rows to return (adds TOP clause)')
    cli.flag('--verbose', help='Enable verbose debug output')
    args = cli.parse()

    sys.exit(execute_sql_query(
        args.workspace_id,
        args.lakehouse_id,
        args.query,
        args.limit,
        args.verbose
    ))


if __name__ == "__main__":
    main()
