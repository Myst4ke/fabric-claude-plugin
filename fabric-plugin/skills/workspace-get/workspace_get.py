#!/usr/bin/env python3
"""
Skill: workspace-get
Description: Get detailed information about a specific Microsoft Fabric workspace

Accepts the workspace as a display name or a GUID.
"""

import json
import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_workspace(workspace, workspace_id):
    """Display workspace details in formatted output"""
    print("=" * 80)
    print("  Workspace Details")
    print("=" * 80)
    print()

    print(f"  ID:           {workspace.get('id', 'N/A')}")
    print(f"  Display Name: {workspace.get('displayName', 'N/A')}")
    print(f"  Description:  {workspace.get('description', 'N/A') or 'None'}")
    print(f"  Type:         {workspace.get('type', 'N/A')}")
    print(f"  State:        {workspace.get('state', 'N/A')}")
    print(f"  Capacity ID:  {workspace.get('capacityId', 'None')}")

    # Show additional properties if available
    if workspace.get('capacityAssignmentProgress'):
        print(f"  Capacity Assignment Progress: {workspace.get('capacityAssignmentProgress')}")

    print()
    print("-" * 80)
    print()
    print("Next steps:")
    print(f"  fabric-plugin:workspace-user-list {workspace_id}")
    print(f"  fabric-plugin:workspace-update {workspace_id} --name \"New Name\"")
    print()

    # Also output JSON for programmatic use
    print("-" * 80)
    print("Raw JSON:")
    print(json.dumps(workspace, indent=2))


def main():
    cli = SkillCLI('workspace_get.py',
                   'Get detailed information about a Microsoft Fabric workspace')
    cli.workspace()
    args = cli.parse()

    print("Fetching workspace details...")
    print(f"  Workspace ID: {args.workspace_id}")
    print()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}"
    try:
        workspace = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_workspace(workspace, args.workspace_id)
    sys.exit(0)


if __name__ == '__main__':
    main()
