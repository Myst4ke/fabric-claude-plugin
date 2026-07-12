#!/usr/bin/env python3
"""
Skill: notebook-update
Description: Update a notebook's name or description

Accepts workspace and notebook as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_updated_notebook(notebook):
    """Display updated notebook details."""
    print("\n[SUCCESS] Notebook updated successfully!")
    print("="*60)
    print(f"Name:        {notebook.get('displayName', 'N/A')}")
    print(f"ID:          {notebook.get('id', 'N/A')}")
    print(f"Description: {notebook.get('description', 'N/A')}")
    print(f"Workspace:   {notebook.get('workspaceId', 'N/A')}")
    print("="*60)


def main():
    cli = SkillCLI('notebook_update.py',
                   "Update a notebook's name or description")
    cli.workspace()
    cli.item('notebook')
    cli.opt('--name', help='New name for the notebook')
    cli.opt('--description', help='New description for the notebook')
    args = cli.parse()

    if not args.name and args.description is None:
        print("[ERROR] Must provide --name or --description to update")
        sys.exit(1)

    body = {}
    if args.name:
        body["displayName"] = args.name
    if args.description is not None:
        body["description"] = args.description

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/notebooks/{args.notebook_id}"
    try:
        notebook = fabric_request_json(url, method='PATCH', data=body)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Notebook"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_updated_notebook(notebook)
    sys.exit(0)


if __name__ == "__main__":
    main()
