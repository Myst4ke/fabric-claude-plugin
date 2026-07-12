#!/usr/bin/env python3
"""
Skill: pipeline-delete
Description: Delete a data pipeline from a Microsoft Fabric workspace

Accepts the workspace and pipeline as display names or GUIDs.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request, handle_http_error


def delete_pipeline(workspace_id, pipeline_id, force=False):
    """Delete a data pipeline."""
    # Confirmation check (unless --force)
    if not force:
        print(f"[WARNING] This will permanently delete the pipeline: {pipeline_id}")
        print("[INFO] Use --force to skip this confirmation")
        print("[INFO] Proceeding with deletion...")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/dataPipelines/{pipeline_id}"

    try:
        response = fabric_request(url, method='DELETE')

        if response.status in [200, 204]:
            print(f"\n[SUCCESS] Pipeline deleted successfully!")
            print(f"Pipeline ID: {pipeline_id}")
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Pipeline")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def main():
    cli = SkillCLI('pipeline_delete.py',
                   'Delete a data pipeline from a Microsoft Fabric workspace')
    cli.workspace()
    cli.item('pipeline')
    cli.flag('--force', help='Skip confirmation prompt')
    args = cli.parse()

    sys.exit(delete_pipeline(args.workspace_id, args.pipeline_id, args.force))


if __name__ == "__main__":
    main()
