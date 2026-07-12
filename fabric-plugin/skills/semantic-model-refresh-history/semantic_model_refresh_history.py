#!/usr/bin/env python3
"""
Skill: semantic-model-refresh-history
Description: Get refresh history of a semantic model (Power BI dataset)
"""

import sys
import os
import json
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_refreshes(refreshes, workspace_id, model_id):
    """Display refresh history."""
    count = len(refreshes)
    print(f"\nRefresh history for model {model_id}:")
    print(f"Showing {count} recent refresh(es):\n")

    if count == 0:
        print("No refresh history available.")
        print(f"\nTrigger a refresh:")
        print(f"  fabric-plugin:semantic-model-refresh {workspace_id} {model_id}")
        return

    print(f"{'Status':<12} {'Type':<10} {'Start Time':<22} {'End Time':<22} {'Duration':<12}")
    print(f"{'-'*12} {'-'*10} {'-'*22} {'-'*22} {'-'*12}")

    for r in refreshes:
        status = r.get('status', 'Unknown')[:12]
        refresh_type = r.get('refreshType', r.get('type', 'N/A'))[:10]
        start = r.get('startTime', 'N/A')[:22]
        end = r.get('endTime', 'N/A')[:22]

        # Calculate duration if both times present
        duration = ''
        if r.get('startTime') and r.get('endTime'):
            try:
                from datetime import datetime
                s = r['startTime'][:19]
                e = r['endTime'][:19]
                dt = datetime.fromisoformat(e) - datetime.fromisoformat(s)
                total_secs = int(dt.total_seconds())
                if total_secs < 60:
                    duration = f"{total_secs}s"
                elif total_secs < 3600:
                    duration = f"{total_secs // 60}m {total_secs % 60}s"
                else:
                    duration = f"{total_secs // 3600}h {(total_secs % 3600) // 60}m"
            except Exception:
                duration = ''
        elif status.lower() in ('unknown', 'inprogress', 'notstarted'):
            duration = '(running)'

        # Status indicator
        sl = status.lower()
        if sl == 'completed':
            status_icon = 'Completed'
        elif sl == 'failed':
            status_icon = 'FAILED'
        elif sl in ('inprogress', 'unknown'):
            status_icon = 'Running...'
        elif sl == 'cancelled':
            status_icon = 'Cancelled'
        elif sl == 'disabled':
            status_icon = 'Disabled'
        else:
            status_icon = status

        print(f"{status_icon:<12} {refresh_type:<10} {start:<22} {end:<22} {duration:<12}")

        # Show error for failed refreshes
        if sl == 'failed' and r.get('serviceExceptionJson'):
            try:
                err = json.loads(r['serviceExceptionJson'])
                msg = err.get('errorCode', '')
                if msg:
                    print(f"  Error: {msg}")
            except (json.JSONDecodeError, TypeError):
                pass

    # Check if any refresh is currently running
    running = [r for r in refreshes
               if r.get('status', '').lower() in ('unknown', 'inprogress')]
    if running:
        print(f"\n[INFO] {len(running)} refresh(es) currently in progress.")


def main():
    cli = SkillCLI('semantic_model_refresh_history.py',
                   'Get refresh history of a semantic model (Power BI dataset)')
    cli.workspace()
    cli.item('semanticmodel', help='Semantic model name or GUID')
    cli.opt('--top', type=int, default=10,
            help='Number of recent refreshes (default: 10)')
    args = cli.parse()

    # The Fabric API has no /semanticModels/{id}/refreshes endpoint; refresh
    # history lives on the Power BI API (same token)
    url = (f"https://api.powerbi.com/v1.0/myorg/groups/{args.workspace_id}"
           f"/datasets/{args.semanticmodel_id}/refreshes?$top={args.top}")
    try:
        data = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Semantic model"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_refreshes(data.get('value', []), args.workspace_id,
                      args.semanticmodel_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
