#!/usr/bin/env python3
"""
Skill: table-load
Description: Load data into a lakehouse table from a file

Accepts workspace and lakehouse as display names or GUIDs.
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

MAX_POLL_TIME = 600  # 10 minutes max
POLL_INTERVAL = 5  # seconds


def load_table(workspace_id, lakehouse_id, table_name, file_path, mode='Overwrite'):
    """Load data into table."""
    url = (f"{FABRIC_API_BASE}/workspaces/{workspace_id}"
           f"/lakehouses/{lakehouse_id}/tables/{table_name}/load")

    body = {
        'pathType': 'File',
        'relativePath': file_path,
        'mode': mode
    }

    print(f"Loading data into table '{table_name}'...")
    print(f"  Source: {file_path}")
    print(f"  Mode:   {mode}")
    print("")

    try:
        response = fabric_request(url, method='POST', data=body)

        if response.status == 200:
            print("[SUCCESS] Data loaded immediately.")
            return 0
        elif response.status == 202:
            # LRO - need to poll
            location = response.headers.get('Location')
            retry_after = int(response.headers.get('Retry-After', POLL_INTERVAL))

            print("Data loading started (LRO)...")
            print("This may take several minutes for large files...\n")

            return poll_operation(location, retry_after, table_name)
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_load_error(e, table_name, file_path)
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def poll_operation(location, initial_delay, table_name):
    """Poll LRO until completion."""
    elapsed = 0
    delay = initial_delay

    while elapsed < MAX_POLL_TIME:
        time.sleep(delay)
        elapsed += delay

        try:
            response = fabric_request(location, method='GET')

            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                status = data.get('status', 'Unknown')
                percent = data.get('percentComplete', 0)

                print(f"  Progress: {percent}% ({status})")

                if status == 'Succeeded':
                    print(f"\n[SUCCESS] Data loaded into table '{table_name}'!")
                    return 0

                elif status == 'Failed':
                    error = data.get('error', {})
                    print(f"\n[ERROR] Load failed: {error.get('message', 'Unknown error')}")
                    return 1

                # Continue polling
                delay = POLL_INTERVAL

        except urllib.error.HTTPError as e:
            if e.code == 429:
                delay = int(e.headers.get('Retry-After', delay * 2))
                print(f"  Rate limited, waiting {delay}s...")
            else:
                print(f"[ERROR] Polling failed: HTTP {e.code}")
                return 2
        except Exception as e:
            print(f"[ERROR] Polling failed: {e}")
            return 2

    print(f"[ERROR] Operation timed out after {MAX_POLL_TIME}s")
    return 2


def handle_load_error(error, table_name, file_path):
    """Handle HTTP errors, distinguishing table vs file 404s."""
    if error.code == 404:
        try:
            error_body = json.loads(error.read().decode('utf-8'))
            message = error_body.get('error', {}).get('message', '')
            if 'table' in message.lower():
                print(f"[ERROR] Table not found: {table_name}")
            elif 'file' in message.lower() or 'path' in message.lower():
                print(f"[ERROR] File not found: {file_path}")
                print("Make sure the file exists in the lakehouse Files section")
            else:
                print(f"[ERROR] Resource not found: {message}")
        except Exception:
            print("[ERROR] Resource not found")
        return 1
    return handle_http_error(error, "Table")


def main():
    cli = SkillCLI('table_load.py',
                   'Load data into a lakehouse table from a file')
    cli.workspace()
    cli.item('lakehouse')
    cli.positional('table_name', help='Target table name')
    cli.positional('file_path', help='Path to file in lakehouse Files section (e.g. Files/data/sales.csv)')
    cli.opt('--mode', choices=['Overwrite', 'Append'], default='Overwrite',
            help='Load mode: Overwrite (default) or Append')
    args = cli.parse()

    sys.exit(load_table(args.workspace_id, args.lakehouse_id,
                        args.table_name, args.file_path, args.mode))


if __name__ == "__main__":
    main()
