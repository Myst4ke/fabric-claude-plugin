#!/usr/bin/env python3
"""
Skill: notebook-list
Description: List all notebooks in a Microsoft Fabric workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_notebooks(notebooks):
    """Display notebooks in formatted table."""
    count = len(notebooks)
    print(f"\nFound {count} notebook(s):\n")

    if count == 0:
        print("No notebooks in workspace")
        return

    print(f"{'Name':<40} {'ID':<38}")
    print(f"{'-'*40} {'-'*38}")

    for nb in notebooks:
        name = nb.get('displayName', 'N/A')[:40]
        nb_id = nb.get('id', 'N/A')
        print(f"{name:<40} {nb_id:<38}")

    print(f"\nUse fabric-plugin:notebook-get <workspace> <notebook> for details")


def main():
    cli = SkillCLI('notebook_list.py',
                   'List all notebooks in a Microsoft Fabric workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of notebooks to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/notebooks"
    try:
        notebooks = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_notebooks(notebooks)
    sys.exit(0)


if __name__ == "__main__":
    main()
