#!/usr/bin/env python3
"""
Skill: kql-database-list
Description: List all KQL databases in a workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_databases(items, workspace_id):
    """Display KQL databases in formatted table."""
    count = len(items)
    print(f"\nFound {count} KQL database(s):\n")
    if count == 0:
        print("No KQL databases in this workspace.")
        return

    print(f"{'Database Name':<35} {'ID':<38} {'Parent Eventhouse':<30}")
    print(f"{'-'*35} {'-'*38} {'-'*30}")
    for item in items:
        name = item.get('displayName', 'N/A')[:35]
        did = item.get('id', 'N/A')[:38]
        props = item.get('properties', {})
        parent = props.get('parentEventhouseItemId', '')[:30] if props else ''
        print(f"{name:<35} {did:<38} {parent:<30}")

    print(f"\nNext steps:")
    print(f"  - Details: fabric-plugin:kql-database-get {workspace_id} <db-id>")
    print(f"  - Query:   fabric-plugin:kql-query {workspace_id} <db-id> \"<KQL query>\"")


def main():
    cli = SkillCLI('kql_database_list.py',
                   'List all KQL databases in a workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of databases to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/kqlDatabases"
    try:
        items = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_databases(items, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
