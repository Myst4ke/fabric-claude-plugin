#!/usr/bin/env python3
"""
Skill: ml-experiment-list
Description: List all ML experiments in a workspace
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_experiments(experiments, workspace_id):
    """Display ML experiments in formatted table."""
    count = len(experiments)
    print(f"\nFound {count} ML experiment(s):\n")
    if count == 0:
        print("No ML experiments in this workspace.")
        return

    print(f"{'Experiment Name':<35} {'ID':<38} {'Description':<30}")
    print(f"{'-'*35} {'-'*38} {'-'*30}")
    for item in experiments:
        name = item.get('displayName', 'N/A')[:35]
        eid = item.get('id', 'N/A')[:38]
        desc = item.get('description', '')[:30]
        print(f"{name:<35} {eid:<38} {desc:<30}")

    print(f"\nDetails: fabric-plugin:ml-experiment-get {workspace_id} <experiment-id>")


def main():
    cli = SkillCLI('ml_experiment_list.py',
                   'List all ML experiments in a workspace')
    cli.workspace()
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/mlExperiments"
    try:
        experiments = fabric_list(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_experiments(experiments, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
