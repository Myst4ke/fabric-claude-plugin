#!/usr/bin/env python3
"""
Skill: notebook-import
Description: Import notebook from .ipynb file

Accepts the workspace as a display name or a GUID.
The new notebook name is taken as-is (no resolution).
"""

import sys
import json
import os
import urllib.error
import base64
import time

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error

LRO_TIMEOUT = 600  # 10 minutes
LRO_POLL_INTERVAL = 5  # seconds


def import_notebook(workspace_id, name, ipynb_file):
    """Import notebook from .ipynb file."""
    # Read and validate the .ipynb file
    try:
        with open(ipynb_file, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {ipynb_file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {ipynb_file}: {e}")
        return 1

    # Fabric requires cell sources as lists of lines (a plain string is rejected
    # with InvalidNotebookContent)
    for cell in notebook.get('cells', []):
        if isinstance(cell.get('source'), str):
            cell['source'] = cell['source'].splitlines(keepends=True)

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/notebooks"

    # Encode content as base64
    notebook_content = json.dumps(notebook, ensure_ascii=False)
    payload_base64 = base64.b64encode(notebook_content.encode('utf-8')).decode('utf-8')

    body = {
        "displayName": name,
        "definition": {
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook-content.ipynb",
                    "payload": payload_base64,
                    "payloadType": "InlineBase64"
                }
            ]
        }
    }

    try:
        response = fabric_request(url, method='POST', data=body)

        if response.status == 201:
            data = json.loads(response.read().decode('utf-8'))
            notebook_id = data.get('id', 'N/A')
            print(f"\n[SUCCESS] Notebook imported!")
            print("="*60)
            print(f"Name:        {name}")
            print(f"Notebook ID: {notebook_id}")
            print(f"Source file: {ipynb_file}")
            print("="*60)
            return 0
        elif response.status == 202:
            # Long-running operation
            location = response.headers.get('Location')
            operation_id = response.headers.get('x-ms-operation-id')
            retry_after = int(response.headers.get('Retry-After', LRO_POLL_INTERVAL))

            print(f"[INFO] Notebook import started (long-running operation)")
            return poll_operation(location, operation_id, retry_after, name)
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def poll_operation(location, operation_id, retry_after, name):
    """Poll LRO until completion."""
    start_time = time.time()
    poll_url = location if location else f"{FABRIC_API_BASE}/operations/{operation_id}"

    while True:
        elapsed = time.time() - start_time
        if elapsed > LRO_TIMEOUT:
            print(f"[ERROR] Operation timed out after {LRO_TIMEOUT} seconds")
            return 2

        time.sleep(retry_after)

        try:
            response = fabric_request(poll_url)
            if response.status == 202:
                # Still processing
                continue
            data = json.loads(response.read().decode('utf-8'))

            status = data.get('status', 'Unknown')
            percent = data.get('percentComplete', 0)
            print(f"  Status: {status} ({percent}% complete)")

            if status == 'Succeeded':
                # Try to get the notebook ID from response
                result = data.get('result', {})
                notebook_id = result.get('id', 'N/A')
                print(f"\n[SUCCESS] Notebook imported!")
                print("="*60)
                print(f"Name:        {name}")
                print(f"Notebook ID: {notebook_id}")
                print("="*60)
                return 0
            elif status in ['Failed', 'Cancelled']:
                error = data.get('error', {})
                print(f"\n[ERROR] Operation {status}")
                print(f"Error: {error.get('message', 'Unknown error')}")
                return 1

        except urllib.error.HTTPError as e:
            return handle_http_error(e, "Operation")
        except Exception as e:
            print(f"[ERROR] Poll failed: {e}")
            return 2


def main():
    cli = SkillCLI('notebook_import.py',
                   'Import notebook from .ipynb file')
    cli.workspace()
    cli.positional('name', help='Name for the new notebook')
    cli.positional('ipynb_file', help='Path to the .ipynb file to import')
    args = cli.parse()

    sys.exit(import_notebook(args.workspace_id, args.name, args.ipynb_file))


if __name__ == "__main__":
    main()
