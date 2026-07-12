#!/usr/bin/env python3
"""
Skill: notebook-get
Description: Get detailed information about a notebook

Accepts workspace and notebook as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_notebook(notebook):
    """Display notebook details."""
    print("\n" + "="*60)
    print("NOTEBOOK DETAILS")
    print("="*60)
    print(f"Name:        {notebook.get('displayName', 'N/A')}")
    print(f"ID:          {notebook.get('id', 'N/A')}")
    print(f"Description: {notebook.get('description', 'N/A')}")
    print(f"Workspace:   {notebook.get('workspaceId', 'N/A')}")
    print("="*60)

    # Print raw JSON for complete details
    print("\nRaw JSON:")
    print(json.dumps(notebook, indent=2))


def main():
    cli = SkillCLI('notebook_get.py',
                   'Get detailed information about a notebook')
    cli.workspace()
    cli.item('notebook')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/notebooks/{args.notebook_id}"
    try:
        notebook = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Notebook"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_notebook(notebook)
    sys.exit(0)


if __name__ == "__main__":
    main()
