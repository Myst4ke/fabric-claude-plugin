#!/usr/bin/env python3
"""
Skill: git-update
Description: Update workspace from Git (pull remote changes)
"""

import sys
import os
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         handle_http_error, check_security)


def update_from_git(workspace_id, conflict_resolution='PreferRemote'):
    """Pull changes from Git into workspace."""
    check_security(workspace_id, "git:update")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/updateFromGit"

    body = {
        'conflictResolution': {
            'conflictResolutionType': conflict_resolution
        }
    }

    try:
        response = fabric_request(url, method='POST', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("[ERROR] Workspace not connected to Git.")
            print(f"  Connect: fabric-plugin:git-connect {workspace_id} ...")
            return 1
        elif e.code == 409:
            print("[ERROR] Conflict. Commit local changes first or use "
                  "--conflict-resolution PreferRemote.")
            print(f"  Commit: fabric-plugin:git-commit {workspace_id}")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 204):
        print(f"\n[SUCCESS] Workspace updated from Git.")
        print(f"  Conflict resolution: {conflict_resolution}")
        return 0
    elif response.status == 202:
        location = response.headers.get('Location', '')
        retry_after = int(response.headers.get('Retry-After', '5'))
        print("[INFO] Update in progress...")
        return poll_lro(location, retry_after)
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def poll_lro(location, retry_after):
    """Poll long-running operation."""
    if not location:
        print("[SUCCESS] Update submitted.")
        return 0

    max_polls = 30
    for i in range(max_polls):
        time.sleep(min(retry_after, 10))
        try:
            data = fabric_request_json(location)
            status = data.get('status', '').lower()
            if status == 'succeeded':
                print(f"\n[SUCCESS] Workspace updated from Git.")
                return 0
            elif status in ('failed', 'cancelled'):
                error = data.get('error', {})
                print(f"[ERROR] Update {status}: {error.get('message', 'Unknown error')}")
                return 1
            else:
                if i % 3 == 0:
                    print(f"  Updating... ({i + 1}/{max_polls})")
        except Exception:
            pass

    print("[WARN] Update still in progress. Check git status later.")
    return 0


def main():
    cli = SkillCLI('git_update.py',
                   'Update workspace from Git (pull remote changes)')
    cli.workspace()
    cli.opt('--conflict-resolution', default='PreferRemote',
            choices=['PreferWorkspace', 'PreferRemote'],
            help='Conflict resolution strategy (default: PreferRemote)')
    args = cli.parse()

    sys.exit(update_from_git(args.workspace_id, args.conflict_resolution))


if __name__ == "__main__":
    main()
