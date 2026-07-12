#!/usr/bin/env python3
"""
Skill: pipeline-get
Description: Get detailed information about a data pipeline

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


def display_pipeline(pipeline):
    """Display pipeline details."""
    print("\n" + "="*60)
    print("DATA PIPELINE DETAILS")
    print("="*60)
    print(f"Name:        {pipeline.get('displayName', 'N/A')}")
    print(f"ID:          {pipeline.get('id', 'N/A')}")
    print(f"Description: {pipeline.get('description', 'N/A')}")
    print(f"Workspace:   {pipeline.get('workspaceId', 'N/A')}")
    print("="*60)

    # Print raw JSON for complete details
    print("\nRaw JSON:")
    print(json.dumps(pipeline, indent=2))


def main():
    cli = SkillCLI('pipeline_get.py',
                   'Get detailed information about a data pipeline')
    cli.workspace()
    cli.item('pipeline')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/dataPipelines/{args.pipeline_id}"
    try:
        pipeline = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Pipeline"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_pipeline(pipeline)
    sys.exit(0)


if __name__ == "__main__":
    main()
