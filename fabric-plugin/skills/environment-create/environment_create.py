#!/usr/bin/env python3
"""
Skill: environment-create
Description: Create a new environment (Spark/Python configuration) in a workspace
"""

import sys
import os
import json
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         handle_http_error, check_security)


def create_environment(workspace_id, name, description=None):
    """Create a new environment."""
    check_security(workspace_id, "environment:create")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/environments"

    body = {'displayName': name}
    if description:
        body['description'] = description

    try:
        response = fabric_request(url, method='POST', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] An environment with this name already exists.")
            return 1
        elif e.code == 403:
            print("[ERROR] Forbidden. Need Contributor role or higher.")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 201):
        result = json.loads(response.read().decode('utf-8'))
        env_id = result.get('id', 'N/A')
        print(f"\n[SUCCESS] Environment created:")
        print(f"  Name: {result.get('displayName', name)}")
        print(f"  ID:   {env_id}")
        print(f"\nNext steps:")
        print(f"  - Add libraries via staging, then publish:")
        print(f"    fabric-plugin:environment-staging {workspace_id} {env_id}")
        print(f"    fabric-plugin:environment-publish {workspace_id} {env_id}")
        return 0
    elif response.status == 202:
        location = response.headers.get('Location', '')
        retry_after = int(response.headers.get('Retry-After', '10'))
        print("[INFO] Environment creation in progress...")
        return poll_lro(location, retry_after)
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def poll_lro(location, retry_after):
    """Poll LRO."""
    if not location:
        print("[SUCCESS] Environment creation submitted.")
        return 0
    max_polls = 20
    for i in range(max_polls):
        time.sleep(min(retry_after, 15))
        try:
            data = fabric_request_json(location)
            status = data.get('status', '').lower()
            if status == 'succeeded':
                print(f"\n[SUCCESS] Environment created.")
                return 0
            elif status in ('failed', 'cancelled'):
                print(f"[ERROR] Creation {status}.")
                return 1
        except Exception:
            pass
    print("[WARN] Still provisioning. Check workspace.")
    return 0


def main():
    cli = SkillCLI('environment_create.py',
                   'Create a new environment (Spark/Python configuration) '
                   'in a workspace')
    cli.workspace()
    cli.positional('name', help='Display name for the new environment')
    cli.positional('description', nargs='?', default=None,
                   help='Optional description')
    args = cli.parse()

    sys.exit(create_environment(args.workspace_id, args.name, args.description))


if __name__ == "__main__":
    main()
