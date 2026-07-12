#!/usr/bin/env python3
"""
Skill: environment-get
Description: Get detailed information about an environment including published libraries
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import FABRIC_API_BASE, fabric_request_json, handle_http_error


def get_environment(workspace_id, env_id):
    """Get environment details and published libraries."""
    base = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/environments/{env_id}"

    try:
        env = fabric_request_json(base)
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "Environment")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    print(f"\nEnvironment Details:")
    print(f"{'='*70}")
    print(f"  Name:        {env.get('displayName', 'N/A')}")
    print(f"  ID:          {env.get('id', 'N/A')}")
    print(f"  Description: {env.get('description', '(none)')}")
    if 'createdDate' in env:
        print(f"  Created:     {env['createdDate']}")
    if 'modifiedDate' in env:
        print(f"  Modified:    {env['modifiedDate']}")

    # Spark compute settings
    try:
        spark = fabric_request_json(f"{base}/sparkcompute")

        print(f"\n  Spark Compute:")
        print(f"  {'-'*60}")
        print(f"    Runtime:    {spark.get('runtimeVersion', 'N/A')}")

        instance_pool = spark.get('instancePool', {})
        if instance_pool:
            print(f"    Pool Name:  {instance_pool.get('name', 'N/A')}")
            print(f"    Pool Type:  {instance_pool.get('type', 'N/A')}")
    except urllib.error.HTTPError:
        print(f"\n  Spark Compute: [not available]")
    except Exception:
        pass

    # Published libraries
    try:
        libs = fabric_request_json(f"{base}/libraries")

        print(f"\n  Published Libraries:")
        print(f"  {'-'*60}")

        custom_libs = libs.get('customLibraries', {})
        pypi_libs = custom_libs.get('pypiLibraries', [])
        conda_libs = custom_libs.get('condaLibraries', [])
        wheel_libs = custom_libs.get('wheelLibraries', [])
        jar_libs = custom_libs.get('jarLibraries', [])

        if pypi_libs:
            print(f"    PyPI packages ({len(pypi_libs)}):")
            for lib in pypi_libs[:20]:
                name = lib if isinstance(lib, str) else lib.get('name', 'N/A')
                version = '' if isinstance(lib, str) else f" == {lib.get('version', '')}"
                print(f"      - {name}{version}")
            if len(pypi_libs) > 20:
                print(f"      ... and {len(pypi_libs) - 20} more")

        if conda_libs:
            print(f"    Conda packages ({len(conda_libs)}):")
            for lib in conda_libs[:10]:
                print(f"      - {lib}")

        if wheel_libs:
            print(f"    Wheel files ({len(wheel_libs)}):")
            for lib in wheel_libs[:10]:
                name = lib if isinstance(lib, str) else lib.get('name', str(lib))
                print(f"      - {name}")

        if jar_libs:
            print(f"    JAR files ({len(jar_libs)}):")
            for lib in jar_libs[:10]:
                name = lib if isinstance(lib, str) else lib.get('name', str(lib))
                print(f"      - {name}")

        if not any([pypi_libs, conda_libs, wheel_libs, jar_libs]):
            print(f"    No custom libraries published.")

    except urllib.error.HTTPError:
        print(f"\n  Libraries: [not available]")
    except Exception:
        pass

    print(f"\n{'='*70}")
    print(f"\nNext steps:")
    print(f"  - Staging:  fabric-plugin:environment-staging {workspace_id} {env_id}")
    print(f"  - Publish:  fabric-plugin:environment-publish {workspace_id} {env_id}")
    return 0


def main():
    cli = SkillCLI('environment_get.py',
                   'Get detailed information about an environment '
                   'including published libraries')
    cli.workspace()
    cli.item('environment', help='Environment name or GUID')
    args = cli.parse()

    sys.exit(get_environment(args.workspace_id, args.environment_id))


if __name__ == "__main__":
    main()
