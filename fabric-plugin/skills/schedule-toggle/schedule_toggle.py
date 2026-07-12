#!/usr/bin/env python3
"""
Skill: schedule-toggle
Description: Enable or disable a pipeline schedule

Accepts the workspace and pipeline as display names or GUIDs. The schedule id
is optional when the pipeline has exactly one schedule.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         fabric_list, handle_http_error)
from schedule_config import describe


def find_single_schedule(base_url):
    schedules = fabric_list(base_url)
    if not schedules:
        print("[ERROR] No schedules on this pipeline. Use fabric-plugin:schedule-create first.")
        sys.exit(1)
    if len(schedules) > 1:
        print("[ERROR] Multiple schedules found - pass the schedule id explicitly:")
        for s in schedules:
            print(f"  {s.get('id')}  enabled={s.get('enabled')}  {describe(s.get('configuration', {}))}")
        sys.exit(1)
    return schedules[0]


def toggle(workspace_id, pipeline_id, schedule_id, force_state):
    base = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/Pipeline/schedules"

    try:
        if schedule_id:
            sched = fabric_request_json(f"{base}/{schedule_id}")
        else:
            sched = find_single_schedule(base)
            schedule_id = sched['id']

        new_state = (not sched.get('enabled')) if force_state is None else force_state
        body = {'enabled': new_state, 'configuration': sched.get('configuration')}
        response = fabric_request(f"{base}/{schedule_id}", method='PATCH', data=body)

        if response.status in (200, 201):
            print(f"\n[SUCCESS] Schedule {'enabled' if new_state else 'disabled'}.")
            print(f"Schedule ID: {schedule_id}")
            print(f"Recurrence:  {describe(sched.get('configuration', {}))}")
            return 0

        print(f"[ERROR] Unexpected status: {response.status}")
        return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Schedule")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('schedule_toggle.py', 'Enable or disable a pipeline schedule')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('schedule_id', nargs='?', default=None,
                   help='Schedule ID (optional if the pipeline has exactly one schedule)')
    cli.flag('--enable', help='Force enabled state')
    cli.flag('--disable', help='Force disabled state')
    args = cli.parse()

    if args.enable and args.disable:
        print("[ERROR] Use either --enable or --disable, not both")
        sys.exit(1)
    force = True if args.enable else (False if args.disable else None)

    sys.exit(toggle(args.workspace_id, args.pipeline_id, args.schedule_id, force))


if __name__ == "__main__":
    main()
