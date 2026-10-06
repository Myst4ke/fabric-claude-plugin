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


def get_sync_state(workspace_id):
    """Return (workspaceHead, remoteCommitHash, remote_change_count).

    The updateFromGit API requires both hashes: they pin the update to the
    state the caller actually observed, so a concurrent commit cannot be
    applied silently."""
    status = fabric_request_json(
        f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/status")
    changes = status.get('changes', []) or []
    remote_changes = [c for c in changes if c.get('remoteChange')]
    return (status.get('workspaceHead'), status.get('remoteCommitHash'),
            len(remote_changes))


def update_from_git(workspace_id, conflict_resolution='PreferRemote',
                    allow_override_items=False):
    """Pull changes from Git into workspace."""
    check_security(workspace_id, "git:update")

    # 1. Read the current sync state — both hashes are mandatory in the body.
    try:
        workspace_head, remote_commit, remote_count = get_sync_state(workspace_id)
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            print("[ERROR] Workspace not connected to Git (or sync state "
                  "unavailable).")
            print(f"  Check:   fabric-plugin:git-status {workspace_id}")
            print(f"  Connect: fabric-plugin:git-connect {workspace_id} ...")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Could not read Git status: {e}")
        return 2

    if not remote_commit:
        print("[ERROR] No remote commit hash returned — workspace is probably "
              "not connected to Git.")
        return 1

    if workspace_head == remote_commit:
        print("[SUCCESS] Workspace already up to date with Git "
              f"(HEAD {remote_commit[:12]}). Nothing to pull.")
        return 0

    print(f"  Workspace HEAD: {workspace_head[:12] if workspace_head else 'N/A'}")
    print(f"  Remote commit:  {remote_commit[:12]}")
    print(f"  Incoming item change(s): {remote_count}")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/updateFromGit"

    # conflictResolutionType selects WHICH side is being resolved ('Workspace'),
    # conflictResolutionPolicy selects WHO wins. Sending the policy value as the
    # type (the historical bug here) makes the API reject the whole request.
    body = {
        'workspaceHead': workspace_head,
        'remoteCommitHash': remote_commit,
        'conflictResolution': {
            'conflictResolutionType': 'Workspace',
            'conflictResolutionPolicy': conflict_resolution,
        },
        'options': {
            'allowOverrideItems': bool(allow_override_items),
        },
    }

    try:
        response = fabric_request(url, method='POST', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("[ERROR] Workspace not connected to Git.")
            print(f"  Connect: fabric-plugin:git-connect {workspace_id} ...")
            return 1
        elif e.code == 400:
            detail = ''
            try:
                detail = e.read().decode('utf-8', 'replace')
            except Exception:
                pass
            if 'OverrideItemsNotAllowed' in detail:
                print("[ERROR] The update would replace existing workspace "
                      "items, which requires explicit consent.")
                print("  Re-run with --allow-override-items to authorize it.")
                return 1
            print(f"[ERROR] Request rejected (HTTP 400): {detail[:500]}")
            return 1
        elif e.code == 409:
            print("[ERROR] Conflict. Commit local changes first, or re-run "
                  "with --conflict-resolution PreferRemote.")
            print(f"  Commit: fabric-plugin:git-commit {workspace_id}")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 204):
        print(f"\n[SUCCESS] Workspace updated from Git.")
        print(f"  Conflict policy: {conflict_resolution}")
        return 0
    elif response.status == 202:
        location = response.headers.get('Location', '')
        operation_id = response.headers.get('x-ms-operation-id', '')
        if not location and operation_id:
            location = f"{FABRIC_API_BASE}/operations/{operation_id}"
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
            help='Which side wins on conflict (default: PreferRemote)')
    cli.flag('--allow-override-items',
             help='Authorize replacing existing workspace items. Required by '
                  'the API whenever an incoming item already exists.')
    args = cli.parse()

    sys.exit(update_from_git(args.workspace_id, args.conflict_resolution,
                             args.allow_override_items))


if __name__ == "__main__":
    main()
