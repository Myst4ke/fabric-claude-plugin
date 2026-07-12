#!/usr/bin/env python3
"""
Skill: table-properties
Description: Get table properties and metadata

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
        return 1
    return handle_http_error(error, "Table")


def get_table_properties(workspace_id, lakehouse_id, table_name):
    """Get table properties using SHOW TBLPROPERTIES."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/query"
    body = {'query': f'SHOW TBLPROPERTIES {table_name}'}

    print(f"Getting properties for table '{table_name}'...")
    print("")

    try:
        result = fabric_request_json(url, method='POST', data=body)
        display_properties(result, table_name)
        return 0

    except urllib.error.HTTPError as e:
        return handle_query_error(e, table_name)
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def display_properties(result, table_name):
    """Display table properties."""
    rows = result.get('rows', [])

    print(f"Properties for table '{table_name}':")
    print("=" * 70)
    print("")

    if not rows:
        print("(No properties available)")
        return

    # Header
    print(f"{'Property':<35} {'Value':<35}")
    print(f"{'-'*35} {'-'*35}")

    # Rows from SHOW TBLPROPERTIES
    for row in rows:
        if len(row) >= 2:
            prop_name = str(row[0])[:35]
            prop_value = str(row[1])[:35]
            print(f"{prop_name:<35} {prop_value:<35}")

    print("")


def main():
    cli = SkillCLI('table_properties.py', 'Get table properties and metadata')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Table name')
    args = cli.parse()

    sys.exit(get_table_properties(args.workspace_id, args.lakehouse_id, args.table_name))


if __name__ == "__main__":
    main()
