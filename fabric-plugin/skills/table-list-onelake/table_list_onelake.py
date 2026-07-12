#!/usr/bin/env python3
"""
Skill: table-list-onelake
Description: List tables in a lakehouse using OneLake Table API

Uses Unity Catalog-compatible API to list schemas and tables.
Works with both schema-enabled and classic lakehouses.
Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import json
import os
import urllib.request
import urllib.error
import urllib.parse

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, get_storage_token

ONELAKE_TABLE_API_BASE = "https://onelake.table.fabric.microsoft.com/delta"


def get_lakehouse_info(workspace_id, lakehouse_id):
    """Get lakehouse display name and schema support flag."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
    try:
        data = fabric_request_json(url)
        return {
            'displayName': data.get('displayName', lakehouse_id),
            'enableSchemas': data.get('properties', {}).get('enableSchemas', False)
        }
    except Exception as e:
        print(f"[WARN] Could not retrieve lakehouse info: {e}")
        return {
            'displayName': lakehouse_id,
            'enableSchemas': True  # Assume schema-enabled (new default)
        }


def list_schemas(workspace_id, lakehouse_id, storage_token):
    """List schemas using OneLake Table API."""
    url = f"{ONELAKE_TABLE_API_BASE}/{workspace_id}/{lakehouse_id}/api/2.1/unity-catalog/schemas"
    params = {'catalog_name': lakehouse_id}
    url_with_params = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {
        'Authorization': f'Bearer {storage_token}',
        'Content-Type': 'application/json'
    }

    try:
        request = urllib.request.Request(url_with_params, headers=headers, method='GET')
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode('utf-8'))

        return data.get('schemas', [])

    except urllib.error.HTTPError as e:
        if e.code == 429:
            retry_after = e.headers.get('Retry-After', '30')
            print(f"[ERROR] Rate limited. Retry after {retry_after} seconds.")
            return None

        error_body = e.read().decode('utf-8')
        print(f"[ERROR] Failed to list schemas: HTTP {e.code}")
        try:
            error_data = json.loads(error_body)
            print(f"[DEBUG] {json.dumps(error_data, indent=2)}")
        except Exception:
            print(f"[DEBUG] {error_body}")

        if e.code == 401:
            print("[HINT] Token expired or invalid. Try re-authenticating.")
        elif e.code == 404:
            print("[HINT] Lakehouse not found or Table API not enabled.")
        return None

    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return None


def list_tables_in_schema(workspace_id, lakehouse_id, schema_name, storage_token):
    """List tables in a specific schema using OneLake Table API."""
    url = f"{ONELAKE_TABLE_API_BASE}/{workspace_id}/{lakehouse_id}/api/2.1/unity-catalog/tables"
    params = {
        'catalog_name': lakehouse_id,
        'schema_name': schema_name
    }
    url_with_params = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {
        'Authorization': f'Bearer {storage_token}',
        'Content-Type': 'application/json'
    }

    try:
        request = urllib.request.Request(url_with_params, headers=headers, method='GET')
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode('utf-8'))

        return data.get('tables', [])

    except urllib.error.HTTPError as e:
        if e.code == 429:
            retry_after = e.headers.get('Retry-After', '30')
            print(f"[ERROR] Rate limited listing tables in schema '{schema_name}'. Retry after {retry_after} seconds.")
            return []

        error_body = e.read().decode('utf-8')
        print(f"[ERROR] Failed to list tables in schema '{schema_name}': HTTP {e.code}")
        try:
            error_data = json.loads(error_body)
            print(f"[DEBUG] {json.dumps(error_data, indent=2)}")
        except Exception:
            print(f"[DEBUG] {error_body}")
        return []

    except Exception as e:
        print(f"[ERROR] Request failed for schema '{schema_name}': {e}")
        return []


def display_tables(schemas_with_tables, lakehouse_info):
    """Display tables grouped by schema."""
    print()
    print("=" * 120)
    print(f"  Lakehouse: {lakehouse_info['displayName']}")
    print(f"  Schemas Enabled: {lakehouse_info['enableSchemas']}")
    print("=" * 120)
    print()

    if not schemas_with_tables:
        print("No schemas found in this lakehouse.")
        return

    total_tables = sum(len(tables) for _, tables in schemas_with_tables)
    total_schemas = len(schemas_with_tables)

    print(f"Total: {total_schemas} schema(s), {total_tables} table(s)")
    print()

    for schema_name, tables in schemas_with_tables:
        print(f"[Schema: {schema_name}] ({len(tables)} tables)")

        if not tables:
            print("  (No tables)")
        else:
            for table in tables:
                name = table.get('name', 'N/A')
                data_format = table.get('data_source_format', 'N/A')
                print(f"  - {name} ({data_format})")

        print()

    print("Next steps:")
    print(f"  • Read table: fabric-plugin:table-read <workspace-id> <lakehouse-id> <table-name> --schema <schema>")
    print(f"  • Example: fabric-plugin:table-read {lakehouse_info.get('workspaceId', '<ws-id>')} {lakehouse_info.get('lakehouseId', '<lh-id>')} \"<table-name>\" --limit 10")
    print()


def main():
    cli = SkillCLI('table_list_onelake.py',
                   'List tables in a lakehouse using OneLake Table API')
    cli.workspace()
    cli.item('lakehouse')
    args = cli.parse()

    workspace_id = args.workspace_id
    lakehouse_id = args.lakehouse_id

    # Get lakehouse info via Fabric API
    print("[INFO] Retrieving lakehouse information...")
    lakehouse_info = get_lakehouse_info(workspace_id, lakehouse_id)
    lakehouse_info['workspaceId'] = workspace_id
    lakehouse_info['lakehouseId'] = lakehouse_id

    # Get OneLake storage token (cached + silent refresh handled by fabric_base)
    storage_token = get_storage_token()

    # List schemas
    print("[INFO] Listing schemas...")
    schemas = list_schemas(workspace_id, lakehouse_id, storage_token)

    if schemas is None:
        print("[ERROR] Failed to list schemas")
        sys.exit(2)

    if not schemas:
        print("[WARN] No schemas found. This might be a classic lakehouse without schema support.")
        print()
        print("[INFO] For classic lakehouses, try using direct file access:")
        print(f"  fabric-plugin:table-read {workspace_id} {lakehouse_id} <table-name>")
        sys.exit(0)

    # List tables in each schema
    print(f"[INFO] Found {len(schemas)} schema(s)")
    schemas_with_tables = []

    for schema in schemas:
        schema_name = schema.get('name', 'unknown')
        print(f"[INFO] Listing tables in schema '{schema_name}'...")

        tables = list_tables_in_schema(workspace_id, lakehouse_id, schema_name, storage_token)
        schemas_with_tables.append((schema_name, tables))

    # Display results
    display_tables(schemas_with_tables, lakehouse_info)

    sys.exit(0)


if __name__ == "__main__":
    main()
