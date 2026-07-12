#!/usr/bin/env python3
"""
Skill: onelake-list-files
Description: List files in OneLake storage (ADLS Gen2 compatible)

Security features:
- Read-only operation
- Requires storage scope token
- Audit logging

Accepts workspace and lakehouse as display names or GUIDs.
"""

import sys
import json
import os
import urllib.request
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request_json,
                         get_storage_token, check_security, log_audit)

ONELAKE_DFS_BASE = "https://onelake.dfs.fabric.microsoft.com"


def get_display_name(url, fallback):
    """Resolve an entity URL to its display name via Fabric API."""
    try:
        data = fabric_request_json(url)
        return data.get('displayName', fallback)
    except Exception as e:
        print(f"[WARN] Could not retrieve display name: {e}")
        return fallback


def list_files(workspace_id, lakehouse_id, path="/Files"):
    """List files in OneLake lakehouse."""

    # Security check (warning-only mode)
    check_security(workspace_id, "onelake:list-files")

    # Get storage token (cached + silent refresh handled by fabric_base)
    storage_token = get_storage_token()

    # Get workspace and lakehouse names (OneLake requires names not GUIDs)
    print(f"[INFO] Retrieving workspace and lakehouse information...")
    workspace_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}", workspace_id)
    lakehouse_name = get_display_name(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}",
        lakehouse_id)

    print(f"[INFO] Workspace: {workspace_name}")
    print(f"[INFO] Lakehouse: {lakehouse_name}")
    print()

    # Construct OneLake DFS API URL
    path_clean = path.strip('/')
    onelake_path = f"/{lakehouse_name}.Lakehouse/{path_clean}" if path_clean else f"/{lakehouse_name}.Lakehouse"

    url = f"{ONELAKE_DFS_BASE}/{workspace_name}{onelake_path}?resource=filesystem&recursive=false"

    headers = {
        'Authorization': f'Bearer {storage_token}',
        'x-ms-version': '2023-11-03'
    }

    try:
        print(f"[INFO] Listing files in path: /{path_clean or 'root'}")
        print(f"[DEBUG] OneLake URI: {url}")
        print()

        request = urllib.request.Request(url, headers=headers, method='GET')
        response = urllib.request.urlopen(request)
        result = response.read().decode('utf-8')

        # Parse response (newline-delimited JSON from ADLS Gen2 API)
        files = []
        for line in result.strip().split('\n'):
            if line:
                try:
                    files.append(json.loads(line))
                except Exception:
                    pass

        log_audit("onelake:list-files", workspace_id, True,
                  lakehouse_id=lakehouse_id, path=path, file_count=len(files))

        display_files(files, workspace_name, lakehouse_name, path)
        return 0

    except urllib.error.HTTPError as e:
        error_msg = handle_dfs_error(e)
        log_audit("onelake:list-files", workspace_id, False,
                  error=error_msg, http_code=e.code,
                  lakehouse_id=lakehouse_id, path=path)
        return 1

    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        log_audit("onelake:list-files", workspace_id, False,
                  error=str(e), lakehouse_id=lakehouse_id, path=path)
        return 2


def display_files(files, workspace_name, lakehouse_name, path):
    """Display file listing."""
    print("=" * 100)
    print(f"  OneLake Files - {workspace_name}/{lakehouse_name}{path}")
    print("=" * 100)
    print()
    print(f"Total: {len(files)} item(s)")
    print()

    if not files:
        print("(No files found)")
        return

    # Separate directories and files
    directories = [f for f in files if f.get('isDirectory', False)]
    regular_files = [f for f in files if not f.get('isDirectory', False)]

    if directories:
        print("Directories:")
        for d in directories:
            print(f"  [DIR] {d.get('name', 'unknown')}/")
        print()

    if regular_files:
        print("Files:")
        print(f"{'Name':<50} {'Size':<15} {'Last Modified':<25}")
        print(f"{'-'*50} {'-'*15} {'-'*25}")

        for f in regular_files:
            name = f.get('name', 'unknown')
            size_str = format_size(f.get('contentLength', 0))
            last_modified = f.get('lastModified', 'unknown')

            if len(name) > 50:
                name = name[:47] + '...'

            print(f"{name:<50} {size_str:<15} {last_modified:<25}")

    print()


def format_size(bytes_size):
    """Format file size in human-readable format."""
    try:
        size = int(bytes_size)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    except Exception:
        return str(bytes_size)


def handle_dfs_error(error):
    """Handle OneLake DFS HTTP errors."""
    if error.code == 401:
        print("[ERROR] Unauthorized. Storage token expired.")
        return "Unauthorized"
    elif error.code == 403:
        print("[ERROR] Forbidden. Check lakehouse permissions.")
        return "Forbidden"
    elif error.code == 404:
        print("[ERROR] Path not found.")
        return "Not found"
    elif error.code == 429:
        retry_after = error.headers.get('Retry-After', '30')
        print(f"[ERROR] Rate limited. Retry after {retry_after} seconds.")
        return "Rate limited"
    else:
        try:
            error_body = error.read().decode('utf-8')
            print(f"[ERROR] HTTP {error.code}: {error.reason}")
            print(f"Details: {error_body}")
        except Exception:
            print(f"[ERROR] HTTP {error.code}: {error.reason}")
        return f"HTTP {error.code}"


def main():
    cli = SkillCLI('onelake_list_files.py',
                   'List files in OneLake lakehouse storage (ADLS Gen2 API)')
    cli.workspace()
    cli.item('lakehouse')
    cli.opt('--path', default='/Files', help='Path to list (default: /Files)')
    args = cli.parse()

    sys.exit(list_files(args.workspace_id, args.lakehouse_id, args.path))


if __name__ == "__main__":
    main()
