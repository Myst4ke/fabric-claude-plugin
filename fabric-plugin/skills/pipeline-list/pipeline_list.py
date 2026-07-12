#!/usr/bin/env python3
"""
Skill: pipeline-list
Description: List all data pipelines in a Microsoft Fabric workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_pipelines(pipelines):
    """Display pipelines in formatted table."""
    count = len(pipelines)
    print(f"\nFound {count} data pipeline(s):\n")

    if count == 0:
        print("No data pipelines in workspace")
        return

    print(f"{'Name':<40} {'ID':<38}")
    print(f"{'-'*40} {'-'*38}")

    for pipeline in pipelines:
        name = pipeline.get('displayName', 'N/A')[:40]
        pipeline_id = pipeline.get('id', 'N/A')
        print(f"{name:<40} {pipeline_id:<38}")

    print(f"\nUse fabric-plugin:pipeline-get <workspace> <pipeline> for details")


def main():
    cli = SkillCLI('pipeline_list.py',
                   'List all data pipelines in a Microsoft Fabric workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of pipelines to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/dataPipelines"
    try:
        pipelines = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_pipelines(pipelines)
    sys.exit(0)


if __name__ == "__main__":
    main()
