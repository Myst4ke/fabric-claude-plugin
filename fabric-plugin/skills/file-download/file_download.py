#!/usr/bin/env python3
"""
Skill: file-download
Description: Download file from lakehouse storage via OneLake DFS API

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import os
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

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


def download_file(workspace_id, lakehouse_id, file_path, local_destination):
    """Download file from lakehouse via OneLake DFS API."""
    storage_token = get_storage_token()

    # Resolve display names (OneLake DFS requires names, not GUIDs)
    workspace_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}", workspace_id)
    lakehouse_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}",
        lakehouse_id)

    # Normalize file path: ensure it starts with Files/ if not already prefixed
    clean_path = file_path.strip('/')
    if not clean_path.startswith('Files/') and not clean_path.startswith('Tables/'):
        clean_path = f"Files/{clean_path}"

    # Build OneLake DFS URL for file read
    encoded_ws = urllib.parse.quote(workspace_name, safe='')
    encoded_lh = urllib.parse.quote(lakehouse_name, safe='')
    encoded_path = urllib.parse.quote(clean_path, safe='/')

    url = f"{ONELAKE_DFS_BASE}/{encoded_ws}/{encoded_lh}.Lakehouse/{encoded_path}"

    headers = {
        'Authorization': f'Bearer {storage_token}',
        'x-ms-version': '2023-11-03'
    }

    print(f"Downloading file...")
    print(f"  Workspace:   {workspace_name}")
    print(f"  Lakehouse:   {lakehouse_name}")
    print(f"  Source:      /{clean_path}")
    print(f"  Destination: {local_destination}")
    print("")

    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        resp = urllib.request.urlopen(req)
        content = resp.read()

        # Create parent directory if needed
        dest_path = Path(local_destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_destination, 'wb') as f:
            f.write(content)

        file_size = len(content)
        print(f"[SUCCESS] File downloaded!")
        print(f"  Size:     {file_size:,} bytes")
        print(f"  Saved to: {local_destination}")
        return 0

    except urllib.error.HTTPError as e:
        return handle_dfs_error(e, clean_path)
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        return 2


def handle_dfs_error(error, file_path):
    """Handle OneLake DFS HTTP errors with path hints."""
    if error.code == 404:
        print(f"[ERROR] File not found: /{file_path}")
        print("")
        print("Use fabric-plugin:file-list to see available files.")
        print("Make sure the path includes the Files/ prefix, e.g.:")
        print("  Files/raw/data.csv")
        return 1
    return handle_http_error(error, "File")


def main():
    cli = SkillCLI('file_download.py',
                   'Download file from lakehouse storage via OneLake DFS API')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('file_path', help='Path to file in lakehouse (e.g. Files/data/sales.csv)')
    cli.positional('local_destination', help='Local path to save file')
    args = cli.parse()

    sys.exit(download_file(args.workspace_id, args.lakehouse_id,
                           args.file_path, args.local_destination))


if __name__ == "__main__":
    main()
