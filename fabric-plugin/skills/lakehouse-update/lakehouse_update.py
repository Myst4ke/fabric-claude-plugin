#!/usr/bin/env python3
"""
Skill: lakehouse-update
Description: Update lakehouse name and description

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def update_lakehouse(workspace_id, lakehouse_id, new_name=None, description=None):
    """Update lakehouse properties."""
    if not new_name and description is None:
        print("[ERROR] At least one of --name or --description is required")
        return 1

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"

    body = {}
    if new_name:
        body['displayName'] = new_name
    if description is not None:
        body['description'] = description

    print(f"Updating lakehouse {lakehouse_id}...")

    try:
        result = fabric_request_json(url, method='PATCH', data=body)
        print(f"\n[SUCCESS] Lakehouse updated!")
        print(f"  Name:        {result.get('displayName', 'N/A')}")
        print(f"  ID:          {result.get('id', 'N/A')}")
        print(f"  Description: {result.get('description', 'N/A')}")
        return 0

    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] Conflict. The new name may already be in use.")
            return 1
        return handle_http_error(e, "Lakehouse")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('lakehouse_update.py',
                   'Update lakehouse name and description')
    cli.workspace()
    cli.item('lakehouse')
    cli.opt('--name', help='New display name')
    cli.opt('--description', help='New description')
    args = cli.parse()

    sys.exit(update_lakehouse(args.workspace_id, args.lakehouse_id,
                              args.name, args.description))


if __name__ == "__main__":
    main()
