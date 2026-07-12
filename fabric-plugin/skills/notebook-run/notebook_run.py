#!/usr/bin/env python3
"""
Skill: notebook-run
Description: Execute a notebook in Microsoft Fabric

Starts the job and returns the job ID immediately (no status polling).
Accepts workspace and notebook as display names or GUIDs.
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
    try:
        parts = location.rstrip('/').split('/')
        return parts[-1] if parts else None
    except Exception:
        return None


def run_notebook(workspace_id, notebook_id):
    """Execute a notebook (fire-and-forget: returns the job ID)."""
    url = (f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{notebook_id}"
           f"/jobs/instances?jobType=RunNotebook")

    try:
        response = fabric_request(url, method='POST', data={})

        # 202 Accepted (async execution started)
        if response.status == 202:
            location = response.headers.get('Location')
            job_id = extract_job_id(location)

            print(f"\n[SUCCESS] Notebook execution started!")
            print("="*60)
            print(f"Workspace ID: {workspace_id}")
            print(f"Notebook ID:  {notebook_id}")
            print(f"Job ID:       {job_id if job_id else 'Check Location header'}")
            if location:
                print(f"Location:     {location}")
            print("="*60)
            print(f"\nCheck status: fabric-plugin:notebook-run-details {workspace_id} {notebook_id} {job_id}")
            return 0

        # Immediate response (200)
        elif response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            print(f"\n[SUCCESS] Notebook execution response:")
            print(json.dumps(data, indent=2))
            return 0

        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Notebook")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('notebook_run.py',
                   'Execute a notebook in Microsoft Fabric')
    cli.workspace()
    cli.item('notebook')
    args = cli.parse()

    sys.exit(run_notebook(args.workspace_id, args.notebook_id))


if __name__ == "__main__":
    main()
