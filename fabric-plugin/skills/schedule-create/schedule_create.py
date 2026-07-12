#!/usr/bin/env python3
"""
Skill: schedule-create
Description: Create a new schedule for a data pipeline

Accepts the workspace and pipeline as display names or GUIDs.
The Fabric scheduler API does not accept unix cron expressions: use
--every N (minutes), --daily HH:MM [...], or --weekly Mon,Fri HH:MM [...].
"""

import json
import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error
from schedule_config import build_configuration, describe

EPILOG = """Examples:
  schedule_create.py "My WS" "Daily ETL" --daily 06:00
  schedule_create.py "My WS" "Hourly sync" --every 60
  schedule_create.py "My WS" "Weekly load" --weekly Mon,Fri 08:30
  schedule_create.py "My WS" "Night job" --daily 02:00 22:00 --timezone "Romance Standard Time"
"""


def create_schedule(workspace_id, pipeline_id, config, enabled):
    """Create a new schedule via the Fabric job scheduler API."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/Pipeline/schedules"
    body = {'enabled': enabled, 'configuration': config}

    try:
        response = fabric_request(url, method='POST', data=body)

        if response.status in (200, 201):
            data = json.loads(response.read().decode('utf-8'))
            print("\n[SUCCESS] Schedule created!")
            print("=" * 60)
            print(f"Schedule ID: {data.get('id', 'N/A')}")
            print(f"Pipeline ID: {pipeline_id}")
            print(f"Recurrence:  {describe(config)}")
            print(f"Window:      {config['startDateTime']} -> {config['endDateTime']}"
                  f" ({config['localTimeZoneId']})")
            print(f"Enabled:     {'Yes' if enabled else 'No'}")
            print("=" * 60)
            print(f"\nUse fabric-plugin:schedule-list <workspace> {pipeline_id} to view schedules")
            return 0

        print(f"[ERROR] Unexpected status: {response.status}")
        return 2

    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("[ERROR] Bad request. Check the schedule options.")
            try:
                print(f"Details: {e.read().decode('utf-8')}")
            except Exception:
                pass
            return 1
        return handle_http_error(e, "Pipeline")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('schedule_create.py',
                   'Create a new schedule for a data pipeline',
                   epilog=EPILOG)
    cli.workspace()
    cli.item('pipeline')
    cli.opt('--every', type=int, metavar='MINUTES', help='Run every N minutes (Cron type)')
    cli.opt('--daily', nargs='+', metavar='HH:MM', help='Run daily at the given time(s)')
    cli.opt('--weekly', nargs='+', metavar='ARG',
            help='Weekly: comma-separated weekdays first (Mon,Fri), then time(s) HH:MM')
    cli.opt('--start', help='Start datetime YYYY-MM-DDTHH:MM:SS (default: now)')
    cli.opt('--end', help='End datetime YYYY-MM-DDTHH:MM:SS (default: +5 years)')
    cli.opt('--timezone', default='UTC', help='Time zone id (default: UTC)')
    cli.flag('--disabled', help='Create the schedule disabled')
    args = cli.parse()

    if sum(1 for v in (args.every, args.daily, args.weekly) if v) != 1:
        print("[ERROR] Exactly one of --every / --daily / --weekly is required")
        sys.exit(1)

    weekly_days = weekly_times = None
    if args.weekly:
        weekly_days = args.weekly[0].split(',')
        weekly_times = args.weekly[1:]

    try:
        config = build_configuration(every=args.every, daily=args.daily,
                                     weekly_days=weekly_days, weekly_times=weekly_times,
                                     start=args.start, end=args.end, tz=args.timezone)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    sys.exit(create_schedule(args.workspace_id, args.pipeline_id, config, not args.disabled))


if __name__ == "__main__":
    main()
