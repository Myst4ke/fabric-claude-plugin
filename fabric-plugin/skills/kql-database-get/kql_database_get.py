#!/usr/bin/env python3
"""
Skill: kql-database-get
Description: Get detailed information about a KQL database

Accepts workspace and database as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_database(data, workspace_id, db_id):
    """Display KQL database details."""
    print(f"\nKQL Database Details:")
    print(f"{'='*60}")
    print(f"  Name:        {data.get('displayName', 'N/A')}")
    print(f"  ID:          {data.get('id', 'N/A')}")
    print(f"  Description: {data.get('description', '(none)')}")

    props = data.get('properties', {})
    if props:
        if props.get('queryServiceUri'):
            print(f"  Query URI:   {props['queryServiceUri']}")
        if props.get('ingestionServiceUri'):
            print(f"  Ingest URI:  {props['ingestionServiceUri']}")
        if props.get('databaseType'):
            print(f"  Type:        {props['databaseType']}")
        if props.get('parentEventhouseItemId'):
            print(f"  Eventhouse:  {props['parentEventhouseItemId']}")

    print(f"{'='*60}")
    print(f"\nQuery: fabric-plugin:kql-query {workspace_id} {data.get('id', db_id)} \"<KQL>\"")


def main():
    cli = SkillCLI('kql_database_get.py',
                   'Get detailed information about a KQL database')
    cli.workspace()
    cli.item('database', 'kqldatabase', help='KQL database name or GUID')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/kqlDatabases/{args.database_id}"
    try:
        data = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "KQL database"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_database(data, args.workspace_id, args.database_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
