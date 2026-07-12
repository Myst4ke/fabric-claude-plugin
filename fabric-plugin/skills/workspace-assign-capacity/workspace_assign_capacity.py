#!/usr/bin/env python3
"""
Skill: workspace-assign-capacity
Description: Assign a workspace to a capacity

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def assign_capacity(workspace_id, capacity_id):
    """Assign workspace to capacity."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/assignToCapacity"

    try:
        response = fabric_request(url, method='POST',
                                  data={"capacityId": capacity_id})
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Workspace or capacity")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status == 202:
        print("\n[SUCCESS] Workspace assigned to capacity!")
        print("=" * 60)
        print(f"Workspace ID: {workspace_id}")
        print(f"Capacity ID:  {capacity_id}")
        print("=" * 60)
        return 0
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def main():
    cli = SkillCLI('workspace_assign_capacity.py',
                   'Assign a Microsoft Fabric workspace to a capacity')
    cli.workspace()
    cli.positional('capacity_id', help='Capacity GUID to assign')
    args = cli.parse()

    sys.exit(assign_capacity(args.workspace_id, args.capacity_id))


if __name__ == '__main__':
    main()
