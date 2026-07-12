#!/usr/bin/env python3
"""
Skill: workspace-user-list
Description: List all users and their roles in a Microsoft Fabric workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_users(users, workspace_id):
    """Display users in formatted table"""
    print()
    print("=" * 110)
    print("  Workspace Users")
    print("=" * 110)
    print()

    if not users:
        print("No users found in this workspace.")
        print()
        return

    print(f"Total: {len(users)} user(s)")
    print()

    # Table header
    print(f"{'Principal ID':<36} | {'Type':<12} | {'Role':<12} | {'Display Name':<30}")
    print(f"{'-'*36}-+-{'-'*12}-+-{'-'*12}-+-{'-'*30}")

    # Table rows
    for user in users:
        principal = user.get('principal', {})
        principal_id = principal.get('id', 'N/A')
        principal_type = principal.get('type', 'Unknown')
        display_name = principal.get('displayName', 'N/A')
        role = user.get('role', 'Unknown')

        # Truncate display name if too long
        if display_name and len(display_name) > 30:
            display_name = display_name[:27] + '...'

        print(f"{principal_id:<36} | {principal_type:<12} | {role:<12} | {display_name:<30}")

    print()
    print("-" * 110)
    print()
    print("Next steps:")
    print(f"  fabric-plugin:workspace-user-add {workspace_id} user@example.com Member")
    print(f"  fabric-plugin:workspace-user-remove {workspace_id} <user-id>")
    print(f"  fabric-plugin:workspace-user-update-role {workspace_id} <user-id> Contributor")
    print()


def main():
    cli = SkillCLI('workspace_user_list.py',
                   'List all users and their roles in a Microsoft Fabric workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of users to return')
    args = cli.parse()

    print("Fetching workspace users...")

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/roleAssignments"
    try:
        users = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_users(users, args.workspace_id)
    sys.exit(0)


if __name__ == '__main__':
    main()
