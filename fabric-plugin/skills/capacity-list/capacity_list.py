#!/usr/bin/env python3
"""
Skill: capacity-list
Description: List all Fabric capacities accessible to the user
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_list, handle_http_error


def display_capacities(capacities):
    """Display capacities in formatted output."""
    count = len(capacities)
    print(f"\nFound {count} capacity(ies):\n")

    if count == 0:
        print("No capacities accessible.")
        return

    print(f"{'Display Name':<30} {'ID':<38} {'SKU':<10} {'Region':<20} {'State':<12}")
    print(f"{'-'*30} {'-'*38} {'-'*10} {'-'*20} {'-'*12}")

    for cap in capacities:
        name = cap.get('displayName', 'N/A')[:30]
        cap_id = cap.get('id', 'N/A')[:38]
        sku = cap.get('sku', 'N/A')[:10]
        region = cap.get('region', 'N/A')[:20]
        state = cap.get('state', 'N/A')[:12]
        print(f"{name:<30} {cap_id:<38} {sku:<10} {region:<20} {state:<12}")

    print(f"\nNext steps:")
    print(f"  - Details: fabric-plugin:capacity-get <capacity-id>")
    print(f"  - Metrics: fabric-plugin:capacity-metrics <capacity-id>")


def main():
    cli = SkillCLI('capacity_list.py',
                   'List all Fabric capacities accessible to the user')
    cli.opt('--limit', type=int, help='Maximum number of capacities to return')
    args = cli.parse()

    url = f"{FABRIC_API_BASE}/capacities"
    try:
        capacities = fabric_list(url, limit=args.limit)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Capacity"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_capacities(capacities)
    sys.exit(0)


if __name__ == "__main__":
    main()
