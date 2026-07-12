#!/usr/bin/env python3
"""
Skill: workspace-user-update-role
Description: Update a user's role in a Microsoft Fabric workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error
from fabric_resolver import is_guid

VALID_ROLES = ['Admin', 'Member', 'Contributor', 'Viewer']

ROLE_INFO = {
    'Admin': [
        "- Full control over workspace",
        "- Manage settings and users",
        "- Create, edit, delete all content",
        "- Delete workspace"
    ],
    'Member': [
        "- Create and edit content",
        "- Share items with others",
        "- Cannot manage workspace settings"
    ],
    'Contributor': [
        "- Edit assigned content only",
        "- Cannot create new items",
        "- Cannot share items"
    ],
    'Viewer': [
        "- View content only",
        "- Cannot edit or create",
        "- Cannot share items"
    ]
}


def display_role_info(role):
    """Display role permissions"""
    for line in ROLE_INFO.get(role, []):
        print(f"  {line}")
    print()


def update_role(workspace_id, user_id, role):
    """Update user role via API"""
    print("Updating user role...")
    print(f"  Workspace: {workspace_id}")
    print(f"  User ID: {user_id}")
    print(f"  New role: {role}")
    print()

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/roleAssignments/{user_id}"
    try:
        fabric_request(url, method='PATCH', data={"role": role})
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Workspace user")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    print("[OK] User role updated successfully!")
    print()
    print(f"User {user_id} now has {role} role in workspace")
    print()
    print("Role permissions:")
    display_role_info(role)
    return 0


def main():
    cli = SkillCLI('workspace_user_update_role.py',
                   "Update a user's role in a Microsoft Fabric workspace")
    cli.workspace()
    cli.positional('user_id', help='User Azure AD Object ID (GUID)')
    cli.positional('role', help='New role: Admin|Member|Contributor|Viewer')
    args = cli.parse()

    if args.role not in VALID_ROLES:
        print(f"[ERROR] Invalid role: {args.role}")
        print()
        print("Valid roles: Admin | Member | Contributor | Viewer")
        sys.exit(1)

    if not is_guid(args.user_id):
        print("[ERROR] Invalid user ID format")
        print()
        print("User ID must be an Azure AD Object ID (GUID format)")
        print("Use fabric-plugin:workspace-user-list to find user IDs")
        sys.exit(1)

    sys.exit(update_role(args.workspace_id, args.user_id, args.role))


if __name__ == '__main__':
    main()
