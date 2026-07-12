#!/usr/bin/env python3
"""
Skill: warehouse-list
Description: List all warehouses in a Microsoft Fabric workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error
from security_guard import check_permission, SecurityViolation
from audit_logger import log_operation


def display_warehouses(warehouses, workspace_id):
    """Display warehouses in formatted table."""
    print(f"Found {len(warehouses)} warehouse(s):\n")

    if not warehouses:
        print("No warehouses in this workspace.")
        return

    print(f"{'Name':<40} {'ID':<38}")
    print(f"{'-'*40} {'-'*38}")

    for wh in warehouses:
        name = wh.get('displayName', 'Unnamed')
        wh_id = wh.get('id', 'N/A')
        if len(name) > 40:
            name = name[:37] + '...'
        print(f"{name:<40} {wh_id:<38}")

    print()
    print(f"Use fabric-plugin:warehouse-get <workspace-id> <warehouse-id> for details")


def main():
    cli = SkillCLI('warehouse_list.py',
                   'List all warehouses in a Microsoft Fabric workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of warehouses to return')
    args = cli.parse()

    try:
        check_permission(args.workspace_id, "warehouse:list")
    except SecurityViolation as e:
        print(str(e))
        log_operation("warehouse:list", args.workspace_id, False, error="Permission denied")
        sys.exit(1)

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/warehouses"
    try:
        warehouses = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        code = handle_http_error(e, "Workspace")
        log_operation("warehouse:list", args.workspace_id, False, http_code=e.code)
        sys.exit(code)
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        log_operation("warehouse:list", args.workspace_id, False, error=str(e))
        sys.exit(2)

    log_operation("warehouse:list", args.workspace_id, True, count=len(warehouses))
    display_warehouses(warehouses, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
