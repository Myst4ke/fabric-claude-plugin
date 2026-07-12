#!/usr/bin/env python3
"""
Skill: pipeline-definition-get
Description: Get the definition of a data pipeline (decoded JSON)

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error
import base64

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def get_pipeline_definition(workspace_id, pipeline_id):
    """Get pipeline definition and decode it."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataPipelines/{pipeline_id}/getDefinition"

    try:
        response = fabric_request(url, method='POST', data={})

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            return decode_and_display(data, workspace_id, pipeline_id)
        elif response.status == 202:
            location = response.headers.get('Location')
            print(f"[INFO] Definition retrieval started as long-running operation")
            print(f"Location: {location}")
            print("[INFO] Please retry in a few moments.")
            return 2
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Pipeline")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def decode_and_display(data, workspace_id, pipeline_id):
    """Decode base64 definition and pretty-print."""
    definition = data.get('definition', {})
    parts = definition.get('parts', [])

    if not parts:
        print("[ERROR] No definition parts found in response")
        print("\nRaw response:")
        print(json.dumps(data, indent=2))
        return 1

    payload = parts[0].get('payload', '')
    payload_type = parts[0].get('payloadType', 'InlineBase64')
    path = parts[0].get('path', 'unknown')

    if not payload:
        print("[ERROR] Empty payload in definition")
        return 1

    try:
        decoded = base64.b64decode(payload).decode('utf-8')
        try:
            json_content = json.loads(decoded)
            print("\n" + "=" * 60)
            print("PIPELINE DEFINITION")
            print("=" * 60)
            print(f"Workspace ID: {workspace_id}")
            print(f"Pipeline ID:  {pipeline_id}")
            print(f"Part path:    {path}")
            print(f"Payload type: {payload_type}")
            print(f"Parts count:  {len(parts)}")
            print("=" * 60)
            print("\nDecoded definition:")
            print(json.dumps(json_content, indent=2))
            return 0
        except json.JSONDecodeError:
            # Not JSON, print as raw text
            print("\n" + "=" * 60)
            print("PIPELINE DEFINITION (raw text)")
            print("=" * 60)
            print(f"Workspace ID: {workspace_id}")
            print(f"Pipeline ID:  {pipeline_id}")
            print(f"Part path:    {path}")
            print("=" * 60)
            print(decoded)
            return 0
    except Exception as e:
        print(f"[ERROR] Failed to decode definition: {e}")
        return 1


def main():
    cli = SkillCLI('pipeline_definition_get.py',
                   'Get the definition of a data pipeline (decoded JSON)')
    cli.workspace()
    cli.item('pipeline')
    args = cli.parse()

    sys.exit(get_pipeline_definition(args.workspace_id, args.pipeline_id))


if __name__ == "__main__":
    main()
