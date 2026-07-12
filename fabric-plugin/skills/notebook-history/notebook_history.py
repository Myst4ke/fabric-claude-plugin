#!/usr/bin/env python3
"""
Skill: notebook-history
Description: Get notebook execution history

Accepts workspace and notebook as display names or GUIDs.
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


def display_history(runs, notebook_id):
    """Display execution history in formatted table."""
    count = len(runs)
    print(f"\nNotebook {notebook_id}")
    print(f"Found {count} run(s):\n")

    if count == 0:
        print("No execution history")
        return

    print(f"{'Job ID':<38} {'Status':<12} {'Start Time':<20} {'End Time':<20}")
    print(f"{'-'*38} {'-'*12} {'-'*20} {'-'*20}")

    for run in runs:
        job_id = run.get('id', 'N/A')
        status = run.get('status', 'N/A')
        start_time = format_datetime(run.get('startTimeUtc'))
        end_time = format_datetime(run.get('endTimeUtc'))
        print(f"{job_id:<38} {status:<12} {start_time:<20} {end_time:<20}")

    print(f"\nUse fabric-plugin:notebook-run-details <workspace> {notebook_id} <job-id> for details")


def main():
    cli = SkillCLI('notebook_history.py',
                   'Get notebook execution history')
    cli.workspace()
    cli.item('notebook')
    cli.opt('--limit', type=int, help='Maximum number of runs to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/items/{args.notebook_id}/jobs/instances"
    try:
        runs = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Notebook"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_history(runs, args.notebook_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
