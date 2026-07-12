#!/usr/bin/env python3
"""
Skill: pipeline-history
Description: Get pipeline execution history

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import os
import urllib.error
from datetime import datetime

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def format_datetime(dt_string):
    """Format datetime string for display."""
    if not dt_string:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return dt_string[:19] if len(dt_string) > 19 else dt_string


def display_history(runs, pipeline_id):
    """Display execution history in formatted table."""
    count = len(runs)
    print(f"\nPipeline {pipeline_id}")
    print(f"Found {count} run(s):\n")

    if count == 0:
        print("No execution history")
        return

    # Header
    print(f"{'Job ID':<38} {'Status':<12} {'Start Time':<20} {'End Time':<20}")
    print(f"{'-'*38} {'-'*12} {'-'*20} {'-'*20}")

    # Rows
    for run in runs:
        job_id = run.get('id', 'N/A')
        status = run.get('status', 'N/A')
        start_time = format_datetime(run.get('startTimeUtc'))
        end_time = format_datetime(run.get('endTimeUtc'))
        print(f"{job_id:<38} {status:<12} {start_time:<20} {end_time:<20}")

    print(f"\nUse fabric-plugin:pipeline-run-details <workspace> {pipeline_id} <job-id> for details")


def main():
    cli = SkillCLI('pipeline_history.py', 'Get pipeline execution history')
    cli.workspace()
    cli.item('pipeline')
    cli.opt('--limit', type=int, help='Maximum number of runs to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/items/{args.pipeline_id}/jobs/instances"
    try:
        runs = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Pipeline"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_history(runs, args.pipeline_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
