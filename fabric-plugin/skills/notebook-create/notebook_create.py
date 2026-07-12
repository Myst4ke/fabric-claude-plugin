#!/usr/bin/env python3
"""
Skill: notebook-create
Description: Create a new notebook in a Microsoft Fabric workspace

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
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error

# LRO settings
MAX_POLL_TIME = 600  # 10 minutes
DEFAULT_POLL_INTERVAL = 5


def create_notebook(workspace_id, name, description=None):
    """Create a new notebook."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/notebooks"

    body = {"displayName": name}
    if description:
        body["description"] = description

    try:
        response = fabric_request(url, method='POST', data=body)

        # Handle LRO (202 Accepted)
        if response.status == 202:
            print(f"[INFO] Creating notebook '{name}'...")
            location = response.headers.get('Location')
            operation_id = response.headers.get('x-ms-operation-id')
            retry_after = int(response.headers.get('Retry-After', DEFAULT_POLL_INTERVAL))

            if location or operation_id:
                return poll_operation(location, operation_id, retry_after)
            else:
                print("[WARNING] LRO started but no Location header. Check workspace for new notebook.")
                return 0

        # Immediate success (201 Created)
        elif response.status == 201:
            notebook = json.loads(response.read().decode('utf-8'))
            display_created_notebook(notebook)
            return 0

        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def poll_operation(location, operation_id, retry_after):
    """Poll LRO until completion."""
    if location:
        poll_url = location
    elif operation_id:
        poll_url = f"{FABRIC_API_BASE}/operations/{operation_id}"
    else:
        print("[ERROR] No location or operation ID for polling")
        return 2

    start_time = time.time()

    while time.time() - start_time < MAX_POLL_TIME:
        time.sleep(retry_after)

        try:
            response = fabric_request(poll_url)

            if response.status == 202:
                retry_after = int(response.headers.get('Retry-After', retry_after))
                continue

            data = json.loads(response.read().decode('utf-8'))
            status = data.get('status', 'Unknown')
            percent = data.get('percentComplete', 0)

            print(f"[INFO] Status: {status} ({percent}%)")

            if status == 'Succeeded':
                resource_id = data.get('resourceId') or data.get('id')
                if resource_id:
                    print(f"\n[SUCCESS] Notebook created successfully!")
                    print(f"Notebook ID: {resource_id}")
                else:
                    print(f"\n[SUCCESS] Notebook created. Check workspace for new notebook.")
                return 0

            elif status == 'Failed':
                error = data.get('error', {})
                error_msg = error.get('message', 'Unknown error')
                print(f"[ERROR] Operation failed: {error_msg}")
                return 1

        except urllib.error.HTTPError as e:
            return handle_http_error(e, "Operation")
        except Exception as e:
            print(f"[ERROR] Polling failed: {e}")
            return 2

    print(f"[ERROR] Operation timed out after {MAX_POLL_TIME} seconds")
    return 2


def display_created_notebook(notebook):
    """Display created notebook details."""
    print("\n[SUCCESS] Notebook created successfully!")
    print("="*60)
    print(f"Name:        {notebook.get('displayName', 'N/A')}")
    print(f"ID:          {notebook.get('id', 'N/A')}")
    print(f"Description: {notebook.get('description', 'N/A')}")
    print(f"Workspace:   {notebook.get('workspaceId', 'N/A')}")
    print("="*60)


def main():
    cli = SkillCLI('notebook_create.py',
                   'Create a new notebook in a Microsoft Fabric workspace')
    cli.workspace()
    cli.positional('name', help='Name for the new notebook')
    cli.opt('--description', help='Optional description')
    args = cli.parse()

    sys.exit(create_notebook(args.workspace_id, args.name, args.description))


if __name__ == "__main__":
    main()
