#!/usr/bin/env python3
"""
Skill: pipeline-export
Description: Export a data pipeline definition to a local file

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


def export_pipeline(workspace_id, pipeline_id, output_file):
    """Export pipeline definition to file."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataPipelines/{pipeline_id}/getDefinition"

    try:
        response = fabric_request(url, method='POST', data={})

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            return save_definition(data, output_file, pipeline_id)
        elif response.status == 202:
            location = response.headers.get('Location')
            print(f"[INFO] Export started as long-running operation")
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


def save_definition(data, output_file, pipeline_id):
    """Decode and save pipeline definition to file."""
    definition = data.get('definition', {})
    parts = definition.get('parts', [])

    if not parts:
        print("[ERROR] No definition parts found in response")
        print("\nRaw response:")
        print(json.dumps(data, indent=2))
        return 1

    payload = parts[0].get('payload', '')

    if not payload:
        print("[ERROR] Empty payload in definition")
        return 1

    try:
        decoded = base64.b64decode(payload).decode('utf-8')

        # Try to parse as JSON for pretty-printing
        try:
            json_content = json.loads(decoded)
            content_to_write = json.dumps(json_content, indent=2)
        except json.JSONDecodeError:
            content_to_write = decoded

        # Ensure directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content_to_write)

        print(f"\n[SUCCESS] Pipeline definition exported!")
        print("=" * 60)
        print(f"Pipeline ID: {pipeline_id}")
        print(f"Output file: {output_file}")
        print(f"File size:   {os.path.getsize(output_file)} bytes")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"[ERROR] Failed to save file: {e}")
        return 1


def main():
    cli = SkillCLI('pipeline_export.py',
                   'Export a data pipeline definition to a local file')
    cli.workspace()
    cli.item('pipeline')
    cli.positional('output_file', help='Path to save the exported JSON definition')
    args = cli.parse()

    sys.exit(export_pipeline(args.workspace_id, args.pipeline_id, args.output_file))


if __name__ == "__main__":
    main()
