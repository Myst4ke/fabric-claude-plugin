#!/usr/bin/env python3
"""
Skill: schedule-delete
Description: Delete a pipeline schedule

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def delete_schedule(workspace_id, pipeline_id, schedule_id):
    """Delete a pipeline schedule."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/Pipeline/schedules/{schedule_id}"

    try:
        response = fabric_request(url, method='DELETE')

        if response.status in [200, 202, 204]:
            print(f"\n[SUCCESS] Schedule deleted successfully!")
            print("="*60)
            print(f"Pipeline ID:  {pipeline_id}")
            print(f"Schedule ID:  {schedule_id}")
            print("="*60)
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Pipeline or schedule")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('schedule_delete.py', 'Delete a pipeline schedule')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('schedule_id', help='The schedule GUID')
    args = cli.parse()

    sys.exit(delete_schedule(args.workspace_id, args.pipeline_id, args.schedule_id))


if __name__ == "__main__":
    main()
