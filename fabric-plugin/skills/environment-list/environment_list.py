#!/usr/bin/env python3
"""
Skill: environment-list
Description: List all environments (Spark/Python configurations) in a workspace
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_environments(envs, workspace_id):
    """Display environments."""
    count = len(envs)
    print(f"\nFound {count} environment(s):\n")

    if count == 0:
        print("No environments in this workspace.")
        print(f"\nCreate one: fabric-plugin:environment-create "
              f"{workspace_id} <name>")
        return

    print(f"{'Environment Name':<35} {'ID':<38} {'Description':<30}")
    print(f"{'-'*35} {'-'*38} {'-'*30}")

    for env in envs:
        name = env.get('displayName', 'N/A')[:35]
        env_id = env.get('id', 'N/A')[:38]
        desc = env.get('description', '')[:30]
        print(f"{name:<35} {env_id:<38} {desc:<30}")

    print(f"\nNext steps:")
    print(f"  - Details:  fabric-plugin:environment-get {workspace_id} <env-id>")
    print(f"  - Staging:  fabric-plugin:environment-staging {workspace_id} <env-id>")
    print(f"  - Publish:  fabric-plugin:environment-publish {workspace_id} <env-id>")


def main():
    cli = SkillCLI('environment_list.py',
                   'List all environments (Spark/Python configurations) '
                   'in a workspace')
    cli.workspace()
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/environments"
    try:
        envs = fabric_list(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_environments(envs, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
