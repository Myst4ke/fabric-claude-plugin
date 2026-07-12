#!/usr/bin/env python3
"""
Skill: capacity-get
Description: Get detailed information about a Fabric capacity
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_capacity(cap):
    """Display capacity details."""
    print(f"\nCapacity Details:")
    print(f"{'='*60}")
    print(f"  Name:           {cap.get('displayName', 'N/A')}")
    print(f"  ID:             {cap.get('id', 'N/A')}")
    print(f"  SKU:            {cap.get('sku', 'N/A')}")
    print(f"  Region:         {cap.get('region', 'N/A')}")
    print(f"  State:          {cap.get('state', 'N/A')}")

    # Additional properties
    if 'admins' in cap:
        admins = cap['admins']
        if isinstance(admins, list):
            admin_names = [a.get('displayName', a.get('emailAddress', 'N/A')) for a in admins]
            print(f"  Admins:         {', '.join(admin_names[:5])}")
    if 'tenantId' in cap:
        print(f"  Tenant ID:      {cap['tenantId']}")

    print(f"{'='*60}")

    cap_id = cap.get('id', '<capacity-id>')
    print(f"\nNext steps:")
    print(f"  - Metrics: fabric-plugin:capacity-metrics {cap_id}")
    print(f"  - List:    fabric-plugin:capacity-list")


def main():
    cli = SkillCLI('capacity_get.py',
                   'Get detailed information about a Fabric capacity')
    cli.positional('capacity_id', help='Capacity GUID')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/capacities/{args.capacity_id}"
    try:
        capacity = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Capacity"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_capacity(capacity)
    sys.exit(0)


if __name__ == "__main__":
    main()
