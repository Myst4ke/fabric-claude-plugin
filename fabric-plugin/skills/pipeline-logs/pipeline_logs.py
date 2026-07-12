#!/usr/bin/env python3
"""
Skill: pipeline-logs
Description: Get execution logs for a pipeline run

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


def display_logs(run_details, pipeline_id, job_id):
    """Display pipeline execution logs."""
    print("\n" + "="*60)
    print("PIPELINE EXECUTION LOGS")
    print("="*60)
    print(f"Pipeline ID: {pipeline_id}")
    print(f"Job ID:      {job_id}")
    print(f"Status:      {run_details.get('status', 'N/A')}")
    print("="*60)

    # Check for failure reason
    failure_reason = run_details.get('failureReason')
    if failure_reason:
        print(f"\n[FAILURE REASON]")
        print(failure_reason)

    # Check for error details
    error_info = run_details.get('error')
    if error_info:
        print(f"\n[ERROR DETAILS]")
        if isinstance(error_info, dict):
            print(f"Code: {error_info.get('code', 'N/A')}")
            print(f"Message: {error_info.get('message', 'N/A')}")
        else:
            print(error_info)

    # Additional activity information if available
    activities = run_details.get('activityRuns', [])
    if activities:
        print(f"\n[ACTIVITY RUNS] ({len(activities)} activities)")
        print("-"*60)
        for i, activity in enumerate(activities, 1):
            print(f"\nActivity {i}:")
            print(f"  Name:   {activity.get('activityName', 'N/A')}")
            print(f"  Type:   {activity.get('activityType', 'N/A')}")
            print(f"  Status: {activity.get('status', 'N/A')}")
            if activity.get('error'):
                print(f"  Error:  {activity.get('error')}")

    # If no detailed logs, show what we have
    if not failure_reason and not error_info and not activities:
        print("\n[INFO] No detailed logs available for this run.")
        print("Status indicates run state. Check run details for more information.")

    print("\n" + "="*60)

    # Raw JSON for complete data
    print("\nRaw JSON:")
    print(json.dumps(run_details, indent=2))


def main():
    cli = SkillCLI('pipeline_logs.py', 'Get execution logs for a pipeline run')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('job_id', help='The job instance ID')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/items/{args.pipeline_id}/jobs/instances/{args.job_id}"
    try:
        run_details = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Pipeline or job"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_logs(run_details, args.pipeline_id, args.job_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
