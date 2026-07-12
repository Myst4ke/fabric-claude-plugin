#!/usr/bin/env python3
"""
Skill: table-read
Description: Read data from a lakehouse table using OneLake File API

Supports both schema-enabled and classic lakehouses.
Uses deltalake library to read Delta/Parquet files directly via OneLake ADLS API.
Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import os

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, get_storage_token


def get_workspace_name(workspace_id):
    """Get workspace display name (OneLake File API requires names)."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
    try:
        data = fabric_request_json(url)
        return data.get('displayName', workspace_id)
    except Exception as e:
        print(f"[WARN] Could not retrieve workspace name: {e}")
        return workspace_id


def get_lakehouse_info(workspace_id, lakehouse_id):
    """Get lakehouse display name and whether schemas are enabled."""
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


def read_table_data(workspace_name, lakehouse_name, table_name, schema_name, limit, storage_token):
    """Read table data using deltalake library via OneLake File API."""

    try:
        # Import deltalake - this is the key library for reading Delta tables
        from deltalake import DeltaTable
        import pandas as pd
    except ImportError as e:
        print(f"[ERROR] Missing required library: {e}")
        print()
        print("Please install required dependencies:")
        print("  pip install deltalake pandas pyarrow")
        print()
        return 1

    # Construct OneLake URI
    # Format: abfss://{workspace_NAME}@onelake.dfs.fabric.microsoft.com/{lakehouse_NAME}.Lakehouse/Tables/{schema}/{table}
    #
    # CRITICAL: OneLake File API requires NAMES not GUIDs!
    # Using GUIDs results in: FriendlyNameSupportDisabled error
    if schema_name:
        table_path = f"{schema_name}/{table_name}"
    else:
        table_path = table_name

    onelake_uri = f"abfss://{workspace_name}@onelake.dfs.fabric.microsoft.com/{lakehouse_name}.Lakehouse/Tables/{table_path}"

    print(f"[INFO] Reading table from OneLake...")
    print(f"[DEBUG] URI: {onelake_uri}")
    print()

    # Configure storage options for Fabric/OneLake
    storage_options = {
        "bearer_token": storage_token,
        "use_fabric_endpoint": "true"  # Critical for OneLake access
    }

    try:
        # Load Delta table
        print("[INFO] Loading Delta table metadata...")
        delta_table = DeltaTable(onelake_uri, storage_options=storage_options)

        # Get table statistics
        print(f"[INFO] Table version: {delta_table.version()}")

        # Convert to pandas with limit
        print(f"[INFO] Reading data (limit: {limit})...")

        # Read via PyArrow first (more efficient)
        dataset = delta_table.to_pyarrow_dataset()

        # Apply limit and convert to pandas
        if limit:
            # Use PyArrow's head() for efficient sampling
            table = dataset.head(limit)
        else:
            table = dataset.to_table()

        df = table.to_pandas()

        # Display results
        display_dataframe(df, table_name, limit)

        return 0

    except FileNotFoundError:
        print(f"[ERROR] Table not found: {table_name}")
        print(f"[HINT] Check if the table exists in schema '{schema_name or 'default'}'")
        return 1
    except PermissionError:
        print("[ERROR] Permission denied accessing table")
        print("[HINT] Check workspace and lakehouse permissions")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to read table: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return 2


def display_dataframe(df, table_name, limit):
    """Display pandas DataFrame in formatted output."""
    row_count = len(df)
    col_count = len(df.columns)

    print()
    print("=" * 100)
    print(f"  Table: {table_name}")
    print("=" * 100)
    print()
    print(f"Rows: {row_count} | Columns: {col_count}")
    print()

    if row_count == 0:
        print("(No data in table)")
        return

    # Configure pandas display options
    pd_options = {
        'display.max_columns': None,
        'display.max_rows': min(100, row_count),
        'display.width': None,
        'display.max_colwidth': 50
    }

    import pandas as pd
    with pd.option_context(*[item for pair in pd_options.items() for item in pair]):
        print(df.to_string(index=False))

    print()

    if limit and row_count >= limit:
        print(f"[INFO] Showing first {limit} rows (use --limit to adjust)")

    # Show column info
    print()
    print("Column Info:")
    print(f"{'Column':<30} {'Type':<20} {'Non-Null':<10}")
    print("-" * 60)
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null_count = df[col].count()
        print(f"{col:<30} {dtype:<20} {non_null_count:<10}")
    print()


def main():
    cli = SkillCLI('table_read.py',
                   'Read data from a Microsoft Fabric lakehouse table via OneLake')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Table name (e.g., "customers")')
    cli.opt('--limit', type=int, default=100, help='Maximum rows to return (default: 100)')
    cli.opt('--schema', default='dbo', help='Schema name (default: "dbo")')
    args = cli.parse()

    # Get workspace and lakehouse names (CRITICAL for OneLake File API)
    print(f"[INFO] Retrieving workspace and lakehouse information...")
    workspace_name = get_workspace_name(args.workspace_id)
    lakehouse_info = get_lakehouse_info(args.workspace_id, args.lakehouse_id)

    lakehouse_name = lakehouse_info['displayName']

    print(f"[INFO] Workspace: {workspace_name}")
    print(f"[INFO] Lakehouse: {lakehouse_name}")
    print(f"[INFO] Schemas enabled: {lakehouse_info['enableSchemas']}")
    print()

    # Determine schema name
    # IMPORTANT: Even if enableSchemas is False in REST API,
    # OneLake Table API may still show schemas (inconsistency in Fabric APIs)
    # Always use the schema parameter if provided by user
    schema_name = args.schema if args.schema else None

    # Get OneLake storage token (cached + silent refresh handled by fabric_base)
    storage_token = get_storage_token()

    # Read table data using NAMES (not GUIDs)
    sys.exit(read_table_data(
        workspace_name,
        lakehouse_name,
        args.table_name,
        schema_name,
        args.limit,
        storage_token
    ))


if __name__ == "__main__":
    main()
