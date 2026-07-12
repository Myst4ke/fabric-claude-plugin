#!/usr/bin/env python3
"""
Skill: git-connect
Description: Connect a workspace to a Git repository (Azure DevOps or GitHub)
"""

import sys
import os
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request, handle_http_error,
                         check_security)


def connect_git(workspace_id, args):
    """Connect workspace to Git repository."""
    check_security(workspace_id, "git:connect")

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/git/connect"

    git_provider_details = {
        'organizationName': args.org,
        'repositoryName': args.repo,
        'branchName': args.branch,
        'directoryName': args.directory,
        'gitProviderType': args.provider,
    }
    if args.provider == 'AzureDevOps':
        git_provider_details['projectName'] = args.project

    body = {'gitProviderDetails': git_provider_details}

    try:
        response = fabric_request(url, method='POST', data=body)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("[ERROR] Forbidden. Need Admin role to connect workspace to Git.")
            return 1
        elif e.code == 409:
            print("[ERROR] Workspace is already connected to a Git repository.")
            print("        Disconnect first: fabric-plugin:git-disconnect <workspace-id>")
            return 1
        return handle_http_error(e, "Workspace")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if response.status in (200, 201, 204):
        print(f"\n[SUCCESS] Workspace connected to Git repository")
        print(f"  Provider:  {args.provider}")
        print(f"  Org:       {args.org}")
        if args.project:
            print(f"  Project:   {args.project}")
        print(f"  Repo:      {args.repo}")
        print(f"  Branch:    {args.branch}")
        print(f"  Directory: {args.directory}")
        print(f"\nNext steps:")
        print(f"  - Status: fabric-plugin:git-status {workspace_id}")
        print(f"  - Sync:   fabric-plugin:git-update {workspace_id}")
        return 0
    else:
        print(f"[ERROR] Unexpected status: {response.status}")
        return 2


def main():
    cli = SkillCLI('git_connect.py',
                   'Connect a workspace to a Git repository '
                   '(Azure DevOps or GitHub)')
    cli.workspace()
    cli.opt('--provider', required=True, choices=['AzureDevOps', 'GitHub'],
            help='Git provider type')
    cli.opt('--org', required=True, help='Organization (or GitHub owner) name')
    cli.opt('--project', help='Project name (required for AzureDevOps)')
    cli.opt('--repo', required=True, help='Repository name')
    cli.opt('--branch', required=True, help='Branch name')
    cli.opt('--directory', default='/', help='Directory in the repo (default: /)')
    args = cli.parse()

    if args.provider == 'AzureDevOps' and not args.project:
        print("[ERROR] --project is required for AzureDevOps provider")
        sys.exit(1)

    sys.exit(connect_git(args.workspace_id, args))


if __name__ == "__main__":
    main()
