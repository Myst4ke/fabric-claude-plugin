#!/usr/bin/env python3
"""
Skill: schedule-list
Description: List all schedules for a data pipeline

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def list_schedules(workspace_id, pipeline_id):
    """List schedules for a pipeline (with pagination)."""
    schedule_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/Pipeline/schedules"

    try:
        schedules = fabric_list(schedule_url)
        display_schedules(schedules, pipeline_id)
        return 0

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Pipeline")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def display_schedules(schedules, pipeline_id):
    """Display schedules in formatted table."""
    count = len(schedules)
    print(f"\nPipeline {pipeline_id}")
    print(f"Found {count} schedule(s):\n")

    if count == 0:
        print("No schedules configured")
        return

    # Header
    print(f"{'Schedule ID':<38} {'Enabled':<8} {'Configuration':<50}")
    print(f"{'-'*38} {'-'*8} {'-'*50}")

    # Rows
    for schedule in schedules:
        schedule_id = schedule.get('id', 'N/A')
        enabled = 'Yes' if schedule.get('enabled', False) else 'No'
        config = schedule.get('configuration', {})
        summary = format_configuration(config)
        print(f"{schedule_id:<38} {enabled:<8} {summary:<50}")


def format_configuration(config):
    """Summarize a schedule configuration (Cron, Daily or Weekly)."""
    sched_type = config.get('type', 'N/A')
    timezone = config.get('localTimeZoneId', '')

    if sched_type == 'Cron':
        detail = f"every {config.get('interval', '?')} min"
    elif sched_type == 'Daily':
        detail = f"at {', '.join(config.get('times', []))}"
    elif sched_type == 'Weekly':
        weekdays = ', '.join(config.get('weekdays', []))
        detail = f"{weekdays} at {', '.join(config.get('times', []))}"
    else:
        detail = json.dumps(config)

    summary = f"{sched_type} {detail}"
    if timezone:
        summary += f" ({timezone})"
    return summary


def main():
    cli = SkillCLI('schedule_list.py', 'List all schedules for a data pipeline')
    cli.workspace()
    cli.item('pipeline')
    args = cli.parse()

    sys.exit(list_schedules(args.workspace_id, args.pipeline_id))


if __name__ == "__main__":
    main()
