#!/usr/bin/env python3
"""
Skill: schedule-update
Description: Update a pipeline schedule's cron expression

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, fabric_request_json, handle_http_error


def update_schedule(workspace_id, pipeline_id, schedule_id, cron_expression):
    """Update a pipeline schedule."""
    # First, get current schedule to preserve other settings
    get_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/getSchedule"

    current_schedule = {}
    try:
        current_schedule = fabric_request_json(get_url, method='POST')
    except Exception:
        # If can't get current schedule, proceed with update anyway
        pass

    # Update schedule
    update_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/updateSchedule"

    # Build updated configuration
    config = current_schedule.get('configuration', {})
    config['expression'] = cron_expression
    if 'type' not in config:
        config['type'] = 'Cron'
    if 'timeZone' not in config:
        config['timeZone'] = 'UTC'

    body = {
        "enabled": current_schedule.get('enabled', True),
        "configuration": config
    }

    try:
        response = fabric_request(update_url, method='POST', data=body)

        if response.status in [200, 202]:
            print(f"\n[SUCCESS] Schedule updated successfully!")
            print("="*60)
            print(f"Pipeline ID:  {pipeline_id}")
            print(f"Schedule ID:  {schedule_id}")
            print(f"New Cron:     {cron_expression}")
            print("="*60)
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("[ERROR] Bad request. Check cron expression format.")
            return 1
        return handle_http_error(e, "Pipeline or schedule")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('schedule_update.py',
                   "Update a pipeline schedule's cron expression")
    cli.workspace()
    cli.item('pipeline')
    cli.positional('schedule_id', help='The schedule GUID')
    cli.positional('cron_expression', help='New cron expression')
    args = cli.parse()

    sys.exit(update_schedule(args.workspace_id, args.pipeline_id,
                             args.schedule_id, args.cron_expression))


if __name__ == "__main__":
    main()
