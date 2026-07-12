#!/usr/bin/env python3
"""
Skill: table-delete
Description: Delete a table from a lakehouse

Accepts workspace and lakehouse as display names or GUIDs.
WARNING: This operation is irreversible!
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def delete_table(workspace_id, lakehouse_id, table_name):
    """Delete table from lakehouse."""
    url = (f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
           f"/lakehouses/{lakehouse_id}/tables/{table_name}")

    print(f"Deleting table '{table_name}'...")

    try:
        response = fabric_request(url, method='DELETE')

        if response.status in [200, 204]:
            print(f"\n[SUCCESS] Table '{table_name}' deleted.")
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Table")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('table_delete.py',
                   'Delete a table from a lakehouse (irreversible)')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Table name to delete')
    args = cli.parse()

    sys.exit(delete_table(args.workspace_id, args.lakehouse_id, args.table_name))


if __name__ == "__main__":
    main()
