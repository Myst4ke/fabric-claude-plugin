#!/usr/bin/env python3
"""
Skill: ml-experiment-get
Description: Get detailed information about an ML experiment
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_experiment(data, workspace_id):
    """Display ML experiment details."""
    print(f"\nML Experiment Details:")
    print(f"{'='*60}")
    print(f"  Name:        {data.get('displayName', 'N/A')}")
    print(f"  ID:          {data.get('id', 'N/A')}")
    print(f"  Description: {data.get('description', '(none)')}")
    if 'createdDate' in data:
        print(f"  Created:     {data['createdDate']}")
    if 'modifiedDate' in data:
        print(f"  Modified:    {data['modifiedDate']}")
    print(f"{'='*60}")
    print(f"\nModels: fabric-plugin:ml-model-list {workspace_id}")


def main():
    cli = SkillCLI('ml_experiment_get.py',
                   'Get detailed information about an ML experiment')
    cli.workspace()
    cli.item('mlexperiment', help='ML experiment name or GUID')
    args = cli.parse()

    url = (f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}"
           f"/mlExperiments/{args.mlexperiment_id}")
    try:
        data = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "ML experiment"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_experiment(data, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
