#!/usr/bin/env python3
"""
Skill: environment-staging
Description: Get the staging area (pending changes) of an environment
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def get_staging(workspace_id, env_id):
    """Get environment staging area."""
    base = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/environments/{env_id}"

    try:
        data = fabric_request_json(f"{base}/staging/libraries")
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Environment")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    print(f"\nStaging Area for environment {env_id}")
    print(f"{'='*70}")
    print(f"  (These changes will be applied on next publish)\n")

    custom_libs = data.get('customLibraries', {})
    has_changes = False

    pypi_libs = custom_libs.get('pypiLibraries', [])
    if pypi_libs:
        has_changes = True
        print(f"  PyPI packages ({len(pypi_libs)}):")
        for lib in pypi_libs:
            if isinstance(lib, dict):
                print(f"    - {lib.get('name', 'N/A')} == {lib.get('version', 'latest')}")
            else:
                print(f"    - {lib}")

    conda_libs = custom_libs.get('condaLibraries', [])
    if conda_libs:
        has_changes = True
        print(f"  Conda packages ({len(conda_libs)}):")
        for lib in conda_libs:
            print(f"    - {lib}")

    wheel_libs = custom_libs.get('wheelLibraries', [])
    if wheel_libs:
        has_changes = True
        print(f"  Wheel files ({len(wheel_libs)}):")
        for lib in wheel_libs:
            name = lib if isinstance(lib, str) else lib.get('name', str(lib))
            print(f"    - {name}")

    jar_libs = custom_libs.get('jarLibraries', [])
    if jar_libs:
        has_changes = True
        print(f"  JAR files ({len(jar_libs)}):")
        for lib in jar_libs:
            name = lib if isinstance(lib, str) else lib.get('name', str(lib))
            print(f"    - {name}")

    if not has_changes:
        print(f"  No pending library changes in staging.")

    # Spark compute staging
    try:
        spark = fabric_request_json(f"{base}/staging/sparkcompute")

        print(f"\n  Spark Compute (staging):")
        print(f"  {'-'*50}")
        print(f"    Runtime: {spark.get('runtimeVersion', 'N/A')}")
    except Exception:
        pass

    print(f"\n{'='*70}")
    print(f"\nTo apply changes:")
    print(f"  fabric-plugin:environment-publish {workspace_id} {env_id}")
    return 0


def main():
    cli = SkillCLI('environment_staging.py',
                   'Get the staging area (pending changes) of an environment')
    cli.workspace()
    cli.item('environment', help='Environment name or GUID')
    args = cli.parse()

    sys.exit(get_staging(args.workspace_id, args.environment_id))


if __name__ == "__main__":
    main()
