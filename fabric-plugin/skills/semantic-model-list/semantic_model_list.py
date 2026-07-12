#!/usr/bin/env python3
"""
Skill: semantic-model-list
Description: List all semantic models (Power BI datasets) in a workspace
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_models(models, workspace_id):
    """Display semantic models in formatted output."""
    count = len(models)
    print(f"\nFound {count} semantic model(s):\n")

    if count == 0:
        print("No semantic models in this workspace.")
        return

    print(f"{'Model Name':<35} {'ID':<38} {'Description':<40}")
    print(f"{'-'*35} {'-'*38} {'-'*40}")

    for model in models:
        name = model.get('displayName', 'N/A')[:35]
        model_id = model.get('id', 'N/A')[:38]
        desc = model.get('description', '')[:40]
        print(f"{name:<35} {model_id:<38} {desc:<40}")

    print(f"\nNext steps:")
    print(f"  - Details: fabric-plugin:semantic-model-get {workspace_id} <model-id>")
    print(f"  - Refresh: fabric-plugin:semantic-model-refresh {workspace_id} <model-id>")
    print(f"  - History: fabric-plugin:semantic-model-refresh-history {workspace_id} <model-id>")


def main():
    cli = SkillCLI('semantic_model_list.py',
                   'List all semantic models (Power BI datasets) in a workspace')
    cli.workspace()
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/semanticModels"
    try:
        models = fabric_list(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_models(models, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
