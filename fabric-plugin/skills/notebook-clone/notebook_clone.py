#!/usr/bin/env python3
"""
Skill: notebook-clone
Description: Clone an existing notebook (get definition + create + apply definition)

Accepts workspace and source notebook as display names or GUIDs.
The new notebook name is taken as-is (no resolution).
"""

import sys
import json
import os
import urllib.error
import time

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, fabric_lro_result, handle_http_error

LRO_TIMEOUT = 300  # 5 minutes per operation
LRO_POLL_INTERVAL = 3  # seconds


def clone_notebook(workspace_id, source_notebook_id, new_name):
    """Clone a notebook by exporting and re-importing."""
    print(f"\n[INFO] Cloning notebook...")
    print(f"Source:   {source_notebook_id}")
    print(f"New name: {new_name}")
    print("-"*60)

    # Step 1: Get source notebook definition
    print("\n[Step 1/3] Getting source definition...")
    definition_payload = get_definition(workspace_id, source_notebook_id)
    if definition_payload is None:
        return 1
    print("  Definition retrieved")

    # Step 2: Create new notebook
    print("\n[Step 2/3] Creating new notebook...")
    new_notebook_id = create_notebook(workspace_id, new_name)
    if new_notebook_id is None:
        return 1
    print(f"  Notebook created: {new_notebook_id}")

    # Step 3: Apply definition to new notebook
    print("\n[Step 3/3] Applying definition to clone...")
    result = update_definition(workspace_id, new_notebook_id, definition_payload)
    if result != 0:
        print("[WARNING] Definition update started but may still be in progress")

    print("\n" + "="*60)
    print("[SUCCESS] Notebook cloned!")
    print("="*60)
    print(f"Source:       {source_notebook_id}")
    print(f"Clone Name:   {new_name}")
    print(f"Clone ID:     {new_notebook_id}")
    print("="*60)

    return 0


def get_definition(workspace_id, notebook_id):
    """Get notebook definition (with LRO handling)."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/notebooks/{notebook_id}/getDefinition"

    try:
        response = fabric_request(url, method='POST', data={})

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            return extract_payload(data)
        elif response.status == 202:
            print("[INFO] Waiting for definition (long-running operation)...")
            data = fabric_lro_result(response)
            if data is None:
                return None
            return extract_payload(data)

    except urllib.error.HTTPError as e:
        handle_http_error(e, "Source notebook")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get definition: {e}")
        return None



def extract_payload(data):
    """Extract base64 payload from definition response."""
    definition = data.get('definition', {})
    parts = definition.get('parts', [])
    for part in parts:
        if 'notebook-content' in part.get('path', ''):
            return part.get('payload')
    if parts:
        return parts[0].get('payload')
    return None


def create_notebook(workspace_id, name):
    """Create a new notebook."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/notebooks"
    body = {"displayName": name}

    try:
        response = fabric_request(url, method='POST', data=body)

        if response.status == 201:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('id')
        elif response.status == 202:
            print("[INFO] Waiting for notebook creation (long-running operation)...")
            data = fabric_lro_result(response)
            return data.get('id') if data else None

    except urllib.error.HTTPError as e:
        handle_http_error(e, "Workspace")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to create notebook: {e}")
        return None



def update_definition(workspace_id, notebook_id, payload):
    """Update notebook definition."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/notebooks/{notebook_id}/updateDefinition"

    body = {
        "definition": {
            "parts": [
                {
                    "path": "notebook-content.py",
                    "payload": payload,
                    "payloadType": "InlineBase64"
                }
            ]
        }
    }

    try:
        response = fabric_request(url, method='POST', data=body)
        if response.status in [200, 202]:
            return 0

    except urllib.error.HTTPError as e:
        handle_http_error(e, "Clone notebook")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to update definition: {e}")
        return 1

    return 0


def main():
    cli = SkillCLI('notebook_clone.py',
                   'Clone an existing notebook')
    cli.workspace()
    cli.item('notebook', help='Source notebook name or GUID to clone')
    cli.positional('new_name', help='Display name for the cloned notebook')
    args = cli.parse()

    sys.exit(clone_notebook(args.workspace_id, args.notebook_id, args.new_name))


if __name__ == "__main__":
    main()
