#!/usr/bin/env python3
"""
Skill: pipeline-import
Description: Import a data pipeline from a local definition file

Accepts the workspace as a display name or a GUID.
"""

import sys
import json
import os
import time
import urllib.error
import base64

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error

LRO_TIMEOUT = 300  # 5 minutes per operation
LRO_POLL_INTERVAL = 3  # seconds


def import_pipeline(workspace_id, name, definition_file):
    """Import pipeline from definition file."""
    print(f"\n[INFO] Importing pipeline...")
    print(f"Name:       {name}")
    print(f"Definition: {definition_file}")
    print("-" * 60)

    try:
        with open(definition_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Definition file not found: {definition_file}")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to read definition file: {e}")
        return 1

    # Base64 encode the content
    encoded_payload = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')

    # Step 1: Create pipeline
    print("\n[Step 1/2] Creating pipeline...")
    pipeline_id = create_pipeline(workspace_id, name)
    if pipeline_id is None:
        return 1
    print(f"  Pipeline created: {pipeline_id}")

    # Step 2: Upload definition
    print("\n[Step 2/2] Uploading definition...")
    result = update_definition(workspace_id, pipeline_id, encoded_payload)
    if result != 0:
        print("[WARNING] Definition update started but may still be in progress")

    print("\n" + "=" * 60)
    print("[SUCCESS] Pipeline imported!")
    print("=" * 60)
    print(f"Name:        {name}")
    print(f"Pipeline ID: {pipeline_id}")
    print(f"Workspace:   {workspace_id}")
    print(f"Definition:  {definition_file}")
    print("=" * 60)

    return 0


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


def update_definition(workspace_id, pipeline_id, encoded_payload):
    """Update pipeline definition."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataPipelines/{pipeline_id}/updateDefinition"

    body = {
        "definition": {
            "parts": [
                {
                    "path": "pipeline-content.json",
                    "payload": encoded_payload,
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
    cli = SkillCLI('pipeline_import.py',
                   'Import a data pipeline from a local definition file')
    cli.workspace()
    cli.positional('name', help='Display name for the new pipeline')
    cli.positional('definition_file', help='Path to the JSON definition file')
    args = cli.parse()

    sys.exit(import_pipeline(args.workspace_id, args.name, args.definition_file))


if __name__ == "__main__":
    main()
