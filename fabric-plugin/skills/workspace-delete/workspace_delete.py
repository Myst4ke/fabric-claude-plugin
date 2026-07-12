#!/usr/bin/env python3
"""
Skill: workspace-delete
Description: Delete a Microsoft Fabric workspace with confirmation

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, fabric_request_json, handle_http_error


def get_workspace_name(workspace_id):
    """Get workspace name for confirmation."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
    workspace = fabric_request_json(url)
    return workspace.get('displayName', 'Unknown')


def confirm_deletion(workspace_id, workspace_name, force):
    """Ask user for confirmation unless --force"""
    if force:
        return True

    print()
    print("=" * 60)
    print("  WARNING: DESTRUCTIVE OPERATION")
    print("=" * 60)
    print()
    print("You are about to DELETE workspace:")
    print()
    print(f"  Name: {workspace_name}")
    print(f"  ID: {workspace_id}")
    print()
    print("This will PERMANENTLY delete:")
    print("  - All lakehouses and data")
    print("  - All notebooks")
    print("  - All pipelines")
    print("  - All reports and dashboards")
    print("  - All semantic models")
    print("  - All other workspace content")
    print()
    print("THIS CANNOT BE UNDONE!")
    print()

    try:
        response = input(f"Type '{workspace_name}' to confirm deletion: ").strip()
        if response == workspace_name:
            return True
        print("\nConfirmation failed. Workspace NOT deleted.")
        return False
    except (EOFError, KeyboardInterrupt):
        print("\n\nCancelled")
        return False


def main():
    cli = SkillCLI('workspace_delete.py',
                   'Delete a Microsoft Fabric workspace')
    cli.workspace()
    cli.flag('--force', help='Skip confirmation')
    args = cli.parse()

    try:
        workspace_name = get_workspace_name(args.workspace_id)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    if not confirm_deletion(args.workspace_id, workspace_name, args.force):
        print("Operation cancelled")
        sys.exit(1)

    print("Deleting workspace...")
    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}"
    try:
        fabric_request(url, method='DELETE')
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    print()
    print("[OK] Workspace deleted successfully!")
    print()
    print(f"Workspace '{workspace_name}' ({args.workspace_id}) has been deleted.")
    sys.exit(0)


if __name__ == '__main__':
    main()
