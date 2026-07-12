#!/usr/bin/env python3
"""
Skill: schedule-toggle
Description: Enable or disable a pipeline schedule

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


def toggle_schedule(workspace_id, pipeline_id, schedule_id, enabled):
    """Enable or disable a pipeline schedule."""
    # First, get current schedule configuration
    get_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/getSchedule"

    current_config = None
    try:
        response = fabric_request(get_url, method='POST')

        if response.status == 200:
            schedule_data = json.loads(response.read().decode('utf-8'))
            current_config = schedule_data.get('configuration')
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return handle_http_error(e, "Pipeline or schedule")
    except Exception as e:
        print(f"[WARNING] Could not get current schedule: {e}")

    if not current_config and enabled:
        print("[ERROR] Cannot enable schedule - no configuration found.")
        print("Use fabric-plugin:schedule-create to create a schedule first.")
        return 1

    # Update schedule enabled status
    update_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/updateSchedule"

    body = {
        "enabled": enabled
    }
    if current_config:
        body["configuration"] = current_config

    try:
        response = fabric_request(update_url, method='POST', data=body)

        if response.status in [200, 202]:
            status_text = "ENABLED" if enabled else "DISABLED"
            print(f"\n[SUCCESS] Schedule {status_text}!")
            print("="*60)
            print(f"Pipeline ID:  {pipeline_id}")
            print(f"Schedule ID:  {schedule_id}")
            print(f"Status:       {status_text}")
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
    cli = SkillCLI('schedule_toggle.py', 'Enable or disable a pipeline schedule')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('schedule_id', help='The schedule GUID')
    cli.positional('enabled', choices=['true', 'false'],
                   help="Enable (true) or disable (false)")
    args = cli.parse()

    sys.exit(toggle_schedule(args.workspace_id, args.pipeline_id,
                             args.schedule_id, args.enabled == 'true'))


if __name__ == "__main__":
    main()
