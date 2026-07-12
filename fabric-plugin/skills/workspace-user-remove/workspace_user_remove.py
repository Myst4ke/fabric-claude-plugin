#!/usr/bin/env python3
"""
Skill: workspace-user-remove
Description: Remove user from Microsoft Fabric workspace
Supports email or Azure AD Object ID input with confirmation
"""

import json
import sys
import os
import urllib.request
import urllib.parse
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, get_graph_token, handle_http_error
from fabric_resolver import is_guid


def lookup_user(email):
    """Lookup user Object ID by email via Microsoft Graph."""
    print(f"Looking up user: {email}")

    graph_token = get_graph_token()  # exits 3 on auth failure

    url = f"https://graph.microsoft.com/v1.0/users/{urllib.parse.quote(email)}"
    request = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {graph_token}',
            'Content-Type': 'application/json'
        }
    )

    try:
        with urllib.request.urlopen(request) as response:
            user_data = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"[ERROR] User not found: {email}")
            sys.exit(1)
        elif e.code == 429:
            retry_after = e.headers.get('Retry-After', '30')
            print(f"[ERROR] Rate limited. Retry after {retry_after} seconds.")
            sys.exit(2)
        else:
            print(f"[ERROR] Graph API error (HTTP {e.code})")
            sys.exit(2)

    object_id = user_data.get('id')
    display_name = user_data.get('displayName')

    if not object_id:
        print(f"[ERROR] No Object ID found for user: {email}")
        sys.exit(1)

    print(f"[OK] Found: {display_name} (ID: {object_id})")
    return object_id


def confirm_removal(workspace_id, user_input, force):
    """Ask user for confirmation unless --force"""
    if force:
        return True

    print()
    print("[WARN] You are about to remove user access")
    print(f"  User: {user_input}")
    print(f"  From workspace: {workspace_id}")
    print()

    try:
        response = input("Are you sure? (yes/no): ").strip().lower()
        return response in ['yes', 'y']
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled")
        return False


def remove_user(workspace_id, user_input, user_guid):
    """Remove user from workspace."""
    print("Removing user from workspace...")
    print(f"  Workspace: {workspace_id}")
    print(f"  User ID: {user_guid}")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/roleAssignments/{user_guid}"
    try:
        fabric_request(url, method='DELETE')
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Workspace user")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    print()
    print("[OK] User removed successfully!")
    print()
    print(f"User {user_input} no longer has access to workspace")
    return 0


def main():
    cli = SkillCLI('workspace_user_remove.py',
                   'Remove user from Microsoft Fabric workspace')
    cli.workspace()
    cli.positional('user', help='User email or Azure AD Object ID')
    cli.flag('--force', help='Skip confirmation')
    args = cli.parse()

    if is_guid(args.user):
        print(f"User input is Object ID: {args.user}")
        user_guid = args.user
    else:
        user_guid = lookup_user(args.user)

    if not confirm_removal(args.workspace_id, args.user, args.force):
        print("Operation cancelled")
        sys.exit(1)

    sys.exit(remove_user(args.workspace_id, args.user, user_guid))


if __name__ == '__main__':
    main()
