#!/usr/bin/env python3
"""
Skill: workspace-create
Description: Create a new Microsoft Fabric workspace
Supports optional capacity assignment and description
"""

import json
import sys
import os
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         handle_http_error)

MAX_POLL_TIME = 300  # 5 minutes max
POLL_INTERVAL = 5    # seconds


def display_success(workspace):
    """Display success message with workspace details"""
    print()
    print("[OK] Workspace created successfully!")
    print()
    print(f"  Workspace ID: {workspace.get('id', 'N/A')}")
    print(f"  Name: {workspace.get('displayName', 'N/A')}")
    if workspace.get('description'):
        print(f"  Description: {workspace.get('description')}")
    if workspace.get('capacityId'):
        print(f"  Capacity ID: {workspace.get('capacityId')}")
    print()
    print("Next steps:")
    ws_id = workspace.get('id', '<workspace-id>')
    print(f"  fabric-plugin:workspace-get {ws_id}")
    print(f"  fabric-plugin:workspace-user-add {ws_id} user@example.com Member")
    print()


def handle_lro(response):
    """Poll a 202 long-running operation until completion."""
    location = response.headers.get('Location')
    operation_id = response.headers.get('x-ms-operation-id')
    retry_after = int(response.headers.get('Retry-After', str(POLL_INTERVAL)))

    print("Workspace creation in progress...")
    if operation_id:
        print(f"  Operation ID: {operation_id}")

    elapsed = 0
    delay = retry_after

    while elapsed < MAX_POLL_TIME:
        time.sleep(delay)
        elapsed += delay

        status_data = fabric_request_json(location)
        status = status_data.get('status', 'Unknown')
        percent = status_data.get('percentComplete', 0)

        print(f"  Status: {status} ({percent}% complete)")

        if status == 'Succeeded':
            resource_location = status_data.get('resourceLocation')
            if resource_location:
                try:
                    workspace = fabric_request_json(resource_location)
                    display_success(workspace)
                except Exception as e:
                    print("[OK] Workspace created successfully!")
                    print(f"  (Could not fetch details: {e})")
            else:
                print("[OK] Workspace created successfully!")
            return 0

        elif status == 'Failed':
            error = status_data.get('error', {})
            print("[ERROR] Workspace creation failed")
            print(f"  Error: {error.get('code', 'Unknown')}")
            print(f"  Message: {error.get('message', 'No details')}")
            return 1

        elif status == 'Cancelled':
            print("[WARN] Workspace creation was cancelled")
            return 1

        delay = POLL_INTERVAL

    print(f"[ERROR] Workspace creation timed out after {MAX_POLL_TIME} seconds")
    return 2


def create_workspace(name, description=None, capacity_id=None):
    """Create workspace via API"""
    print(f"Creating workspace: {name}")
    print(f"  Description: {description or 'None'}")
    print(f"  Capacity: {capacity_id or 'None (will use default)'}")
    print()

    request_data = {"displayName": name}
    if description:
        request_data["description"] = description
    if capacity_id:
        request_data["capacityId"] = capacity_id

    url = f"{FABRIC_API_BASE}/workspaces"

    try:
        response = fabric_request(url, method='POST', data=request_data)

        if response.status in [200, 201]:
            workspace = json.loads(response.read().decode('utf-8'))
            display_success(workspace)
            return 0
        elif response.status == 202:
            return handle_lro(response)
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] A workspace with this name may already exist.")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('workspace_create.py',
                   'Create a new Microsoft Fabric workspace')
    cli.positional('name', help='Workspace display name')
    cli.opt('--description', help='Workspace description')
    cli.opt('--capacity', dest='capacity_id', help='Capacity ID to assign')
    args = cli.parse()

    sys.exit(create_workspace(args.name, args.description, args.capacity_id))


if __name__ == '__main__':
    main()
