#!/usr/bin/env python3
"""
Skill: notebook-export
Description: Export notebook to .ipynb file

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
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def export_notebook(workspace_id, notebook_id, output_file):
    """Export notebook to .ipynb file."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/notebooks/{notebook_id}/getDefinition"

    try:
        response = fabric_request(url, method='POST', data={})

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            return save_definition(data, output_file, notebook_id)
        elif response.status == 202:
            # Long-running operation - would need to poll
            location = response.headers.get('Location')
            print(f"[INFO] Export started as long-running operation")
            print(f"Location: {location}")
            print("[INFO] Please retry in a few moments.")
            return 2
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Notebook")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def save_definition(data, output_file, notebook_id):
    """Save notebook definition to file."""
    definition = data.get('definition', {})
    parts = definition.get('parts', [])

    notebook_content = None

    # Find the notebook content part
    for part in parts:
        path = part.get('path', '')
        payload = part.get('payload', '')
        payload_type = part.get('payloadType', 'InlineBase64')

        # Look for the main notebook content
        if payload_type == 'InlineBase64' and payload:
            try:
                decoded = base64.b64decode(payload).decode('utf-8')
                # Check if it's valid JSON (notebook format)
                try:
                    json_content = json.loads(decoded)
                    # Prefer the .ipynb or notebook content
                    if path.endswith('.ipynb') or 'notebook' in path.lower() or notebook_content is None:
                        notebook_content = json_content
                except json.JSONDecodeError:
                    # Not JSON, might be Python code
                    if path.endswith('.py') and notebook_content is None:
                        # Create a simple notebook structure
                        notebook_content = {
                            "cells": [
                                {
                                    "cell_type": "code",
                                    "source": decoded.split('\n'),
                                    "metadata": {},
                                    "outputs": []
                                }
                            ],
                            "metadata": {
                                "kernelspec": {
                                    "name": "python3",
                                    "display_name": "Python 3"
                                }
                            },
                            "nbformat": 4,
                            "nbformat_minor": 4
                        }
            except Exception as e:
                print(f"[WARNING] Could not decode part {path}: {e}")

    if notebook_content is None:
        print("[ERROR] Could not extract notebook content from definition")
        print("\nRaw response:")
        print(json.dumps(data, indent=2))
        return 1

    # Save to file
    try:
        # Ensure directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(notebook_content, f, indent=2)

        print(f"\n[SUCCESS] Notebook exported!")
        print("="*60)
        print(f"Notebook ID: {notebook_id}")
        print(f"Output file: {output_file}")
        print(f"File size:   {os.path.getsize(output_file)} bytes")
        print("="*60)
        return 0

    except Exception as e:
        print(f"[ERROR] Failed to save file: {e}")
        return 1


def main():
    cli = SkillCLI('notebook_export.py',
                   'Export notebook to .ipynb file')
    cli.workspace()
    cli.item('notebook')
    cli.positional('output_file', help='Path to save the .ipynb file')
    args = cli.parse()

    sys.exit(export_notebook(args.workspace_id, args.notebook_id, args.output_file))


if __name__ == "__main__":
    main()
