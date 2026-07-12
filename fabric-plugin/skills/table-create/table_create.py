#!/usr/bin/env python3
"""
Skill: table-create
Description: Create a new table in a lakehouse

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def create_table(workspace_id, lakehouse_id, table_name):
    """Create table in lakehouse."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables"
    body = {'name': table_name}

    print(f"Creating table '{table_name}'...")

    try:
        result = fabric_request_json(url, method='POST', data=body)
        print(f"\n[SUCCESS] Table created!")
        print(f"  Name:     {result.get('name', table_name)}")
        print(f"  Type:     {result.get('type', 'N/A')}")
        print(f"  Location: {result.get('location', 'N/A')}")
        print("")
        print(f"Next: Load data with fabric-plugin:table-load {workspace_id} {lakehouse_id} {table_name} <file-path>")
        return 0

    except urllib.error.HTTPError as e:
        if e.code == 409:
            print(f"[ERROR] Conflict. A table named '{table_name}' may already exist.")
            return 1
        return handle_http_error(e, "Lakehouse")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('table_create.py', 'Create a new table in a lakehouse')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Name for the new table')
    args = cli.parse()

    sys.exit(create_table(args.workspace_id, args.lakehouse_id, args.table_name))


if __name__ == "__main__":
    main()
