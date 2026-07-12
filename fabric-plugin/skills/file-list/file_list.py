#!/usr/bin/env python3
"""
Skill: file-list
Description: List files in lakehouse storage via OneLake DFS API

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
from fabric_base import (FABRIC_API_BASE, fabric_request_json,
                         get_storage_token, handle_http_error)

ONELAKE_DFS_BASE = "https://onelake.dfs.fabric.microsoft.com"


def get_display_name(url, fallback):
    """Resolve an entity URL to its display name via Fabric API."""
    try:
        data = fabric_request_json(url)
        return data.get('displayName', fallback)
    except Exception:
        return fallback


def list_files(workspace_id, lakehouse_id, path=None):
    """List files in lakehouse via OneLake DFS API."""
    storage_token = get_storage_token()

    # OneLake DFS requires display names, not GUIDs
    workspace_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}", workspace_id)
    lakehouse_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}",
        lakehouse_id)

    # Build DFS path (default to Files/ directory if no path specified)
    if not path:
        dfs_directory = "Files"
    else:
        dfs_directory = path.strip('/')

    # OneLake DFS URL: /{workspace}/{lakehouse}.Lakehouse/?resource=filesystem&directory={path}
    encoded_ws = urllib.parse.quote(workspace_name, safe='')
    encoded_lh = urllib.parse.quote(lakehouse_name, safe='')
    encoded_dir = urllib.parse.quote(dfs_directory, safe='/')

    url = (f"{ONELAKE_DFS_BASE}/{encoded_ws}/{encoded_lh}.Lakehouse"
           f"?resource=filesystem&recursive=false&directory={encoded_dir}")

    headers = {
        'Authorization': f'Bearer {storage_token}',
        'x-ms-version': '2023-11-03'
    }

    print(f"Listing files in lakehouse...")
    print(f"  Workspace: {workspace_name}")
    print(f"  Lakehouse: {lakehouse_name}")
    print(f"  Path:      /{dfs_directory}")
    print("")

    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode('utf-8'))

        paths = result.get('paths', [])
        display_files(paths, dfs_directory)
        return 0

    except urllib.error.HTTPError as e:
        return handle_dfs_error(e, dfs_directory)
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def handle_dfs_error(error, path):
    """Handle OneLake DFS HTTP errors with path hints."""
    if error.code == 404:
        print(f"[ERROR] Path not found: /{path}")
        print("")
        print("Common paths in a lakehouse:")
        print("  Files/         - Unmanaged files area")
        print("  Tables/        - Managed Delta tables")
        print("")
        print("Use without --path to list the root, or try:")
        print("  --path Files")
        print("  --path Tables")
        return 1
    return handle_http_error(error, "Lakehouse")


def format_size(size_bytes):
    """Format bytes to human readable."""
    try:
        size = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:,.0f} {unit}"
            size /= 1024
        return f"{size:,.2f} PB"
    except (ValueError, TypeError):
        return str(size_bytes)


def display_files(paths, base_directory):
    """Display DFS paths in formatted output."""
    count = len(paths)
    print(f"Found {count} item(s):\n")

    if count == 0:
        print("(Empty folder)")
        return

    # Separate directories and files
    folders = [p for p in paths if p.get('isDirectory', 'false') == 'true']
    files = [p for p in paths if p.get('isDirectory', 'false') != 'true']

    # Header
    print(f"{'Type':<8} {'Name':<50} {'Size':<15} {'Last Modified':<25}")
    print(f"{'-'*8} {'-'*50} {'-'*15} {'-'*25}")

    for item in folders:
        name = item.get('name', 'N/A')
        # Show only relative name (strip base directory prefix)
        if '/' in name:
            name = name.rsplit('/', 1)[-1]
        print(f"{'[DIR]':<8} {name[:50]:<50} {'-':<15} {'':<25}")

    for item in files:
        name = item.get('name', 'N/A')
        if '/' in name:
            name = name.rsplit('/', 1)[-1]
        size = format_size(item.get('contentLength', 0))
        modified = item.get('lastModified', '')
        print(f"{'[FILE]':<8} {name[:50]:<50} {size:<15} {modified[:25]:<25}")

    print("")


def main():
    cli = SkillCLI('file_list.py',
                   'List files in lakehouse storage via OneLake DFS API')
    cli.workspace()
    cli.item('lakehouse')
    cli.opt('--path', help='Folder path to list (default: Files/)')
    args = cli.parse()

    sys.exit(list_files(args.workspace_id, args.lakehouse_id, args.path))


if __name__ == "__main__":
    main()
