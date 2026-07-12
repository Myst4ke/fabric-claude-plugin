#!/usr/bin/env python3
"""
Skill: warehouse-get
Description: Get detailed information about a SQL warehouse

Accepts workspace and warehouse as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_warehouse(wh, workspace_id):
    """Display warehouse details."""
    print(f"\nWarehouse Details:")
    print(f"{'='*60}")
    print(f"  Name:            {wh.get('displayName', 'N/A')}")
    print(f"  ID:              {wh.get('id', 'N/A')}")
    print(f"  Description:     {wh.get('description', '(none)')}")
    print(f"  Workspace:       {workspace_id}")

    if 'createdDate' in wh:
        print(f"  Created:         {wh['createdDate']}")
    if 'modifiedDate' in wh:
        print(f"  Modified:        {wh['modifiedDate']}")

    # Properties
    props = wh.get('properties', {})
    if props:
        if 'connectionString' in props:
            print(f"  SQL Endpoint:    {props['connectionString']}")
        if 'createdDate' in props:
            print(f"  Provisioned:     {props['createdDate']}")

    print(f"{'='*60}")

    wh_id = wh.get('id', '<warehouse-id>')
    print(f"\nNext steps:")
    print(f"  - Query:  fabric-plugin:warehouse-query {workspace_id} {wh_id} \"SELECT TOP 10 * FROM dbo.mytable\"")
    print(f"  - Tables: fabric-plugin:warehouse-list-tables {workspace_id} {wh_id}")


def main():
    cli = SkillCLI('warehouse_get.py',
                   'Get detailed information about a SQL warehouse')
    cli.workspace()
    cli.item('warehouse')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/warehouses/{args.warehouse_id}"
    try:
        data = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Warehouse"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_warehouse(data, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
