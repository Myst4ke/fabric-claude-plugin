#!/usr/bin/env python3
"""
Skill: semantic-model-get
Description: Get detailed information about a semantic model (Power BI dataset)
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_model(model, workspace_id):
    """Display semantic model details."""
    print(f"\nSemantic Model Details:")
    print(f"{'='*60}")
    print(f"  Name:         {model.get('displayName', 'N/A')}")
    print(f"  ID:           {model.get('id', 'N/A')}")
    print(f"  Description:  {model.get('description', '(none)')}")
    print(f"  Workspace:    {workspace_id}")

    # Additional properties if available
    if 'createdDate' in model:
        print(f"  Created:      {model['createdDate']}")
    if 'modifiedDate' in model:
        print(f"  Modified:     {model['modifiedDate']}")
    if 'configuredBy' in model:
        print(f"  Configured by: {model['configuredBy']}")
    if 'targetStorageMode' in model:
        print(f"  Storage Mode: {model['targetStorageMode']}")
    if 'isRefreshable' in model:
        print(f"  Refreshable:  {model['isRefreshable']}")

    print(f"{'='*60}")
    print(f"\nNext steps:")
    model_id = model.get('id', '<model-id>')
    print(f"  - Refresh:  fabric-plugin:semantic-model-refresh {workspace_id} {model_id}")
    print(f"  - History:  fabric-plugin:semantic-model-refresh-history {workspace_id} {model_id}")


def main():
    cli = SkillCLI('semantic_model_get.py',
                   'Get detailed information about a semantic model '
                   '(Power BI dataset)')
    cli.workspace()
    cli.item('semanticmodel', help='Semantic model name or GUID')
    args = cli.parse()

    url = (f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}"
           f"/semanticModels/{args.semanticmodel_id}")
    try:
        model = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Semantic model"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_model(model, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
