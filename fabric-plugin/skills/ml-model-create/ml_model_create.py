#!/usr/bin/env python3
"""
Skill: ml-model-create
Description: Create a new ML model in a workspace
"""

import sys
import os
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, fabric_request_json,
                         handle_http_error, check_security)


def create_ml_model(workspace_id, name, description=None):
    """Create ML model, polling the LRO if creation is asynchronous."""
    check_security(workspace_id, "ml:create")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/mlModels"
    body = {'displayName': name}
    if description:
        body['description'] = description

    try:
        resp = fabric_request(url, method='POST', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[ERROR] An ML model with this name already exists.")
            return 1
        return handle_http_error(e, "ML model")

    if resp.status in (200, 201):
        import json
        result = json.loads(resp.read().decode('utf-8'))
        print(f"\n[SUCCESS] ML model created:")
        print(f"  Name: {result.get('displayName', name)}")
        print(f"  ID:   {result.get('id', 'N/A')}")
        return 0
    elif resp.status == 202:
        print("[INFO] Creating ML model...")
        location = resp.headers.get('Location', '')
        if location:
            for i in range(15):
                time.sleep(5)
                try:
                    d = fabric_request_json(location)
                    if d.get('status', '').lower() == 'succeeded':
                        print(f"[SUCCESS] ML model created.")
                        return 0
                    elif d.get('status', '').lower() in ('failed', 'cancelled'):
                        print(f"[ERROR] Creation failed.")
                        return 1
                except Exception:
                    pass
        return 0
    else:
        print(f"[ERROR] Unexpected status: {resp.status}")
        return 2


def main():
    cli = SkillCLI('ml_model_create.py', 'Create a new ML model in a workspace')
    cli.workspace()
    cli.positional('name', help='Display name for the new ML model')
    cli.positional('description', nargs='?', default=None,
                   help='Optional description')
    args = cli.parse()

    sys.exit(create_ml_model(args.workspace_id, args.name, args.description))


if __name__ == "__main__":
    main()
