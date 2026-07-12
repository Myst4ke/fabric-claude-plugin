#!/usr/bin/env python3
"""
Skill: git-status
Description: Get Git connection status and sync state of a workspace
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def show_status(workspace_id):
    """Show Git connection and sync status."""
    print(f"\nGit Status for workspace {workspace_id}")
    print(f"{'='*70}")

    # 1. Connection details
    try:
        conn = fabric_request_json(
            f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/connection")
        provider = conn.get('gitProviderDetails', {})
        print(f"\n  Connection:")
        print(f"    Provider:    {provider.get('gitProviderType', 'N/A')}")
        print(f"    Org:         {provider.get('organizationName', 'N/A')}")
        if provider.get('projectName'):
            print(f"    Project:     {provider['projectName']}")
        print(f"    Repository:  {provider.get('repositoryName', 'N/A')}")
        print(f"    Branch:      {provider.get('branchName', 'N/A')}")
        print(f"    Directory:   {provider.get('directoryName', '/')}")

        sync_details = conn.get('gitSyncDetails', {})
        if sync_details:
            head = sync_details.get('head', 'N/A')
            last_sync = sync_details.get('lastSyncTime', 'N/A')
            print(f"\n  Sync Details:")
            print(f"    HEAD commit: {head[:12] if len(head) > 12 else head}...")
            print(f"    Last sync:   {last_sync}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("\n  [INFO] Workspace is not connected to Git.")
            print(f"  Connect: fabric-plugin:git-connect {workspace_id} ...")
            return 0
        return handle_http_error(e, "Workspace")

    # 2. Sync status (changed items)
    print(f"\n  Changed Items:")
    print(f"  {'-'*60}")
    try:
        status = fabric_request_json(
            f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/status")
        changes = status.get('changes', [])

        if not changes:
            print(f"    Workspace is in sync with Git. No changes.")
        else:
            workspace_changes = [c for c in changes if c.get('workspaceChange')]
            remote_changes = [c for c in changes if c.get('remoteChange')]

            if workspace_changes:
                print(f"\n    Workspace changes (not committed):")
                for c in workspace_changes:
                    name = c.get('itemMetadata', {}).get('displayName', 'N/A')
                    item_type = c.get('itemMetadata', {}).get('itemType', '')
                    change_type = c.get('workspaceChange', 'modified')
                    print(f"      {change_type:<12} {item_type:<20} {name}")

            if remote_changes:
                print(f"\n    Remote changes (not pulled):")
                for c in remote_changes:
                    name = c.get('itemMetadata', {}).get('displayName', 'N/A')
                    item_type = c.get('itemMetadata', {}).get('itemType', '')
                    change_type = c.get('remoteChange', 'modified')
                    print(f"      {change_type:<12} {item_type:<20} {name}")

            print(f"\n    Total: {len(workspace_changes)} workspace, "
                  f"{len(remote_changes)} remote change(s)")
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            print(f"    [INFO] Could not retrieve sync status.")
        else:
            print(f"    [WARN] HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"    [WARN] Could not get status: {e}")

    print(f"\n{'='*70}")
    print(f"\nActions:")
    print(f"  - Commit to Git:    fabric-plugin:git-commit {workspace_id}")
    print(f"  - Update from Git:  fabric-plugin:git-update {workspace_id}")
    print(f"  - Disconnect:       fabric-plugin:git-disconnect {workspace_id}")
    return 0


def main():
    cli = SkillCLI('git_status.py',
                   'Get Git connection status and sync state of a workspace')
    cli.workspace()
    args = cli.parse()

    sys.exit(show_status(args.workspace_id))


if __name__ == "__main__":
    main()
