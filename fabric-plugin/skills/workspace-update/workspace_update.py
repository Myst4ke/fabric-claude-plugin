#!/usr/bin/env python3
"""
Skill: workspace-update
Description: Update Microsoft Fabric workspace properties

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_success(workspace):
    """Display success message with updated workspace details"""
    print("[OK] Workspace updated successfully!")
    print()
    print(f"  Workspace ID: {workspace.get('id', 'N/A')}")
    print(f"  Name: {workspace.get('displayName', 'N/A')}")
    print(f"  Description: {workspace.get('description', 'N/A') or 'None'}")
    print()


def update_workspace(workspace_id, name=None, description=None):
    """Update workspace via API"""
    print(f"Updating workspace: {workspace_id}")

    # Build request body with only provided fields
    request_data = {}

    if name:
        print(f"  New name: {name}")
        request_data["displayName"] = name

    if description is not None:
        print(f"  New description: {description or '(cleared)'}")
        request_data["description"] = description

    if not request_data:
        print("[WARN] Nothing to update. Provide --name or --description")
        return 0

    print()

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
    try:
        workspace = fabric_request_json(url, method='PATCH', data=request_data)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] A workspace with this name may already exist.")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    display_success(workspace)
    return 0


def main():
    cli = SkillCLI('workspace_update.py',
                   'Update Microsoft Fabric workspace properties')
    cli.workspace()
    cli.opt('--name', help='New workspace display name')
    cli.opt('--description', help='New workspace description')
    args = cli.parse()

    if not args.name and args.description is None:
        print("[ERROR] At least --name or --description must be provided")
        sys.exit(1)

    sys.exit(update_workspace(args.workspace_id, args.name, args.description))


if __name__ == '__main__':
    main()
