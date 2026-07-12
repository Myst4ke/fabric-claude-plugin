#!/usr/bin/env python3
"""
Skill: table-get
Description: Get detailed information about a table

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_table(table, workspace_id, lakehouse_id):
    """Display table details."""
    print("\nTable Details:")
    print("=" * 50)
    print(f"  Name:     {table.get('name', 'N/A')}")
    print(f"  Type:     {table.get('type', 'N/A')}")
    print(f"  Location: {table.get('location', 'N/A')}")
    print(f"  Format:   {table.get('format', 'N/A')}")
    print("=" * 50)
    print("")
    print("Next steps:")
    print(f"  - Schema: fabric-plugin:table-schema {workspace_id} {lakehouse_id} {table.get('name', '<table>')}")
    print(f"  - Query:  fabric-plugin:lakehouse-sql-query {workspace_id} {lakehouse_id} \"SELECT * FROM {table.get('name', '<table>')} LIMIT 10\"")


def main():
    cli = SkillCLI('table_get.py', 'Get detailed information about a table')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Table name')
    args = cli.parse()

    url = (f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}"
           f"/lakehouses/{args.lakehouse_id}/tables/{args.table_name}")
    try:
        table = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Table"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_table(table, args.workspace_id, args.lakehouse_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
