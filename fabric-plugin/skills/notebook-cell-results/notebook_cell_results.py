#!/usr/bin/env python3
"""
Skill: notebook-cell-results
Description: Get cell execution results from a notebook run

Accepts workspace and notebook as display names or GUIDs.
"""

import sys
import json
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def display_cell_results(run_details, notebook_id, job_id):
    """Display cell execution results."""
    print("\n" + "="*60)
    print("NOTEBOOK CELL RESULTS")
    print("="*60)
    print(f"Notebook ID: {notebook_id}")
    print(f"Job ID:      {job_id}")
    print(f"Status:      {run_details.get('status', 'N/A')}")
    print("="*60)

    # Check for cell outputs in various formats
    cell_outputs = run_details.get('cellOutputs', [])
    execution_output = run_details.get('executionOutput')
    output_data = run_details.get('output')

    if cell_outputs:
        print(f"\n[CELL OUTPUTS] ({len(cell_outputs)} cells)")
        print("-"*60)
        for i, cell in enumerate(cell_outputs):
            print(f"\nCell {i + 1}:")
            print(f"  Status: {cell.get('status', 'N/A')}")
            if cell.get('output'):
                print(f"  Output: {cell.get('output')[:500]}...")
            if cell.get('error'):
                print(f"  Error: {cell.get('error')}")

    elif execution_output:
        print(f"\n[EXECUTION OUTPUT]")
        print("-"*60)
        if isinstance(execution_output, dict):
            print(json.dumps(execution_output, indent=2))
        else:
            print(execution_output)

    elif output_data:
        print(f"\n[OUTPUT DATA]")
        print("-"*60)
        if isinstance(output_data, dict):
            print(json.dumps(output_data, indent=2))
        else:
            print(output_data)

    else:
        print("\n[INFO] No cell-level results available for this run.")
        print("The notebook may still be running or results are in a different format.")

    # Check for failure reason
    failure_reason = run_details.get('failureReason')
    if failure_reason:
        print(f"\n[FAILURE REASON]")
        print("-"*60)
        print(failure_reason)

    print("\n" + "="*60)

    # Raw JSON for complete data
    print("\nRaw JSON:")
    print(json.dumps(run_details, indent=2))


def main():
    cli = SkillCLI('notebook_cell_results.py',
                   'Get cell execution results from a notebook run')
    cli.workspace()
    cli.item('notebook')
    cli.positional('job_id', help='The job instance ID')
    args = cli.parse()

    url = (f"{FABRIC_API_BASE}/workspaces/{args.workspace_id}/items/{args.notebook_id}"
           f"/jobs/instances/{args.job_id}")
    try:
        run_details = fabric_request_json(url)
    except urllib.error.HTTPError as e:
        sys.exit(handle_http_error(e, "Notebook or job"))
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        sys.exit(2)

    display_cell_results(run_details, args.notebook_id, args.job_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
