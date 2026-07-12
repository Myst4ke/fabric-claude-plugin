#!/usr/bin/env python3
"""
Skill: table-stats
Description: Get table statistics (row count, size, etc.)

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import json
import os
import re
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error

# Allowed characters for a SQL table identifier (prevents SQL injection,
# since the table name is interpolated into the query text)
TABLE_NAME_RE = re.compile(r'[A-Za-z0-9_\.\[\]]+')


def handle_query_error(error, table_name):
    """Handle HTTP errors, treating 400 as a permanent invalid-table error."""
    if error.code == 400:
        try:
            error_body = json.loads(error.read().decode('utf-8'))
            message = error_body.get('error', {}).get('message', 'Invalid table')
            print(f"[ERROR] {message}")
        except Exception:
            print(f"[ERROR] Table not found or invalid: {table_name}")
        return 1
    return handle_http_error(error, "Table")


def get_table_stats(workspace_id, lakehouse_id, table_name):
    """Get table statistics."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/query"

    print(f"Getting statistics for table '{table_name}'...")
    print("")

    stats = {}

    # Get row count
    try:
        body = {'query': f'SELECT COUNT(*) as row_count FROM {table_name}'}
        result = fabric_request_json(url, method='POST', data=body)
        rows = result.get('rows', [])
        if rows and len(rows[0]) > 0:
            stats['row_count'] = rows[0][0]
    except Exception:
        stats['row_count'] = 'Error'

    # Get table details via DESCRIBE DETAIL
    try:
        body = {'query': f'DESCRIBE DETAIL {table_name}'}
        result = fabric_request_json(url, method='POST', data=body)
        columns = result.get('columns', [])
        rows = result.get('rows', [])

        if rows and columns:
            col_names = [c.get('name', '') for c in columns]
            row = rows[0]

            for i, col in enumerate(col_names):
                if i < len(row):
                    col_lower = col.lower()
                    if 'numfiles' in col_lower or 'num_files' in col_lower:
                        stats['num_files'] = row[i]
                    elif 'sizeinbytes' in col_lower or 'size' in col_lower:
                        stats['size_bytes'] = row[i]
                    elif 'partition' in col_lower:
                        stats['partitions'] = row[i]
                    elif 'format' in col_lower:
                        stats['format'] = row[i]

    except urllib.error.HTTPError as e:
        return handle_query_error(e, table_name)
    except Exception:
        pass  # DESCRIBE DETAIL may not be supported

    display_stats(stats, table_name)
    return 0


def format_size(size_bytes):
    """Format bytes to human readable."""
    try:
        size = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    except Exception:
        return str(size_bytes)


def display_stats(stats, table_name):
    """Display table statistics."""
    print(f"Statistics for table '{table_name}':")
    print("=" * 50)
    print("")

    row_count = stats.get('row_count', 'N/A')
    print(f"  Row Count:    {row_count:,}" if isinstance(row_count, int) else f"  Row Count:    {row_count}")

    if 'num_files' in stats:
        print(f"  File Count:   {stats['num_files']}")

    if 'size_bytes' in stats:
        print(f"  Size:         {format_size(stats['size_bytes'])}")

    if 'partitions' in stats:
        print(f"  Partitions:   {stats['partitions']}")

    if 'format' in stats:
        print(f"  Format:       {stats['format']}")

    print("")
    print("=" * 50)


def main():
    cli = SkillCLI('table_stats.py',
                   'Get table statistics (row count, size, etc.)')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Table name')
    args = cli.parse()

    # Validate table identifier before interpolating it into SQL text
    if not TABLE_NAME_RE.fullmatch(args.table_name):
        print(f"[ERROR] Invalid table name: '{args.table_name}'")
        print("Table names may only contain letters, digits, underscores, dots and brackets.")
        sys.exit(1)

    sys.exit(get_table_stats(args.workspace_id, args.lakehouse_id, args.table_name))


if __name__ == "__main__":
    main()
