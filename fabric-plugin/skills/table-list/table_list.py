#!/usr/bin/env python3
"""
Skill: table-list
Description: List all tables in a lakehouse

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def handle_list_error(error, lakehouse_id):
    """Handle HTTP errors, with a hint for schema-enabled lakehouses (400)."""
    if error.code == 400:
        try:
            error_body = error.read().decode('utf-8')
        except Exception:
            error_body = ""
        print("[ERROR] HTTP 400: Bad Request")
        print("")
        print("[INFO] This lakehouse likely has schemas enabled.")
        print("       The standard tables API does not work with schema-enabled lakehouses.")
        print("")
        print("Use SQL instead to list tables:")
        print(f"  fabric-plugin:lakehouse-sql-query <workspace-id> {lakehouse_id} \\")
        print('    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_SCHEMA, TABLE_NAME"')
        if error_body:
            try:
                err_json = json.loads(error_body)
                msg = err_json.get('error', {}).get('message', '')
                if msg:
                    print(f"\nAPI details: {msg}")
            except json.JSONDecodeError:
                pass
        return 1
    return handle_http_error(error, "Lakehouse")


def display_tables(tables, workspace_id, lakehouse_id):
    """Display tables in formatted output."""
    count = len(tables)
    print(f"\nFound {count} table(s):\n")

    if count == 0:
        print("No tables in lakehouse")
        print(f"\nCreate one: fabric-plugin:table-create {workspace_id} {lakehouse_id} <table-name>")
        return

    # Header
    print(f"{'Table Name':<30} {'Type':<15} {'Location':<40}")
    print(f"{'-'*30} {'-'*15} {'-'*40}")

    # Rows
    for table in tables:
        name = table.get('name', 'N/A')[:30]
        table_type = table.get('type', 'N/A')[:15]
        location = table.get('location', 'N/A')[:40]
        print(f"{name:<30} {table_type:<15} {location:<40}")

    print(f"\nNext steps:")
    print(f"  - Query: fabric-plugin:lakehouse-sql-query {workspace_id} {lakehouse_id} \"SELECT * FROM <table> LIMIT 10\"")
    print(f"  - Schema: fabric-plugin:table-schema {workspace_id} {lakehouse_id} <table-name>")


def main():
    cli = SkillCLI('table_list.py', 'List all tables in a lakehouse')
    cli.workspace()
    cli.item('lakehouse')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/lakehouses/{args.lakehouse_id}/tables"
    try:
        tables = fabric_list(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_list_error(e, args.lakehouse_id))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_tables(tables, args.workspace_id, args.lakehouse_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
