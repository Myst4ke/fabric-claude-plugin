#!/usr/bin/env python3
"""
Skill: environment-publish
Description: Publish pending staging changes to an environment
"""

import sys
import os
import json
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         handle_http_error, check_security)


def publish_environment(workspace_id, env_id):
    """Publish environment staging changes."""
    check_security(workspace_id, "environment:publish")

    url = (f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
           f"/environments/{env_id}/staging/publish")

    try:
        response = fabric_request(url, method='POST')
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("[ERROR] Bad request. Check staging area first:")
            print(f"  fabric-plugin:environment-staging {workspace_id} {env_id}")
            try:
                body = e.read().decode('utf-8')
                msg = json.loads(body).get('error', {}).get('message', '')
                if msg:
                    print(f"Details: {msg}")
            except Exception:
                pass
            return 1
        elif e.code == 409:
            print("[ERROR] A publish is already in progress. Wait for it to complete.")
            return 1
        return handle_http_error(e, "Environment")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 204):
        print(f"\n[SUCCESS] Environment published successfully.")
        return 0
    elif response.status == 202:
        location = response.headers.get('Location', '')
        retry_after = int(response.headers.get('Retry-After', '15'))
        print("[INFO] Publishing environment (installing libraries)...")
        print("       This may take several minutes.")
        return poll_lro(location, retry_after)
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def poll_lro(location, retry_after):
    """Poll long-running operation."""
    if not location:
        print("[SUCCESS] Publish submitted.")
        return 0

    max_polls = 60  # Publishing can take a while
    for i in range(max_polls):
        time.sleep(min(retry_after, 15))
        try:
            data = fabric_request_json(location)
            status = data.get('status', '').lower()
            if status == 'succeeded':
                print(f"\n[SUCCESS] Environment published. Libraries installed.")
                return 0
            elif status == 'failed':
                error = data.get('error', {})
                print(f"\n[ERROR] Publish failed: {error.get('message', 'Unknown error')}")
                if error.get('details'):
                    for d in error['details'][:5]:
                        print(f"  - {d.get('message', d)}")
                return 1
            elif status == 'cancelled':
                print("[ERROR] Publish cancelled.")
                return 1
            else:
                if i % 4 == 0:
                    elapsed = (i + 1) * min(retry_after, 15)
                    print(f"  Publishing... ({elapsed}s elapsed)")
        except Exception:
            pass

    print("[WARN] Still publishing. Check environment status later.")
    return 0


def main():
    cli = SkillCLI('environment_publish.py',
                   'Publish pending staging changes to an environment')
    cli.workspace()
    cli.item('environment', help='Environment name or GUID')
    args = cli.parse()

    sys.exit(publish_environment(args.workspace_id, args.environment_id))


if __name__ == "__main__":
    main()
