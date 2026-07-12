#!/usr/bin/env python3
"""
Skill: pipeline-diagnose
Description: Diagnose a failed Fabric pipeline run down to the real per-activity
error (notebook / Spark / Livy), which the standard run-details and logs
endpoints do NOT expose.

It calls the Data Factory activity-runs endpoint:
    POST /workspaces/{ws}/datapipelines/pipelineruns/{runId}/queryactivityruns
which returns one object per activity (including ForEach iterations) with the
embedded notebook/Spark error, the Spark session id and the Spark monitor URL.

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error
from datetime import datetime, timedelta, timezone

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error

PORTAL_BASE = "https://app.fabric.microsoft.com/"


# =============================================================================
# Helpers
# =============================================================================

def parse_iso(ts):
    """Parse an ISO-8601 timestamp (optional fractional secs / 'Z') to an aware
    datetime, or None if it can't be parsed."""
    if not ts:
        return None
    s = str(ts).strip().replace('Z', '+00:00')
    # Trim fractional seconds to 6 digits (datetime.fromisoformat limit)
    if '.' in s:
        head, rest = s.split('.', 1)
        tz = ''
        for marker in ('+', '-'):
            idx = rest.find(marker)
            if idx != -1:
                tz = rest[idx:]
                rest = rest[:idx]
                break
        s = f"{head}.{rest[:6]}{tz}"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def fmt_duration(ms):
    """Format a millisecond duration as '42m 53s' / '1h 03m 12s'."""
    if ms is None:
        return "N/A"
    try:
        total = int(ms) // 1000
    except (TypeError, ValueError):
        return "N/A"
    h, rem = divmod(total, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m {sec:02d}s"
    if m:
        return f"{m}m {sec:02d}s"
    return f"{sec}s"


def flatten_params(parameters):
    """Turn {'k': {'value': 'v', 'type': 't'}} into 'k=v' pairs."""
    if not isinstance(parameters, dict):
        return ""
    pairs = []
    for k, v in parameters.items():
        val = v.get('value') if isinstance(v, dict) else v
        pairs.append(f"{k}={val}")
    return ", ".join(pairs)


def short_label(activity):
    """A concise label for a notebook iteration: the target table if present,
    else the activity name."""
    params = (activity.get('input') or {}).get('parameters') or {}
    for key in ('bronze_table_name', 'silver_table_name', 'table_name'):
        v = params.get(key)
        val = v.get('value') if isinstance(v, dict) else v
        if val:
            return str(val)
    return activity.get('activityName', 'unknown')


def get_run_window(workspace_id, pipeline_id, job_id):
    """Fetch the run instance to derive a query window and a run summary.

    Returns (run_details_or_None, after_dt, before_dt). The window brackets the
    run with a 1-day margin on each side, capped to 30 days (the activity-runs
    endpoint's max). Falls back to [now-30d, now+1d] if timings are missing."""
    now = datetime.now(timezone.utc)
    run = None
    url = (f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
           f"/items/{pipeline_id}/jobs/instances/{job_id}")
    try:
        run = fabric_request_json(url)
    except Exception:
        run = None

    start = end = None
    if run:
        start = parse_iso(run.get('startTimeUtc') or run.get('startTime'))
        end = parse_iso(run.get('endTimeUtc') or run.get('endTime'))

    after = (start - timedelta(days=1)) if start else (now - timedelta(days=30))
    before = (end + timedelta(days=1)) if end else (now + timedelta(days=1))
    if (before - after) > timedelta(days=30):
        after = before - timedelta(days=30)
    return run, after, before


def query_activity_runs(workspace_id, run_id, after, before):
    """POST queryactivityruns, following continuationToken pagination."""
    url = (f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
           f"/datapipelines/pipelineruns/{run_id}/queryactivityruns")
    body = {
        "lastUpdatedAfter": after.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "lastUpdatedBefore": before.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "filters": [],
        "orderBy": [],
    }
    activities = []
    while True:
        resp = fabric_request_json(url, method='POST', data=body)
        activities.extend(resp.get('value', []))
        token = resp.get('continuationToken')
        if not token:
            break
        body['continuationToken'] = token
    return activities


# =============================================================================
# Diagnosis
# =============================================================================

def diagnose_notebook(activity):
    """Extract the real Spark/notebook error from a TridentNotebook activity."""
    output = activity.get('output') or {}
    result = output.get('result') or {}
    err = result.get('error') or {}
    spark_rel = output.get('SparkMonitoringURL')
    return {
        'ename': err.get('ename'),
        'evalue': err.get('evalue'),
        'traceback': err.get('traceback') or [],
        'session_id': result.get('sessionId'),
        'notebook_run_id': result.get('runId') or activity.get('activityRunId'),
        'spark_monitor_url': (PORTAL_BASE + spark_rel) if spark_rel else None,
        'params': flatten_params((activity.get('input') or {}).get('parameters')),
        'exit_value': result.get('exitValue'),
    }


def display(run, activities, pipeline_id, job_id):
    print("\n" + "=" * 64)
    print("PIPELINE RUN DIAGNOSIS")
    print("=" * 64)
    print(f"Pipeline ID:  {pipeline_id}")
    print(f"Run ID:       {job_id}")
    if run:
        print(f"Status:       {run.get('status', 'N/A')}")
        print(f"Invoke type:  {run.get('invokeType', 'N/A')}")
        start = run.get('startTimeUtc') or run.get('startTime') or 'N/A'
        end = run.get('endTimeUtc') or run.get('endTime') or 'N/A'
        print(f"Start (UTC):  {start}")
        print(f"End (UTC):    {end}")
        if run.get('failureReason'):
            fr = run['failureReason']
            msg = fr.get('message') if isinstance(fr, dict) else fr
            print(f"Run failure:  {msg}")
    print("=" * 64)

    if not activities:
        print("\n[INFO] No activity runs returned for this run.")
        print("The run may be too old (activity history is time-windowed) or")
        print("still initializing. Nothing to diagnose.")
        print("=" * 64)
        return

    # Activity overview
    print(f"\n[ACTIVITIES] ({len(activities)})")
    print("-" * 64)
    for a in activities:
        name = a.get('activityName', 'N/A')
        atype = a.get('activityType', 'N/A')
        status = a.get('status', 'N/A')
        dur = fmt_duration(a.get('durationInMs'))
        marker = "FAIL" if status == 'Failed' else "ok  "
        print(f"  [{marker}] {status:<10} {atype:<18} {name}  ({dur})")

    failed = [a for a in activities if a.get('status') == 'Failed']
    if not failed:
        print("\n[RESULT] No failed activities. Run did not fail at the activity level.")
        print("=" * 64)
        return

    failed_notebooks = [a for a in failed
                        if a.get('activityType') == 'TridentNotebook']

    print("\n" + "=" * 64)
    print("ROOT CAUSE")
    print("=" * 64)

    if failed_notebooks:
        print("The pipeline failed because of a notebook execution error.")
        print("(Note: a 'Fail' / ForEach activity may carry a misleading name -")
        print(" the real cause is the failed notebook activity below.)\n")
        for a in failed_notebooks:
            d = diagnose_notebook(a)
            print(f"  Notebook activity : {a.get('activityName')}")
            if d['params']:
                print(f"  Iteration params  : {d['params']}")
            print(f"  Error name        : {d['ename'] or 'N/A'}")
            print(f"  Error value       : {d['evalue'] or 'N/A'}")
            if d['traceback']:
                print("  Traceback         :")
                for line in d['traceback']:
                    print(f"      {line}")
            print(f"  Notebook run id   : {d['notebook_run_id'] or 'N/A'}")
            print(f"  Spark session id  : {d['session_id'] or 'N/A'}")
            if d['spark_monitor_url']:
                print(f"  Spark monitor     : {d['spark_monitor_url']}")
            print()
    else:
        print("No failed notebook activity. Failed activities and their errors:\n")
        for a in failed:
            err = a.get('error') or {}
            msg = err.get('message') if isinstance(err, dict) else err
            code = err.get('errorCode') if isinstance(err, dict) else None
            print(f"  Activity : {a.get('activityName')} ({a.get('activityType')})")
            if code:
                print(f"  Code     : {code}")
            print(f"  Error    : {msg}")
            print()

    # Misleading-label hint
    fail_acts = [a for a in failed if a.get('activityType') == 'Fail']
    if failed_notebooks and fail_acts:
        label = short_label(failed_notebooks[0])
        print(f"[HINT] The pipeline 'failureReason' points at the Fail activity "
              f"'{fail_acts[0].get('activityName')}', but the actual failing "
              f"iteration is the notebook above (table: {label}).")

    print("=" * 64)


def main():
    cli = SkillCLI('pipeline_diagnose.py',
                   'Diagnose a failed pipeline run down to the notebook/Spark error')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('job_id', help='The pipeline run / job instance ID')
    cli.flag('--raw', help='Also print the raw activity-runs JSON')
    args = cli.parse()

    try:
        run, after, before = get_run_window(
            args.workspace_id, args.pipeline_id, args.job_id)
        activities = query_activity_runs(
            args.workspace_id, args.job_id, after, before)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Pipeline run"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display(run, activities, args.pipeline_id, args.job_id)

    if args.raw:
        print("\nRaw activity-runs JSON:")
        print(json.dumps(activities, indent=2))

    sys.exit(0)


if __name__ == "__main__":
    main()
