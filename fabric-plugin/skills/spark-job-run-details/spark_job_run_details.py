#!/usr/bin/env python3
"""
Skill: spark-job-run-details
Description: Get run details and status of a Spark job execution

Accepts workspace and job as display names or GUIDs.
"""

import sys
import os
import urllib.error
from datetime import datetime

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_runs(instances, workspace_id, job_id):
    """Display Spark job run history."""
    print(f"\nSpark Job Run History for {job_id}")
    print(f"{'='*80}")

    if not instances:
        print("No runs found.")
        print(f"\nRun: fabric-plugin:spark-job-run {workspace_id} {job_id}")
        return

    print(f"\n{'Status':<15} {'Start Time':<22} {'End Time':<22} {'Duration':<12}")
    print(f"{'-'*15} {'-'*22} {'-'*22} {'-'*12}")

    for inst in instances[:20]:
        status = inst.get('status', 'N/A')[:15]
        start = inst.get('startTimeUtc', inst.get('startTime', 'N/A'))[:22]
        end = inst.get('endTimeUtc', inst.get('endTime', 'N/A'))[:22]

        duration = ''
        try:
            if start != 'N/A' and end != 'N/A':
                s = datetime.fromisoformat(start[:19])
                e = datetime.fromisoformat(end[:19])
                secs = int((e - s).total_seconds())
                if secs < 60: duration = f"{secs}s"
                elif secs < 3600: duration = f"{secs//60}m {secs%60}s"
                else: duration = f"{secs//3600}h {(secs%3600)//60}m"
        except Exception:
            pass

        print(f"{status:<15} {start:<22} {end:<22} {duration:<12}")

        # Show error for failed runs
        if 'failed' in status.lower() and inst.get('failureReason'):
            print(f"  Error: {inst['failureReason'][:100]}")

    print(f"\n{'='*80}")


def main():
    cli = SkillCLI('spark_job_run_details.py',
                   'Get run details and status of a Spark job execution')
    cli.workspace()
    cli.item('job', 'sparkjobdefinition', help='Spark job name or GUID')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/items/{args.job_id}/jobs/instances"
    try:
        data = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Spark job"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_runs(data.get('value', []), args.workspace_id, args.job_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
