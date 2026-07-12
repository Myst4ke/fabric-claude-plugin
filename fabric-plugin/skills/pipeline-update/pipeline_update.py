#!/usr/bin/env python3
"""
Skill: pipeline-update
Description: Update a data pipeline's name or description

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_updated_pipeline(pipeline):
    """Display updated pipeline details."""
    print("\n[SUCCESS] Pipeline updated successfully!")
    print("="*60)
    print(f"Name:        {pipeline.get('displayName', 'N/A')}")
    print(f"ID:          {pipeline.get('id', 'N/A')}")
    print(f"Description: {pipeline.get('description', 'N/A')}")
    print(f"Workspace:   {pipeline.get('workspaceId', 'N/A')}")
    print("="*60)


def main():
    cli = SkillCLI('pipeline_update.py',
                   "Update a data pipeline's name or description")
    cli.workspace()
    cli.item('pipeline')
    cli.opt('--name', help='New name for the pipeline')
    cli.opt('--description', help='New description for the pipeline')
    args = cli.parse()

    if not args.name and args.description is None:
        print("[ERROR] Must provide --name or --description to update")
        sys.exit(1)

    body = {}
    if args.name:
        body["displayName"] = args.name
    if args.description is not None:
        body["description"] = args.description

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/dataPipelines/{args.pipeline_id}"
    try:
        pipeline = fabric_request_json(url, method='PATCH', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] Conflict. A pipeline with this name may already exist.")
            sys.exit(1)
        sys.exit(handle_http_error(e, "Pipeline"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_updated_pipeline(pipeline)
    sys.exit(0)


if __name__ == "__main__":
    main()
