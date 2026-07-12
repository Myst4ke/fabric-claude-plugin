#!/usr/bin/env python3
"""
Skill: workspace-unassign-capacity
Description: Unassign a workspace from its capacity

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def unassign_capacity(workspace_id):
    """Unassign workspace from capacity."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/unassignFromCapacity"

    try:
        response = fabric_request(url, method='POST', data=b'')
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 202):
        print("\n[SUCCESS] Workspace unassigned from capacity!")
        print("=" * 60)
        print(f"Workspace ID: {workspace_id}")
        print("=" * 60)
        return 0
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def main():
    cli = SkillCLI('workspace_unassign_capacity.py',
                   'Unassign a Microsoft Fabric workspace from its capacity')
    cli.workspace()
    args = cli.parse()

    sys.exit(unassign_capacity(args.workspace_id))


if __name__ == '__main__':
    main()
