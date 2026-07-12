#!/usr/bin/env python3
"""
Skill: git-disconnect
Description: Disconnect a workspace from its Git repository
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, handle_http_error,
                         check_security)


def disconnect_git(workspace_id):
    """Disconnect workspace from Git."""
    check_security(workspace_id, "git:disconnect")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/disconnect"

    try:
        response = fabric_request(url, method='POST')
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("[ERROR] Forbidden. Need Admin role to disconnect from Git.")
            return 1
        elif e.code == 404:
            print("[INFO] Workspace is not connected to Git (nothing to disconnect).")
            return 0
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 204):
        print(f"\n[SUCCESS] Workspace disconnected from Git.")
        print(f"  Workspace items are preserved (not deleted).")
        print(f"\nTo reconnect:")
        print(f"  fabric-plugin:git-connect {workspace_id} ...")
        return 0
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def main():
    cli = SkillCLI('git_disconnect.py',
                   'Disconnect a workspace from its Git repository')
    cli.workspace()
    args = cli.parse()

    sys.exit(disconnect_git(args.workspace_id))


if __name__ == "__main__":
    main()
