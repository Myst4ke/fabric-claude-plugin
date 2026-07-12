#!/usr/bin/env python3
"""
Skill: notebook-run-details
Description: Get detailed information about a notebook run

Accepts workspace and notebook as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error
from datetime import datetime

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def format_datetime(dt_string):
    """Format datetime string for display."""
    if not dt_string:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except Exception:
        return dt_string


def calculate_duration(start, end):
    """Calculate duration between start and end times."""
    if not start or not end:
        return 'N/A'
    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        duration = end_dt - start_dt
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    except Exception:
        return 'N/A'


def display_run_details(run, notebook_id):
    """Display notebook run details."""
    print("\n" + "="*60)
    print("NOTEBOOK RUN DETAILS")
    print("="*60)
    print(f"Notebook ID: {notebook_id}")
    print(f"Job ID:      {run.get('id', 'N/A')}")
    print(f"Status:      {run.get('status', 'N/A')}")
    print(f"Job Type:    {run.get('jobType', 'N/A')}")
    print("-"*60)

    start_time = run.get('startTimeUtc')
    end_time = run.get('endTimeUtc')

    print(f"Start Time:  {format_datetime(start_time)}")
    print(f"End Time:    {format_datetime(end_time)}")
    print(f"Duration:    {calculate_duration(start_time, end_time)}")

    # Error info if present
    failure_reason = run.get('failureReason')
    if failure_reason:
        print("-"*60)
        print(f"Failure:     {failure_reason}")

    print("="*60)

    # Print raw JSON for complete details
    print("\nRaw JSON:")
    print(json.dumps(run, indent=2))


def main():
    cli = SkillCLI('notebook_run_details.py',
                   'Get detailed information about a notebook run')
    cli.workspace()
    cli.item('notebook')
    cli.positional('job_id', help='The job instance ID')
    args = cli.parse()

    url = (f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/items/{args.notebook_id}"
           f"/jobs/instances/{args.job_id}")
    try:
        run = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Notebook or job"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_run_details(run, args.notebook_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
