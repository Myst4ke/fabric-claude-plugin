#!/usr/bin/env python3
"""
Skill: semantic-model-refresh
Description: Trigger a refresh of a semantic model (Power BI dataset)

Supports both GUIDs and names for workspace and model arguments.
"""

import sys
import os
import json
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import fabric_request, handle_http_error, check_security


def refresh_semantic_model(workspace_id, model_id):
    """Trigger semantic model refresh."""
    check_security(workspace_id, "semantic-model:refresh")

    # The Fabric API has no /semanticModels/{id}/refresh endpoint; refreshes go
    # through the Power BI API (same Entra token)
    url = (f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}"
           f"/datasets/{model_id}/refreshes")

    body = {"type": "Full"}

    try:
        response = fabric_request(url, method='POST', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("[ERROR] Bad Request. The semantic model may not be refreshable.")
            print("        Check that the model has refreshable data sources.")
            try:
                error_body = e.read().decode('utf-8')
                msg = json.loads(error_body).get('error', {}).get('message', '')
                if msg:
                    print(f"\nAPI details: {msg}")
            except Exception:
                pass
            return 1
        elif e.code == 409:
            print("[INFO] A refresh is already in progress for this model.")
            print("       Wait for it to complete or check refresh history.")
            return 1
        return handle_http_error(e, "Semantic model")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 202):
        print(f"\n[SUCCESS] Refresh triggered for semantic model {model_id}")
        print(f"  Status: Accepted (running asynchronously)")

        request_id = response.headers.get('x-ms-request-id', '')
        if request_id:
            print(f"  Request ID: {request_id}")

        print(f"\nCheck progress:")
        print(f"  fabric-plugin:semantic-model-refresh-history {workspace_id} {model_id}")
        return 0
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def main():
    cli = SkillCLI('semantic_model_refresh.py',
                   'Trigger a refresh of a semantic model (Power BI dataset)')
    cli.workspace()
    cli.item('semanticmodel', help='Semantic model name or GUID')
    args = cli.parse()

    sys.exit(refresh_semantic_model(args.workspace_id, args.semanticmodel_id))


if __name__ == "__main__":
    main()
