#!/usr/bin/env python3
"""
Skill: lakehouse-get
Description: Get detailed information about a specific lakehouse

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_lakehouse(lakehouse):
    """Display lakehouse details in formatted output."""
    print("\nLakehouse Details:")
    print("=" * 50)
    print(f"  Name:        {lakehouse.get('displayName', 'N/A')}")
    print(f"  ID:          {lakehouse.get('id', 'N/A')}")
    print(f"  Type:        {lakehouse.get('type', 'N/A')}")
    print(f"  Description: {lakehouse.get('description', 'N/A')}")
    print(f"  Workspace:   {lakehouse.get('workspaceId', 'N/A')}")
    print("=" * 50)
    print("")
    print("Next steps:")
    print(f"  - List tables: fabric-plugin:table-list <workspace> {lakehouse.get('displayName', '<lakehouse>')}")
    print(f"  - Query SQL:   fabric-plugin:lakehouse-sql-query <workspace> {lakehouse.get('displayName', '<lakehouse>')} \"SELECT * FROM table\"")


def main():
    cli = SkillCLI('lakehouse_get.py',
                   'Get detailed information about a specific lakehouse')
    cli.workspace()
    cli.item('lakehouse')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/lakehouses/{args.lakehouse_id}"
    try:
        lakehouse = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Lakehouse"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_lakehouse(lakehouse)
    sys.exit(0)


if __name__ == "__main__":
    main()
