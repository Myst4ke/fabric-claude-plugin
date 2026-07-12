#!/usr/bin/env python3
"""
Skill: eventhouse-list
Description: List all eventhouses in a workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_eventhouses(items, workspace_id):
    """Display eventhouses in formatted table."""
    count = len(items)
    print(f"\nFound {count} eventhouse(s):\n")
    if count == 0:
        print("No eventhouses in this workspace.")
        return

    print(f"{'Eventhouse Name':<35} {'ID':<38} {'Description':<30}")
    print(f"{'-'*35} {'-'*38} {'-'*30}")
    for item in items:
        name = item.get('displayName', 'N/A')[:35]
        eid = item.get('id', 'N/A')[:38]
        desc = item.get('description', '')[:30]
        print(f"{name:<35} {eid:<38} {desc:<30}")

    print(f"\nKQL databases: fabric-plugin:kql-database-list {workspace_id}")


def main():
    cli = SkillCLI('eventhouse_list.py',
                   'List all eventhouses in a workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of eventhouses to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/eventhouses"
    try:
        items = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_eventhouses(items, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
