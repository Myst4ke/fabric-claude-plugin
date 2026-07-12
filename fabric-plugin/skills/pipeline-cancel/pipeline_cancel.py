#!/usr/bin/env python3
"""
Skill: pipeline-cancel
Description: Cancel a running pipeline job

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def cancel_pipeline(workspace_id, pipeline_id, job_id):
    """Cancel a running pipeline job."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/instances/{job_id}/cancel"

    try:
        response = fabric_request(url, method='POST', data={})

        if response.status in [200, 202]:
            print(f"\n[SUCCESS] Pipeline job cancellation requested!")
            print("="*60)
            print(f"Pipeline ID: {pipeline_id}")
            print(f"Job ID:      {job_id}")
            print("="*60)
            print("\nNote: Cancellation may take a moment to complete.")
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("[ERROR] Bad request. Job may already be completed or cancelled.")
            return 1
        return handle_http_error(e, "Pipeline or job")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('pipeline_cancel.py', 'Cancel a running pipeline job')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('job_id', help='The job instance ID to cancel')
    args = cli.parse()

    sys.exit(cancel_pipeline(args.workspace_id, args.pipeline_id, args.job_id))


if __name__ == "__main__":
    main()
