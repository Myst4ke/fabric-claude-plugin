#!/usr/bin/env python3
"""
Skill: file-upload
Description: Upload file to lakehouse storage via OneLake DFS API

Uses the ADLS Gen2 protocol (3-step: create, append, flush).
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


def upload_file(workspace_id, lakehouse_id, local_file, destination_path):
    """Upload file to lakehouse via OneLake DFS API (ADLS Gen2 protocol)."""
    # Validate local file
    local_path = Path(local_file)
    if not local_path.exists():
        print(f"[ERROR] Local file not found: {local_file}")
        return 1
    if not local_path.is_file():
        print(f"[ERROR] Not a file: {local_file}")
        return 1

    file_size = local_path.stat().st_size

    storage_token = get_storage_token()

    # Resolve display names (OneLake DFS requires names, not GUIDs)
    workspace_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}", workspace_id)
    lakehouse_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}",
        lakehouse_id)

    # Normalize destination path: ensure it starts with Files/
    clean_dest = destination_path.strip('/')
    if not clean_dest.startswith('Files/') and not clean_dest.startswith('Tables/'):
        clean_dest = f"Files/{clean_dest}"

    # Build OneLake DFS base URL for the file
    encoded_ws = urllib.parse.quote(workspace_name, safe='')
    encoded_lh = urllib.parse.quote(lakehouse_name, safe='')
    encoded_path = urllib.parse.quote(clean_dest, safe='/')

    base_url = f"{ONELAKE_DFS_BASE}/{encoded_ws}/{encoded_lh}.Lakehouse/{encoded_path}"

    base_headers = {
        'Authorization': f'Bearer {storage_token}',
        'x-ms-version': '2023-11-03'
    }

    print(f"Uploading file...")
    print(f"  Workspace:   {workspace_name}")
    print(f"  Lakehouse:   {lakehouse_name}")
    print(f"  Source:      {local_file}")
    print(f"  Size:        {file_size:,} bytes")
    print(f"  Destination: /{clean_dest}")
    print("")

    try:
        # Step 1: Create file (PUT ?resource=file)
        create_url = f"{base_url}?resource=file"
        create_headers = {**base_headers, 'Content-Length': '0'}
        req = urllib.request.Request(create_url, data=b'', headers=create_headers, method='PUT')
        urllib.request.urlopen(req)
        print("  [1/3] File created")

        # Step 2: Append data (PATCH ?action=append&position=0)
        with open(local_file, 'rb') as f:
            file_data = f.read()

        append_url = f"{base_url}?action=append&position=0"
        append_headers = {
            **base_headers,
            'Content-Length': str(file_size),
            'Content-Type': 'application/octet-stream'
        }
        req = urllib.request.Request(append_url, data=file_data, headers=append_headers, method='PATCH')
        urllib.request.urlopen(req)
        print("  [2/3] Data uploaded")

        # Step 3: Flush (PATCH ?action=flush&position={size})
        flush_url = f"{base_url}?action=flush&position={file_size}"
        flush_headers = {**base_headers, 'Content-Length': '0'}
        req = urllib.request.Request(flush_url, data=b'', headers=flush_headers, method='PATCH')
        urllib.request.urlopen(req)
        print("  [3/3] File committed")

        print("")
        print(f"[SUCCESS] File uploaded!")
        print(f"  Destination: /{clean_dest}")
        return 0

    except urllib.error.HTTPError as e:
        return handle_dfs_error(e, clean_dest)
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return 2


def handle_dfs_error(error, destination_path):
    """Handle OneLake DFS HTTP errors with path hints."""
    if error.code == 404:
        print(f"[ERROR] Lakehouse path not found: /{destination_path}")
        print("")
        print("Make sure the parent folder exists. Destination should include the Files/ prefix:")
        print("  Files/raw/data.csv")
        return 1
    elif error.code == 409:
        print(f"[ERROR] Conflict. File already exists at: /{destination_path}")
        print("        Delete the existing file first or use a different name.")
        return 1
    return handle_http_error(error, "File")


def main():
    cli = SkillCLI('file_upload.py',
                   'Upload file to lakehouse storage via OneLake DFS API')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('local_file', help='Path to local file to upload')
    cli.positional('destination_path', help='Destination path in lakehouse (e.g. Files/raw/data.csv)')
    args = cli.parse()

    sys.exit(upload_file(args.workspace_id, args.lakehouse_id,
                         args.local_file, args.destination_path))


if __name__ == "__main__":
    main()
