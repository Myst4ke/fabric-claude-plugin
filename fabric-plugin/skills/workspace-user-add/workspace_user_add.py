#!/usr/bin/env python3
"""
Skill: workspace-user-add
Description: Add user to Microsoft Fabric workspace with specified role
Supports email or Azure AD Object ID input
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
from fabric_base import (FABRIC_API_BASE, fabric_request, get_graph_token,
                         handle_http_error)
from fabric_resolver import is_guid

VALID_ROLES = ['Admin', 'Member', 'Contributor', 'Viewer']


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


def add_user(workspace_id, user_input, user_guid, role):
    """Add user to workspace."""
    print("Adding user to workspace...")
    print(f"  Workspace: {workspace_id}")
    print(f"  User ID: {user_guid}")
    print(f"  Role: {role}")

    request_data = {
        "principal": {
            "id": user_guid,
            "type": "User"
        },
        "role": role
    }

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/roleAssignments"
    try:
        fabric_request(url, method='POST', data=request_data)
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    print()
    print("[OK] User added successfully!")
    print()
    print(f"User {user_input} now has {role} access to workspace")
    return 0


def main():
    cli = SkillCLI('workspace_user_add.py',
                   'Add user to Microsoft Fabric workspace with specified role')
    cli.workspace()
    cli.positional('user', help='User email or Azure AD Object ID')
    cli.positional('role', help='Role: Admin|Member|Contributor|Viewer')
    args = cli.parse()

    if args.role not in VALID_ROLES:
        print(f"[ERROR] Invalid role: {args.role}")
        print()
        print("Valid roles: Admin | Member | Contributor | Viewer")
        sys.exit(1)

    if is_guid(args.user):
        print(f"User input is Object ID: {args.user}")
        user_guid = args.user
    else:
        user_guid = lookup_user(args.user)

    sys.exit(add_user(args.workspace_id, args.user, user_guid, args.role))


if __name__ == '__main__':
    main()
