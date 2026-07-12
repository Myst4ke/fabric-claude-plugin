#!/usr/bin/env python3
"""
Skill: schedule-create
Description: Create a new schedule for a data pipeline

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import os
import urllib.error
from datetime import datetime, timezone

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error

CRON_EPILOG = """Cron Format: minute hour day-of-month month day-of-week

Examples:
  "0 0 * * *"     - Daily at midnight
  "0 */6 * * *"   - Every 6 hours
  "0 9 * * 1-5"   - Weekdays at 9 AM
  "30 8 1 * *"    - Monthly on 1st at 8:30 AM"""


def create_schedule(workspace_id, pipeline_id, cron_expression):
    """Create a new schedule for a pipeline."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/updateSchedule"

    # Build schedule configuration
    body = {
        "enabled": True,
        "configuration": {
            "type": "Cron",
            "expression": cron_expression,
            "timeZone": "UTC",
            "startDateTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }

    try:
        response = fabric_request(url, method='POST', data=body)

        if response.status in [200, 201, 202]:
            print(f"\n[SUCCESS] Schedule created successfully!")
            print("="*60)
            print(f"Pipeline ID: {pipeline_id}")
            print(f"Cron:        {cron_expression}")
            print(f"Enabled:     Yes")
            print(f"Timezone:    UTC")
            print("="*60)
            print(f"\nUse fabric-plugin:schedule-list <workspace> {pipeline_id} to view schedules")
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        if e.code == 400:
            try:
                error_body = e.read().decode('utf-8')
                print(f"[ERROR] Bad request. Check cron expression format.")
                print(f"Details: {error_body}")
            except Exception:
                print("[ERROR] Bad request. Check cron expression format.")
            return 1
        return handle_http_error(e, "Pipeline")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('schedule_create.py',
                   'Create a new schedule for a data pipeline',
                   epilog=CRON_EPILOG)
    cli.workspace()
    cli.item('pipeline')
    cli.positional('cron_expression', help='Cron expression (quote if contains spaces)')
    args = cli.parse()

    sys.exit(create_schedule(args.workspace_id, args.pipeline_id, args.cron_expression))


if __name__ == "__main__":
    main()
