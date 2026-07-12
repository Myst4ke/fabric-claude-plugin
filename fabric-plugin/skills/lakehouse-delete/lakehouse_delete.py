#!/usr/bin/env python3
"""
Skill: lakehouse-delete
Description: Delete a lakehouse from workspace

Accepts workspace and lakehouse as display names or GUIDs.
WARNING: This operation is IRREVERSIBLE!
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, fabric_request_json, handle_http_error


def get_lakehouse_name(workspace_id, lakehouse_id):
    """Get lakehouse name for confirmation."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
    try:
        data = fabric_request_json(url)
        return data.get('displayName', lakehouse_id)
    except Exception:
        return lakehouse_id


def delete_lakehouse(workspace_id, lakehouse_id, force=False):
    """Delete lakehouse."""
    # Get lakehouse name for confirmation
    lakehouse_name = get_lakehouse_name(workspace_id, lakehouse_id)

    # Confirmation prompt (unless --force)
    if not force:
        print("=" * 60)
        print("WARNING: This will permanently delete the lakehouse!")
        print("=" * 60)
        print(f"  Lakehouse: {lakehouse_name}")
        print(f"  ID:        {lakehouse_id}")
        print("")
        print("All data will be lost including:")
        print("  - Tables")
        print("  - Files")
        print("  - Metadata")
        print("")
        print(f"To confirm, type the lakehouse name: {lakehouse_name}")
        print("")

        try:
            confirmation = input("Confirmation: ").strip()
        except EOFError:
            print("\n[ERROR] Cannot read input. Use --force to skip confirmation.")
            return 1

        if confirmation != lakehouse_name:
            print("\n[CANCELLED] Lakehouse name did not match. Deletion cancelled.")
            return 1

        print("")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"

    print(f"Deleting lakehouse '{lakehouse_name}'...")

    try:
        response = fabric_request(url, method='DELETE')

        if response.status in [200, 204]:
            print(f"\n[SUCCESS] Lakehouse '{lakehouse_name}' deleted.")
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Lakehouse")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('lakehouse_delete.py',
                   'Delete a lakehouse from workspace (IRREVERSIBLE)')
    cli.workspace()
    cli.item('lakehouse')
    cli.flag('--force', help='Skip confirmation prompt')
    args = cli.parse()

    sys.exit(delete_lakehouse(args.workspace_id, args.lakehouse_id, args.force))


if __name__ == "__main__":
    main()
