#!/usr/bin/env python3
"""
Skill: spark-job-list
Description: List all Spark job definitions in a workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_jobs(items, workspace_id):
    """Display Spark job definitions in formatted table."""
    count = len(items)
    print(f"\nFound {count} Spark job definition(s):\n")
    if count == 0:
        print("No Spark job definitions in this workspace.")
        return

    print(f"{'Job Name':<35} {'ID':<38} {'Description':<30}")
    print(f"{'-'*35} {'-'*38} {'-'*30}")
    for item in items:
        name = item.get('displayName', 'N/A')[:35]
        jid = item.get('id', 'N/A')[:38]
        desc = item.get('description', '')[:30]
        print(f"{name:<35} {jid:<38} {desc:<30}")

    print(f"\nNext steps:")
    print(f"  - Details: fabric-plugin:spark-job-get {workspace_id} <job-id>")
    print(f"  - Run:     fabric-plugin:spark-job-run {workspace_id} <job-id>")


def main():
    cli = SkillCLI('spark_job_list.py',
                   'List all Spark job definitions in a workspace')
    cli.workspace()
    cli.opt('--limit', type=int, help='Maximum number of jobs to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/sparkJobDefinitions"
    try:
        items = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Workspace"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_jobs(items, args.workspace_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
