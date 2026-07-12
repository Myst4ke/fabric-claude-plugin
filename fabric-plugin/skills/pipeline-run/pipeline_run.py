#!/usr/bin/env python3
"""
Skill: pipeline-run
Description: Execute a data pipeline in Microsoft Fabric

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def extract_job_id(location):
    """Extract job ID from Location header."""
    if not location:
        return None
    # Location format: .../jobs/instances/{jobId}
    try:
        parts = location.rstrip('/').split('/')
        return parts[-1] if parts else None
    except Exception:
        return None


def run_pipeline(workspace_id, pipeline_id):
    """Execute a data pipeline."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/instances?jobType=Pipeline"

    try:
        response = fabric_request(url, method='POST', data={})

        # Handle 202 Accepted (async execution started)
        if response.status == 202:
            location = response.headers.get('Location')
            job_id = extract_job_id(location)

            print(f"\n[SUCCESS] Pipeline execution started!")
            print("="*60)
            print(f"Pipeline ID: {pipeline_id}")
            print(f"Job ID:      {job_id if job_id else 'Check Location header'}")
            if location:
                print(f"Location:    {location}")
            print("="*60)
            print(f"\nUse fabric-plugin:pipeline-run-details <workspace> {pipeline_id} <job-id> to check status")
            return 0

        # Handle immediate response (200)
        elif response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            print(f"\n[SUCCESS] Pipeline execution response:")
            print(json.dumps(data, indent=2))
            return 0

        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Pipeline")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('pipeline_run.py',
                   'Execute a data pipeline in Microsoft Fabric')
    cli.workspace()
    cli.item('pipeline')
    args = cli.parse()

    sys.exit(run_pipeline(args.workspace_id, args.pipeline_id))


if __name__ == "__main__":
    main()
