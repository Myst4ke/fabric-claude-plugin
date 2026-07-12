#!/usr/bin/env python3
"""
Skill: spark-job-get
Description: Get detailed information about a Spark job definition

Accepts workspace and job as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_job(data, workspace_id, job_id):
    """Display Spark job definition details."""
    print(f"\nSpark Job Definition:")
    print(f"{'='*60}")
    print(f"  Name:        {data.get('displayName', 'N/A')}")
    print(f"  ID:          {data.get('id', 'N/A')}")
    print(f"  Description: {data.get('description', '(none)')}")
    if 'createdDate' in data:
        print(f"  Created:     {data['createdDate']}")
    if 'modifiedDate' in data:
        print(f"  Modified:    {data['modifiedDate']}")
    props = data.get('properties', {})
    if props:
        if props.get('oneLakeRootPath'):
            print(f"  Root Path:   {props['oneLakeRootPath']}")
    print(f"{'='*60}")
    print(f"\nRun: fabric-plugin:spark-job-run {workspace_id} {data.get('id', job_id)}")


def main():
    cli = SkillCLI('spark_job_get.py',
                   'Get detailed information about a Spark job definition')
    cli.workspace()
    cli.item('job', 'sparkjobdefinition', help='Spark job name or GUID')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/sparkJobDefinitions/{args.job_id}"
    try:
        data = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Spark job"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_job(data, args.workspace_id, args.job_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
