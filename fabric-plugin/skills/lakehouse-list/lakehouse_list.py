#!/usr/bin/env python3
"""
Skill: lakehouse-list
Description: List all lakehouses in a Microsoft Fabric workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_lakehouses(lakehouses):
    """Display lakehouses in formatted table."""
    count = len(lakehouses)
    print(f"\nFound {count} lakehouse(s):\n")

    if count == 0:
        print("No lakehouses in workspace")
        return

    print(f"{'Name':<40} {'ID':<38}")
    print(f"{'-'*40} {'-'*38}")

    for lh in lakehouses:
        name = lh.get('displayName', 'N/A')[:40]
        lh_id = lh.get('id', 'N/A')
        print(f"{name:<40} {lh_id:<38}")

    print(f"\nUse fabric-plugin:lakehouse-get <workspace> <lakehouse> for details")


def main():
    cli = SkillCLI('lakehouse_list.py',
                   'List all lakehouses in a Microsoft Fabric workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of lakehouses to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/lakehouses"
    try:
        lakehouses = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_lakehouses(lakehouses)
    sys.exit(0)


if __name__ == "__main__":
    main()
