#!/usr/bin/env python3
"""
Skill: file-delete
Description: Delete file from lakehouse storage via OneLake DFS API

Accepts workspace and lakehouse as display names or GUIDs.
WARNING: This operation is IRREVERSIBLE!
"""

import sys
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


def delete_file(workspace_id, lakehouse_id, file_path):
    """Delete file from lakehouse via OneLake DFS API."""
    storage_token = get_storage_token()

    # Resolve display names (OneLake DFS requires names, not GUIDs)
    workspace_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}", workspace_id)
    lakehouse_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}",
        lakehouse_id)

    # Normalize file path
    clean_path = file_path.strip('/')
    if not clean_path.startswith('Files/') and not clean_path.startswith('Tables/'):
        clean_path = f"Files/{clean_path}"

    # Build OneLake DFS URL
    encoded_ws = urllib.parse.quote(workspace_name, safe='')
    encoded_lh = urllib.parse.quote(lakehouse_name, safe='')
    encoded_path = urllib.parse.quote(clean_path, safe='/')

    url = f"{ONELAKE_DFS_BASE}/{encoded_ws}/{encoded_lh}.Lakehouse/{encoded_path}"

    headers = {
        'Authorization': f'Bearer {storage_token}',
        'x-ms-version': '2023-11-03'
    }

    print(f"Deleting file...")
    print(f"  Workspace: {workspace_name}")
    print(f"  Lakehouse: {lakehouse_name}")
    print(f"  Path:      /{clean_path}")
    print("")

    try:
        req = urllib.request.Request(url, headers=headers, method='DELETE')
        urllib.request.urlopen(req)

        print(f"[SUCCESS] File deleted: /{clean_path}")
        return 0

    except urllib.error.HTTPError as e:
        return handle_dfs_error(e, clean_path)
    except Exception as e:
        print(f"[ERROR] Delete failed: {e}")
        return 2


def handle_dfs_error(error, file_path):
    """Handle OneLake DFS HTTP errors with path hints."""
    if error.code == 404:
        print(f"[ERROR] File not found: /{file_path}")
        print("Use fabric-plugin:file-list to see available files.")
        return 1
    return handle_http_error(error, "File")


def main():
    cli = SkillCLI('file_delete.py',
                   'Delete file from lakehouse storage (IRREVERSIBLE)')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('file_path', help='Path to file in lakehouse (e.g. Files/raw/data.csv)')
    args = cli.parse()

    sys.exit(delete_file(args.workspace_id, args.lakehouse_id, args.file_path))


if __name__ == "__main__":
    main()
