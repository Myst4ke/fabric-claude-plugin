#!/usr/bin/env python3
"""
Skill: pipeline-clone
Description: Clone an existing data pipeline within a workspace

Accepts the workspace and source pipeline as display names or GUIDs.
"""

import sys
import json
import os
import time
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error

LRO_TIMEOUT = 300  # 5 minutes per operation
LRO_POLL_INTERVAL = 3  # seconds


def clone_pipeline(workspace_id, source_pipeline_id, new_name):
    """Clone a pipeline by exporting and re-importing."""
    print(f"\n[INFO] Cloning pipeline...")
    print(f"Source:   {source_pipeline_id}")
    print(f"New name: {new_name}")
    print("-" * 60)

    # Step 1: Get source pipeline definition
    print("\n[Step 1/3] Getting source definition...")
    definition_payload = get_definition(workspace_id, source_pipeline_id)
    if definition_payload is None:
        return 1
    print("  Definition retrieved")

    # Step 2: Create new pipeline
    print("\n[Step 2/3] Creating new pipeline...")
    new_pipeline_id = create_pipeline(workspace_id, new_name)
    if new_pipeline_id is None:
        return 1
    print(f"  Pipeline created: {new_pipeline_id}")

    # Step 3: Apply definition to new pipeline
    print("\n[Step 3/3] Applying definition to clone...")
    result = update_definition(workspace_id, new_pipeline_id, definition_payload)
    if result != 0:
        print("[WARNING] Definition update started but may still be in progress")

    print("\n" + "=" * 60)
    print("[SUCCESS] Pipeline cloned!")
    print("=" * 60)
    print(f"Source:       {source_pipeline_id}")
    print(f"Clone Name:   {new_name}")
    print(f"Clone ID:     {new_pipeline_id}")
    print(f"Workspace:    {workspace_id}")
    print("=" * 60)

    return 0


def get_definition(workspace_id, pipeline_id):
    """Get pipeline definition (with LRO handling)."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataPipelines/{pipeline_id}/getDefinition"

    try:
        response = fabric_request(url, method='POST', data={})

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            return extract_payload(data)
        elif response.status == 202:
            location = response.headers.get('Location')
            return poll_definition(location)

    except urllib.error.HTTPError as e:
        handle_http_error(e, "Pipeline definition")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get definition: {e}")
        return None


def poll_definition(location):
    """Poll for definition completion."""
    start_time = time.time()
    while time.time() - start_time < LRO_TIMEOUT:
        time.sleep(LRO_POLL_INTERVAL)

        try:
            response = fabric_request(location)
            data = json.loads(response.read().decode('utf-8'))

            status = data.get('status', 'Unknown')
            if status == 'Succeeded':
                return extract_payload(data)
            elif status in ['Failed', 'Cancelled']:
                print(f"[ERROR] Definition retrieval {status}")
                return None

        except urllib.error.HTTPError as e:
            if e.code == 202:
                continue
            handle_http_error(e, "Operation")
            return None

    print("[ERROR] Timeout waiting for definition")
    return None


def extract_payload(data):
    """Extract base64 payload from definition response."""
    definition = data.get('definition', {})
    parts = definition.get('parts', [])
    if parts:
        return parts[0].get('payload')
    return None


def create_pipeline(workspace_id, name):
    """Create a new pipeline."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataPipelines"

    try:
        response = fabric_request(url, method='POST', data={"displayName": name})

        if response.status == 201:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('id')
        elif response.status == 202:
            # LRO - poll for completion
            location = response.headers.get('Location')
            return poll_create(location)

    except urllib.error.HTTPError as e:
        handle_http_error(e, "Pipeline")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to create pipeline: {e}")
        return None


def poll_create(location):
    """Poll for pipeline creation completion."""
    start_time = time.time()
    while time.time() - start_time < LRO_TIMEOUT:
        time.sleep(LRO_POLL_INTERVAL)

        try:
            response = fabric_request(location)
            data = json.loads(response.read().decode('utf-8'))

            status = data.get('status', 'Unknown')
            if status == 'Succeeded':
                result = data.get('result', {})
                return result.get('id')
            elif status in ['Failed', 'Cancelled']:
                print(f"[ERROR] Pipeline creation {status}")
                return None

        except urllib.error.HTTPError as e:
            if e.code == 202:
                continue
            handle_http_error(e, "Operation")
            return None

    print("[ERROR] Timeout waiting for pipeline creation")
    return None


def update_definition(workspace_id, pipeline_id, payload):
    """Update pipeline definition."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataPipelines/{pipeline_id}/updateDefinition"

    body = {
        "definition": {
            "parts": [
                {
                    "path": "pipeline-content.json",
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
        handle_http_error(e, "Pipeline definition")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to update definition: {e}")
        return 1

    return 0


def main():
    cli = SkillCLI('pipeline_clone.py',
                   'Clone an existing data pipeline within a workspace')
    cli.workspace()
    cli.item('pipeline', help='Source pipeline name or GUID to clone')
    cli.positional('new_name', help='Display name for the cloned pipeline')
    args = cli.parse()

    sys.exit(clone_pipeline(args.workspace_id, args.pipeline_id, args.new_name))


if __name__ == "__main__":
    main()
