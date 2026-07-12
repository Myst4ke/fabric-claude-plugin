#!/usr/bin/env python3
"""
Skill: spark-job-create
Description: Create a new Spark job definition in a workspace

Accepts the workspace as a display name or a GUID.
"""

import sys
import json
import os
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         check_security, handle_http_error)


def create_spark_job(workspace_id, name, description=None):
    """Create a new Spark job definition."""
    check_security(workspace_id, "spark-job:create")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/sparkJobDefinitions"

    body = {'displayName': name}
    if description:
        body['description'] = description

    try:
        resp = fabric_request(url, method='POST', data=body)

        if resp.status in (200, 201):
            result = json.loads(resp.read().decode('utf-8'))
            print(f"\n[SUCCESS] Spark job definition created:")
            print(f"  Name: {result.get('displayName', name)}")
            print(f"  ID:   {result.get('id', 'N/A')}")
            return 0
        elif resp.status == 202:
            location = resp.headers.get('Location', '')
            print("[INFO] Creating Spark job definition...")
            if location:
                for i in range(20):
                    time.sleep(5)
                    try:
                        d = fabric_request_json(location)
                        if d.get('status', '').lower() == 'succeeded':
                            print(f"\n[SUCCESS] Spark job definition created.")
                            return 0
                        elif d.get('status', '').lower() in ('failed', 'cancelled'):
                            print(f"[ERROR] Creation failed.")
                            return 1
                    except Exception:
                        pass
            return 0
        else:
            print(f"[ERROR] Unexpected status: {resp.status}")
            return 2
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] A Spark job with this name already exists.")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('spark_job_create.py',
                   'Create a new Spark job definition in a workspace')
    cli.workspace()
    cli.positional('name', help='Spark job display name')
    cli.positional('description', nargs='?', default=None,
                   help='Optional description')
    args = cli.parse()

    sys.exit(create_spark_job(args.workspace_id, args.name, args.description))


if __name__ == "__main__":
    main()
