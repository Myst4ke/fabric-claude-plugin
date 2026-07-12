#!/usr/bin/env python3
"""
Skill: warehouse-create
Description: Create a new SQL warehouse in a workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import json
import os
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         check_security, handle_http_error)


def poll_lro(location, retry_after):
    """Poll long-running operation until completion."""
    if not location:
        print("[INFO] No operation location header. Warehouse may still be provisioning.")
        return 0

    max_polls = 20
    for i in range(max_polls):
        time.sleep(min(retry_after, 30))
        try:
            data = fabric_request_json(location)

            status = data.get('status', '').lower()
            if status == 'succeeded':
                print(f"\n[SUCCESS] Warehouse created successfully.")
                if 'id' in data:
                    print(f"  ID: {data['id']}")
                return 0
            elif status == 'failed':
                error = data.get('error', {})
                print(f"[ERROR] Warehouse creation failed: {error.get('message', 'Unknown error')}")
                return 1
            elif status == 'cancelled':
                print("[ERROR] Warehouse creation was cancelled.")
                return 1
            else:
                print(f"  Provisioning... ({i + 1}/{max_polls})")
        except Exception as e:
            print(f"[WARN] Polling error: {e}")

    print("[WARN] Operation still running. Check workspace for status.")
    return 0


def create_warehouse(workspace_id, name, description=None):
    """Create a new warehouse."""
    check_security(workspace_id, "warehouse:create")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/warehouses"

    body = {'displayName': name}
    if description:
        body['description'] = description

    try:
        response = fabric_request(url, method='POST', data=body)

        if response.status in (200, 201):
            result = json.loads(response.read().decode('utf-8'))
            print(f"\n[SUCCESS] Warehouse created:")
            print(f"  Name: {result.get('displayName', name)}")
            print(f"  ID:   {result.get('id', 'N/A')}")
            if result.get('description'):
                print(f"  Desc: {result['description']}")
            return 0
        elif response.status == 202:
            # Long-running operation
            location = response.headers.get('Location', '')
            retry_after = int(response.headers.get('Retry-After', '30'))
            print(f"[INFO] Warehouse creation started (LRO)...")
            return poll_lro(location, retry_after)
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] Conflict. A warehouse with this name may already exist.")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('warehouse_create.py',
                   'Create a new SQL warehouse in a workspace')
    cli.workspace()
    cli.positional('name', help='Warehouse display name')
    cli.positional('description', nargs='?', default=None,
                   help='Optional description')
    args = cli.parse()

    sys.exit(create_warehouse(args.workspace_id, args.name, args.description))


if __name__ == "__main__":
    main()
