#!/usr/bin/env python3
"""
Skill: schedule-update
Description: Update a pipeline schedule (recurrence, window, timezone, enabled)

Accepts the workspace and pipeline as display names or GUIDs.
The Fabric scheduler API does not accept unix cron expressions: use
--every N (minutes), --daily HH:MM [...], or --weekly Mon,Fri HH:MM [...].
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         handle_http_error)
from schedule_config import build_configuration, describe


def update_schedule(workspace_id, pipeline_id, schedule_id, args):
    base = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/Pipeline/schedules"

    try:
        current = fabric_request_json(f"{base}/{schedule_id}")
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Schedule")

    config = current.get('configuration', {})

    if args.every or args.daily or args.weekly:
        weekly_days = weekly_times = None
        if args.weekly:
            weekly_days = args.weekly[0].split(',')
            weekly_times = args.weekly[1:]
        try:
            config = build_configuration(
                every=args.every, daily=args.daily,
                weekly_days=weekly_days, weekly_times=weekly_times,
                start=args.start or config.get('startDateTime'),
                end=args.end or config.get('endDateTime'),
                tz=args.timezone or config.get('localTimeZoneId', 'UTC'))
        except ValueError as e:
            print(f"[ERROR] {e}")
            return 1
    else:
        # Keep the recurrence, patch only the provided window/timezone fields
        if args.start:
            config['startDateTime'] = args.start
        if args.end:
            config['endDateTime'] = args.end
        if args.timezone:
            config['localTimeZoneId'] = args.timezone

    enabled = current.get('enabled', True)
    if args.enable:
        enabled = True
    elif args.disable:
        enabled = False

    body = {'enabled': enabled, 'configuration': config}

    try:
        response = fabric_request(f"{base}/{schedule_id}", method='PATCH', data=body)

        if response.status in (200, 201):
            print("\n[SUCCESS] Schedule updated!")
            print("=" * 60)
            print(f"Schedule ID: {schedule_id}")
            print(f"Recurrence:  {describe(config)}")
            print(f"Window:      {config.get('startDateTime')} -> {config.get('endDateTime')}"
                  f" ({config.get('localTimeZoneId')})")
            print(f"Enabled:     {'Yes' if enabled else 'No'}")
            print("=" * 60)
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
        return handle_http_error(e, "Schedule")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('schedule_update.py',
                   'Update a pipeline schedule (recurrence, window, timezone, enabled)')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('schedule_id', help='Schedule ID (see fabric-plugin:schedule-list)')
    cli.opt('--every', type=int, metavar='MINUTES', help='Run every N minutes (Cron type)')
    cli.opt('--daily', nargs='+', metavar='HH:MM', help='Run daily at the given time(s)')
    cli.opt('--weekly', nargs='+', metavar='ARG',
            help='Weekly: comma-separated weekdays first (Mon,Fri), then time(s) HH:MM')
    cli.opt('--start', help='Start datetime YYYY-MM-DDTHH:MM:SS')
    cli.opt('--end', help='End datetime YYYY-MM-DDTHH:MM:SS')
    cli.opt('--timezone', help='Time zone id (e.g. UTC)')
    cli.flag('--enable', help='Enable the schedule')
    cli.flag('--disable', help='Disable the schedule')
    args = cli.parse()

    if args.enable and args.disable:
        print("[ERROR] Use either --enable or --disable, not both")
        sys.exit(1)

    sys.exit(update_schedule(args.workspace_id, args.pipeline_id, args.schedule_id, args))


if __name__ == "__main__":
    main()
