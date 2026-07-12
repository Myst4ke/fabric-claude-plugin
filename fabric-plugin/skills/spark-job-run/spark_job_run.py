#!/usr/bin/env python3
"""
Skill: spark-job-run
Description: Run a Spark job definition

Accepts workspace and job as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request,
                         check_security, handle_http_error)


def run_spark_job(workspace_id, job_id):
    """Trigger a Spark job run."""
    check_security(workspace_id, "spark-job:run")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{job_id}/jobs/instances?jobType=SparkJob"

    try:
        resp = fabric_request(url, method='POST')

        if resp.status in (200, 202):
            location = resp.headers.get('Location', '')
            request_id = resp.headers.get('x-ms-request-id', '')

            print(f"\n[SUCCESS] Spark job started:")
            print(f"  Job ID: {job_id}")
            if request_id:
                print(f"  Request ID: {request_id}")
            if location:
                print(f"  Monitor: {location}")
            print(f"\nCheck status:")
            print(f"  fabric-plugin:spark-job-run-details {workspace_id} {job_id}")
            return 0
        else:
            print(f"[ERROR] Unexpected status: {resp.status}")
            return 2
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[INFO] Job is already running.")
            return 1
        return handle_http_error(e, "Spark job")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('spark_job_run.py', 'Run a Spark job definition')
    cli.workspace()
    cli.item('job', 'sparkjobdefinition', help='Spark job name or GUID')
    args = cli.parse()

    sys.exit(run_spark_job(args.workspace_id, args.job_id))


if __name__ == "__main__":
    main()
