#!/usr/bin/env python3
"""
Skill: capacity-metrics
Description: Get usage metrics and workload information for a Fabric capacity

Retrieves capacity details, workload states, and lists workspaces assigned
to the capacity for monitoring and cost optimization.
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, fabric_list, handle_http_error

CU_MAP = {
    'F2': 2, 'F4': 4, 'F8': 8, 'F16': 16, 'F32': 32,
    'F64': 64, 'F128': 128, 'F256': 256, 'F512': 512,
    'F1024': 1024, 'F2048': 2048
}


def get_capacity_metrics(capacity_id):
    """Get capacity metrics and workload information."""
    # 1. Get capacity details
    print(f"\nCapacity Metrics for {capacity_id}")
    print(f"{'='*70}")

    try:
        cap = fabric_request_json(f"{FABRIC_API_BASE}/capacities/{capacity_id}")
        print(f"\n  Capacity:  {cap.get('displayName', 'N/A')}")
        print(f"  SKU:       {cap.get('sku', 'N/A')}")
        print(f"  Region:    {cap.get('region', 'N/A')}")
        print(f"  State:     {cap.get('state', 'N/A')}")

        # SKU-based CU info
        sku = cap.get('sku', '')
        if sku in CU_MAP:
            print(f"  CU Units:  {CU_MAP[sku]} CU")
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Capacity")
    except Exception as e:
        print(f"[WARN] Could not get capacity details: {e}")

    # 2. List workspaces assigned to this capacity
    print(f"\n  Workspaces on this capacity:")
    print(f"  {'-'*60}")
    try:
        workspaces = fabric_list(f"{FABRIC_API_BASE}/workspaces")
        assigned = [w for w in workspaces
                    if w.get('capacityId', '').lower() == capacity_id.lower()]

        if assigned:
            for ws in assigned:
                ws_name = ws.get('displayName', 'N/A')[:40]
                ws_id = ws.get('id', 'N/A')[:38]
                print(f"    {ws_name:<40} {ws_id}")
            print(f"  Total: {len(assigned)} workspace(s)")
        else:
            print(f"    No workspaces found on this capacity.")
    except Exception as e:
        print(f"  [WARN] Could not list workspaces: {e}")

    # 3. Try to get workload states (admin API)
    print(f"\n  Workload States:")
    print(f"  {'-'*60}")
    try:
        workloads_url = f"{FABRIC_API_BASE}/admin/capacities/{capacity_id}/workloads"
        workloads = fabric_request_json(workloads_url)

        for wl in workloads.get('value', []):
            wl_name = wl.get('name', 'N/A')[:25]
            wl_state = wl.get('state', 'N/A')[:15]
            max_mem = wl.get('maxMemoryPercentageSetByUser', '')
            mem_str = f"  Max Memory: {max_mem}%" if max_mem else ""
            print(f"    {wl_name:<25} State: {wl_state:<15}{mem_str}")

        if not workloads.get('value'):
            print(f"    No workload data available.")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"    [INFO] Capacity Admin access required for workload details.")
        elif e.code == 404:
            print(f"    [INFO] Workloads API not available for this capacity type.")
        else:
            print(f"    [WARN] Could not get workloads: HTTP {e.code}")
    except Exception as e:
        print(f"    [WARN] Could not get workloads: {e}")

    print(f"\n{'='*70}")
    print(f"\nNext steps:")
    print(f"  - Capacity list:  fabric-plugin:capacity-list")
    print(f"  - Assign workspace: fabric-plugin:workspace-assign-capacity <workspace-id> {capacity_id}")
    return 0


def main():
    cli = SkillCLI('capacity_metrics.py',
                   'Get usage metrics and workload information for a Fabric capacity')
    cli.positional('capacity_id', help='Capacity GUID')
    args = cli.parse()

    sys.exit(get_capacity_metrics(args.capacity_id))


if __name__ == "__main__":
    main()
