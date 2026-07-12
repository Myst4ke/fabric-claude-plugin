#!/usr/bin/env python3
"""
Skill: workspace-list
Description: List all Microsoft Fabric workspaces accessible to the user
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_workspaces(workspaces):
    """Display workspaces in formatted table"""
    print()
    print("=" * 106)
    print("  Microsoft Fabric Workspaces")
    print("=" * 106)
    print()

    if not workspaces:
        print("No workspaces found.")
        print()
        print("You may need:")
        print("  - A Fabric trial or license")
        print("  - Access granted by workspace admin")
        print()
        return

    print(f"Total: {len(workspaces)} workspace(s)")
    print()

    # Table header
    print(f"{'ID':<36} | {'Display Name':<38} | {'Type':<12} | {'Capacity ID':<36}")
    print(f"{'-'*36}-+-{'-'*38}-+-{'-'*12}-+-{'-'*36}")

    # Table rows
    for ws in workspaces:
        ws_id = ws.get('id', 'N/A')
        name = ws.get('displayName', 'Unnamed')
        ws_type = ws.get('type', 'Workspace')
        capacity_id = ws.get('capacityId', 'None')

        # Truncate name if too long
        if len(name) > 38:
            name = name[:35] + '...'

        print(f"{ws_id:<36} | {name:<38} | {ws_type:<12} | {capacity_id:<36}")

    print()
    print("Next steps:")
    print("  /get-workspace <workspace-id>    Get workspace details")
    print("  /list-users <workspace-id>       List workspace users")
    print()


def main():
    cli = SkillCLI('list_workspaces.py',
                   'List all Microsoft Fabric workspaces accessible to the user')
    cli.opt('--limit', type=int, help='Maximum number of workspaces to return')
    args = cli.parse()

    print("Fetching workspaces...")

    url = f"{FABRIC_API_BASE}/workspaces"
    try:
        workspaces = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_workspaces(workspaces)
    sys.exit(0)


if __name__ == '__main__':
    main()
