#!/usr/bin/env python3
"""
Skill: lakehouse-create
Description: Create a new lakehouse in a Microsoft Fabric workspace

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

MAX_POLL_TIME = 300  # 5 minutes max
POLL_INTERVAL = 5  # seconds


def create_lakehouse(workspace_id, name, description=None):
    """Create lakehouse in workspace."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items"

    body = {
        'displayName': name,
        'type': 'Lakehouse'
    }
    if description:
        body['description'] = description

    print(f"Creating lakehouse '{name}'...")

    try:
        response = fabric_request(url, method='POST', data=body)

        if response.status == 201:
            # Immediate creation (rare)
            result = json.loads(response.read().decode('utf-8'))
            print(f"\n[SUCCESS] Lakehouse created!")
            print(f"  Name: {name}")
            print(f"  ID:   {result.get('id', 'N/A')}")
            return 0

        elif response.status == 202:
            # LRO - need to poll
            location = response.headers.get('Location')
            retry_after = int(response.headers.get('Retry-After', POLL_INTERVAL))

            print(f"Creation started (LRO)...")
            print(f"This may take 10-30 seconds...\n")

            return poll_operation(location, retry_after, name)
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        if e.code == 409:
            print(f"[ERROR] Conflict. A lakehouse named '{name}' may already exist.")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def poll_operation(location, initial_delay, name):
    """Poll LRO until completion."""
    elapsed = 0
    delay = initial_delay

    while elapsed < MAX_POLL_TIME:
        time.sleep(delay)
        elapsed += delay

        try:
            response = fabric_request(location, method='GET')

            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                status = data.get('status', 'Unknown')
                percent = data.get('percentComplete', 0)

                print(f"  Progress: {percent}% ({status})")

                if status == 'Succeeded':
                    # Get the created lakehouse ID from response
                    resource_location = data.get('resourceLocation', '')
                    lakehouse_id = resource_location.split('/')[-1] if resource_location else 'Unknown'

                    print(f"\n[SUCCESS] Lakehouse created!")
                    print(f"  Name: {name}")
                    print(f"  ID:   {lakehouse_id}")
                    print(f"\nNext: fabric-plugin:table-list <workspace-id> {lakehouse_id}")
                    return 0

                elif status == 'Failed':
                    error = data.get('error', {})
                    print(f"\n[ERROR] Creation failed: {error.get('message', 'Unknown error')}")
                    return 1

                # Continue polling
                delay = POLL_INTERVAL

        except urllib.error.HTTPError as e:
            if e.code == 429:
                delay = int(e.headers.get('Retry-After', delay * 2))
                print(f"  Rate limited, waiting {delay}s...")
            else:
                print(f"[ERROR] Polling failed: HTTP {e.code}")
                return 2
        except Exception as e:
            print(f"[ERROR] Polling failed: {e}")
            return 2

    print(f"[ERROR] Operation timed out after {MAX_POLL_TIME}s")
    return 2


def main():
    cli = SkillCLI('lakehouse_create.py',
                   'Create a new lakehouse in a Microsoft Fabric workspace')
    cli.workspace()
    cli.positional('name', help='Display name for the new lakehouse')
    cli.opt('--description', help='Optional description')
    args = cli.parse()

    sys.exit(create_lakehouse(args.workspace_id, args.name, args.description))


if __name__ == "__main__":
    main()
