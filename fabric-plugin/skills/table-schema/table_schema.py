#!/usr/bin/env python3
"""
Skill: table-schema
Description: Get table schema information

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def handle_query_error(error, table_name):
    """Handle HTTP errors, treating 400 as a permanent invalid-table error."""
    if error.code == 400:
        try:
            error_body = json.loads(error.read().decode('utf-8'))
            message = error_body.get('error', {}).get('message', 'Invalid table')
            print(f"[ERROR] {message}")
        except Exception:
            print(f"[ERROR] Table not found or invalid: {table_name}")
        _print_schema_hint()
        return 1
    rc = handle_http_error(error, "Table")
    if error.code == 404:
        _print_schema_hint()
    return rc

def _print_schema_hint():
    print("")
    print("[INFO] If this lakehouse has schemas enabled, the REST query API cannot")
    print("       see its tables. Get the schema via SQL instead:")
    print("  fabric-plugin:lakehouse-sql-query <workspace> <lakehouse> \\")
    print("    \"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS\"")
    print("    \" WHERE TABLE_NAME = '<table>' ORDER BY ORDINAL_POSITION\"")



def get_table_schema(workspace_id, lakehouse_id, table_name):
    """Get table schema using DESCRIBE TABLE."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/query"
    body = {'query': f'DESCRIBE TABLE {table_name}'}

    print(f"Getting schema for table '{table_name}'...")
    print("")

    try:
        result = fabric_request_json(url, method='POST', data=body)
        display_schema(result, table_name)
        return 0

    except urllib.error.HTTPError as e:
        return handle_query_error(e, table_name)
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def display_schema(result, table_name):
    """Display table schema."""
    rows = result.get('rows', [])

    print(f"Schema for table '{table_name}':")
    print("=" * 70)
    print("")

    if not rows:
        print("(No schema information available)")
        return

    # Header
    print(f"{'Column Name':<30} {'Data Type':<25} {'Nullable':<10}")
    print(f"{'-'*30} {'-'*25} {'-'*10}")

    # Rows from DESCRIBE
    for row in rows:
        if len(row) >= 2:
            col_name = str(row[0])[:30]
            data_type = str(row[1])[:25]
            nullable = str(row[2]) if len(row) > 2 else 'N/A'
            print(f"{col_name:<30} {data_type:<25} {nullable:<10}")

    print("")
    print(f"Total columns: {len(rows)}")


def main():
    cli = SkillCLI('table_schema.py', 'Get table schema information')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Table name')
    args = cli.parse()

    sys.exit(get_table_schema(args.workspace_id, args.lakehouse_id, args.table_name))


if __name__ == "__main__":
    main()
