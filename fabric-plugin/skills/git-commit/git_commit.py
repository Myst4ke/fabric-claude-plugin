#!/usr/bin/env python3
"""
Skill: git-commit
Description: Commit workspace changes to the connected Git repository
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


def commit_to_git(workspace_id, message=None):
    """Commit workspace changes to Git."""
    check_security(workspace_id, "git:commit")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/commitToGit"

    body = {'mode': 'All'}
    if message:
        body['comment'] = message

    try:
        response = fabric_request(url, method='POST', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("[ERROR] Workspace not connected to Git.")
            print(f"  Connect: fabric-plugin:git-connect {workspace_id} ...")
            return 1
        elif e.code == 409:
            print("[ERROR] Conflict. There may be remote changes to pull first.")
            print(f"  Update: fabric-plugin:git-update {workspace_id}")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 204):
        print(f"\n[SUCCESS] Workspace changes committed to Git.")
        if message:
            print(f"  Message: {message}")
        return 0
    elif response.status == 202:
        location = response.headers.get('Location', '')
        retry_after = int(response.headers.get('Retry-After', '5'))
        print("[INFO] Commit in progress...")
        return poll_lro(location, retry_after, message)
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def poll_lro(location, retry_after, message):
    """Poll long-running operation."""
    if not location:
        print("[SUCCESS] Commit submitted.")
        return 0

    max_polls = 30
    for i in range(max_polls):
        time.sleep(min(retry_after, 10))
        try:
            data = fabric_request_json(location)
            status = data.get('status', '').lower()
            if status == 'succeeded':
                print(f"\n[SUCCESS] Workspace changes committed to Git.")
                if message:
                    print(f"  Message: {message}")
                return 0
            elif status in ('failed', 'cancelled'):
                error = data.get('error', {})
                print(f"[ERROR] Commit {status}: {error.get('message', 'Unknown error')}")
                return 1
            else:
                if i % 3 == 0:
                    print(f"  Committing... ({i + 1}/{max_polls})")
        except Exception:
            pass

    print("[WARN] Commit still in progress. Check git status later.")
    return 0


def main():
    cli = SkillCLI('git_commit.py',
                   'Commit workspace changes to the connected Git repository')
    cli.workspace()
    cli.opt('--message', help='Commit message')
    args = cli.parse()

    sys.exit(commit_to_git(args.workspace_id, args.message))


if __name__ == "__main__":
    main()
