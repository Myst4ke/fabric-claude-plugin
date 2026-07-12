#!/usr/bin/env python3
"""
Skill: notebook-definition-get
Description: Get notebook definition (.ipynb format)

Accepts workspace and notebook as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error
import base64

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, fabric_lro_result, handle_http_error


def display_definition(data, notebook_id):
    """Display the notebook definition."""
    print(f"\n[SUCCESS] Retrieved definition for notebook {notebook_id}")
    print("="*60)

    # The definition response contains 'definition' with 'parts'
    definition = data.get('definition', {})
    parts = definition.get('parts', [])

    if parts:
        for part in parts:
            path = part.get('path', 'unknown')
            payload = part.get('payload', '')
            payload_type = part.get('payloadType', 'InlineBase64')

            print(f"\nPart: {path}")
            print("-"*60)

            if payload_type == 'InlineBase64' and payload:
                try:
                    decoded = base64.b64decode(payload).decode('utf-8')
                    # Try to parse as JSON for pretty printing
                    try:
                        json_content = json.loads(decoded)
                        print(json.dumps(json_content, indent=2))
                    except json.JSONDecodeError:
                        print(decoded)
                except Exception as e:
                    print(f"[Could not decode: {e}]")
                    print(f"Raw payload: {payload[:200]}...")
            else:
                print(f"Payload type: {payload_type}")
                print(f"Payload: {payload[:500]}..." if len(payload) > 500 else f"Payload: {payload}")
    else:
        # Raw response
        print("\nRaw response:")
        print(json.dumps(data, indent=2))

    print("\n" + "="*60)


def get_notebook_definition(workspace_id, notebook_id):
    """Get notebook definition in .ipynb format."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/notebooks/{notebook_id}/getDefinition?format=ipynb"

    try:
        response = fabric_request(url, method='POST', data={})

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            display_definition(data, notebook_id)
            return 0
        elif response.status == 202:
            print("[INFO] Definition retrieval started (long-running operation), waiting...")
            data = fabric_lro_result(response)
            if data is None:
                return 2
            display_definition(data, notebook_id)
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Notebook")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('notebook_definition_get.py',
                   'Get notebook definition (.ipynb format)')
    cli.workspace()
    cli.item('notebook')
    args = cli.parse()

    sys.exit(get_notebook_definition(args.workspace_id, args.notebook_id))


if __name__ == "__main__":
    main()
